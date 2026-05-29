from django.db import models
from usuarios.models import Perfil


# Os imports de Album e Clube foram removidos daqui

class Review(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    album = models.ForeignKey('albuns.Album', on_delete=models.CASCADE)
    clube = models.ForeignKey('clubes.Clube', on_delete=models.CASCADE, null=True, blank=True,
                              related_name="reviews_clube")

    nota = models.PositiveIntegerField()
    comentario = models.TextField(max_length=1000, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('perfil', 'album', 'clube')
        ordering = ['data_criacao']

    def __str__(self):
        contexto = f" no clube {self.clube.nome_clube}" if self.clube else " Individual"
        return f"Nota {self.nota} de Perfil {self.perfil.id} para {self.album.titulo}{contexto}"