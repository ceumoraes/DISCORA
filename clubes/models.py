from django.db import models
from usuarios.models import Perfil
# O import de Album foi removido daqui

class Clube(models.Model):
    nome_clube = models.CharField(max_length=100)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    membros = models.ManyToManyField(Perfil, through='MembroGrupo', related_name='clubes_que_participo')

    def __str__(self):
        return self.nome_clube

class MembroGrupo(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE)
    data_entrada = models.DateTimeField(auto_now_add=True)
    admin = models.BooleanField(default=False)
    ultima_vez_curador = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('perfil', 'clube')

    def __str__(self):
        funcao = "Admin" if self.admin else "Membro"
        return f"{self.perfil.usuario.username} é {funcao} no clube {self.clube.nome_clube}"

class Queue(models.Model):
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE, related_name='queue')
    # Alterado para string 'albuns.Album'
    album = models.ForeignKey('albuns.Album', on_delete=models.CASCADE)
    sugerido_por = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True)
    adicionado_em = models.DateTimeField(auto_now_add=True)
    posicao = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['posicao', 'adicionado_em']
        unique_together = ('clube', 'album')

    def __str__(self):
        return f"{self.album.titulo} na fila de {self.clube.nome_clube}"