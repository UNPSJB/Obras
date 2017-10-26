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
        return self.annotate(max_id=models.Max('estados__id')).filter(
            estados__id=models.F('max_id'),
            estados__tipo__in=[e.TIPO for e in estados])


PlanillaManager = PlanillaInspeccionBaseManager.from_queryset(PlanillaInspeccionQuerySet)


class CategoriaInspeccion(models.Model):
    # Categoria A, Categoria B .....
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300)
    tipo = models.CharField(max_length=1)    # A, B, C, D, F

    def __str__(self):
        return self.nombre

class ItemInspeccion(models.Model): #Frente o fachada, paredes, techos, cielorraso,
    # revoques, puertas, ventanas, baños, cocinas, revestimientos, instalaciones complementarias, pisos
    nombre = models.CharField(max_length=100)
    categorias = models.ManyToManyField(CategoriaInspeccion, through='DetalleDeItemInspeccion')

    def __str__(self):
        return self.nombre

class DetalleDeItemInspeccion(models.Model):
    item_inspeccion = models.ForeignKey(ItemInspeccion)
    categoria_inspeccion = models.ForeignKey(CategoriaInspeccion)
    nombre = models.CharField(max_length=100)   # Marmol, piedra - Cristales,

    def __str__(self):
        return self.nombre

class DocumentoTecnicoInspeccion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=150)
    detalles = models.ManyToManyField(DetalleDeItemInspeccion, related_name="documentos")

    def __str__(self):
        return self.nombre