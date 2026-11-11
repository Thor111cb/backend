# Módulo de Pedidos y Contacto — Coramanda

## 1. Objetivo

El módulo de Pedidos y Contacto permite gestionar las compras realizadas por los clientes y recibir consultas desde el formulario de contacto de Coramanda.

El módulo de Pedidos permite crear pedidos, consultar su estado, administrar sus transiciones y mantener la consistencia del inventario. El módulo de Contacto recibe mensajes de los visitantes y permite que los administradores los gestionen desde la API y Django Admin.

Ambos módulos utilizan Django REST Framework y PostgreSQL, y se integran con los módulos de Productos, Usuarios y Autenticación.

## 2. Modelos y estructura de datos

La aplicación contiene tres modelos principales: `Pedido`, `DetallePedido` y `Mensaje`.

### 2.1. Modelo Pedido

Representa una compra realizada por un usuario.

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id                  | Clave primaria automática | Identificador del pedido. |
| usuario             | ForeignKey                | Usuario que realizó el pedido. |
| estado              | CharField(20)             | Estado actual del pedido. |
| direccion_envio     | CharField(255)            | Dirección donde se enviará la compra. |
| observaciones       | TextField                 | Información adicional opcional. |
| total               | DecimalField(12,2)        | Importe total del pedido. |
| fecha_creacion      | DateTimeField             | Fecha de creación automática. |
| fecha_actualizacion | DateTimeField             | Última actualización automática. |

La relación con Usuario utiliza `on_delete=models.PROTECT`, evitando eliminar un usuario que tenga pedidos asociados.

Los estados posibles son:

- `PENDIENTE`: pedido creado y todavía sin confirmar.
- `CONFIRMADO`: compra aceptada y stock descontado.
- `ENVIADO`: pedido despachado.
- `ENTREGADO`: pedido recibido por el cliente.
- `CANCELADO`: pedido cancelado.

### 2.2. Modelo DetallePedido

Representa cada producto incluido en un pedido.

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id | Clave primaria automática | Identificador del detalle. |
| pedido | ForeignKey | Pedido al que pertenece. |
| producto | ForeignKey | Producto solicitado. |
| color | ForeignKey opcional | Color seleccionado para el producto. |
| cantidad | PositiveIntegerField | Unidades solicitadas. |
| precio_unitario | DecimalField(10,2) | Precio registrado al realizar la compra. |

La relación con Pedido utiliza `on_delete=models.CASCADE`: al eliminar un pedido, se eliminan sus detalles.

Las relaciones con Producto y ColorProducto utilizan `on_delete=models.PROTECT`, para evitar eliminar elementos que forman parte de pedidos existentes.

El precio unitario se conserva al momento de crear el pedido. De esta manera, si posteriormente cambia el precio del producto, el importe de una compra anterior no se modifica.

Cada detalle calcula su subtotal multiplicando el precio unitario por la cantidad.

Además, existe una restricción de unicidad para impedir que se repita el mismo producto con el mismo color dentro de un pedido. El mismo producto puede aparecer en líneas diferentes cuando se seleccionan colores distintos.

### 2.3. Modelo Mensaje

Almacena los mensajes enviados mediante el formulario de contacto.

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id | Clave primaria automática | Identificador del mensaje. |
| nombre | CharField(100) | Nombre de quien realiza la consulta. |
| email | EmailField | Correo electrónico de contacto. |
| telefono | CharField(20) | Teléfono opcional. |
| asunto | CharField(150) | Motivo de la consulta. |
| mensaje | TextField(1000) | Contenido del mensaje. |
| leido | BooleanField | Indica si el administrador lo revisó. |
| fecha | DateTimeField | Fecha de recepción automática. |

Los mensajes se ordenan desde el más reciente al más antiguo.

## 3. Relaciones entre modelos

Las relaciones principales son:

- Un usuario puede realizar varios pedidos.
- Cada pedido pertenece a un único usuario.
- Un pedido puede contener varios detalles.
- Cada detalle pertenece a un único pedido.
- Un producto puede aparecer en distintos detalles de pedidos.
- Un detalle puede tener un color seleccionado, que es opcional.
- Un color puede estar asociado a distintos detalles de pedidos.

El modelo Mensaje es independiente de Pedido y almacena las consultas recibidas desde el formulario de contacto.

Las relaciones se implementan mediante claves foráneas (`ForeignKey`).

## 4. Creación y cálculo de pedidos

Los clientes autenticados pueden crear pedidos mediante `POST /api/pedidos/`.

Para crear un pedido, deben enviar una dirección de envío y al menos un detalle con el producto y la cantidad solicitada. El color es opcional.

El usuario se obtiene de la autenticación de la solicitud. Por lo tanto, no puede indicar libremente a qué usuario pertenece el pedido.

Antes de guardar los datos, el serializador verifica:

- Que exista al menos un producto.
- Que los productos estén activos.
- Que las cantidades estén entre 1 y 100.
- Que el color seleccionado pertenezca al producto correspondiente.
- Que no se repita el mismo producto con el mismo color.
- Que el stock disponible sea suficiente, sumando las cantidades del mismo producto aunque se hayan seleccionado colores diferentes.
- Que la dirección de envío tenga al menos cinco caracteres.

La creación se realiza mediante `transaction.atomic()`. Dentro de la transacción se crea el pedido, se guardan sus detalles y se calcula el total.

El precio de cada detalle se obtiene del precio vigente del producto en el momento de la compra.

El pedido comienza con estado `PENDIENTE`. La creación no descuenta todavía el stock: el descuento se realiza cuando un administrador confirma el pedido.

## 5. Estados y transiciones permitidas

El modelo `Pedido` define las transiciones permitidas mediante la estructura `TRANSICIONES`.

| Estado actual | Estados permitidos |
|---|---|
| PENDIENTE | CONFIRMADO, CANCELADO |
| CONFIRMADO | ENVIADO, CANCELADO |
| ENVIADO | ENTREGADO |
| ENTREGADO | Ninguno |
| CANCELADO | Ninguno |

No se permite avanzar directamente de pendiente a enviado, ni modificar pedidos que ya se encuentran en un estado terminal.

La validación se realiza en el método `puede_pasar_a()` del modelo y se aplica desde el servicio `cambiar_estado_pedido()`.

Los clientes solamente pueden cancelar sus propios pedidos cuando todavía están pendientes. Las demás transiciones quedan reservadas a los administradores.

## 6. Integración con Productos y Stock

La gestión del inventario se realiza durante las operaciones de cambio de estado del pedido.

El servicio `cambiar_estado_pedido()` está protegido mediante `transaction.atomic()` y utiliza `select_for_update()` para bloquear el pedido durante la operación.

### 6.1. Confirmación

Cuando un administrador cambia el estado a `CONFIRMADO`:

1. Se bloquea el pedido para evitar operaciones simultáneas sobre el mismo registro.
2. Se consultan sus detalles.
3. Se recorren los productos solicitados.
4. Se ejecuta `descontar_stock()` para cada producto.
5. Se verifica que exista stock suficiente.
6. Se actualiza el estado del pedido.

Si no existe stock suficiente, se produce un error de validación y la transacción evita que se confirme parcialmente la operación.

### 6.2. Cancelación

Cuando se cancela un pedido que estaba `CONFIRMADO`, el sistema devuelve al inventario las unidades que habían sido descontadas.

La devolución utiliza una actualización mediante `F('stock') + cantidad`, evitando depender de un valor de stock previamente leído en memoria.

Si el pedido estaba `PENDIENTE`, no se devuelve stock porque todavía no se había descontado.

### 6.3. Importancia de las transacciones

Las transacciones permiten mantener la consistencia entre los pedidos y el inventario.

Si una operación falla durante la confirmación, los cambios realizados dentro de la transacción se revierten. Esto evita que un pedido quede confirmado sin haber podido descontar correctamente todas sus unidades.

## 7. Endpoints de Pedidos

Las rutas se registran mediante `DefaultRouter` y `PedidoViewSet`.

Base utilizada en el entorno local:

`http://127.0.0.1:8000/api/`

| Método | Ruta | Función | Autorización |
|---|---|---|---|
| GET | `/api/pedidos/` | Listar pedidos propios. | Cliente o administrador autenticado. |
| GET | `/api/pedidos/{id}/` | Consultar un pedido. | Propietario o administrador. |
| POST | `/api/pedidos/` | Crear un pedido. | Cliente autenticado. |
| PATCH | `/api/pedidos/{id}/cambiar-estado/` | Cambiar el estado del pedido. | Administrador; el cliente puede cancelar su pedido pendiente. |

El ViewSet utiliza `CreateModelMixin`, `ListModelMixin` y `RetrieveModelMixin`, por lo que no expone operaciones PUT, PATCH general ni DELETE sobre pedidos.

### 7.1. Filtro por estado

El listado admite el parámetro `estado`.

Ejemplo:

`GET /api/pedidos/?estado=CONFIRMADO`

Permite consultar los pedidos que se encuentran en un estado determinado, respetando siempre las restricciones de acceso por usuario.

### 7.2. Ejemplo de creación

Solicitud:

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

El identificador del producto debe corresponder a un producto existente y activo.

El usuario se obtiene del token de autenticación. El estado y el total son calculados por el backend y no pueden establecerse directamente desde la solicitud.

### 7.3. Ejemplo de cambio de estado

Solicitud:

```json
{
  "estado": "CONFIRMADO"
}
```

Ruta:

`PATCH /api/pedidos/1/cambiar-estado/`

La solicitud debe realizarla un administrador autenticado. El backend valida la transición y ejecuta el descuento de stock correspondiente.

## 8. Permisos y protección de datos

El módulo utiliza las clases `EsClienteOAdmin`, `EsDuenioOAdmin` y `EsAdministrador`.

Los permisos se aplican de la siguiente manera:

| Operación | Visitante | Cliente | Administrador |
|---|---|---|---|
| Crear pedido | No | Sí | Sí |
| Listar pedidos | No | Sí, propios | Sí, todos |
| Consultar pedido | No | Sí, propios | Sí |
| Confirmar pedido | No | No | Sí |
| Enviar pedido | No | No | Sí |
| Marcar como entregado | No | No | Sí |
| Cancelar pedido pendiente | No | Sí, propios | Sí |
| Cancelar pedido confirmado | No | No | Sí |

El `get_queryset()` de `PedidoViewSet` limita los resultados al usuario autenticado. Los administradores pueden consultar todos los pedidos.

La combinación de filtrado del queryset y permisos por objeto evita que un cliente consulte pedidos pertenecientes a otras personas.

Los usuarios anónimos y los visitantes autenticados no pueden operar sobre pedidos.

## 9. Módulo de Contacto

El formulario de contacto permite que cualquier visitante envíe una consulta sin necesidad de iniciar sesión.

Los datos recibidos se validan mediante `MensajeSerializer`.

Entre las validaciones implementadas se encuentran:

- El nombre debe contener al menos tres caracteres y utilizar caracteres permitidos.
- El correo electrónico debe tener formato válido y se almacena en minúsculas.
- El teléfono es opcional y, si se informa, debe respetar el formato admitido.
- El asunto debe tener al menos tres caracteres.
- El mensaje debe contener al menos diez caracteres.
- El mensaje no puede superar los 1000 caracteres.
- Se limita a dos la cantidad de enlaces HTTP o HTTPS incluidos en el texto.

El campo `leido` no puede modificarse al enviar el formulario. Se establece automáticamente en falso.

Cuando el mensaje se recibe correctamente, la API responde con HTTP `201 Created` y un mensaje de confirmación.

### 9.1. Endpoints de Contacto

Las rutas se registran mediante `DefaultRouter` y `MensajeViewSet`.

| Método | Ruta | Función | Autorización |
|---|---|---|---|
| POST | `/api/contacto/` | Enviar un mensaje. | Pública. |
| GET | `/api/contacto/` | Listar mensajes recibidos. | Administrador. |
| GET | `/api/contacto/{id}/` | Consultar un mensaje. | Administrador. |
| PATCH | `/api/contacto/{id}/` | Marcar un mensaje como leído o no leído. | Administrador. |
| DELETE | `/api/contacto/{id}/` | Eliminar un mensaje. | Administrador. |

El ViewSet permite únicamente los métodos GET, POST, PATCH y DELETE.

La modificación parcial está restringida al campo `leido`. Si se intenta modificar otro campo o enviar campos adicionales, la API rechaza la solicitud.

### 9.2. Filtro por estado de lectura

El listado admite el parámetro `leido`.

Ejemplos:

- `GET /api/contacto/?leido=true`
- `GET /api/contacto/?leido=false`

Esto permite separar los mensajes que ya fueron revisados de aquellos que todavía requieren atención.

## 10. Administración mediante Django Admin

Los modelos `Pedido`, `DetallePedido` y `Mensaje` están registrados en Django Admin.

La administración de pedidos permite:

- Visualizar el identificador, usuario, estado, total y fecha de creación.
- Filtrar por estado y fecha.
- Buscar por nombre de usuario, correo electrónico y dirección de envío.
- Consultar los detalles del pedido dentro de su ficha mediante `TabularInline`.
- Visualizar el subtotal de cada detalle.

La administración de mensajes permite:

- Consultar nombre, correo, asunto, estado de lectura y fecha.
- Filtrar por estado de lectura y fecha.
- Buscar por nombre, correo, asunto y contenido del mensaje.
- Marcar mensajes como leídos desde el listado administrativo.

## 11. Pruebas automatizadas

El módulo cuenta con pruebas automatizadas desarrolladas mediante `APITestCase`.

Las pruebas verifican, entre otros comportamientos:

- Creación de pedidos y cálculo del total.
- Conservación del precio al momento de la compra.
- Restricciones de acceso para visitantes.
- Protección de pedidos pertenecientes a otros clientes.
- Acceso administrativo a todos los pedidos.
- Rechazo de pedidos sin productos o con stock insuficiente.
- Confirmación de pedidos y descuento de inventario.
- Devolución de stock al cancelar un pedido confirmado.
- Validación de colores pertenecientes al producto seleccionado.
- Control de transiciones de estado.
- Envío público de mensajes de contacto.
- Validación de los datos del formulario.
- Acceso administrativo a los mensajes.
- Modificación del estado de lectura.

En la última ejecución informada se encontraron 22 pruebas del módulo de Pedidos y Contacto. El usuario confirmó que finalizaron correctamente.

Para ejecutar las pruebas en el entorno de desarrollo:

```powershell
$env:RUN_TESTS = "1"
python manage.py test pedidos -v 2
Remove-Item Env:RUN_TESTS
```

La variable `RUN_TESTS=1` permite utilizar la configuración de pruebas prevista para evitar utilizar la base de datos remota durante la ejecución automatizada.

## 12. Integración con los demás módulos

El módulo de Pedidos y Contacto se integra con el resto del backend:

- **Usuarios y Autenticación:** identifica al cliente que realiza el pedido y verifica su rol mediante permisos.
- **Productos y Stock:** obtiene los productos, sus precios y colores, y utiliza el método `descontar_stock()` durante la confirmación.
- **PostgreSQL:** almacena pedidos, detalles y mensajes mediante Django ORM.
- **Frontend React:** recibe y envía información mediante los endpoints REST de la API.

La separación entre modelos, serializadores, ViewSets y servicios permite mantener organizada la lógica del negocio y facilita su mantenimiento.

## 13. Consideraciones técnicas

- Los endpoints se registran mediante `DefaultRouter`.
- Los pedidos utilizan `ModelSerializer` y serializadores anidados para sus detalles.
- Las operaciones críticas utilizan `transaction.atomic()`.
- El bloqueo de registros se realiza mediante `select_for_update()`.
- La devolución de stock utiliza expresiones `F()` para actualizar cantidades directamente en la base de datos.
- Los permisos se verifican en el backend y no dependen de las restricciones visuales del frontend.
- Los datos personales de los pedidos se protegen limitando las consultas al propietario o al administrador.

Esta documentación describe el comportamiento implementado en los módulos de Pedidos y Contacto del backend de Coramanda.