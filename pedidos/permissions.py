from rest_framework.permissions import BasePermission
from usuarios.permissions import es_admin


class EsAdministrador(BasePermission):
    message = "Solo un administrador puede realizar esta acción."

    def has_permission(self, request, view):
        return es_admin(request.user)

class EsClienteOAdmin(BasePermission):
    """Solo clientes y administradores pueden operar con pedidos."""

    message = "Solo los clientes y administradores pueden realizar esta acción."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return es_admin(user) or getattr(user, "rol", "") == "cliente"

class EsDuenioOAdmin(BasePermission):
    """El pedido pertenece al usuario o el usuario es administrador."""

    message = "No tenés permiso para acceder a este pedido."

    def has_object_permission(self, request, view, obj):
        return es_admin(request.user) or obj.usuario_id == request.user.id