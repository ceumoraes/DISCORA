from django.shortcuts import render, redirect

def listar_clubes(request):
    return render(request, 'clubes/listar.html')
def detalhar_clube(request, clube_id):
    return render(request, 'clubes/detalhar.html')

def criar_clube(request):
    return render(request, 'clubes/criar.html')

def aderir_clube(request, clube_id):
    return redirect('listar_clubes')