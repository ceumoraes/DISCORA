from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_clubes, name='listar_clubes'),
    path('<int:clube_id>', views.detalhar_clube, name='detalhar_clube'),
    path('criar/', views.criar_clube, name='criar_clube'),
    path('<int:clube_id>/entrar/', views.aderir_clube, name='entrar_clube'),
]