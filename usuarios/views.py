from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from .forms import DiscoraCadastroForm, DiscoraLoginForm
def home(request):
    return render(request, 'usuarios/home.html')

def cadastro_view(request):
    if request.method == 'POST':
        form = DiscoraCadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            auth_login(request, usuario)  # Loga o usuário automaticamente
            return redirect('home')  # Redireciona para a home (ou outra tela de sua preferência)
    else:
        form = DiscoraCadastroForm()
    return render(request, 'usuarios/cadastro.html', {'form': form})

class DiscoraLoginView(LoginView):
    template_name = 'usuarios/login.html'
    authentication_form = DiscoraLoginForm

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def perfil_view(request):
    return render(request, 'usuarios/perfil.html')
