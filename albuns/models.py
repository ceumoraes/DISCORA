from django.db import models
from usuarios.models import Perfil

class Album(models.Model):

    id_spotify = models.CharField(max_length = 255, unique = True, null=True, blank=True)
    id_lastfm = models.CharField(max_length = 255, unique = True, null=True, blank=True)

    titulo = models.CharField(max_length=255)
    artista = models.CharField(max_length=255)
    url_capa = models.URLField(max_length = 255, null=True, blank=True)
    ano_lancamento = models.IntegerField(null=True, blank=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.artista} - {self.titulo}"

class Historico(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name="historico_album")
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="historico_perfil")

    data_escutado = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ["-data_escutado"]

    def __str__(self):
        return f"{self.perfil.usuario.username} ouviu {self.album.titulo} em {self.data_escutado.strftime('%d/%m/%Y')}"