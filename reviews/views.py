from django.shortcuts import render, redirect

def criar_review(request, album_id):
    return render(request, 'reviews/criar.html')

def editar_review(request, review_id):
    return render(request, 'reviews/editar.html')

def deletar_review(request, review_id):
    return redirect('home')