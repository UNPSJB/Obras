# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class PlanillaInspeccionBaseManager(models.Manager):
    pass

class PlanillaInspeccionQuerySet(models.QuerySet):
    def en_estado(self, estados):
        if type(estados) != list:
            estados = [estados]
        return self.annotate(max_id=models.Max('estados__id')).filter(estados__id=models.F('max_id'),estados__tipo__in=[e.TIPO for e in estados])

PlanillaManager = PlanillaInspeccionBaseManager.from_queryset(PlanillaInspeccionQuerySet)

class CategoriaInspeccion(models.Model):
    # Categoria A, Categoria B .....
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300)
    tipo = models.CharField(max_length=1)    # A, B, C, D, F

    def __str__(self):
        return self.nombre
    
    def relacionar_con_items(self, items):
        for item in items:
            self.relacionar_con_item(item)

    def relacionar_con_item(self, item):
        try:
            detalle = self.detalles.get(item_de_inspeccion=item)
            detalle.activo = True
            detalle.save()
            return detalle
        except DetalleDeItemInspeccion.DoesNotExist as ex:
            return DetalleDeItemInspeccion.objects.create(categoria_de_inspeccion=self, item_de_inspeccion=item)

    def quitar_item(self, item):
        try:
            detalle = self.detalles.get(item_de_inspeccion=item)
            detalle.activo = False
            detalle.save()
        except DetalleDeItemInspeccion.DoesNotExist as ex:
            pass

class ItemInspeccion(models.Model): #Frente o fachada, paredes, techos, cielorraso,
    # revoques, puertas, ventanas, baños, cocinas, revestimientos, instalaciones complementarias, pisos
    nombre = models.CharField(max_length=100)
    categorias = models.ManyToManyField(CategoriaInspeccion, through='DetalleDeItemInspeccion')

    def __str__(self):
        return self.nombre

    def relacionar_con_categorias(self, categorias):
        for categoria in categorias:
            self.relacionar_con_categoria(categoria)

    def relacionar_con_categoria(self, categoria):
        try:
            detalle = self.detalles.get(categoria_de_inspeccion=categoria)
            detalle.activo = True
            detalle.save()
            return detalle
        except DetalleDeItemInspeccion.DoesNotExist as ex:
            return DetalleDeItemInspeccion.objects.create(categoria_de_inspeccion=categoria, item_de_inspeccion=self)

    def quitar_item(self, categoria):
        try:
            detalle = self.detalles.get(categoria_de_inspeccion=categoria)
            detalle.activo = False
            detalle.save()
        except DetalleDeItemInspeccion.DoesNotExist as ex:
            pass

class DetalleDeItemInspeccion(models.Model):
    item_inspeccion = models.ForeignKey(ItemInspeccion, related_name="detalles")
    categoria_inspeccion = models.ForeignKey(CategoriaInspeccion, related_name="detalles")
    nombre = models.CharField(max_length=100)   # Marmol, piedra - Cristales,

    class Meta:
        ordering = ['item_inspeccion', 'categoria_inspeccion']

    def __str__(self):
        return "{categoria}, {item}".format(categoria=self.categoria_inspeccion.nombre, item=self.item_inspeccion.nombre)

 # class DocumentoTecnicoInspeccion(models.Model):
 #    nombre = models.CharField(max_length=100)
 #    descripcion = models.CharField(max_length=150)
 #    #detalles = models.ManyToManyField(DetalleDeItemInspeccion, related_name="nombre")
 #
 #    def __str__(self):
 #        return self.nombre

class PlanillaDeInspeccion(models.Model):
    #tramite = models.ForeignKey(Tramite)
    detalles = models.ManyToManyField(DetalleDeItemInspeccion, related_name="planillasInspeccion")
   # planillaLocales = models.ManyToManyField(PlanillaLocales, related_name="planillas")#esto nose si es asi

    def agregar_detalle(self, detalle):
        self.detalles.add(detalle)

    def quitar_detalle(self, detalle):
        self.detalles.remove(detalle)

    def detalle_activo(self, detalle):
        return self.detalles.filter(pk=detalle.pk).exists()







