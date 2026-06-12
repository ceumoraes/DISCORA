from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from usuarios.models import Usuario  # Buscando o model no app de albuns

class DiscoraCadastroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ['username', 'email']

        labels = { 'username': 'Nome de Usuário', 'email': 'E-mail'}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado no Discora.")
        return email

class DiscoraLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}), label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
