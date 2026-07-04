from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from core.constants import BookingStatus, PaymentMethod
from core.utils import notify_status_change
from .models import PaymentTransaction


class SSLCommerzError(Exception):
    pass


def sslcommerz_is_configured():
    return bool(settings.SSLCOMMERZ_STORE_ID and settings.SSLCOMMERZ_STORE_PASSWORD)


def ensure_sslcommerz_configured():
    if not sslcommerz_is_configured():
        raise SSLCommerzError("SSLCommerz Store ID and Store Password are not configured.")


def payment_redirect_response(request, booking, serializer_class, service_label):
    data = serializer_class(booking, context={'request': request}).data
    if booking.payment_method != PaymentMethod.PAY_NOW:
        return data

    data['payment_url'] = create_sslcommerz_session(request, booking, service_label)
    return data


def create_sslcommerz_session(request, booking, service_label):
    ensure_sslcommerz_configured()
    transaction, _ = PaymentTransaction.objects.get_or_create(
        tran_id=booking.invoice_id,
        defaults={
            'booking_content_type': ContentType.objects.get_for_model(booking),
            'booking_object_id': booking.pk,
            'amount': booking.total_amount,
            'currency': settings.SSLCOMMERZ_CURRENCY,
        },
    )

    payload = _build_init_payload(request, booking, service_label)
    try:
        response = requests.post(settings.SSLCOMMERZ_INIT_URL, data=payload, timeout=20)
        response.raise_for_status()
        gateway_data = response.json()
    except (requests.RequestException, ValueError) as exc:
        transaction.status = PaymentTransaction.STATUS_FAILED
        transaction.gateway_response = {'error': str(exc)}
        transaction.save(update_fields=['status', 'gateway_response', 'updated_at'])
        raise SSLCommerzError("Could not initialize SSLCommerz payment.") from exc

    gateway_url = gateway_data.get('GatewayPageURL') or gateway_data.get('redirectGatewayURL')
    if gateway_data.get('status') != 'SUCCESS' or not gateway_url:
        transaction.status = PaymentTransaction.STATUS_FAILED
        transaction.gateway_response = gateway_data
        transaction.save(update_fields=['status', 'gateway_response', 'updated_at'])
        failed_reason = gateway_data.get('failedreason') or "SSLCommerz did not return a payment page."
        raise SSLCommerzError(failed_reason)

    transaction.session_key = gateway_data.get('sessionkey', '')
    transaction.gateway_response = gateway_data
    transaction.save(update_fields=['session_key', 'gateway_response', 'updated_at'])
    return gateway_url


def process_gateway_callback(data, cancelled=False):
    tran_id = data.get('tran_id')
    if not tran_id:
        raise SSLCommerzError("Missing transaction ID.")

    transaction = PaymentTransaction.objects.select_related('booking_content_type').filter(tran_id=tran_id).first()
    if not transaction:
        raise SSLCommerzError("Unknown transaction ID.")

    booking = transaction.booking
    if cancelled:
        transaction.status = PaymentTransaction.STATUS_CANCELLED
        transaction.gateway_response = dict(data)
        transaction.save(update_fields=['status', 'gateway_response', 'updated_at'])
        _update_booking_status(booking, BookingStatus.CANCELLED, "Payment was cancelled.")
        return transaction

    gateway_status = data.get('status')
    if gateway_status not in ('VALID', 'VALIDATED'):
        transaction.status = PaymentTransaction.STATUS_FAILED
        transaction.gateway_response = dict(data)
        transaction.save(update_fields=['status', 'gateway_response', 'updated_at'])
        _update_booking_status(booking, BookingStatus.DECLINED, "Payment failed.")
        return transaction

    validation_data = _validate_transaction(data.get('val_id'))
    if not _validation_matches(transaction, validation_data):
        transaction.status = PaymentTransaction.STATUS_INVALID
        transaction.val_id = data.get('val_id', '')
        transaction.gateway_response = validation_data
        transaction.save(update_fields=['status', 'val_id', 'gateway_response', 'updated_at'])
        _update_booking_status(booking, BookingStatus.DECLINED, "Payment validation failed.")
        raise SSLCommerzError("SSLCommerz validation failed.")

    transaction.status = PaymentTransaction.STATUS_VALIDATED
    transaction.val_id = validation_data.get('val_id', data.get('val_id', ''))
    transaction.bank_tran_id = validation_data.get('bank_tran_id', data.get('bank_tran_id', ''))
    transaction.card_type = validation_data.get('card_type', data.get('card_type', ''))
    transaction.gateway_response = validation_data
    transaction.save(update_fields=[
        'status', 'val_id', 'bank_tran_id', 'card_type', 'gateway_response', 'updated_at',
    ])
    _update_booking_status(booking, BookingStatus.CONFIRMED, "")
    return transaction


def _build_init_payload(request, booking, service_label):
    customer = booking.customer
    profile = getattr(customer, 'profile', None)
    customer_name = getattr(profile, 'full_name', '') or customer.get_username()
    phone = getattr(profile, 'phone', '') or '01700000000'

    return {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'total_amount': str(booking.total_amount),
        'currency': settings.SSLCOMMERZ_CURRENCY,
        'tran_id': booking.invoice_id,
        'success_url': _absolute_url(request, 'payment-success'),
        'fail_url': _absolute_url(request, 'payment-fail'),
        'cancel_url': _absolute_url(request, 'payment-cancel'),
        'ipn_url': _absolute_url(request, 'payment-ipn'),
        'product_name': f"Make A Trip {service_label}",
        'product_category': service_label,
        'product_profile': 'general',
        'cus_name': customer_name,
        'cus_email': customer.email,
        'cus_add1': 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_postcode': '1000',
        'cus_country': 'Bangladesh',
        'cus_phone': phone,
        'shipping_method': 'NO',
        'num_of_item': 1,
    }


def _validate_transaction(val_id):
    if not val_id:
        raise SSLCommerzError("Missing validation ID.")
    ensure_sslcommerz_configured()
    params = {
        'val_id': val_id,
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'v': 1,
        'format': 'json',
    }
    try:
        response = requests.get(settings.SSLCOMMERZ_VALIDATION_URL, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise SSLCommerzError("Could not validate SSLCommerz payment.") from exc


def _validation_matches(transaction, validation_data):
    if validation_data.get('status') not in ('VALID', 'VALIDATED'):
        return False
    if validation_data.get('tran_id') != transaction.tran_id:
        return False
    if validation_data.get('currency') and validation_data.get('currency') != transaction.currency:
        return False
    try:
        paid_amount = Decimal(str(validation_data.get('amount')))
    except (InvalidOperation, TypeError):
        return False
    return paid_amount == transaction.amount


def _update_booking_status(booking, status, decline_reason):
    if not booking:
        return
    if booking.status == status:
        return

    booking.status = status
    update_fields = ['status']
    if status == BookingStatus.DECLINED:
        booking.decline_reason = decline_reason
        update_fields.append('decline_reason')
    booking.save(update_fields=update_fields)
    notify_status_change(booking, booking.invoice_id, _service_label_for_booking(booking))


def _absolute_url(request, route_name):
    configured_base = settings.SSLCOMMERZ_CALLBACK_BASE_URL.rstrip('/')
    if configured_base:
        return configured_base + reverse(route_name)
    return request.build_absolute_uri(reverse(route_name))


def _service_label_for_booking(booking):
    if hasattr(booking, 'room_id'):
        return 'hotel room'
    if hasattr(booking, 'bus_id'):
        return 'bus'
    if hasattr(booking, 'car_id'):
        return 'car'
    if hasattr(booking, 'package_id'):
        return 'tour package'
    return 'booking'
