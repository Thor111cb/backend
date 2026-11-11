
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from productos.models import Producto

from .models import Pedido


@transaction.atomic
def cambiar_estado_pedido(pedido, nuevo_estado, solo_pendiente=False):
    """
    Cambia el estado de un pedido de forma segura.

    Bloquea el pedido para evitar confirmaciones o cancelaciones duplicadas.
    El stock se descuenta al confirmar y se devuelve al cancelar un pedido
    que ya estaba confirmado.
    """

    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)

    if solo_pendiente and pedido.estado != Pedido.Estado.PENDIENTE:
        raise ValidationError(
            {'estado': 'Solo podés cancelar pedidos que estén pendientes.'}
        )

    if not pedido.puede_pasar_a(nuevo_estado):
        raise ValidationError(
            {'estado': f'No se puede pasar de {pedido.estado} a {nuevo_estado}.'}
        )

    if nuevo_estado == Pedido.Estado.CONFIRMADO:
        detalles = pedido.detalles.select_related('producto').order_by('producto_id')

        for detalle in detalles:
            try:
                detalle.producto.descontar_stock(detalle.cantidad)
            except DjangoValidationError:
                raise ValidationError(
                    {'estado': f"Stock insuficiente para '{detalle.producto}'."}
                )

    elif (
        nuevo_estado == Pedido.Estado.CANCELADO
        and pedido.estado == Pedido.Estado.CONFIRMADO
    ):
        detalles = pedido.detalles.all().order_by('producto_id')

        for detalle in detalles:
            Producto.objects.filter(pk=detalle.producto_id).update(
                stock=F('stock') + detalle.cantidad
            )

    pedido.estado = nuevo_estado
    pedido.save(update_fields=['estado', 'fecha_actualizacion'])

    return pedido
