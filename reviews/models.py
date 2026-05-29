from django.db import models
from usuarios.models import Perfil
from albuns.models import Album
from clubes.models import Clube


class Review(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    # Campo adicionado para permitir reviews associadas a discussões de clubes específicos
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE, null=True, blank=True, related_name="reviews_clube")

    nota = models.PositiveIntegerField()  # Na View limite o input de 0 a 5
    comentario = models.TextField(max_length=1000, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        # Alterado para que o usuário possa reavaliar o álbum se estiver em clubes diferentes
        unique_together = ('perfil', 'album', 'clube')
        ordering = ['data_criacao']

    def __str__(self):
        contexto = f" no clube {self.clube.nome_clube}" if self.clube else " Individual"
        return f"Nota {self.nota} de Perfil {self.perfil.id} para {self.album.titulo}{contexto}"