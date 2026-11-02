from rest_framework.permissions import BasePermission


def es_admin(user):
    
    if not user or not user.is_authenticated:
        return False
    rol = str(getattr(user, 'rol', '')).upper()
    return user.is_staff or rol in ('ADMINISTRADOR', 'ADMIN')


class EsAdministrador(BasePermission):
    message = 

    def has_permission(self, request, view):
        return es_admin(request.user)


class EsDuenioOAdmin(BasePermission):

    message = 

    def has_object_permission(self, request, view, obj):
        return es_admin(request.user) or obj.usuario_id == request.user.id