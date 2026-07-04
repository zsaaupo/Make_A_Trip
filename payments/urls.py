from django.urls import path

from . import views

urlpatterns = [
    path('sslcommerz/success/', views.payment_success, name='payment-success'),
    path('sslcommerz/fail/', views.payment_fail, name='payment-fail'),
    path('sslcommerz/cancel/', views.payment_cancel, name='payment-cancel'),
    path('sslcommerz/ipn/', views.payment_ipn, name='payment-ipn'),
]
