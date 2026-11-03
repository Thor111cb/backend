
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

Usuario = get_user_model()


class UsuariosAPITests(APITestCase):

    def setUp(self):
        self.password = "Zx!84pLm#qR29vT"

        self.usuario = Usuario.objects.create_user(
            username="usuario_test",
            email="usuario@test.com",
            password=self.password,
            rol="cliente",
        )

    def test_registro_exitoso(self):
        response = self.client.post(
            "/api/usuarios/registro/",
            {
                "username": "nuevo_test",
                "email": "nuevo@test.com",
                "password": self.password,
                "password2": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        usuario = Usuario.objects.get(username="nuevo_test")
        self.assertTrue(usuario.check_password(self.password))
        self.assertEqual(usuario.rol, "cliente")

    def test_registro_con_contrasenas_diferentes(self):
        response = self.client.post(
            "/api/usuarios/registro/",
            {
                "username": "nuevo_test",
                "email": "nuevo@test.com",
                "password": self.password,
                "password2": "OtraClave!2026",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_registro_con_email_duplicado(self):
        response = self.client.post(
            "/api/usuarios/registro/",
            {
                "username": "otro_usuario",
                "email": "usuario@test.com",
                "password": self.password,
                "password2": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login_correcto_genera_tokens(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": "usuario_test",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_con_contrasena_incorrecta(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": "usuario_test",
                "password": "ClaveIncorrecta123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_renovacion_de_token(self):
        login = self.client.post(
            "/api/token/",
            {
                "username": "usuario_test",
                "password": self.password,
            },
            format="json",
        )

        refresh_token = login.data["refresh"]

        response = self.client.post(
            "/api/token/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)
