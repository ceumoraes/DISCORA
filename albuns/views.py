from django.shortcuts import render, redirect
from django.http import JsonResponse
from .services import OrquestradorAlbunsService


def listar_album(request):
    return render(request, 'albuns/listar.html')


def detalhar_album(request, album_id):
    return render(request, 'albuns/detalhe.html')


def adicionar_album(request):
    return render(request, 'albuns/adicionar.html')


def registrar_escuta(request, album_id):
    return redirect('listar_album')


def vinil(request):
    """
    Entrega o lote sorteado do banco de dados imediatamente.
    A API externa roda de forma assíncrona se o estoque local estiver baixo.
    """
    lote_albuns = OrquestradorAlbunsService.sortear_lote_do_banco()
    return JsonResponse({'albuns': lote_albuns}, status=200)