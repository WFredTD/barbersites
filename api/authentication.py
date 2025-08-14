from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # CORREÇÃO: LÊ O HEADER X-API-KEY
        api_key = request.headers.get("X-API-KEY")
        
        if not api_key:
            return None # Retorna None se o cabeçalho não existir.

        allowed_api_key = getattr(settings, 'CRM_TO_TEMPLATES_API_KEY', None)

        if not allowed_api_key:
            logger.error("CRM_TO_TEMPLATES_API_KEY não configurada no settings.py.")
            raise AuthenticationFailed("Erro de configuração da API.")
        
        if api_key != allowed_api_key:
            raise AuthenticationFailed("Chave de API inválida.")

        # Se a chave for válida, a autenticação é um sucesso.
        return (None, None)