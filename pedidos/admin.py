from django.contrib import admin

from .models import DetallePedido, Mensaje, Pedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    fields = ['producto', 'color', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'estado', 'total', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['usuario__username', 'usuario__email', 'direccion_envio']
    readonly_fields = ['total', 'fecha_creacion', 'fecha_actualizacion']
    inlines = [DetallePedidoInline]


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'asunto', 'leido', 'fecha']
    list_filter = ['leido', 'fecha']
    search_fields = ['nombre', 'email', 'asunto', 'mensaje']
    list_editable = ['leido']