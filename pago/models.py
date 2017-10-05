# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from pago.models import *

# Create your models here.
class Tipo_Pago(models.Model):
    Pagos = [
        ('A','Debito'),
        ('B','Efectivo'),
    ]
    tipoPago=models.CharField(choices=Pagos, max_length=2)
    nombre= models.CharField(max_length=100)

    def __str__(self):
        return self.tipoPago


class Cuota(models.Model):
    fechaVencimiento=models.DateField
    fechaPago=models.DateField
    monto=models.IntegerField

    def calcularValorCuota(self):
        var=Pago()
        monto= Pago().valor / Pago().cantidadCuotas
        return self.monto

    def estado(self):
        if self.fechaPago is not None:
            return "cancelada"
        else:
            return "en espera de cancelacion"

class Pago(models.Model):
    tipoPago = models.ForeignKey(Tipo_Pago)
    cuota = models.ForeignKey(Cuota)
    valor = models.IntegerField()
    cantidadCuotas=models.IntegerField(null=False)
    fecha = models.DateField()

    def __str__(self):
        return 0

    def importe(self):
        return self.valor


    # def estado(self):
    #     if self.estados.exists():
    #         return self.estados.latest().related()

    # def hacer(self,accion,cuota=None):
    #     estado=self.estado()
    #     if estado is not None and hasattr(estado, accion):
    #         metodo = getattr(estado, accion)
    #         estado_nuevo = metodo(self)
    #         if estado is not None:
    #             estado_nuevo.cuota = cuota
    #             estado_nuevo.save()
    #     elif estado is None:
    #         cancelacion(cuota=cuota).save()
    #     else:
    #         raise Exception("La accion solicitada no se pudo realizar")
    #
    #



# class Estado(models.Model):
#     TIPO = 0
#     TIPOS = [
#         (0, "Estado")
#     ]
#     cuota = models.ForeignKey(Cuota, related_name='estados')  # FK related_name=estados
#     tipo = models.PositiveSmallIntegerField(choices=TIPOS)
#
#     class Meta:
#         get_latest_by = 'timestamp'
#     def save(self, *args, **kwargs):
#         if self.pk is None:
#             self.tipo = self.__class__.TIPO
#         super(Estado, self).save(*args, **kwargs)
#
#     def related(self):
#         return self.__class__ != Estado and self or getattr(self, self.get_tipo_display())
#
#
# class cancelacion(Estado):
#     TIPO = 1
#     def cancelacion(self, cuota):
#         if cuota.fechaPago is not None:
#             return cancelada(cuota=cuota)
#
# class cancelada(Estado):
#     TIPO = 2
#     def cancelada(self,cuota):
#         return cancelada(cuota=cuota)
