# Coramanda Backend

Backend de la aplicación de comercio electrónico **Coramanda**, desarrollado con Django y Django REST Framework. Proporciona una API REST para gestionar productos, categorías, stock, usuarios, autenticación, pedidos y mensajes de contacto, utilizando PostgreSQL como base de datos.

## Tecnologías utilizadas

- Python
- Django
- Django REST Framework
- PostgreSQL
- Psycopg 3
- Simple JWT
- django-filter
- django-cors-headers
- drf-spectacular (Swagger / OpenAPI)
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

Para ejecutar el proyecto se necesita:

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