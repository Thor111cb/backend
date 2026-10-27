
from django.db import models


class Producto(models.Model):
    CATEGORIAS = [
        ("Riñoneras", "Riñoneras"),
        ("Pilusos", "Pilusos"),
        ("Chuflines", "Chuflines"),
        ("Accesorios", "Accesorios"),
    ]

    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class ColorProducto(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="colores",
    )
    nombre = models.CharField(max_length=50)
    hexadecimal = models.CharField(max_length=7, default="#000000")

    def __str__(self):
        return f"{self.nombre} - {self.producto.nombre}"


class ImagenProducto(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="imagenes",
    )
    imagen = models.URLField(max_length=500)

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"
