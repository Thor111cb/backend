
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
