# Documentación de Endpoints — Coramanda Backend

## 1. Introducción

El backend de Coramanda proporciona una API REST desarrollada con Django REST Framework. Los endpoints permiten consultar y administrar productos, registrar usuarios, gestionar pedidos y recibir mensajes de contacto.

La API utiliza JSON para intercambiar información y autenticación mediante JSON Web Tokens (JWT) para las operaciones que requieren usuarios autenticados.

URL base del entorno local:

`http://127.0.0.1:8000/api/`

## 2. Convenciones de autenticación

Los endpoints protegidos utilizan el encabezado:

`Authorization: Bearer <access_token>`

Los roles utilizados por el sistema son:

| Rol | Descripción |
|---|---|
| admin | Administrador con permisos de gestión. |
| cliente | Usuario registrado que puede realizar y consultar sus propios pedidos. |
| visitante | Usuario sin permisos para operar sobre pedidos. |

Los endpoints públicos no requieren autenticación.

## 3. Productos

Base de rutas: `/api/productos/`

| Método | Ruta | Descripción | Acceso |
|---|---|---|---|
| GET | `/api/productos/` | Lista los productos activos. | Público |
| GET | `/api/productos/{id}/` | Consulta un producto por su identificador. | Público |
| POST | `/api/productos/` | Crea un producto. | Administrador |
| PUT | `/api/productos/{id}/` | Reemplaza los datos de un producto. | Administrador |
| PATCH | `/api/productos/{id}/` | Modifica parcialmente un producto. | Administrador |
| DELETE | `/api/productos/{id}/` | Elimina un producto. | Administrador |

### 3.1. Campos del producto

Los datos que admite el serializador son:

| Campo | Tipo | Descripción |
|---|---|---|
| nombre | String | Nombre del producto. |
| categoria | Integer | Identificador de la categoría. |
| precio | Decimal | Precio mayor que cero. |
| descripcion | String | Descripción del producto. |
| stock | Integer | Cantidad disponible, no negativa. |
| destacado | Boolean | Indica si es un producto destacado. |
| activo | Boolean | Indica si está disponible en el catálogo. |
| colores | Array | Colores asociados, de solo lectura en este serializador. |
| imagenes | Array | Imágenes asociadas, de solo lectura en este serializador. |
| creado | DateTime | Fecha de creación, administrada por el sistema. |

Los campos `colores`, `imagenes` y `creado` no se modifican mediante el serializador principal de productos.

### 3.2. Ejemplo de creación

Método: `POST`

Ruta: `/api/productos/`

```json
{
  "nombre": "Producto de ejemplo",
  "categoria": 1,
  "precio": "25000.00",
  "descripcion": "Descripción del producto",
  "stock": 15,
  "destacado": true,
  "activo": true
}
```

Validaciones principales:

- El nombre no puede estar vacío.
- El precio debe ser mayor que cero.
- El stock no puede ser negativo.
- La operación requiere permisos de administrador.

### 3.3. Búsqueda, filtros y ordenamiento

El listado permite utilizar los siguientes parámetros:

| Parámetro | Función | Ejemplo |
|---|---|---|
| categoria | Filtra por identificador de categoría. | `?categoria=1` |
| destacado | Filtra productos destacados. | `?destacado=true` |
| search | Busca por nombre o descripción. | `?search=vestido` |
| ordering | Ordena los resultados. | `?ordering=precio` |

Campos disponibles para ordenar:

- `precio`
- `nombre`
- `creado`

Para ordenar de manera descendente se utiliza el signo menos delante del campo.

Ejemplo:

`GET /api/productos/?categoria=1&search=vestido&ordering=-precio`

Los usuarios que no sean administradores solamente reciben productos activos.

## 4. Usuarios y autenticación

### 4.1. Registro

Método: `POST`

Ruta: `/api/usuarios/registro/`

Acceso: público.

Campos:

| Campo | Tipo | Descripción |
|---|---|---|
| username | String | Nombre de usuario. |
| email | Email | Correo electrónico único. |
| password | String | Contraseña, validada mediante los validadores de Django. |
| password2 | String | Confirmación de contraseña. |

Ejemplo:

```json
{
  "username": "cliente01",
  "email": "cliente@example.com",
  "password": "ContraseñaSegura123!",
  "password2": "ContraseñaSegura123!"
}
```

Validaciones:

- Las contraseñas deben coincidir.
- La contraseña debe cumplir las reglas de validación configuradas en Django.
- El correo electrónico debe ser único.
- El usuario se crea mediante `create_user()`, que aplica el mecanismo de hashing de contraseñas de Django.
- El rol se asigna automáticamente como `cliente`.

El campo `rol` no puede ser elegido libremente durante el registro.

### 4.2. Obtener tokens JWT

Método: `POST`

Ruta: `/api/token/`

Acceso: público.

Permite iniciar sesión y obtener un token de acceso y uno de actualización.

Ejemplo:

```json
{
  "username": "cliente01",
  "password": "ContraseñaSegura123!"
}
```

La respuesta incluye:

- `access`: token utilizado para acceder a endpoints protegidos.
- `refresh`: token utilizado para solicitar un nuevo access token.

### 4.3. Renovar token

Método: `POST`

Ruta: `/api/token/refresh/`

Acceso: público, requiere un refresh token válido.

Ejemplo:

```json
{
  "refresh": "<refresh_token>"
}
```

La respuesta devuelve un nuevo token de acceso.

## 5. Pedidos

Base de rutas: `/api/pedidos/`

| Método | Ruta | Descripción | Acceso |
|---|---|---|---|
| GET | `/api/pedidos/` | Lista pedidos. | Cliente o administrador |
| GET | `/api/pedidos/{id}/` | Consulta un pedido. | Propietario o administrador |
| POST | `/api/pedidos/` | Crea un pedido. | Cliente autenticado |
| PATCH | `/api/pedidos/{id}/cambiar-estado/` | Cambia el estado del pedido. | Administrador; cliente solo cancela pendientes |

### 5.1. Crear pedido

Ejemplo:

```json
{
  "direccion_envio": "Belgrano 123, Trelew",
  "observaciones": "Entregar por la tarde",
  "detalles": [
    {
      "producto": 1,
      "cantidad": 2
    }
  ]
}
```

El color es opcional. El usuario se obtiene del token de autenticación.

El backend calcula el total y conserva el precio unitario vigente al momento de la compra.

### 5.2. Cambiar estado

Ejemplo:

```json
{
  "estado": "CONFIRMADO"
}
```

Estados admitidos:

- `PENDIENTE`
- `CONFIRMADO`
- `ENVIADO`
- `ENTREGADO`
- `CANCELADO`

El backend controla las transiciones permitidas y administra el descuento o devolución del stock según corresponda.

### 5.3. Filtro de pedidos

El listado admite el parámetro `estado`.

Ejemplo:

`GET /api/pedidos/?estado=CONFIRMADO`

Los clientes solamente pueden consultar sus propios pedidos. Los administradores pueden consultar todos.

## 6. Contacto

Base de rutas: `/api/contacto/`

| Método | Ruta | Descripción | Acceso |
|---|---|---|---|
| POST | `/api/contacto/` | Envía un mensaje desde el formulario de contacto. | Público |
| GET | `/api/contacto/` | Lista los mensajes recibidos. | Administrador |
| GET | `/api/contacto/{id}/` | Consulta un mensaje. | Administrador |
| PATCH | `/api/contacto/{id}/` | Modifica el estado de lectura. | Administrador |
| DELETE | `/api/contacto/{id}/` | Elimina un mensaje. | Administrador |

### 6.1. Enviar mensaje

Ejemplo:

```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "2804000000",
  "asunto": "Consulta sobre un producto",
  "mensaje": "Quisiera conocer más información sobre este producto."
}
```

El campo `telefono` es opcional.

El campo `leido` se establece automáticamente en falso y no puede modificarse desde el formulario público.

La respuesta exitosa utiliza HTTP `201 Created`.

### 6.2. Marcar mensaje como leído

Método: `PATCH`

Ruta: `/api/contacto/{id}/`

Ejemplo:

```json
{
  "leido": true
}
```

La modificación está restringida exclusivamente al campo `leido`.

### 6.3. Filtro de mensajes

El listado permite filtrar por estado de lectura:

- `GET /api/contacto/?leido=true`
- `GET /api/contacto/?leido=false`

## 7. Documentación de la API

El backend incorpora documentación OpenAPI mediante `drf-spectacular`.

| Método | Ruta | Descripción | Acceso |
|---|---|---|---|
| GET | `/api/schema/` | Obtiene el esquema OpenAPI. | Según configuración del proyecto |
| GET | `/api/docs/` | Abre la interfaz Swagger. | Según configuración del proyecto |

La interfaz Swagger permite visualizar las operaciones disponibles, consultar sus parámetros y probar solicitudes HTTP.

## 8. Resumen general de endpoints

| Módulo | Cantidad de operaciones documentadas |
|---|---:|
| Productos | 6 |
| Usuarios y autenticación | 3 |
| Pedidos | 4 |
| Contacto | 5 |
| Documentación | 2 |
| **Total** | **20** |

El total contempla las operaciones HTTP y las rutas de documentación enumeradas en este archivo.

## 9. Códigos HTTP utilizados

Los endpoints utilizan los códigos HTTP correspondientes al resultado de cada operación.

| Código | Significado | Situación habitual |
|---|---|---|
| 200 | OK | Consulta o modificación exitosa. |
| 201 | Created | Registro o creación exitosa. |
| 204 | No Content | Eliminación exitosa. |
| 400 | Bad Request | Datos inválidos o transición no permitida. |
| 401 | Unauthorized | Falta autenticación válida. |
| 403 | Forbidden | El usuario autenticado no tiene permisos. |
| 404 | Not Found | El recurso solicitado no existe o no es visible para el usuario. |

## 10. Consideraciones de seguridad

La API aplica autenticación JWT y permisos en el backend.

Las operaciones administrativas se encuentran restringidas por rol. Los clientes solamente pueden consultar sus propios pedidos y no pueden modificar directamente estados ni información de otros usuarios.

Los serializadores validan los datos recibidos antes de guardarlos en la base de datos.

La protección no depende de las restricciones visuales del frontend, sino de las validaciones y permisos implementados en Django REST Framework.

## 11. Conclusión

La API REST de Coramanda organiza sus operaciones en módulos independientes y permite integrar el frontend React con el backend Django.

La utilización de ViewSets, serializadores, routers, autenticación JWT y permisos por rol proporciona una estructura organizada y facilita el mantenimiento y la ampliación del sistema.