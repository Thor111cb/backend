from rest_framework.routers import DefaultRouter

from .views import MensajeViewSet, PedidoViewSet

router = DefaultRouter()
router.register('pedidos', PedidoViewSet, basename='pedido')
router.register('contacto', MensajeViewSet, basename='contacto')

urlpatterns = router.urls