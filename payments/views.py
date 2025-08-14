# payments/views_alpha.py (VERSÃO FINAL E CORRIGIDA)

import json
import stripe
import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from datetime import datetime, timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from crm.models import Plano, Usuario, Barbearia, Assinatura
from crm.forms import UsuarioForm, BarbeariaForm
# <<< CORREÇÃO: Removido a importação redundante do generate_random_password >>>
from crm.utils import provisionar_admin_em_instancia_mock, generate_random_password

MOCK_INSTANCE_URLS = [
    "https://templates-barber.vercel.app/",
    "https://templates-barber-2.vercel.app/",
    "https://templates-barber-3.vercel.app/",
]

stripe.api_key = settings.STRIPE_SECRET_KEY

def list_plans(request):
    planos = Plano.objects.all().order_by('valor')
    context = {'planos': planos, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY}
    return render(request, 'payments/list_plans.html', context)

@csrf_exempt
def create_checkout_session(request, plano_pk):
    plano = get_object_or_404(Plano, pk=plano_pk)
    if request.method == 'POST':
        if not plano.stripe_price_id:
            return JsonResponse({'error': 'Este plano não tem um ID de preço configurado no Stripe.'}, status=400)
        try:
            data = json.loads(request.body) #TODO: Verificar se é request.payload ou request.body, que estava antes
            usuario_data = data.get('usuario_data')
            barbearia_data = data.get('barbearia_data')

            # <<< CORREÇÃO: Removido a validação do usuario_form aqui para lidar com multi-assinatura >>>
            barbearia_form_validation = BarbeariaForm(data=barbearia_data)

            if barbearia_form_validation.is_valid():
                barbearia_cleaned_data = barbearia_form_validation.cleaned_data

                try:
                    usuario = Usuario.objects.get(email=usuario_data['email'])
                    print("DEBUG: Usuário existente encontrado.")
                except Usuario.DoesNotExist:
                    usuario = Usuario.objects.create(
                        email=usuario_data['email'], nome_completo=usuario_data['nome_completo'], telefone=usuario_data['telefone'], aceite_termos=usuario_data.get('aceite_termos', False), receber_notificacoes=usuario_data.get('receber_notificacoes', False))
                    print("DEBUG: Novo usuário criado com sucesso.")

                barbearia_count = Barbearia.objects.count()
                url_index = barbearia_count % len(MOCK_INSTANCE_URLS)
                allocated_url = MOCK_INSTANCE_URLS[url_index]

                barbearia, _ = Barbearia.objects.get_or_create(nome_barbearia=barbearia_cleaned_data['nome_barbearia'], defaults={'endereco': barbearia_cleaned_data['endereco'], 'cidade': barbearia_cleaned_data['cidade'], 'estado': barbearia_cleaned_data['estado'], 'cep': barbearia_cleaned_data['cep'], 'usuario_responsavel': usuario, 'instance_url': allocated_url})
                customer_stripe_id = usuario.stripe_customer_id
                session_params = {'line_items': [{'price': plano.stripe_price_id, 'quantity': 1}], 'mode': 'subscription', 'success_url': request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}', 'cancel_url': request.build_absolute_uri(reverse('payment_cancel')), 'metadata': {'barbearia_nome': barbearia_data['nome_barbearia'], 'usuario_email_origem': usuario_data['email']}}
                if customer_stripe_id:
                    session_params['customer'] = customer_stripe_id
                else:
                    session_params['customer_email'] = usuario.email
                if plano.trial_period_days > 0:
                    session_params['subscription_data'] = {'trial_period_days': plano.trial_period_days}
                checkout_session = stripe.checkout.Session.create(**session_params)
                if not usuario.stripe_customer_id and checkout_session.customer:
                    usuario.stripe_customer_id = checkout_session.customer
                    usuario.save()
                    print(f"DEBUG: stripe_customer_id salvo para o usuário {usuario.id}.")
                return JsonResponse({'id': checkout_session.id})
            else:
                errors = {'barbearia_errors': barbearia_form_validation.errors.as_json()}
                return JsonResponse({'error': 'Dados do formulário inválidos.', 'details': errors}, status=400)
        except Exception as e:
            print(f"ERRO ao criar sessão de checkout: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método não permitido.'}, status=405)

def payment_success(request):
    session_id = request.GET.get('session_id')
    session = None
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            return render(request, 'payments/error.html', {'message': f"Erro ao recuperar sessão: {e}"})
    return render(request, 'payments/success.html', {'session': session})

def payment_cancel(request):
    return render(request, 'payments/cancel.html')

def checkout_page(request, plano_pk):
    plano = get_object_or_404(Plano, pk=plano_pk)
    usuario_form_display = UsuarioForm()
    barbearia_form_display = BarbeariaForm()
    context = {'plano': plano, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY, 'usuario_form': usuario_form_display, 'barbearia_form': barbearia_form_display}
    return render(request, 'payments/checkout.html', context)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body #TODO: Verificar se é request.payload ou request.body, que estava antes
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    print("Webhook chamado")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        print(f"Erro no Webhook: Payload inválido: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"Erro no Webhook: Assinatura inválida: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        print(f"Erro inesperado na construção do evento webhook: {e}")
        return HttpResponse(status=400)

    print(f"Evento recebido: {event['type']}")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(f"Webhook: Checkout Session Completed - Session ID: {session.id}")

        if session.mode == 'subscription':
            subscription_id = session.subscription
            customer_email = session.metadata.get('usuario_email_origem')

            try:
                stripe_subscription_obj = stripe.Subscription.retrieve(subscription_id)

                usuario = Usuario.objects.get(email=customer_email)
                barbearia = Barbearia.objects.get(nome_barbearia=session.metadata.get('barbearia_nome'))
                line_items_from_session = stripe.checkout.Session.list_line_items(session.id)
                plano = Plano.objects.get(stripe_price_id=line_items_from_session.data[0].price.id)

                if not usuario.stripe_customer_id and session.customer:
                    usuario.stripe_customer_id = session.customer
                    usuario.save()
                    print(f"DEBUG: stripe_customer_id salvo para o usuário {usuario.id}.")

                status_assinatura = getattr(stripe_subscription_obj, 'status', None)
                cancel_at_period_end = getattr(stripe_subscription_obj, 'cancel_at_period_end', False)
                subscription_created = getattr(stripe_subscription_obj, 'created', None)
                trial_end = getattr(stripe_subscription_obj, 'trial_end', None)

                data_inicio_dt = datetime.fromtimestamp(subscription_created, tz=timezone.utc) if subscription_created else None
                trial_end_dt = datetime.fromtimestamp(trial_end, tz=timezone.utc) if trial_end else None

                assinatura, created_sub = Assinatura.objects.get_or_create(
                    stripe_subscription_id=subscription_id,
                    defaults={
                        'usuario': usuario,
                        'plano': plano,
                        'barbearia': barbearia,
                        'status_assinatura': status_assinatura,
                        'cancel_at_period_end': cancel_at_period_end,
                        'data_inicio': data_inicio_dt,
                        'trial_end': trial_end_dt,
                    }
                )

                if created_sub:
                    print(f"DEBUG: Assinatura {assinatura.pk} criada com status {assinatura.status_assinatura}.")
                    assinatura.conceder_acesso()
                else:
                    print(f"DEBUG: Assinatura {assinatura.pk} já existia. Apenas atualizada.")
            except Exception as e:
                print(f"ERRO CRÍTICO no webhook checkout.session.completed: {e}")
                return HttpResponse(status=500)

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        subscription_id = subscription.id
        print(f"Webhook: Subscription Updated - ID: {subscription_id} - Status: {subscription.status}")
        try:
            assinatura = Assinatura.objects.get(stripe_subscription_id=subscription_id)
            assinatura.status_assinatura = subscription.status
            assinatura.cancel_at_period_end = subscription.cancel_at_period_end
            current_period_end = getattr(subscription, 'current_period_end', None)
            if current_period_end:
                assinatura.data_expiracao = datetime.fromtimestamp(current_period_end, tz=timezone.utc)
            assinatura.save()
            print(f"Assinatura {assinatura.pk} atualizada com sucesso.")
        except Assinatura.DoesNotExist:
            print(f"ERRO: Assinatura com Stripe ID {subscription_id} não encontrada.")
            return HttpResponse(status=404)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        subscription_id = subscription.id
        print(f"Webhook: Subscription Deleted - ID: {subscription_id}")
        try:
            assinatura = Assinatura.objects.get(stripe_subscription_id=subscription_id)
            assinatura.status_assinatura = 'canceled'
            assinatura.save()
            print(f"Assinatura {assinatura.pk} deletada/cancelada com sucesso no DB.")
        except Assinatura.DoesNotExist:
            print(f"ERRO: Assinatura com Stripe ID {subscription_id} não encontrada para deleção.")
            return HttpResponse(status=404)

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        print(f"Webhook: Invoice Payment Succeeded - Invoice ID: {invoice.id}")
        if hasattr(invoice, 'subscription') and invoice.subscription:
            try:
                assinatura = Assinatura.objects.get(stripe_subscription_id=invoice.subscription)
                payment_intent = getattr(invoice, 'payment_intent', None)
                period_start = getattr(invoice, 'period_start', None)
                period_end = getattr(invoice, 'period_end', None)

                assinatura.status_assinatura = 'active'
                if payment_intent:
                    assinatura.id_transacao_pagamento = payment_intent
                if period_start:
                    assinatura.data_inicio = datetime.fromtimestamp(period_start, tz=timezone.utc)
                if period_end:
                    assinatura.data_expiracao = datetime.fromtimestamp(period_end, tz=timezone.utc)

                assinatura.save()
                print(f"Assinatura {assinatura.pk} teve fatura paga com sucesso. Dados de transação e expiração atualizados.")
            except Assinatura.DoesNotExist:
                print(f"ERRO: Assinatura local com ID {invoice.subscription} não encontrada.")
                return HttpResponse(status=404)

    return HttpResponse(status=200)