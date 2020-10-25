from __future__ import unicode_literals
import datetime
from django.utils import timezone

from django.db import models


class TipoDocumento(models.Model):
    INICIAR = 1 << 0
    REVISAR = 1 << 1
    CORREGIR = 1 << 2
    VISAR = 1 << 3
    AGENDAR = 1 << 4
    #INSPECCIONAR = 1 << 5 se cambio nro de estado en tramite
    INSPECCIONAR = 1 << 6
    # realizar el pago de un tramite
    #PAGAR = 1 << 6 se cambio nro de estado en tramite
    PAGAR = 1 << 7
    # Finalizar la obra esto es cuando se pide un final de obra por el ...
    #FINALIZAR = 1 << 7 se cambio nro de estado en tramite
    FINALIZAR = 1 << 8
    ACCIONES = [
        (INICIAR, 'Iniciar un tramite'),
        (CORREGIR, 'Corregir un documento durante el tramite'),
        (REVISAR, 'Revisar Correcciones'),
        (VISAR, 'Visar un Tramite'),
        (AGENDAR, 'Agendar nueva fecha de inspeccion'),
        (INSPECCIONAR, 'Registrar una inspeccion'),
        (PAGAR, 'Realizar el pago de un tramite'),
        (FINALIZAR, 'Solicitud de final de obra')
    ]
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateField()
    fecha_baja = models.DateField(blank=True, null=True)
    requerido = models.IntegerField(default=0)

    def __str__(self):
        return "{}, {}".format(self.nombre, self.descripcion)


    # recibe una accion "visar", "iniciar", etc y devuelve una lista de tipos para esa accion particular
    @staticmethod
    def get_tipos_documentos_para_momento(accion):
        devolucion = []
        for tipo in TipoDocumento.objects.all():
            if ((tipo.requerido & accion) == accion):
                devolucion.append(tipo)
        return devolucion


class TipoObra(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=100)
    categorias = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return "Cat. %s" %(self.nombre)

    @staticmethod
    def tipos_para_profesional(categorias):
        return TipoObra.objects.filter(categorias__contains=categorias)

#AGREGO EL TIPO DE PAGO

class Tipo_Pago(models.Model):
    nombre = models.CharField(max_length=50,unique=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre