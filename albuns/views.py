from django.shortcuts import render, redirect
from django.http import JsonResponse
from .services import VitrineService  # <--- Importamos o novo serviço focado na Home


def listar_album(request):
    return render(request, 'albuns/listar.html')


def detalhar_album(request, album_id):
    return render(request, 'albuns/detalhe.html')


def adicionar_album(request):
    return render(request, 'albuns/adicionar.html')


def registrar_escuta(request, album_id):
    return redirect('listar_album')


def vinil(request):
    lote_albuns = VitrineService.obter_lote_aleatorio_home()
    return JsonResponse({'albuns': lote_albuns}, status=200)