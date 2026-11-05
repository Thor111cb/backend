
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Producto
from .permissions import IsAdministrador
from .serializers import ProductoSerializer
from usuarios.permissions import es_admin


class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    queryset = Producto.objects.all()

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["categoria", "destacado"]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["precio", "nombre", "creado"]
    ordering = ["nombre"]

    def get_queryset(self):
        queryset = Producto.objects.all()

        # Los administradores pueden ver todos los productos.
        # Los demás usuarios solo pueden ver los productos activos.
        if not es_admin(self.request.user):
            queryset = queryset.filter(activo=True)

        return queryset

    def get_permissions(self):
        # Cualquier persona puede consultar productos.
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        # Solo los administradores pueden crear, modificar o eliminar.
        return [IsAdministrador()]
