# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class PlanillaVisadoBaseManager(models.Manager):
    pass


class PlanillaVisadoQuerySet(models.QuerySet):
    def en_estado(self, estados):
        if type(estados) != list:
            estados = [estados]
        return self.annotate(max_id=models.Max('estados__id')).filter(
            estados__id=models.F('max_id'),
            estados__tipo__in=[e.TIPO for e in estados])


PlanillaManager = PlanillaVisadoBaseManager.from_queryset(PlanillaVisadoQuerySet)


class Doc_Balance_Superficie(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre


class Elemento_Balance_Superficie(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=150)

    def __str__(self):
        return self.elementoBalance

class PlanillaLocales(models.Model):
    planillaLocales = models.CharField(max_length=2)

    def __str__(self):
        return self.planillaLocales

class ColumnaDeVisado(models.Model):
    """las columnas de una vista de planilla de visado
    Plantas, Cortes, Fachadas, etc...."""
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    def relacionar_con_filas(self, filas):
        for fila in filas:
            self.relacionar_con_fila(fila)

    def relacionar_con_fila(self, fila):
        try:
            item = self.items.get(fila_de_visado=fila)
            item.activo = True
            item.save()
            return item
        except ItemDeVisado.DoesNotExist as ex:
            return ItemDeVisado.objects.create(columna_de_visado=self, fila_de_visado=fila)

    def quitar_fila(self, fila):
        try:
            item = self.items.get(fila_de_visado=fila)
            item.activo = False
            item.save()
        except ItemDeVisado.DoesNotExist as ex:
            pass

class FilaDeVisado(models.Model):
    """las filas de una vista de plantilla de visado
    Linea minicipal...
    Indicacion de corte....
    """
    nombre = models.CharField(max_length=200)
    #items = models.ManyToManyField(ColumnaDeVisado, through='ItemDeVisado', related_name='items')

    def __str__(self):
        return self.nombre

    def relacionar_con_columnas(self, columnas):
        for columna in columnas:
            self.relacionar_con_columna(columna)

    def relacionar_con_columna(self, columna):
        try:
            item = self.items.get(columna_de_visado=columna)
            item.activo = True
            item.save()
            return item
        except ItemDeVisado.DoesNotExist as ex:
            return ItemDeVisado.objects.create(columna_de_visado=columna, fila_de_visado=self)

    def quitar_columna(self, columna):
        try:
            item = self.items.get(columna_de_visado=columna)
            item.activo = False
            item.save()
        except ItemDeVisado.DoesNotExist as ex:
            pass

class ItemDeVisado(models.Model):
    columna_de_visado = models.ForeignKey(ColumnaDeVisado, related_name="items")
    fila_de_visado = models.ForeignKey(FilaDeVisado, related_name="items")
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['columna_de_visado__nombre', 'fila_de_visado__nombre']

    def __str__(self):
        return "{fila}, {columna}".format(fila=self.fila_de_visado.nombre, columna=self.columna_de_visado.nombre)

class PlanillaDeVisado(models.Model):
    #tramite = models.ForeignKey(Tramite)
    items = models.ManyToManyField(ItemDeVisado, related_name="planillas")
   # planillaLocales = models.ManyToManyField(PlanillaLocales, related_name="planillas")#esto nose si es asi

    def agregar_item(self, item):
        self.items.add(item)

    def quitar_item(self, item):
        self.items.remove(item)

    def item_activo(self, item):
        return self.items.filter(pk=item.pk).exists()

    def marcar_items(self, items):
        for item in items:
            if self.item_activo(item):
                print("{item}: O".format(item=item))
            else:
                print("{item}: X".format(item=item))

    def agregar_local(self, local):   #agregue esto para agregar lo de la planilla de locales
        self.locales.add(local)

    def quita_local(self, local):
        self.locales.remove(local)

    def local_activo(self, local):
        return self.locales.filter(pk=local.pk).exists()

        def marcar_locales(self, locales):
            for local in locales:
                if self.local_activo(local):
                    print("{item}: O".format(item=local))
                else:
                    print("{item}: X".format(item=local))