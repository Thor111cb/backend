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