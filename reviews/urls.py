from django.urls import path
from . import views

urlpatterns = [
    path('album/<int:album_id>/criar/', views.criar_review, name='criar_reviews'),
    path('<int:album_id>/editar/', views.editar_review, name='editar_reviews'),
    path('<int:review_id>/deletar', views.deletar_review, name='deletar_reviews'),

]