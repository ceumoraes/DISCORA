from django.db import models
from django.contrib.auth.models import AbstractUser


# 1. Tabela Pai de Perfil (Generalização)
class Perfil(models.Model):
    TIPO_PERFIL = [
        ('U', 'Usuário'),
        ('G', 'Grupo')
    ]
    tipo = models.CharField(max_length=1, choices=TIPO_PERFIL)

    def __str__(self):
        return f"Perfil ID {self.id} ({self.get_tipo_display()})"


# 2. Modelo de Usuário (Especialização)
class Usuario(AbstractUser):
    perfil_ptr = models.OneToOneField(
        Perfil,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True
    )

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # Garante a inserção correta na tabela pai Perfil
        if not self.perfil_ptr_id:
            perfil_pai = Perfil.objects.create(tipo='U')
            self.perfil_ptr = perfil_pai
        else:
            self.tipo = 'U'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username