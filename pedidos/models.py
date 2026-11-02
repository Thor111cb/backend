from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Pedido(models.Model):
    """Pedido realizado por un usuario (cliente)."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        ENVIADO = 'ENVIADO', 'Enviado'
        ENTREGADO = 'ENTREGADO', 'Entregado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    # Transiciones de estado permitidas: estado_actual -> {estados a los que puede pasar}
    TRANSICIONES = {
        Estado.PENDIENTE: {Estado.CONFIRMADO, Estado.CANCELADO},
        Estado.CONFIRMADO: {Estado.ENVIADO, Estado.CANCELADO},
        Estado.ENVIADO: {Estado.ENTREGADO},
        Estado.ENTREGADO: set(),
        Estado.CANCELADO: set(),
    }

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos',
    )
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    direccion_envio = models.CharField(max_length=255)
    observaciones = models.TextField(blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'

    def __str__(self):
        return f'Pedido #{self.pk} - {self.usuario} ({self.get_estado_display()})'

    def puede_pasar_a(self, nuevo_estado):
        return nuevo_estado in self.TRANSICIONES.get(self.estado, set())

    def recalcular_total(self):
        self.total = sum((d.subtotal for d in self.detalles.all()), Decimal('0.00'))
        self.save(update_fields=['total'])


class DetallePedido(models.Model):
    """Una línea del pedido: qué producto, en qué color, cuántos y a qué precio."""

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT, related_name='detalles_pedido')
    # Color elegido (opcional): tiene que ser uno de los colores de ese producto.
    color = models.ForeignKey(
        'productos.ColorProducto',
        on_delete=models.PROTECT,
        related_name='detalles_pedido',
        blank=True,
        null=True,
    )
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    # Se guarda el precio al momento de la compra: si después cambia el precio
    # del producto, el pedido viejo no se modifica.
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'detalle de pedido'
        verbose_name_plural = 'detalles de pedido'
        constraints = [
            # El mismo producto puede ir dos veces solo si es en colores distintos.
            models.UniqueConstraint(fields=['pedido', 'producto', 'color'], name='producto_color_unico_por_pedido'),
        ]

    def __str__(self):
        if self.color:
            return f'{self.cantidad} x {self.producto} ({self.color.nombre})'
        return f'{self.cantidad} x {self.producto}'

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


class Mensaje(models.Model):
    """Mensaje enviado desde el formulario de contacto."""

    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField(max_length=1000)
    leido = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'mensaje de contacto'
        verbose_name_plural = 'mensajes de contacto'

    def __str__(self):
        return f'{self.nombre} - {self.asunto}'