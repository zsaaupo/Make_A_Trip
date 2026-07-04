from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .services import SSLCommerzError, process_gateway_callback


def _callback_data(request):
    return request.data if request.method == 'POST' else request.query_params


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def payment_success(request):
    try:
        process_gateway_callback(_callback_data(request))
    except SSLCommerzError:
        return redirect('/bookings/?payment=invalid')
    return redirect('/bookings/?payment=success')


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def payment_fail(request):
    try:
        process_gateway_callback(_callback_data(request))
    except SSLCommerzError:
        pass
    return redirect('/bookings/?payment=failed')


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def payment_cancel(request):
    try:
        process_gateway_callback(_callback_data(request), cancelled=True)
    except SSLCommerzError:
        pass
    return redirect('/bookings/?payment=cancelled')


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def payment_ipn(request):
    try:
        transaction = process_gateway_callback(request.data)
    except SSLCommerzError as exc:
        return Response({'detail': str(exc)}, status=400)
    return Response({'status': transaction.status, 'tran_id': transaction.tran_id})
