# Módulo de productos y stock — Coramanda

## 1. Objetivo

Implementar la gestión del catálogo de productos de Coramanda mediante Django REST Framework y PostgreSQL, permitiendo consultar, buscar, filtrar y administrar los productos de la tienda.

## 2. Datos del producto

- **Nombre:** obligatorio, con una longitud máxima definida.
- **Categoría:** Riñoneras, Pilusos, Chuflines o Accesorios.
- **Precio:** valor decimal positivo.
- **Descripción:** texto descriptivo del producto.
- **Colores:** opciones disponibles, cada una con nombre y código hexadecimal.
- **Imágenes:** una o varias imágenes asociadas al producto.
- **Stock:** cantidad disponible, igual o mayor que cero.
- **Destacado:** indica si el producto aparece en las secciones destacadas de la página principal.

Los tipos de datos, las relaciones y las restricciones definitivas se establecerán al implementar los modelos.

## 3. Funcionalidades previstas

- Listar los productos disponibles.
- Consultar el detalle de un producto.
- Crear, modificar y eliminar productos con permisos administrativos.
- Buscar productos por nombre.
- Filtrar por categoría y, cuando corresponda, por color.
- Ordenar por precio y otros campos pertinentes.
- Paginar los resultados.
- Consultar los productos destacados.
- Validar los cambios de stock para evitar cantidades negativas.

## 4. Seguridad y consistencia

Las operaciones administrativas deberán requerir los permisos correspondientes. Las validaciones se realizarán en el servidor, aunque el frontend también valide los formularios.

El stock no debe descontarse únicamente desde el módulo de productos: la confirmación de pedidos deberá coordinarse con el módulo de pedidos y utilizar una transacción de base de datos.

## 5. Pruebas previstas

1. Listado de productos.
2. Consulta de un producto existente.
3. Búsqueda y filtros.
4. Ordenamiento y paginación.
5. Rechazo de precios o cantidades inválidas.
6. Restricción de operaciones de escritura para usuarios sin permisos administrativos.
7. Verificación de la consistencia del stock al confirmar pedidos.

## 6. Dependencias de integración

Antes de crear las relaciones definitivas y ejecutar migraciones, se deben acordar con el equipo los nombres de las aplicaciones y modelos, el modelo de usuario personalizado y la relación entre productos, detalles de pedido y stock.

## 7. Reglas de validación

- El nombre del producto es obligatorio y no puede superar la longitud máxima establecida en el modelo.
- El precio debe ser un número decimal mayor que cero.
- La categoría debe pertenecer a las opciones permitidas: Riñoneras, Pilusos, Chuflines o Accesorios.
- La cantidad de stock debe ser un número entero igual o mayor que cero.
- El campo destacado debe admitir un valor booleano.
- Los colores deben tener un nombre y un código hexadecimal válido.
- Los productos inexistentes deben devolver una respuesta HTTP 404 al consultar su detalle.
- Los datos inválidos deben generar una respuesta HTTP 400 con información sobre los errores.

## 8. Permisos y seguridad

- Los visitantes podrán consultar el catálogo y los detalles de los productos.
- Solamente los usuarios con permisos administrativos podrán crear, modificar o eliminar productos.
- La autorización deberá comprobarse en el backend; no alcanza con ocultar botones en la interfaz.
- Los datos recibidos deberán validarse antes de guardarse en la base de datos.

La implementación definitiva de los permisos se coordinará con el módulo de autenticación.

## 9. Búsqueda, filtros y paginación

- La búsqueda permitirá localizar productos por nombre.
- Los filtros permitirán consultar productos por categoría y, si el diseño de datos lo permite, por color.
- El ordenamiento permitirá ordenar los resultados por precio y otros campos acordados.
- La paginación limitará la cantidad de resultados devueltos por página.
- Los parámetros de búsqueda y filtrado deberán poder combinarse cuando corresponda.

## 10. Pruebas previstas

- Crear un producto con datos válidos.
- Rechazar un producto con nombre vacío.
- Rechazar un precio negativo o igual a cero.
- Rechazar una categoría que no esté permitida.
- Rechazar una cantidad de stock negativa.
- Consultar la lista y el detalle de los productos.
- Buscar productos por nombre y filtrarlos por categoría.
- Comprobar que un usuario sin permisos administrativos no pueda modificar el catálogo.
- Comprobar que un administrador autorizado pueda crear, modificar y eliminar productos.
- Verificar que la paginación y el ordenamiento funcionen correctamente.

Las pruebas automatizadas se implementarán con las herramientas de Django REST Framework una vez definidos los modelos y los permisos definitivos.

## 11. Dependencias de integración

- Confirmar con el equipo la estructura definitiva del modelo de usuario y sus permisos.
- Coordinar con el módulo de pedidos la forma de consultar productos y actualizar el stock.
- Acordar cómo se almacenarán las imágenes y los colores.
- Integrar las rutas del módulo en el enrutamiento general de la API.
- Mantener las migraciones y los cambios de configuración coordinados con el resto del equipo.