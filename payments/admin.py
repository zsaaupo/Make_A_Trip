from django.contrib import admin

from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['tran_id', 'status', 'amount', 'currency', 'bank_tran_id', 'created_at']
    list_filter = ['status', 'currency']
    search_fields = ['tran_id', 'bank_tran_id', 'val_id']
