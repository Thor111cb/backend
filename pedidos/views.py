from drf_spectacular.utils import extend_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Mensaje, Pedido
from .permissions import EsAdministrador, EsClienteOAdmin, EsDuenioOAdmin, es_admin
from .serializers import CambiarEstadoSerializer, MensajeSerializer, PedidoSerializer
from .services import cambiar_estado_pedido


class PedidoViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated, EsClienteOAdmin, EsDuenioOAdmin]

    def get_queryset(self):
        # Swagger (drf-spectacular) genera la doc sin usuario real.
        if getattr(self, 'swagger_fake_view', False):
            return Pedido.objects.none()

        qs = Pedido.objects.select_related('usuario').prefetch_related(
            'detalles__producto', 'detalles__color'
        )
        user = self.request.user

        # Regla clave: un usuario solo ve SUS pedidos. El admin ve todos.
        if not es_admin(user):
            qs = qs.filter(usuario=user)

        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado.upper())
        return qs

@extend_schema(request=CambiarEstadoSerializer, responses=PedidoSerializer)
@action(detail=True, methods=['patch'], url_path='cambiar-estado')
def cambiar_estado(self, request, pk=None):
    pedido = self.get_object()

    serializer = CambiarEstadoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    nuevo = serializer.validated_data['estado']

    # Los clientes únicamente pueden cancelar sus pedidos pendientes.
    solo_pendiente = False

    if not es_admin(request.user):
        if nuevo != Pedido.Estado.CANCELADO:
            return Response(
                {'detail': 'Solo podés cancelar tus pedidos mientras están pendientes.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        solo_pendiente = True

    pedido_actualizado = cambiar_estado_pedido(
        pedido,
        nuevo,
        solo_pendiente=solo_pendiente,
    )

    return Response(
        PedidoSerializer(
            pedido_actualizado,
            context={'request': request},
        ).data
    )


class MensajeViewSet(viewsets.ModelViewSet):


    queryset = Mensaje.objects.all()
    serializer_class = MensajeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [EsAdministrador()]

    def get_queryset(self):
        qs = super().get_queryset()
        leido = self.request.query_params.get('leido')
        if leido in ('true', 'false'):
            qs = qs.filter(leido=(leido == 'true'))
        return qs


def partial_update(self, request, *args, **kwargs):
    mensaje = self.get_object()

    # Solo se permite modificar el campo "leido".
    if set(request.data.keys()) != {'leido'}:
        return Response(
            {'detail': 'Debés enviar únicamente el campo leido.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    campo_leido = serializers.BooleanField()

    try:
        valor_leido = campo_leido.run_validation(request.data['leido'])
    except serializers.ValidationError as error:
        return Response(
            {'leido': error.detail},
            status=status.HTTP_400_BAD_REQUEST,
        )

    mensaje.leido = valor_leido
    mensaje.save(update_fields=['leido'])

    return Response(self.get_serializer(mensaje).data)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(
            {'detail': '¡Gracias! Recibimos tu mensaje y te vamos a responder a la brevedad.'},
            status=status.HTTP_201_CREATED,
        )