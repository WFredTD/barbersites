# crm/views.py

from django.shortcuts import render
from .models import Plano # Importa o modelo Plano do CRM
# NOTA: Removido 'from crm.forms import PlanoForms' pois PlanoForms não é usado aqui.
# NOTA: Removidas as views 'checkout_plano' e 'plano_form' se existiam, pois não fazem parte
#       do fluxo de checkout Stripe que implementamos em 'payments/views.py'.

def index(request):
    """
    Renderiza a página inicial (landing page) do seu site.
    Carrega todos os Planos do CRM para exibição direta na página.
    """
    # Busca todos os objetos Plano no banco de dados e os ordena pelo valor.
    # Isso permite que os planos sejam exibidos na landing page.
    planos = Plano.objects.all().order_by('valor')
    context = {
        'planos': planos, # Passa a lista de planos para o template index.html.
        # Você pode passar outras variáveis se sua index precisar delas.
    }
    # Renderiza o template 'crm/index.html'.
    # Este template deve estar em 'sua_pasta_do_projeto/templates/crm/index.html'.
    return render(request, 'crm/index.html', context)




