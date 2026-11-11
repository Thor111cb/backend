from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from productos.models import Categoria, ColorProducto, Producto

from .models import Mensaje

User = get_user_model()


class BasePedidosTest(APITestCase):
    def setUp(self):
        self.cliente = User.objects.create_user('ana', 'ana@test.com', 'Clave1234!')
        self.otro = User.objects.create_user('beto', 'beto@test.com', 'Clave1234!')
        self.visitante = User.objects.create_user(
            'visitante',
            'visitante@test.com',
            'Clave1234!',
            rol='visitante'
        )

        self.admin = User.objects.create_user('admin', 'admin@test.com', 'Clave1234!', is_staff=True)
        categoria = Categoria.objects.create(nombre='Bazar')
        self.producto = Producto.objects.create(
            nombre='Taza', categoria=categoria, precio=Decimal('1500.00'), stock=10
        )

    def crear_pedido(self, usuario, cantidad=2):
        self.client.force_authenticate(usuario)
        return self.client.post('/api/pedidos/', {
            'direccion_envio': 'Belgrano 123, Trelew',
            'detalles': [{'producto': self.producto.id, 'cantidad': cantidad}],
        }, format='json')


class PedidoTests(BasePedidosTest):
    def test_crear_pedido_calcula_total_y_congela_precio(self):
        r = self.crear_pedido(self.cliente, cantidad=3)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(r.data['total']), Decimal('4500.00'))
        self.assertEqual(r.data['estado'], 'PENDIENTE')

    def test_visitante_no_puede_crear_pedido(self):
        r = self.client.post('/api/pedidos/', {}, format='json')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_visitante_autenticado_no_puede_crear_pedido(self):
        self.client.force_authenticate(self.visitante)

        r = self.client.post('/api/pedidos/', {
            'direccion_envio': 'Belgrano 123',
            'detalles': [
                {'producto': self.producto.id, 'cantidad': 1}
            ],
        }, format='json')

        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_visitante_autenticado_no_puede_listar_pedidos(self):
        self.client.force_authenticate(self.visitante)

        r = self.client.get('/api/pedidos/')


        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
    def test_pedido_sin_productos_es_rechazado(self):
        self.client.force_authenticate(self.cliente)
        r = self.client.post('/api/pedidos/', {'direccion_envio': 'Belgrano 123', 'detalles': []}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stock_insuficiente_es_rechazado(self):
        r = self.crear_pedido(self.cliente, cantidad=50)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cliente_solo_ve_sus_pedidos(self):
        self.crear_pedido(self.cliente)
        self.crear_pedido(self.otro)
        self.client.force_authenticate(self.cliente)
        r = self.client.get('/api/pedidos/')
        self.assertEqual(r.data['count'], 1)

    def test_cliente_no_puede_ver_pedido_ajeno(self):
        pedido_id = self.crear_pedido(self.otro).data['id']
        self.client.force_authenticate(self.cliente)
        r = self.client.get(f'/api/pedidos/{pedido_id}/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_ve_todos_los_pedidos(self):
        self.crear_pedido(self.cliente)
        self.crear_pedido(self.otro)
        self.client.force_authenticate(self.admin)
        r = self.client.get('/api/pedidos/')
        self.assertEqual(r.data['count'], 2)

    def test_admin_confirma_y_descuenta_stock(self):
        pedido_id = self.crear_pedido(self.cliente, cantidad=4).data['id']
        self.client.force_authenticate(self.admin)
        r = self.client.patch(f'/api/pedidos/{pedido_id}/cambiar-estado/', {'estado': 'CONFIRMADO'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 6)

    def test_cancelar_confirmado_devuelve_stock(self):
        pedido_id = self.crear_pedido(self.cliente, cantidad=4).data['id']
        self.client.force_authenticate(self.admin)
        self.client.patch(f'/api/pedidos/{pedido_id}/cambiar-estado/', {'estado': 'CONFIRMADO'}, format='json')
        self.client.patch(f'/api/pedidos/{pedido_id}/cambiar-estado/', {'estado': 'CANCELADO'}, format='json')
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)

    def test_mismo_producto_en_dos_colores(self):
        rojo = ColorProducto.objects.create(producto=self.producto, nombre='Rojo', hexadecimal='#FF0000')
        azul = ColorProducto.objects.create(producto=self.producto, nombre='Azul', hexadecimal='#0000FF')
        self.client.force_authenticate(self.cliente)
        r = self.client.post('/api/pedidos/', {
            'direccion_envio': 'Belgrano 123, Trelew',
            'detalles': [
                {'producto': self.producto.id, 'color': rojo.id, 'cantidad': 2},
                {'producto': self.producto.id, 'color': azul.id, 'cantidad': 3},
            ],
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(r.data['total']), Decimal('7500.00'))

    def test_color_de_otro_producto_es_rechazado(self):
        otro = Producto.objects.create(
            nombre='Plato', categoria=self.producto.categoria, precio=Decimal('900.00'), stock=5
        )
        verde = ColorProducto.objects.create(producto=otro, nombre='Verde')
        self.client.force_authenticate(self.cliente)
        r = self.client.post('/api/pedidos/', {
            'direccion_envio': 'Belgrano 123, Trelew',
            'detalles': [{'producto': self.producto.id, 'color': verde.id, 'cantidad': 1}],
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transicion_invalida(self):
        pedido_id = self.crear_pedido(self.cliente).data['id']
        self.client.force_authenticate(self.admin)
        r = self.client.patch(f'/api/pedidos/{pedido_id}/cambiar-estado/', {'estado': 'ENTREGADO'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cliente_puede_cancelar_pendiente_pero_no_confirmar(self):
        pedido_id = self.crear_pedido(self.cliente).data['id']
        r = self.client.patch(f'/api/pedidos/{pedido_id}/cambiar-estado/', {'estado': 'CONFIRMADO'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        r = self.client.patch(f'/api/pedidos/{pedido_id}/cambiar-estado/', {'estado': 'CANCELADO'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)


class ContactoTests(BasePedidosTest):
    datos_ok = {
        'nombre': 'María López',
        'email': 'MARIA@test.com',
        'asunto': 'Consulta envío',
        'mensaje': '¿Hacen envíos a Rawson? Gracias.',
    }

    def test_visitante_puede_enviar_mensaje(self):
        r = self.client.post('/api/contacto/', self.datos_ok, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Mensaje.objects.get().email, 'maria@test.com')

    def test_validaciones_del_formulario(self):
        malos = {**self.datos_ok, 'nombre': 'M4', 'email': 'no-es-mail', 'mensaje': 'corto'}
        r = self.client.post('/api/contacto/', malos, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nombre', r.data)
        self.assertIn('email', r.data)
        self.assertIn('mensaje', r.data)

    def test_solo_admin_lista_mensajes(self):
        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.get('/api/contacto/').status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get('/api/contacto/').status_code, status.HTTP_200_OK)
    
    def test_admin_puede_marcar_mensaje_como_leido(self):
        self.client.post('/api/contacto/', self.datos_ok, format='json')
        mensaje = Mensaje.objects.get()

        self.client.force_authenticate(self.admin)
        r = self.client.patch(
            f'/api/contacto/{mensaje.id}/',
            {'leido': True},
            format='json',
        )

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        mensaje.refresh_from_db()
        self.assertTrue(mensaje.leido)

    def test_valor_invalido_de_leido_es_rechazado(self):
        self.client.post('/api/contacto/', self.datos_ok, format='json')
        mensaje = Mensaje.objects.get()

        self.client.force_authenticate(self.admin)
        r = self.client.patch(
            f'/api/contacto/{mensaje.id}/',
            {'leido': 'cualquier-cosa'},
            format='json',
        )

        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        mensaje.refresh_from_db()
        self.assertFalse(mensaje.leido)

    def test_patch_vacio_de_mensaje_es_rechazado(self):
        self.client.post('/api/contacto/', self.datos_ok, format='json')
        mensaje = Mensaje.objects.get()

        self.client.force_authenticate(self.admin)
        r = self.client.patch(
            f'/api/contacto/{mensaje.id}/',
            {},
            format='json',
        )

        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cliente_no_puede_modificar_mensaje(self):
        self.client.post('/api/contacto/', self.datos_ok, format='json')
        mensaje = Mensaje.objects.get()

        self.client.force_authenticate(self.cliente)
        r = self.client.patch(
            f'/api/contacto/{mensaje.id}/',
            {'leido': True},
            format='json',
        )

        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
