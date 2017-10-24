# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
import random

# Create your tests here.
from .models import ColumnaDeVisado, FilaDeVisado, ItemDeVisado, PlanillaDeVisado


class TestItemsDeVisado(TestCase):
    def setUp(self):
        textos1 = ["Planta", "Fachada", "Estructura", "Planta de Techo", "Corte"]
        self.columnas = [ColumnaDeVisado.objects.create(nombre=texto) for texto in textos1]
        textos2 = ["Linea municipal", "Denominacion", "Espesores de muros", "Cotas de nivel", "Salientes de fachada", "Escalera reglamentaria", "Proyeccion de tanque de agua"]
        self.filas = [FilaDeVisado.objects.create(nombre=texto) for texto in textos2]

    def test_crear_relacion(self):
        item1 = self.filas[0].relacionar_con_columna(self.columnas[0])
        item2 = self.columnas[0].relacionar_con_fila(self.filas[0])
        self.assertEqual(item1.pk, item2.pk)
        self.assertEqual(ItemDeVisado.objects.count(), 1)

    def test_planilla_de_visado(self):
        for _ in range((len(self.filas) * len(self.columnas)) // 2):
            fila = random.choice(self.filas)
            columna = random.choice(self.columnas)
            fila.relacionar_con_columna(columna)
        items = list(ItemDeVisado.objects.all())

        planilla1 = PlanillaDeVisado.objects.create()
        planilla1.agregar_item(items[0])
        planilla1.agregar_item(items[0])
        self.assertEqual(planilla1.items.count(), 1)
        planilla1.quitar_item(items[0])
        self.assertEqual(planilla1.items.count(), 0)
        item = random.choice(items)
        planilla1.agregar_item(item)
        planilla2 = PlanillaDeVisado.objects.create()
        planilla2.agregar_item(item)
        for i in items:
            if i.planillas.count() == 2:
                self.assertEqual(i.pk, item.pk)

    def test_planilla_de_print(self):
        for _ in range((len(self.filas) * len(self.columnas)) // 2):
            fila = random.choice(self.filas)
            columna = random.choice(self.columnas)
            fila.relacionar_con_columna(columna)
        items = list(ItemDeVisado.objects.all())

        planilla = PlanillaDeVisado.objects.create()
        for _ in range(len(items)):
            planilla.agregar_item(random.choice(items))
        planilla.marcar_items(items)
