from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class PaymentTransaction(models.Model):
    STATUS_INITIATED = 'initiated'
    STATUS_VALIDATED = 'validated'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_INVALID = 'invalid'

    STATUS_CHOICES = [
        (STATUS_INITIATED, 'Initiated'),
        (STATUS_VALIDATED, 'Validated'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_INVALID, 'Invalid'),
    ]

    booking_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    booking_object_id = models.PositiveBigIntegerField()
    booking = GenericForeignKey('booking_content_type', 'booking_object_id')

    tran_id = models.CharField(max_length=80, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_INITIATED)

    session_key = models.CharField(max_length=120, blank=True)
    val_id = models.CharField(max_length=120, blank=True)
    bank_tran_id = models.CharField(max_length=120, blank=True)
    card_type = models.CharField(max_length=120, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.tran_id
