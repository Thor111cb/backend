from rest_framework.permissions import BasePermission
from usuarios.permissions import es_admin


class IsAdministrador(BasePermission):
    """Permite el acceso solo a usuarios administradores."""

    message = "Solo un administrador puede realizar esta acción."

    def has_permission(self, request, view):
        return es_admin(request.user)