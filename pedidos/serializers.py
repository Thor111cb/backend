import re

from django.db import transaction
from rest_framework import serializers

from .models import DetallePedido, Mensaje, Pedido


def stock_disponible(producto):
    return producto.stock


# ---------------------------------------------------------------- Pedidos

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    color_nombre = serializers.CharField(source='color.nombre', read_only=True, default=None)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = DetallePedido
        fields = [
            'id', 'producto', 'producto_nombre', 'color', 'color_nombre',
            'cantidad', 'precio_unitario', 'subtotal',
        ]
        read_only_fields = ['precio_unitario']

    def validate_producto(self, producto):
        if not getattr(producto, 'activo', True):
            raise serializers.ValidationError('El producto no está disponible.')
        return producto

    def validate_cantidad(self, cantidad):
        if cantidad < 1:
            raise serializers.ValidationError('La cantidad debe ser al menos 1.')
        if cantidad > 100:
            raise serializers.ValidationError('No se pueden pedir más de 100 unidades de un producto.')
        return cantidad

    def validate(self, attrs):
        color = attrs.get('color')
        if color and color.producto_id != attrs['producto'].id:
            raise serializers.ValidationError(
                {'color': f"El color '{color.nombre}' no corresponde a '{attrs['producto'].nombre}'."}
            )
        return attrs


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True)
    usuario = serializers.StringRelatedField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'usuario', 'estado', 'estado_display', 'direccion_envio',
            'observaciones', 'detalles', 'total', 'fecha_creacion', 'fecha_actualizacion',
        ]
        read_only_fields = ['estado', 'total', 'fecha_creacion', 'fecha_actualizacion']

    def validate_direccion_envio(self, valor):
        valor = valor.strip()
        if len(valor) < 5:
            raise serializers.ValidationError('Ingresá una dirección de envío válida.')
        return valor

    def validate_detalles(self, detalles):
        if not detalles:
            raise serializers.ValidationError('El pedido debe tener al menos un producto.')
        claves = [(d['producto'].id, getattr(d.get('color'), 'id', None)) for d in detalles]
        if len(claves) != len(set(claves)):
            raise serializers.ValidationError(
                'Hay productos repetidos con el mismo color: sumá las cantidades en una sola línea.'
            )

        # El stock es por producto (no por color): se suma lo pedido en todos los colores.
        pedido_por_producto = {}
        for d in detalles:
            pedido_por_producto.setdefault(d['producto'], 0)
            pedido_por_producto[d['producto']] += d['cantidad']
        for producto, total_pedido in pedido_por_producto.items():
            disponible = stock_disponible(producto)
            if total_pedido > disponible:
                raise serializers.ValidationError(
                    f"Stock insuficiente para '{producto.nombre}' (disponible: {disponible})."
                )
        return detalles

    @transaction.atomic
    def create(self, validated_data):
        detalles = validated_data.pop('detalles')
        pedido = Pedido.objects.create(usuario=self.context['request'].user, **validated_data)
        DetallePedido.objects.bulk_create([
            DetallePedido(
                pedido=pedido,
                producto=d['producto'],
                color=d.get('color'),
                cantidad=d['cantidad'],
                precio_unitario=d['producto'].precio,  # precio congelado al momento de comprar
            )
            for d in detalles
        ])
        pedido.recalcular_total()
        return pedido


class CambiarEstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Pedido.Estado.choices)

    def validate_estado(self, nuevo):
        pedido = self.context['pedido']
        if not pedido.puede_pasar_a(nuevo):
            raise serializers.ValidationError(
                f'No se puede pasar de {pedido.estado} a {nuevo}.'
            )
        return nuevo


# ---------------------------------------------------------------- Contacto

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ['id', 'nombre', 'email', 'telefono', 'asunto', 'mensaje', 'leido', 'fecha']
        read_only_fields = ['leido', 'fecha']

    def validate_nombre(self, valor):
        valor = valor.strip()
        if len(valor) < 3:
            raise serializers.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü' .-]+", valor):
            raise serializers.ValidationError('El nombre solo puede contener letras y espacios.')
        return valor

    def validate_email(self, valor):
        return valor.strip().lower()

    def validate_telefono(self, valor):
        valor = valor.strip()
        if valor and not re.fullmatch(r'\+?[\d\s-]{7,20}', valor):
            raise serializers.ValidationError('Teléfono inválido: usá solo números, espacios o guiones.')
        return valor

    def validate_asunto(self, valor):
        valor = valor.strip()
        if len(valor) < 3:
            raise serializers.ValidationError('El asunto debe tener al menos 3 caracteres.')
        return valor

    def validate_mensaje(self, valor):
        valor = valor.strip()
        if len(valor) < 10:
            raise serializers.ValidationError('El mensaje debe tener al menos 10 caracteres.')
        if len(re.findall(r'https?://', valor)) > 2:
            raise serializers.ValidationError('El mensaje no puede contener más de 2 enlaces.')
        return valor