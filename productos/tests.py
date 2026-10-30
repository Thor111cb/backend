from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from productos.models import Producto

Usuario = get_user_model()


class ProductoAPITests(APITestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="ClaveSegura123",
            rol="admin",
        )
        self.cliente = Usuario.objects.create_user(
            username="cliente_test",
            email="cliente@test.com",
            password="ClaveSegura123",
            rol="cliente",
        )
        self.activo = Producto.objects.create(
            nombre="Riñonera Test",
            categoria="Riñoneras",
            precio=Decimal("18500.00"),
            descripcion="Producto de prueba",
            stock=10,
            destacado=True,
            activo=True,
        )
        self.inactivo = Producto.objects.create(
            nombre="Piluso Oculto",
            categoria="Pilusos",
            precio=Decimal("12000.00"),
            stock=5,
            destacado=False,
            activo=False,
        )
        self.otro = Producto.objects.create(
            nombre="Chuflín Test",
            categoria="Chuflines",
            precio=Decimal("3500.00"),
            descripcion="Accesorio de prueba",
            stock=3,
            destacado=False,
            activo=True,
        )

    def test_listado_publico_solo_activos(self):
        response = self.client.get("/api/productos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nombres = [item["nombre"] for item in response.data["results"]]
        self.assertIn("Riñonera Test", nombres)
        self.assertNotIn("Piluso Oculto", nombres)

    def test_detalle_existente(self):
        response = self.client.get(f"/api/productos/{self.activo.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "Riñonera Test")

    def test_detalle_inexistente_404(self):
        response = self.client.get("/api/productos/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filtro_por_categoria(self):
        response = self.client.get("/api/productos/", {"categoria": "Riñoneras"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertEqual(item["categoria"], "Riñoneras")

    def test_busqueda_por_nombre(self):
        response = self.client.get("/api/productos/", {"search": "Riñonera"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nombres = [item["nombre"] for item in response.data["results"]]
        self.assertIn("Riñonera Test", nombres)
        self.assertNotIn("Chuflín Test", nombres)

    def test_ordenamiento_por_precio(self):
        response = self.client.get("/api/productos/", {"ordering": "precio"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        precios = [Decimal(item["precio"]) for item in response.data["results"]]
        self.assertEqual(precios, sorted(precios))

    def test_anonimo_no_puede_crear(self):
        response = self.client.post(
            "/api/productos/",
            {
                "nombre": "Nuevo",
                "categoria": "Accesorios",
                "precio": "5000.00",
                "stock": 1,
            },
            format="json",
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_cliente_no_puede_crear(self):
        self.client.force_authenticate(user=self.cliente)
        response = self.client.post(
            "/api/productos/",
            {
                "nombre": "Nuevo",
                "categoria": "Accesorios",
                "precio": "5000.00",
                "stock": 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_crear(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/productos/",
            {
                "nombre": "Tote Test",
                "categoria": "Accesorios",
                "precio": "13500.00",
                "stock": 4,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nombre"], "Tote Test")

    def test_admin_puede_modificar(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/productos/{self.activo.id}/",
            {"precio": "19000.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data["precio"]), Decimal("19000.00"))

    def test_admin_puede_eliminar(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/api/productos/{self.otro.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_precio_invalido_400(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/productos/",
            {
                "nombre": "Malo",
                "categoria": "Accesorios",
                "precio": "0",
                "stock": 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("precio", response.data)

    def test_descontar_stock_ok(self):
        self.activo.descontar_stock(3)
        self.activo.refresh_from_db()
        self.assertEqual(self.activo.stock, 7)

    def test_descontar_stock_insuficiente(self):
        with self.assertRaises(ValidationError):
            self.activo.descontar_stock(999)
        self.activo.refresh_from_db()
        self.assertEqual(self.activo.stock, 10)