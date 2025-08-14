# payments/urls.py

from django.urls import path
from . import views_beta as views
# from . import views

urlpatterns = [
    # URL para criar a sessão de checkout no Stripe para um plano específico.
    # Note que agora usamos 'plano_pk' para identificar o plano a ser assinado.
    path(
        'create-checkout-session/<int:plano_pk>/',
        views.create_checkout_session,
        name='create_checkout_session',
    ),
    path(
        'checkout/<int:plano_pk>/', views.checkout_page, name='checkout_page'
    ),  # O nome aqui deve ser 'checkout_page' para corresponder ao index.html
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
