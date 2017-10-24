# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from pago.models import *
from django import template


# Create your models here.
class PagoBaseManager(models.Manager):
    pass


class PagoQuerySet(models.QuerySet):
    def en_estado(self, estados):
        if type(estados) != list:
            estados = [estados]
        return self.annotate(max_id=models.Max('estados__id')).filter(
            estados__id=models.F('max_id'),
            estados__tipo__in=[e.TIPO for e in estados])


PagoManager = PagoBaseManager.from_queryset(PagoQuerySet)


class Tipo_Pago(models.Model):
    Pagos = [
        ('A', 'Debito'),
        ('B', 'Efectivo'),
    ]
    tipoPago = models.CharField(choices=Pagos, max_length=2)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.tipoPago


class Cuota(models.Model):
    fechaVencimiento = models.DateField()
    fechaPago = models.DateField()
    monto = models.IntegerField()
    objects = PagoManager()

    def calcular_valor_cuota(self):
        self.monto = Pago().valor / Pago().cantidadCuotas
        return self.monto

    def estado(self):
        if self.estados.exists():
            return self.estados.latest().related()

    @classmethod
    def new(cls, tipo):
        t = cls(tipo=tipo)
        t.save()
        t.hacer(None, observacion="")
        return t

    def estados_related(self):
        return [estado.related() for estado in self.estados.all()]

    def hacer(self, accion, *args, **kwargs):
        estado_actual = self.estado()
        if estado_actual is not None and hasattr(estado_actual, accion):
            metodo = getattr(estado_actual, accion)
            estado_nuevo = metodo(self, *args, **kwargs)
            if estado_actual is not None:
                estado_nuevo.save()
        elif estado_actual is None:
            Cancelacion(cuota=self, *args, **kwargs).save()
        else:
            raise Exception("Tramite: La accion solicitada no se pudo realizar")


class Estado(models.Model):
    TIPO = 0
    TIPOS = [
        (0, "Estado")
    ]
    cuota = models.ForeignKey(Cuota, related_name='estados')  # FK related_name=estados
    tipo = models.PositiveSmallIntegerField(choices=TIPOS)
    marca = models.DateTimeField(auto_now=True)
    # usuario = models.ForeignKey(Usuario, null=True, blank=True)

    class Meta:
        get_latest_by = 'timestamp'

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.tipo = self.__class__.TIPO
        super(Estado, self).save(*args, **kwargs)

    def related(self):
        return self.__class__ != Estado and self or getattr(self, self.get_tipo_display())

    @classmethod
    def register(cls, klass):
        cls.TIPOS.append((klass.TIPO, klass.__name__.lower()))


class Cancelacion(Estado):
    TIPO = 1

    def cancelacion(self, cuota):
        if (cuota.fechaPago is not None):
            return Cancelada(cuota=cuota)
        return self


class Cancelada(Estado):
    TIPO = 2

    def cancelada(self, cuota):
        return Cancelada(cuota=cuota)

for Klass in [Cancelacion, Cancelada]:
    Estado.register(Klass)


class Pago(models.Model):
    CUOTAS = [
        (1, "Una Cuota"),
        (3, "Tres Cuotas"),
        (6, "Seis Cuotas"),
        (12, "Doce Cuotas"),
    ]
    tipoPago = models.ForeignKey(Tipo_Pago)
    cuota = models.ForeignKey(Cuota)
    valor = models.IntegerField()
    cantidadCuotas = models.IntegerField(null=False, choices=CUOTAS)
    fecha = models.DateField()

    def __str__(self):
        return 0

    def importe(self):
        return self.valor
