
from decimal import Decimal

from django.core.management.base import BaseCommand
from productos.models import Producto, ColorProducto


PRODUCTOS = [
    {
        "nombre": "Riñonera Urbana",
        "categoria": "Riñoneras",
        "precio": Decimal("18500.00"),
        "descripcion": "Riñonera práctica para llevar objetos personales.",
        "stock": 15,
        "destacado": True,
        "colores": [("Negro", "#000000"), ("Beige", "#D8C3A5")],
    },
    {
        "nombre": "Riñonera Compacta",
        "categoria": "Riñoneras",
        "precio": Decimal("15000.00"),
        "descripcion": "Diseño compacto para uso diario.",
        "stock": 10,
        "destacado": False,
        "colores": [("Negro", "#000000")],
    },
    {
        "nombre": "Riñonera Deportiva",
        "categoria": "Riñoneras",
        "precio": Decimal("22000.00"),
        "descripcion": "Riñonera liviana para actividades al aire libre.",
        "stock": 8,
        "destacado": True,
        "colores": [("Azul", "#2457A7"), ("Negro", "#000000")],
    },
    {
        "nombre": "Piluso Clásico",
        "categoria": "Pilusos",
        "precio": Decimal("12000.00"),
        "descripcion": "Piluso clásico para complementar cualquier look.",
        "stock": 20,
        "destacado": True,
        "colores": [("Beige", "#D8C3A5"), ("Negro", "#000000")],
    },
    {
        "nombre": "Piluso Reversible",
        "categoria": "Pilusos",
        "precio": Decimal("16500.00"),
        "descripcion": "Piluso reversible con dos estilos en una sola prenda.",
        "stock": 12,
        "destacado": False,
        "colores": [("Verde", "#4B6043")],
    },
    {
        "nombre": "Piluso Urbano",
        "categoria": "Pilusos",
        "precio": Decimal("14000.00"),
        "descripcion": "Diseño urbano para uso cotidiano.",
        "stock": 9,
        "destacado": False,
        "colores": [("Negro", "#000000"), ("Gris", "#808080")],
    },
    {
        "nombre": "Chuflín Clásico",
        "categoria": "Chuflines",
        "precio": Decimal("3500.00"),
        "descripcion": "Accesorio para el cabello de uso diario.",
        "stock": 30,
        "destacado": True,
        "colores": [("Rosa", "#E8A0BF"), ("Lila", "#B8A1D9")],
    },
    {
        "nombre": "Chuflín de Tela",
        "categoria": "Chuflines",
        "precio": Decimal("4200.00"),
        "descripcion": "Accesorio textil suave y versátil.",
        "stock": 25,
        "destacado": False,
        "colores": [("Azul", "#2457A7"), ("Beige", "#D8C3A5")],
    },
    {
        "nombre": "Llavero Coramanda",
        "categoria": "Accesorios",
        "precio": Decimal("5000.00"),
        "descripcion": "Llavero decorativo para llevar todos los días.",
        "stock": 18,
        "destacado": False,
        "colores": [("Negro", "#000000")],
    },
    {
        "nombre": "Tote Bag",
        "categoria": "Accesorios",
        "precio": Decimal("13500.00"),
        "descripcion": "Bolsa reutilizable para llevar objetos personales.",
        "stock": 14,
        "destacado": True,
        "colores": [("Natural", "#E8DCC8"), ("Negro", "#000000")],
    },
]


class Command(BaseCommand):
    help = "Carga 10 productos de prueba para Coramanda."

    def handle(self, *args, **options):
        creados = 0
        existentes = 0

        for datos in PRODUCTOS:
            colores = datos.pop("colores")
            producto, creado = Producto.objects.get_or_create(
                nombre=datos["nombre"],
                defaults=datos,
            )

            if creado:
                creados += 1
                for nombre, hexadecimal in colores:
                    ColorProducto.objects.get_or_create(
                        producto=producto,
                        nombre=nombre,
                        defaults={"hexadecimal": hexadecimal},
                    )
            else:
                existentes += 1

            datos["colores"] = colores

        self.stdout.write(
            self.style.SUCCESS(
                f"Carga finalizada. Productos creados: {creados}. "
                f"Ya existentes: {existentes}."
            )
        )
