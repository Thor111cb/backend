def es_admin(user):
    """Comprueba si un usuario tiene permisos de administrador."""
    if not user or not user.is_authenticated:
        return False

    rol = str(getattr(user, "rol", "")).strip().lower()

    return user.is_staff or rol in ("admin", "administrador")