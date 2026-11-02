from rest_framework.permissions import BasePermission


def es_admin(user):
    """True si el usuario es Administrador (is_staff o rol ADMINISTRADOR)."""
    if not user or not user.is_authenticated:
        return False
    rol = str(getattr(user, 'rol', '')).upper()
    return user.is_staff or rol in ('ADMINISTRADOR', 'ADMIN')


class EsAdministrador(BasePermission):
    message = 'Solo un administrador puede realizar esta acción.'

    def has_permission(self, request, view):
        return es_admin(request.user)


class EsDuenioOAdmin(BasePermission):
    """A nivel objeto: el pedido tiene que ser del usuario, o ser admin."""

    message = 'No tenés permiso para acceder a este pedido.'

    def has_object_permission(self, request, view, obj):
        return es_admin(request.user) or obj.usuario_id == request.user.id
