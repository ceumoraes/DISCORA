from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import transaction

class Perfil(models.Model):
    TIPO_PERFIL = [
        ('U', 'Usuário'),
        ('G', 'Grupo')
    ]
    tipo = models.CharField(max_length=1, choices=TIPO_PERFIL)

    def __str__(self):
        return f"Perfil ID {self.id} ({self.get_tipo_display()})"


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
        if not self.perfil_ptr_id:
            with transaction.atomic():
                perfil_pai = Perfil.objects.create(tipo='U')
                self.perfil_ptr = perfil_pai
                super().save(*args, **kwargs)
        else:
            self.tipo = 'U'
            super().save(*args, **kwargs)

    def __str__(self):
        return self.username