from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from productos.models import Producto

from .models import Pedido


@transaction.atomic
def confirmar_pedido(pedido):
   
    for detalle in pedido.detalles.select_related('producto'):
        try:
            detalle.producto.descontar_stock(detalle.cantidad)
        except DjangoValidationError:
            # Se convierte a error de DRF para que la API responda 400 y no 500.
            raise ValidationError(
                {'estado': f"Stock insuficiente para '{detalle.producto}'."}
            )

    pedido.estado = Pedido.Estado.CONFIRMADO
    pedido.save(update_fields=['estado', 'fecha_actualizacion'])
    return pedido


@transaction.atomic
def cancelar_pedido(pedido):
    """Cancela el pedido. Si ya estaba confirmado, devuelve el stock."""
    if pedido.estado == Pedido.Estado.CONFIRMADO:
        for detalle in pedido.detalles.all():
            # F() suma directo en la base de datos, sin pisar cambios de otros.
            Producto.objects.filter(pk=detalle.producto_id).update(
                stock=F('stock') + detalle.cantidad
            )

    pedido.estado = Pedido.Estado.CANCELADO
    pedido.save(update_fields=['estado', 'fecha_actualizacion'])
    return pedido