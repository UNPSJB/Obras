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


PagoManager = PlanillaVisadoBaseManager.from_queryset(PlanillaVisadoQuerySet)

class Doc_Balance_Superficie(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre


class Elemento_Balance_Superficie(models.Model):
    Es = [
        ('C', 'Correcto'),
        ('I', 'Incorrecto'),
    ]
    elementoBalance = models.CharField(choices=Es, max_length=2)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=150)

    def __str__(self):
        return self.elementoBalance


class Tipo_De_Vista(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Elemento_De_Vista(models.Model):
    tipo_de_vista = models.ForeignKey(Tipo_De_Vista)
    nombre = models.CharField(choices=Pertenece, max_length=2)
    descripcion = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre


class Item_de_vista_en_elemento(models.Model):
    Pertenece = [
        ('S', 'Si'),
        ('N', 'No'),
    ]
    elementoDeVista = models.ForeignKey(Elemento_De_Vista)
    descripcion = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre