
from django.conf import settings
from django.db import models


class Pedido(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("confirmado", "Confirmado"),
        ("cancelado", "Cancelado"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pedidos",
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default="pendiente",
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.pk} - {self.usuario}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    producto = models.ForeignKey(
        "productos.Producto",
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
