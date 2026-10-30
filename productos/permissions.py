from rest_framework.permissions import BasePermission


class IsAdministrador(BasePermission):
    """Permite el acceso solo a usuarios autenticados con rol admin."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "rol", None) == "admin"
        )