from decimal import Decimal

from rest_framework import serializers
from .models import Producto, ColorProducto, ImagenProducto


class ColorProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorProducto
        fields = ["id", "nombre", "hexadecimal"]


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ["id", "imagen"]


class ProductoSerializer(serializers.ModelSerializer):
    colores = ColorProductoSerializer(many=True, read_only=True)
    imagenes = ImagenProductoSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "categoria",
            "precio",
            "descripcion",
            "stock",
            "destacado",
            "activo",
            "colores",
            "imagenes",
            "creado",
        ]

    def validate_nombre(self, value):
        nombre = value.strip()
        if not nombre:
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return nombre

    def validate_precio(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("El precio debe ser mayor que cero.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value