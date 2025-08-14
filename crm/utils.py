import random
import string
import requests
import json
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist # Importado para manter a compatibilidade

# Define o conjunto de caracteres especiais permitidos
ALLOWED_SPECIAL_CHARS = ',.!?@#$%&*-_=+/-'

def generate_random_password(length=12):
    """
    Gera uma senha aleatória forte com o comprimento especificado.
    """
    if length < 4:
        raise ValueError("O comprimento da senha deve ser de pelo menos 4 caracteres.")

    all_chars = string.ascii_letters + string.digits + ALLOWED_SPECIAL_CHARS

    password_chars = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(ALLOWED_SPECIAL_CHARS)
    ]

    for _ in range(length - len(password_chars)):
        password_chars.append(random.choice(all_chars))

    random.shuffle(password_chars)
    return "".join(password_chars)

# --- VERSÃO DE PRODUÇÃO (CHAMADA DE API REAL) ---
# Use esta versão para tentar a comunicação real com o servidor Vercel.
def provisionar_admin_em_instancia_mock(instancia_url, api_key, username, email, password, stripe_subscription_id):
    """
    Envia as informações do novo admin para a API da instância de templates.
    """
    url = f"{instancia_url}external/admin-users/"
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': api_key,
    }
    
    payload = {
        "username": username,
        "email": email,
        "password": password,
        "stripe_subscription_id": stripe_subscription_id
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Levanta um erro para status 4xx/5xx
        print(f"DEBUG: Admin {username} provisionado com sucesso na instância em {instancia_url}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha ao provisionar admin na instância: {e}")
        print(f"ERRO: Resposta da API (se disponível): {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
        return False


# --- VERSÃO MOCK (USADA SE A CONEXÃO REAL FALHAR) ---
# Se a versão acima não funcionar devido a restrições do PythonAnywhere,
# comente a função acima e descomente a função abaixo.
# def provisionar_admin_em_instancia_mock(instancia_url, api_key, username, email, password, stripe_subscription_id):
#     """
#     Função mock para simular o provisionamento do admin na instância de templates.
#     Retorna True para permitir que o fluxo de e-mail continue.
#     """
#     print(f"DEBUG MOCK: Simulação de provisionamento para {username} em {instancia_url}.")
#     return True