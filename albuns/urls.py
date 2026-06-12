from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_album, name='listar_albuns'),
    path('<int:album_id>/', views.detalhar_album, name='detalhar_album'),
    path('adicionar/', views.adicionar_album, name='adicionar_album'),
    path('registrar-escuta/<int:album_id>/', views.registrar_escuta, name='registrar_escuta'),
    # Endpoint unificado do Vinil da Home
    path('api/lote-vinil/', views.vinil, name='lote_vinil_api'),
]