# crm/forms.py

# Importa o módulo 'forms' do Django. Essencial para criar formulários.
from django import forms
# Importa os modelos do seu próprio aplicativo 'crm' para criar ModelForms.
from .models import Barbearia, Usuario, Assinatura # Certifique-se de que todos os modelos são importados

# --- Formulário Django para o modelo Barbearia ---
# (Baseado no ModelForm, que facilita a criação de formulários a partir de modelos)
class BarbeariaForm(forms.ModelForm):
    """
    Formulário Django para coletar e validar dados da Barbearia.
    Este formulário é gerado automaticamente a partir do modelo 'Barbearia'
    definido em crm/models.py.
    """
    class Meta:
        model = Barbearia # Vincula este formulário ao modelo Barbearia.
        # Define quais campos do modelo 'Barbearia' o formulário irá incluir.
        # Incluímos apenas os campos que o usuário preenche na página de checkout.
        fields = ['nome_barbearia', 'endereco', 'cidade', 'estado', 'cep']

        # 'widgets' são usados para personalizar a renderização HTML dos campos do formulário.
        # Aqui, estamos adicionando classes CSS do Bootstrap ('form-control', 'form-select')
        # e placeholders para melhor UX.
        widgets = {
            'nome_barbearia': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            # O choices será setado no __init__ do formulário para garantir que o modelo já foi carregado.
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
        }
        # 'labels' são usados para definir o texto exibido ao lado de cada campo do formulário.
        labels = {
            'nome_barbearia': 'Nome da Barbearia',
            'endereco': 'Endereço',
            'cidade': 'Cidade',
            'estado': 'Estado',
            'cep': 'CEP',
        }

    # Sobrescrevemos o método __init__ do formulário.
    # Isso é necessário para atribuir as choices do campo 'estado' dinamicamente.
    # Garante que o modelo 'Barbearia' e suas choices já foram totalmente carregados antes de tentar acessá-los.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Verifica se o campo 'estado' existe no formulário.
        if 'estado' in self.fields:
            # Obtém as escolhas do campo 'estado' diretamente do modelo 'Barbearia'.
            model_choices = list(Barbearia._meta.get_field('estado').choices or [])

            # Adiciona uma opção padrão "Selecione" no início das escolhas, se ela ainda não existir.
            if not self.initial.get('estado') and ('', 'Selecione') not in model_choices:
                self.fields['estado'].widget.choices = [('', 'Selecione')] + model_choices
            else:
                self.fields['estado'].widget.choices = model_choices


# --- Formulário Django para o modelo Usuário ---
class UsuarioForm(forms.ModelForm):
    """
    Formulário Django para coletar e validar dados do Usuário.
    Baseado no modelo 'Usuario' do crm/models.py.
    """
    class Meta:
        model = Usuario # Vincula este formulário ao modelo Usuario.
        # Incluímos os campos que o usuário preenche no formulário de cadastro.
        # 'aceite_termos' e 'receber_notificacoes' também são incluídos para serem validados.
        fields = ['nome_completo', 'email', 'telefone', 'aceite_termos', 'receber_notificacoes']

        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            # Para checkboxes, usamos CheckboxInput e adicionamos a classe Bootstrap.
            'aceite_termos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receber_notificacoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome_completo': 'Nome Completo',
            'email': 'Email',
            'telefone': 'Telefone',
            'aceite_termos': 'Aceito os Termos de Uso', # O label será o texto da checkbox.
            'receber_notificacoes': 'Desejo receber notificações', # O label será o texto da checkbox.
        }
        help_texts = {
            'email': 'Endereço de e-mail único para contato.',
        }

# --- Formulário Django para o modelo Assinatura ---
# (Embora não seja usado diretamente no fluxo de criação da assinatura via Stripe Checkout,
# é útil ter para outras operações, como edição de assinaturas no Admin ou em outras views.)
class AssinaturaForm(forms.ModelForm):
    """
    Formulário Django para o modelo Assinatura.
    Principalmente útil para gerenciamento em interfaces administrativas.
    """
    class Meta:
        model = Assinatura
        # Incluímos campos de relacionamento para que possam ser selecionados em formulários.
        fields = ['usuario', 'barbearia', 'plano']
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'barbearia': forms.Select(attrs={'class': 'form-control'}),
            'plano': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'usuario': 'Usuário',
            'barbearia': 'Barbearia',
            'plano': 'Plano',
        }





# Em que situação podemos usar uma nova camada forms no Django.

# Resposta:

# Em várias situações, principalmente quando precisar de validação de dados,
# limpeza de dados e renderização de formulários.

# Veja as principais situações:

# - Processamento de Entrada do Usuário (aplicação dos métodos GET e POST);

# - Validação e Limpeza de Dados (*garantir a integridade dos dados antes de salvá-los no banco de dados ou processá-los de outra forma);

# - Criação de Formulários para Modelos (* método: ModelForms)

# - Reaproveitamento de Lógica (reaproveitamento do código);

# - Integração com Ferramentas de Terceiros (* Muitos pacotes e bibliotecas de terceiros para Django - como Django REST Framework, Django Crispy Forms, etc.) se integram perfeitamente com o sistema de forms.)

# - Formulários sem um Modelo Associado: Nem todo formulário precisa estar diretamente ligado a um modelo de banco de dados.
# Dentro podemos usar a nossa orientação a objetos para criar formulários que representem os modelos do Django.




# from django import forms
# from .models import Barbearia, Usuario, Assinatura

# class BarbeariaForm(forms.ModelForm):
#     class Meta:
#         model = Barbearia
#         fields = ['nome_barbearia', 'endereco', 'cep']
#         widgets = {
#             'nome_barbearia': forms.TextInput(attrs={'class': 'form-control'}),
#             'endereco': forms.TextInput(attrs={'class': 'form-control'}),
#             'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
#         }
#         labels = {
#             'nome_barbearia': 'Nome da Barbearia',
#             'endereco': 'Endereço',
#             'cep': 'CEP',
#         }
# class UsuarioForm(forms.ModelForm):
#     class Meta:
#         model = Usuario
#         fields = ['nome_completo', 'email', 'telefone', 'aceite_termos', 'receber_notificacoes']
#         widgets = {
#             'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXX-XXXX'}),
#             'aceite_termos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'receber_notificacoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }
#         labels = {
#             'nome_completo': 'Nome Completo',
#             'email': 'Email',
#             'telefone': 'Telefone',
#             'aceite_termos': 'Aceitou os Termos de Uso',
#             'receber_notificacoes': 'Deseja receber notificações?',
#         }
# class AssinaturaForm(forms.ModelForm):
#     class Meta:
#         model = Assinatura
#         fields = ['usuario', 'barbearia', 'plano']
#         widgets = {
#             'usuario': forms.Select(attrs={'class': 'form-control'}),
#             'barbearia': forms.Select(attrs={'class': 'form-control'}),
#             'plano': forms.Select(attrs={'class': 'form-control'}),
#         }
#         labels = {
#             'usuario': 'Usuário',
#             'barbearia': 'Barbearia',
#             'plano': 'Plano',
#         }


# # Orientação a Objetos

# from django import forms

# from .models import Plano


# # Herança de classes
# class PlanoForms(forms.Form):
#     nome_plano = forms.CharField(
#         max_length=100,  # quantidade de caracteres
#         required=True,  # campo obrigatório
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#         label='Nome do Plano',  # rótulo do campo
#     )
#     valor = forms.DecimalField(
#         max_digits=10,  # número máximo de dígitos
#         decimal_places=2,  # número de casas decimais
#         required=True,  # campo obrigatório
#         widget=forms.NumberInput(attrs={'class': 'form-control'}),
#         label='Valor do Plano',  # rótulo do campo
#     )
#     descricao = forms.CharField(
#         widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         required=False,  # campo opcional
#         label='Descrição do Plano',  # rótulo do campo
#     )
