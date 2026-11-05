# Módulo de Productos y Stock — Coramanda

## 1. Objetivo

El módulo de Productos y Stock se encarga de administrar el catálogo de productos de Coramanda mediante Django y Django REST Framework, utilizando PostgreSQL como sistema de almacenamiento.

Permite consultar productos, obtener sus detalles, realizar búsquedas, aplicar filtros, ordenar resultados y ejecutar operaciones administrativas de creación, modificación y eliminación.

También incorpora un mecanismo para descontar unidades del inventario de manera segura, verificando que exista stock suficiente antes de realizar la operación.

## 2. Modelos y estructura de datos

El módulo está compuesto por cuatro modelos: `Categoria`, `Producto`, `ColorProducto` e `ImagenProducto`.

### 2.1. Modelo Categoria

Representa las categorías utilizadas para clasificar los productos.

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id | Clave primaria automática | Identificador único de la categoría. |
| nombre | CharField(80) | Nombre de la categoría. Es único. |
| descripcion | TextField | Descripción opcional de la categoría. |

Las categorías utilizadas en los datos iniciales son Riñoneras, Pilusos, Chuflines y Accesorios.

### 2.2. Modelo Producto

Representa los artículos disponibles en la tienda.

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id | Clave primaria automática | Identificador único del producto. |
| nombre | CharField(150) | Nombre del producto. |
| categoria | ForeignKey | Relación con el modelo Categoria. |
| precio | DecimalField(10,2) | Precio del producto con dos posiciones decimales. |
| descripcion | TextField | Descripción opcional del producto. |
| stock | PositiveIntegerField | Cantidad de unidades disponibles. |
| destacado | BooleanField | Indica si el producto está destacado. |
| activo | BooleanField | Determina si el producto está activo. |
| creado | DateTimeField | Fecha y hora de creación, asignadas automáticamente. |

La relación con `Categoria` utiliza `on_delete=models.PROTECT`, por lo que no se puede eliminar una categoría mientras tenga productos asociados.

### 2.3. Modelo ColorProducto

Permite asociar diferentes colores a un mismo producto.

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id | Clave primaria automática | Identificador del color. |
| producto | ForeignKey | Relación con el producto al que pertenece. |
| nombre | CharField(50) | Nombre del color. |
| hexadecimal | CharField(7) | Código hexadecimal del color. |

La relación utiliza `related_name="colores"` y `on_delete=models.CASCADE`.

### 2.4. Modelo ImagenProducto

Permite asociar imágenes a los productos mediante direcciones URL.

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id | Clave primaria automática | Identificador de la imagen. |
| producto | ForeignKey | Relación con el producto correspondiente. |
| imagen | URLField(500) | Dirección URL de la imagen. |

La relación utiliza `related_name="imagenes"` y `on_delete=models.CASCADE`.

### 2.5. Relaciones entre modelos

La estructura presenta las siguientes relaciones:

- Una categoría puede tener varios productos.
- Cada producto pertenece a una única categoría.
- Un producto puede tener varios colores.
- Un producto puede tener varias imágenes.
- Cada color y cada imagen pertenecen a un único producto.

Estas relaciones se implementan mediante claves foráneas (`ForeignKey`).

## 3. Funcionalidades implementadas

El módulo utiliza `ModelViewSet` de Django REST Framework para proporcionar las operaciones habituales de administración de productos.

Las funcionalidades implementadas son:

- Listado de productos activos.
- Consulta individual de productos.
- Creación de productos.
- Modificación completa o parcial.
- Eliminación de productos.
- Búsqueda por nombre y descripción.
- Filtrado por categoría y estado destacado.
- Ordenamiento por precio, nombre y fecha de creación.
- Control de acceso según el rol del usuario.
- Descuento seguro de unidades del stock.

Las operaciones de escritura están restringidas a usuarios con permisos administrativos.

## 4. Endpoints de la API

La aplicación registra las rutas del módulo mediante `DefaultRouter`, asociando el recurso `productos` con `ProductoViewSet`.

Base utilizada en el entorno local:

`http://127.0.0.1:8000/api/`

| Método | Ruta | Función | Autorización |
|---|---|---|---|
| GET | `/api/productos/` | Listar productos activos. | Pública. |
| GET | `/api/productos/{id}/` | Consultar el detalle de un producto. | Pública. |
| POST | `/api/productos/` | Crear un producto. | Administrador. |
| PUT | `/api/productos/{id}/` | Reemplazar los datos de un producto. | Administrador. |
| PATCH | `/api/productos/{id}/` | Modificar parcialmente un producto. | Administrador. |
| DELETE | `/api/productos/{id}/` | Eliminar un producto. | Administrador. |

### 4.1. Parámetros de consulta

El listado admite los siguientes parámetros:

| Parámetro | Función | Ejemplo |
|---|---|---|
| categoria | Filtra por el identificador de la categoría. | `?categoria=1` |
| destacado | Filtra por estado destacado. | `?destacado=true` |
| search | Busca coincidencias en nombre o descripción. | `?search=piluso` |
| ordering | Ordena los resultados. | `?ordering=precio` |

También se pueden utilizar los siguientes criterios de ordenamiento:

- `precio`: precio ascendente.
- `-precio`: precio descendente.
- `nombre`: orden alfabético por nombre.
- `creado`: orden por fecha de creación.

La configuración de paginación depende de los ajustes generales de Django REST Framework.

### 4.2. Estructura de los datos

El serializador `ProductoSerializer` devuelve los siguientes campos:

- `id`
- `nombre`
- `categoria`
- `precio`
- `descripcion`
- `stock`
- `destacado`
- `activo`
- `colores`
- `imagenes`
- `creado`

Los colores y las imágenes se incluyen como estructuras anidadas mediante sus respectivos serializadores.

Estos campos relacionados están configurados como `read_only=True`. Por lo tanto, se pueden consultar desde la API, pero no crear ni modificar mediante el envío de datos anidados al serializador de productos.

## 5. Validaciones de datos

Las validaciones se implementan en `ProductoSerializer`, complementando las restricciones definidas en los modelos.

| Campo | Validación aplicada |
|---|---|
| nombre | Se eliminan espacios al principio y al final. No se permite que quede vacío. |
| precio | Debe ser mayor que cero. |
| stock | No puede ser negativo. |
| categoria | Debe corresponder a una categoría existente, identificada mediante su clave primaria. |

Cuando los datos enviados no cumplen las validaciones, Django REST Framework devuelve una respuesta HTTP `400 Bad Request`, acompañada de información sobre el campo que contiene el error.

Por ejemplo, un producto con precio igual a cero es rechazado por el serializador.

## 6. Seguridad y permisos

El control de acceso se realiza en el backend mediante el método `get_permissions()` de `ProductoViewSet` y la clase `IsAdministrador`.

Las operaciones se dividen de la siguiente manera:

**Consultas públicas:**
- Listar productos.
- Consultar detalles.

**Operaciones administrativas:**
- Crear productos.
- Modificar productos.
- Eliminar productos.

La autorización administrativa se basa en el rol del usuario. El método `get_queryset()` comprueba si el usuario está autenticado y si su atributo `rol` tiene el valor `admin`.

Los usuarios que no cumplen esta condición solamente reciben los productos cuyo campo `activo` es verdadero. Los administradores pueden consultar tanto productos activos como inactivos.

## 7. Gestión y consistencia del stock

El modelo `Producto` incorpora el método `descontar_stock(cantidad)`, destinado a reducir la cantidad disponible de un producto.

El procedimiento realiza las siguientes comprobaciones:

1. Verifica que la cantidad solicitada sea mayor que cero.
2. Inicia una transacción mediante `transaction.atomic()`.
3. Obtiene el producto utilizando `select_for_update()`, bloqueando temporalmente el registro durante la operación.
4. Comprueba que exista stock suficiente.
5. Descuenta las unidades solicitadas.
6. Guarda únicamente el campo `stock`.

Si la cantidad solicitada es igual o inferior a cero, se genera un error de validación.

Si no existe stock suficiente, la operación se rechaza y el inventario permanece sin modificaciones.

La utilización de transacciones y bloqueo del registro ayuda a evitar inconsistencias cuando varias operaciones intentan modificar simultáneamente el inventario.

**Importante:** `descontar_stock()` es un método del modelo y no un endpoint independiente. Su integración con la confirmación de pedidos debe realizarse desde el módulo responsable de los pedidos.

## 8. Administración mediante Django Admin

Los modelos `Producto`, `ColorProducto` e `ImagenProducto` están registrados en el panel administrativo de Django.

La configuración de `ProductoAdmin` permite:

- Visualizar el identificador, nombre, categoría, precio, stock, estado destacado y estado activo.
- Filtrar productos por categoría, destacado y activo.
- Buscar productos por nombre y descripción.
- Administrar colores e imágenes asociados directamente desde la ficha de cada producto mediante formularios integrados (`TabularInline`).

Además, los modelos de colores e imágenes también están registrados individualmente en el panel administrativo.

Esta configuración facilita la administración del catálogo sin necesidad de realizar todas las operaciones mediante solicitudes HTTP.

## 9. Pruebas automatizadas

El módulo cuenta con pruebas automatizadas desarrolladas utilizando `APITestCase` de Django REST Framework.

Las pruebas preparan usuarios de tipo administrador y cliente, además de productos activos e inactivos para verificar los distintos comportamientos.

Se implementaron 14 pruebas:

| Prueba | Comportamiento verificado |
|---|---|
| `test_listado_publico_solo_activos` | El listado público muestra únicamente productos activos. |
| `test_detalle_existente` | Permite consultar un producto existente. |
| `test_detalle_inexistente_404` | Devuelve HTTP 404 cuando el producto no existe. |
| `test_filtro_por_categoria` | Filtra correctamente por categoría. |
| `test_busqueda_por_nombre` | Permite buscar productos por nombre. |
| `test_ordenamiento_por_precio` | Ordena los productos por precio. |
| `test_anonimo_no_puede_crear` | Impide la creación por parte de usuarios anónimos. |
| `test_cliente_no_puede_crear` | Impide la creación por parte de usuarios con rol cliente. |
| `test_admin_puede_crear` | Permite crear productos a un administrador. |
| `test_admin_puede_modificar` | Permite modificar productos a un administrador. |
| `test_admin_puede_eliminar` | Permite eliminar productos a un administrador. |
| `test_precio_invalido_400` | Rechaza productos con precio igual a cero. |
| `test_descontar_stock_ok` | Comprueba el descuento correcto de unidades. |
| `test_descontar_stock_insuficiente` | Impide descontar más unidades que las disponibles. |

Estas pruebas permiten comprobar las operaciones principales, las validaciones, los permisos y la consistencia del inventario.

## 10. Integración con los demás módulos

El módulo de Productos y Stock forma parte del backend general de Coramanda.

Sus principales puntos de integración son:

- **Usuarios:** utiliza el rol del usuario autenticado para determinar los permisos administrativos.
- **Pedidos:** proporciona los productos y el método de descuento de stock que debe utilizarse durante la confirmación de una compra.
- **Base de datos:** almacena los productos, colores e imágenes mediante los modelos de Django.

La confirmación de pedidos debe coordinarse con el módulo de Pedidos para garantizar que el descuento de inventario se realice de forma consistente.

## 11. Consideraciones técnicas

- Los productos se administran mediante Django ORM y Django REST Framework.
- Las rutas se generan utilizando `DefaultRouter`.
- Los filtros se implementan con `DjangoFilterBackend`.
- La búsqueda utiliza `SearchFilter`.
- El ordenamiento utiliza `OrderingFilter`.
- Los permisos administrativos se aplican mediante `IsAdministrador`.
- Los colores y las imágenes se representan mediante relaciones de clave foránea.
- La modificación del stock utiliza transacciones y bloqueo de registros.

Esta documentación describe el comportamiento respaldado por la implementación actual del módulo. Las integraciones con autenticación JWT, confirmación de pedidos y configuración general de la base de datos deben documentarse conjuntamente con los módulos responsables.
