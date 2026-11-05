# Coramanda Backend

Backend de la aplicación de comercio electrónico **Coramanda**, desarrollado con Django y Django REST Framework. Proporciona una API REST para gestionar productos, categorías, stock, usuarios, autenticación y pedidos, utilizando PostgreSQL como base de datos.

## Tecnologías utilizadas

- Python
- Django
- Django REST Framework
- PostgreSQL
- Psycopg 3
- Simple JWT
- django-filter
- django-cors-headers
- drf-spectacular (Swagger)
- python-dotenv

## Estructura del proyecto

```text
backend/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── productos/
│   ├── management/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── usuarios/
├── pedidos/
├── docs/
├── .env.example
├── .gitignore
├── manage.py
└── requirements.txt
```

## Requisitos previos

- Python instalado.
- Git.
- Acceso a una base de datos PostgreSQL.
- Credenciales de conexión a la base de datos.

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/Thor111cb/backend.git
cd backend
```

Crear el entorno virtual:

```bash
python -m venv .venv
```

Activarlo en Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Configuración de variables de entorno

Crear una copia del archivo de ejemplo:

```powershell
Copy-Item .env.example .env
```

Completar el archivo `.env` con los datos correspondientes al entorno de trabajo:

| Variable | Descripción |
|---|---|
| SECRET_KEY | Clave secreta de Django. |
| JWT_SIGNING_KEY | Clave utilizada para firmar los tokens JWT. |
| DEBUG | Activa o desactiva el modo de depuración. |
| ALLOWED_HOSTS | Hosts autorizados para acceder al backend. |
| DB_NAME | Nombre de la base de datos. |
| DB_USER | Usuario de PostgreSQL. |
| DB_PASSWORD | Contraseña de PostgreSQL. |
| DB_HOST | Dirección del servidor PostgreSQL. |
| DB_PORT | Puerto de conexión. |
| CORS_ALLOWED_ORIGINS | Orígenes autorizados para solicitudes del frontend. |

No compartir ni subir el archivo `.env` al repositorio.

## Base de datos y migraciones

Una vez configuradas las credenciales de PostgreSQL, ejecutar:

```bash
python manage.py migrate
```

Este comando aplica las migraciones y crea las tablas necesarias.

## Carga de datos iniciales

Para cargar los productos de prueba:

```bash
python manage.py cargar_productos
```

El comando incorpora diez productos, sus categorías y sus colores asociados.

## Ejecución del servidor

Iniciar el servidor de desarrollo:

```bash
python manage.py runserver
```

El backend estará disponible en:

`http://127.0.0.1:8000/`

## Autenticación

La API utiliza JSON Web Tokens (JWT) mediante Simple JWT.

Obtener un par de tokens:

`POST /api/token/`

Renovar el token de acceso:

`POST /api/token/refresh/`

Las solicitudes que requieren autenticación deben enviar el token de acceso mediante el encabezado:

```http
Authorization: Bearer <access_token>
```

## Documentación de la API

El proyecto utiliza drf-spectacular para generar la documentación OpenAPI.

- Esquema: `http://127.0.0.1:8000/api/schema/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`

## Pruebas automatizadas

El proyecto permite ejecutar las pruebas utilizando una base SQLite independiente de PostgreSQL.

En Windows PowerShell:

```powershell
$env:RUN_TESTS="1"
python manage.py test
```

La variable `RUN_TESTS=1` configura SQLite para las pruebas y evita utilizar la base PostgreSQL configurada en `.env`.

## Aplicaciones principales

- **Productos:** gestión del catálogo, categorías, colores, imágenes y stock.
- **Usuarios:** gestión de usuarios, roles y autenticación.
- **Pedidos:** gestión de pedidos y operaciones relacionadas con las compras.

## Desarrollo y seguridad

- Las credenciales se administran mediante variables de entorno.
- El archivo `.env` está excluido del control de versiones.
- La API utiliza autenticación JWT.
- Los permisos se controlan desde el backend.
- Las operaciones de inventario utilizan transacciones para mantener la consistencia del stock.
- CORS permite configurar los orígenes autorizados del frontend.

## Equipo de desarrollo

Proyecto académico desarrollado en equipo para la aplicación Coramanda.