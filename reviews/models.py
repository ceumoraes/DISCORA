from django.db import models
from usuarios.models import Perfil
from albuns.models import Album

class Review(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    nota = models.PositiveIntegerField()

    comentario = models.TextField(max_length=1000, blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('perfil', 'album')
        ordering = ['data_criacao']

    def __str__(self):
        return f"Nota {self.nota} de {self.perfil.usuario.username} para {self.album.titulo}"
