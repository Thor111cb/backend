
from django.contrib import admin
from .models import Producto, ColorProducto, ImagenProducto


class ColorProductoInline(admin.TabularInline):
    model = ColorProducto
    extra = 1


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "categoria", "precio", "stock", "destacado", "activo")
    list_filter = ("categoria", "destacado", "activo")
    search_fields = ("nombre", "descripcion")
    inlines = [ColorProductoInline, ImagenProductoInline]


admin.site.register(ColorProducto)
admin.site.register(ImagenProducto)
