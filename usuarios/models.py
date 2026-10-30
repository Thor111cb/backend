
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name="Correo electrónico",
    )

    ROLES = [
    ("admin", "Administrador"),
    ("cliente", "Cliente"),
    ("visitante", "Visitante"),
]

    rol = models.CharField(
        max_length=10,
        choices=ROLES,
        default="cliente",
    )

    def __str__(self):
        return self.email
