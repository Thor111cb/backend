from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Producto
from .permissions import IsAdministrador
from .serializers import ProductoSerializer


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
        user = self.request.user

        es_admin = (
            user.is_authenticated
            and getattr(user, "rol", None) == "admin"
        )
        if not es_admin:
            queryset = queryset.filter(activo=True)

        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdministrador()]