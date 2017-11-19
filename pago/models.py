# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from pago.models import *
from tramite.models import *
from django import template
from django.shortcuts import get_object_or_404

# Create your models here.
class PagoBaseManager(models.Manager):
    pass


class PagoQuerySet(models.QuerySet):
    def en_estado(self, estado_cuota):
        if type(estado_cuota) != list:
            estado_cuota = [estado_cuota]
        return self.annotate(max_id=models.Max('estado_cuota__id')).filter(
            estado_cuota__id=models.F('max_id'),
            estado_cuota__tipo__in=[e.TIPO for e in estado_cuota])

PagoManager = PagoBaseManager.from_queryset(PagoQuerySet)

class Tipo_Pago(models.Model):
    Pagos = [
        ('A', 'Debito'),
        ('B', 'Efectivo'),
    ]
    tipoPago = models.CharField(choices=Pagos, max_length=2)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Cuota(models.Model):
    fechaVencimiento = models.DateField(null=True, blank=True)
    fechaPago = models.DateField(auto_now_add=False) #false sino se llena cuando se crea el pago
    monto = models.IntegerField(null=True, blank=True)
    numeroCuota=models.IntegerField(null=True, blank=True)

    # pago=models.ForeignKey(Pago, related_name='pago', blank=True, null=True)
    objects = PagoManager()
    def __str__(self):
        return "Numero de Cuota: {} - monto: {}" .format(self.numeroCuota, self.monto)

    def guardar_fecha(self):
        self.fechaPago = datetime.datetime.now()

    def estados(self):
        if self.estado_cuota.exists():
            return self.estado_cuota.latest().related()

    @classmethod
    def new(cls, tipo):
        t = cls(tipo=tipo)
        t.save()
        t.hacer(None, observacion="")
        return t

    def hacer(self, accion, *args, **kwargs):
        estado_actual = self.estados()
        if estado_actual is not None and hasattr(estado_actual, accion):
            metodo = getattr(estado_actual, accion)
            estado_nuevo = metodo(self, *args, **kwargs)
            if estado_actual is not None:
                estado_nuevo.save()
        elif estado_actual is None:
            Cancelacion(cuota=self, *args, **kwargs).save()
        else:
            raise Exception("Cuota: La accion solicitada no se pudo realizar")

class Estado(models.Model):
    TIPO = 0
    TIPOS = [
        (0, "Estado")
    ]
    cuota = models.ForeignKey(Cuota, related_name='estado_cuota')  # FK related_name=estados
    tipo = models.PositiveSmallIntegerField(choices=TIPOS)
    marca = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'marca'

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
    tipoPago = models.ForeignKey(Tipo_Pago, blank=True, null=True)
    valor = models.IntegerField()#sacar
    cantidadCuotas = models.IntegerField(null=True, choices=CUOTAS, blank=True)
    cuota=models.ForeignKey(Cuota, blank=True, null=True) #foreign key o relacion uno a muchos
    fecha = models.DateTimeField(auto_now_add=True)  # para que sea la del momento que se da el alta

    def __str__(self):
        return "Numero de Pago: {} - cantidad de cuotas: {} - valor: {}" .format(self.pk, self.cantidadCuotas, self.valor)

    def guardar_valor(self): #sacar
        if self.tramite is not None:
            self.valor=self.tramite.monto_a_pagar
        return self.valor

    def importe(self):
        resultado=self.valor/self.cantidadCuotas
        return resultado
