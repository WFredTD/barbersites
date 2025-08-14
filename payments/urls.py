# payments/urls_alpha.py

from django.urls import path

from . import views

urlpatterns = [
    path(
        'create-checkout-session/<int:plano_pk>/',
        views.create_checkout_session,
        name='create_checkout_session',
    ),
    path(
        'checkout/<int:plano_pk>/', views.checkout_page, name='checkout_page'
    ),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]