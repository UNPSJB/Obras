# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from tramite.models import *


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
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class PlanillaLocales(models.Model):
    planillaLocales = models.CharField(max_length=2)

    def __str__(self):
        return self.planillaLocales

class ColumnaDeVisado(models.Model):
    """las columnas de una vista de planilla de visado
    Plantas, Cortes, Fachadas, etc...."""
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

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
    activo = models.BooleanField(default=True)
    #items = models.ManyToManyField(ColumnaDeVisado, through='ItemDeVisado', related_name='items')

    def __str__(self):
        return self.nombre

    def crearItem(self,columna, fila):
        item=ItemDeVisado.objects.create(columna_de_visado=columna, fila_de_visado=fila)
        return item

    def guardarItems(self, lista):
        for i in range(0, len(lista)):
            try:
                item=lista[i]["item"]
                if item.activo==0 and lista[i]["cantidad"]==1:
                            self.relacionar_con_columna(lista[i]["item"])
                elif lista[i]["cantidad"]==0 and  item.activo==1:
                            self.quitar_columna(lista[i]["item"])
                else:
                    if lista[i]["cantidad"]==1:
                            self.relacionar_con_columna(lista[i]["item"])
            except:
                pass
        return

    def relacionar_con_columnas(self,lista):
        items=ItemDeVisado.objects.all().distinct()
        sigue=True
        listaEncontrados=[]
        for it in items:
            i=0
            aux={'item':it, 'cantidad':0}
            encontrado=False
            crear=False
            for i in range(0, len(lista)):
                try:
                        item=ItemDeVisado.objects.get(columna_de_visado=lista[i]['columna'],fila_de_visado=lista[i]['fila'])
                        if it.columna_de_visado==item.columna_de_visado and  it.fila_de_visado==item.fila_de_visado:
                            aux={"item":it,"cantidad":1}

                except ObjectDoesNotExist:
                        item = self.crearItem(lista[i]['columna'], lista[i]['fila'])
                        aux={'item':item, 'cantidad':1}
                        break; #ver si al crear no impide que agregue los demas items
            listaEncontrados.append(aux)
        self.guardarItems(listaEncontrados)
        return

    def relacionar_con_columna(self, item):
        try:
            item.activo = True
            item.save()
            return item
        except ItemDeVisado.DoesNotExist as ex:
            pass
       #  return ItemDeVisado.objects.create(columna_de_visado=item, fila_de_visado=self)

    def quitar_columna(self, item):
        try:
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
    tramite = models.ForeignKey(Tramite, related_name="visados")
    observacion = models.CharField(max_length=500, null=True, blank=True)
    items = models.ManyToManyField(ItemDeVisado, related_name="planillas")   
    elementos = models.ManyToManyField(Elemento_Balance_Superficie, related_name="elementos_balance")
    fecha = models.DateTimeField(auto_now_add=True, null=True)

    def agregar_elemento(self, elemento):
        self.elementos.add(elemento)

    def agregar_observacion(self, observacion):
        self.observacion.add(observacion)

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

    def __str__(self):
        cadena = "Elementos: "
        for e in self.elementos.all():
            cadena += e.nombre+" "
        cadena += "  Items: "
        for item in self.items.all():
            cadena += "{fila}, {columna}".format(fila=item.fila_de_visado.nombre, columna=item.columna_de_visado.nombre)
        return cadena





