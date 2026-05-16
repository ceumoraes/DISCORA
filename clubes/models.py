from django.db import models
from usuarios.models import Perfil


class Clube(models.Model):
    nome_clube = models.CharField(max_length=100)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    membros = models.ManyToManyField(
        Perfil,
        through='MembroGrupo',
        related_name='clubes_que_participo'
    )

    def __str__(self):
        return self.nome_clube


class MembroGrupo(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE)

    # Suas colunas customizadas da junção:
    data_entrada = models.DateTimeField(auto_now_add=True)
    admin = models.BooleanField(default=False)  # True se for dono/admin, False se for membro comum

    class Meta:
        unique_together = ('perfil', 'clube')

    def __str__(self):
        funcao = "Admin" if self.admin else "Membro"
        return f"{self.perfil.usuario.username} é {funcao} no clube {self.clube.nome_clube}"