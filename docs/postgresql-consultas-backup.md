# PostgreSQL, consultas SQL y copias de seguridad

## 1. Objetivo

El proyecto Coramanda utiliza PostgreSQL como sistema de gestión de bases de datos. Django se conecta mediante el controlador `psycopg`, mientras que Django ORM permite consultar, crear, modificar y eliminar registros desde el código Python.

Este documento describe la configuración de la conexión, presenta consultas SQL relacionadas con el negocio y explica el procedimiento para generar una copia de seguridad de la base de datos.

## 2. Configuración de PostgreSQL

La conexión con PostgreSQL se configura en `config/settings.py` mediante variables de entorno.

Las principales variables utilizadas son:

| Variable | Función |
|---|---|
| `DB_NAME` | Nombre de la base de datos. |
| `DB_USER` | Usuario de conexión. |
| `DB_PASSWORD` | Contraseña del usuario. |
| `DB_HOST` | Dirección del servidor PostgreSQL. |
| `DB_PORT` | Puerto de conexión. |

Los valores reales se almacenan en el archivo `.env`, que no se incluye en el repositorio por motivos de seguridad.

El archivo `.env.example` contiene los nombres de las variables y valores de ejemplo para que otros integrantes puedan configurar su entorno local.

El proyecto utiliza `psycopg` como controlador para establecer la comunicación entre Django y PostgreSQL.

## 3. Conexión entre Django y PostgreSQL

La configuración de la base de datos se encuentra en `config/settings.py`.

Django utiliza el motor:

`django.db.backends.postgresql`

La conexión se establece utilizando los valores definidos en las variables de entorno. De esta manera, las credenciales no quedan escritas directamente en el código fuente.

Además, el proyecto contempla una configuración alternativa para las pruebas automatizadas: cuando se establece `RUN_TESTS=1`, Django utiliza SQLite en lugar de PostgreSQL. Esto permite ejecutar los tests sin modificar los datos de la base real.

## 4. Primera consulta SQL: productos más vendidos

Esta consulta permite identificar los productos que acumulan mayor cantidad de unidades vendidas en pedidos confirmados, enviados o entregados.

```sql
SELECT
    pr.id AS producto_id,
    pr.nombre AS producto,
    SUM(dp.cantidad) AS unidades_vendidas
FROM pedidos_detallepedido AS dp
INNER JOIN pedidos_pedido AS pe
    ON dp.pedido_id = pe.id
INNER JOIN productos_producto AS pr
    ON dp.producto_id = pr.id
WHERE UPPER(pe.estado) IN (
    'CONFIRMADO',
    'ENVIADO',
    'ENTREGADO'
)
GROUP BY pr.id, pr.nombre
ORDER BY unidades_vendidas DESC
LIMIT 10;
```

**Objetivo:** conocer cuáles son los productos con mayor cantidad de unidades vendidas, considerando únicamente pedidos que avanzaron más allá del estado pendiente.

**Utilidad para el negocio:** permite identificar los productos con mayor demanda y utilizar esa información para planificar futuras reposiciones de stock.

**Resultado esperado:** una lista de hasta diez productos ordenados de mayor a menor según la cantidad total de unidades vendidas.

## 5. Segunda consulta SQL: productos con stock bajo

Esta consulta permite identificar los productos que tienen cinco unidades o menos disponibles.

```sql
SELECT
    id,
    nombre,
    stock,
    activo
FROM productos_producto
WHERE stock <= 5
ORDER BY stock ASC, nombre ASC;
```

**Objetivo:** detectar productos que necesitan reposición de stock.

**Utilidad para el negocio:** facilita el control del inventario y permite anticipar posibles faltantes antes de que afecten la disponibilidad de los productos.

**Resultado esperado:** una lista de productos ordenados desde el menor stock disponible hasta el mayor.

## 6. Uso del ORM y SQL directo

En Coramanda se utiliza principalmente Django ORM para interactuar con la base de datos.

El ORM permite trabajar con los modelos de Django mediante Python, evitando escribir manualmente las consultas SQL habituales. Se utiliza, por ejemplo, para:

- Consultar productos y categorías.
- Crear y actualizar pedidos.
- Consultar el stock disponible.
- Registrar usuarios.
- Aplicar filtros y condiciones.
- Realizar operaciones dentro de transacciones.

Las consultas SQL directas también permiten realizar análisis específicos sobre los datos almacenados. En este documento se utilizan para obtener información comercial, como los productos más vendidos y los artículos con stock bajo.

Por lo tanto, el ORM se utiliza principalmente en la lógica de funcionamiento de la aplicación, mientras que SQL directo permite realizar consultas específicas de análisis y administración.

## 7. Copias de seguridad de PostgreSQL

Las copias de seguridad permiten conservar una copia de los datos ante posibles errores, pérdidas o problemas en la infraestructura.

Para generar una copia de seguridad se puede utilizar `pg_dump`, herramienta incluida en PostgreSQL.

El siguiente procedimiento genera un archivo de respaldo en la carpeta Documentos del usuario.

Primero se debe comprobar que `pg_dump` esté instalado y disponible desde PowerShell:

```powershell
pg_dump --version
```

Luego, desde la carpeta raíz del backend, con el entorno virtual activado, se puede ejecutar:

```powershell
@'
import os
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

pg_dump = shutil.which("pg_dump")

if not pg_dump:
    raise SystemExit("No se encontró pg_dump. Verificar la instalación de PostgreSQL.")

salida = Path.home() / "Documents" / "backup_coramanda.dump"

variables = ["DB_NAME", "DB_USER", "DB_HOST", "DB_PORT"]

faltantes = [v for v in variables if not os.getenv(v)]

if faltantes:
    raise SystemExit("Faltan variables de conexión en el archivo .env.")

entorno = os.environ.copy()
entorno["PGSSLMODE"] = "require"

comando = [
    pg_dump,
    "-h", os.environ["DB_HOST"],
    "-p", os.getenv("DB_PORT", "5432"),
    "-U", os.environ["DB_USER"],
    "-d", os.environ["DB_NAME"],
    "-F", "c",
    "--no-owner",
    "--no-acl",
    "-W",
    "-f", str(salida),
]

subprocess.run(comando, env=entorno, check=True)

print(f"Copia de seguridad creada: {salida}")
'@ | python -
```

El comando solicita la contraseña durante la ejecución, por lo que no es necesario escribirla en el código ni incluirla en el historial de comandos.

El archivo generado utiliza el formato personalizado de PostgreSQL (`custom`), que permite restaurarlo mediante `pg_restore`.

**Importante:** la copia se guarda fuera del repositorio para evitar subir información de la base de datos a GitHub. El procedimiento no modifica ni elimina los registros originales.

## 8. Evidencias de PostgreSQL

Para demostrar el funcionamiento de la base de datos se incorporarán las siguientes capturas:

- **Evidencia 1:** conexión exitosa de Django con PostgreSQL.
- **Evidencia 2:** ejecución de la consulta de productos más vendidos y sus resultados.
- **Evidencia 3:** ejecución de la consulta de productos con stock bajo y sus resultados.
- **Evidencia 4:** generación exitosa del archivo de copia de seguridad.

Las capturas se incorporarán al informe final del proyecto.

## 9. Seguridad y mantenimiento

La configuración de PostgreSQL contempla las siguientes medidas:

- Las credenciales se almacenan en variables de entorno.
- El archivo `.env` está excluido del repositorio.
- Se proporciona `.env.example` para facilitar la configuración de otros entornos.
- Las operaciones críticas del sistema utilizan transacciones para mantener la integridad de los datos.
- Las copias de seguridad permiten recuperar información ante posibles incidentes.

La administración de los permisos de la base de datos debe realizarse mediante un usuario con los privilegios necesarios para el funcionamiento de la aplicación, evitando utilizar una cuenta de superusuario en la conexión habitual.

## 10. Conclusión

PostgreSQL constituye el sistema de almacenamiento principal de Coramanda. Su integración con Django permite administrar los datos de productos, categorías, usuarios y pedidos de manera organizada.

La utilización del ORM facilita el desarrollo y mantenimiento de la aplicación, mientras que las consultas SQL directas permiten obtener información útil para la gestión del negocio.

Finalmente, las copias de seguridad y la configuración mediante variables de entorno contribuyen a mejorar la seguridad y confiabilidad del sistema.