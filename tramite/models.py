from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
import datetime
from persona.models import *
from tipos.models import *
from pago.models import *
from django import template

register = template.Library()

from openpyxl import load_workbook

"""from django_excel import *
import pyexcel as pe"""
from os.path import basename
import csv
from decimal import Decimal


class TramiteBaseManager(models.Manager):
    pass


class TramiteQuerySet(models.QuerySet):
    def en_estado(self, estados):
        if type(estados) != list:
            estados = [estados]
        return self.annotate(max_id=models.Max('estados__id')).filter(
            estados__id=models.F('max_id'),
            estados__tipo__in=[e.TIPO for e in estados])


TramiteManager = TramiteBaseManager.from_queryset(TramiteQuerySet)


class Tramite(models.Model):
    INICIAR = "iniciar"
    REVISAR = "revisar"
    CORREGIR = "corregir"
    ACEPTAR = "aceptar"
    RECHAZAR = "rechazar"
    VISAR = "visar"
    AGENDAR = "agendar"
    INSPECCIONAR = "inspeccionar"
    # realizar el pago de un tramite
    PAGAR = "pagar"
    # Finalizar la obra esto es cuando se pide un final de obra por el ...
    FINALIZAR = "finalizar"
    SOLICITAR_FINAL_OBRA = "solicitar_final_obra"
    propietario = models.ForeignKey(Propietario, blank=True, null=True, unique=False)
    profesional = models.ForeignKey(Profesional, unique=False)
    medidas = models.IntegerField()
    tipo_obra = models.ForeignKey(TipoObra)
    domicilio = models.CharField(max_length=50)
    pago = models.OneToOneField(Pago, default=True, blank=True, null=True)
    mactivo = models.IntegerField(blank=True, null=True)
    # -------------------------------------------------------------------------------------
    # DATOS CATASTRALES
    parcela = models.IntegerField() #models.CharField(max_length=20)
    circunscripcion = models.IntegerField()#models.CharField(max_length=20)
    manzana = models.IntegerField()#models.CharField(max_length=20)
    sector = models.IntegerField()#models.CharField(max_length=20)
    # -------------------------------------------------------------------------------------
    monto_a_pagar = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    monto_pagado = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    objects = TramiteManager()

    def __str__(self):
        return "Numero de tramite: {} - Profesional: {} - Propietario: {} - Pago {} ".format(self.pk, self.profesional,
                                                                                             self.propietario,
                                                                                             self.pago)

    @classmethod
    def new(cls, usuario, propietario, profesional, tipo_obra, medidas, domicilio, parcela, circunscripcion, manzana,
            sector, documentos):
        print("nuevo tramite")
        if any(map(lambda d: d.tipo_documento.requerido != TipoDocumento.INICIAR, documentos)):
            raise Exception("Un documento no es de tipo iniciar")
        t = cls(
            domicilio=domicilio,
            propietario=propietario,
            profesional=profesional,
            medidas=medidas,
            parcela=parcela,
            circunscripcion=circunscripcion,
            sector=sector,
            manzana=manzana,
            tipo_obra=TipoObra.objects.get(pk=tipo_obra),
            pago=None,
            monto_pagado=0
        )
        t.save()
        for doc in documentos:
            doc.tramite = t
            doc.save()
        t.hacer(Tramite.INICIAR, usuario, observacion="Arranca el tramite")
        return t

    def saldo_restante_a_pagar(self):
        if self.monto_a_pagar == None or self.monto_pagado == None:
            return 0
        else:
            return self.monto_a_pagar - self.monto_pagado

    def esta_pagado(self):
        if (self.monto_pagado is None):
            self.monto_pagado = 0
        if ((self.monto_pagado) == self.monto_a_pagar):
            return True
        else:
            return False

    def documentacion_para_estado(self, estado):
        previo = estado.previo()
        primero = estado.siguiente()
        # visados = list(self.visados.all())
        # inspecciones = list(self.inspecciones.all())
        # documentos = list(self.documentos.all())
        if primero and not previo:
            visados = list(self.visados.filter(fecha__lte=estado.timestamp, fecha__gte=primero.timestamp))
            inspecciones = list(self.inspecciones.filter(fecha__lte=estado.timestamp, fecha__gte=primero.timestamp))
            documentos = list(self.documentos.filter(fecha__lte=estado.timestamp))
            return {'planillas': visados, 'inspecciones': inspecciones, 'documentos': documentos}
        else:
            if previo:
                if estado.tipo==2 :
                    anterior = previo.previo()
                    try:
                        visados = list(self.visados.filter(fecha__lte=previo.timestamp, fecha__gte=anterior.timestamp))
                    except:
                        visados = list(self.visados.filter(fecha__lte=previo.timestamp))
                    try:
                        inspecciones = list(
                            self.inspecciones.filter(fecha__lte=estado.timestamp, fecha__gte=primero.timestamp))
                    except:
                        inspecciones = list(self.inspecciones.filter(fecha__lte=previo.timestamp))

                    try:
                        documentos = list(self.documentos.filter(fecha__lte=estado.timestamp))
                    except:
                        pass
                elif  estado.tipo==4:
                    anterior=previo.previo()
                    try:
                        visados = list(self.visados.filter(fecha__range=(previo.timestamp,estado.timestamp)))
                    except:
                        visados = list(self.visados.filter(fecha__lte=previo.timestamp))
                    try:
                        inspecciones = list(self.inspecciones.filter(fecha__lte=estado.timestamp, fecha__gte=primero.timestamp))
                    except:
                        inspecciones = list(self.inspecciones.filter(fecha__lte=previo.timestamp))

                    try:
                        anterior=previo.previo()
                        documentos = list(self.documentos.filter(fecha__lte=estado.timestamp, fecha__gte=anterior.timestamp))
                    except:
                        documentos = list(self.documentos.filter(fecha__lte=estado.timestamp))
                elif estado.tipo==5:
                    documentos=None
                    visados = None
                    try:
                        inspecciones = list(self.inspecciones.filter(fecha__lte=primero.timestamp, fecha__gte=estado.timestamp))
                    except:
                        inspecciones = None
                elif estado.tipo==7:
                    inspecciones = list(self.inspecciones.all())
                    visados=None
                    documentos=None
                elif estado.tipo==8 or estado.tipo==9:
                    visados = list(self.visados.all())
                    inspecciones = list(self.inspecciones.all())
                    documentos = list(self.documentos.all())
                else:
                    try:
                        visados = list(self.visados.filter(fecha__range=(previo.timestamp,estado.timestamp)))
                    except:
                        visados=None
                    try:
                        inspecciones = list(self.inspecciones.filter(fecha__lte=estado.timestamp, fecha__gte=previo.timestamp))
                    except:
                        inspecciones=None
                    try:
                        documentos = list(self.documentos.filter(fecha__range=(previo.timestamp, estado.timestamp)))
                    except:
                        documentos=None
            else:
                visados = list(self.visados.filter(fecha=estado.timestamp))
                inspecciones = list(self.inspecciones.filter(fecha=estado.timestamp))
                documentos = list(self.documentos.filter(fecha__lte=estado.timestamp))

            return {'planillas': visados, 'inspecciones': inspecciones, 'documentos': documentos}

            #previo = estado.previo()
        # visados = list(self.visados.all())
        # inspecciones = list(self.inspecciones.all())
        # documentos = list(self.documentos.all())
        #if previo:
         #   visados = list(self.visados.filter(fecha__lte=estado.timestamp, fecha__gte=previo.timestamp))
          #  inspecciones = list(self.inspecciones.filter(fecha__lte=estado.timestamp, fecha__gte=previo.timestamp))
           # documentos = list(self.documentos.filter(fecha__lte=estado.timestamp))
            #tramites = get_object_or_404(Tramite, pk=self.pk)
        #else:
         #   visados = list(self.visados.filter(fecha=estado.timestamp))
          #  inspecciones = list(self.inspecciones.filter(fecha=estado.timestamp))
           # documentos = list(self.documentos.filter(fecha=estado.timestamp))
            # return visados + inspecciones + documentos
        #return {'planillas': visados, 'inspecciones': inspecciones, 'documentos': documentos}

    def estado(self):
        if self.estados.exists():
            return self.estados.latest().related()

    def estadosTramite(self):
        if self.estados.exists():
            return self.estados.all()

    def quien_lo_inspecciono(self):
        agendados = filter(lambda e: isinstance(e, Agendado), self.estados)
        return ", ".join(["%s %s lo inspecciono" % (a.fecha_inspeccion, a.inspector) for a in agendados])

    def hacer(self, accion, usuario=None, *args, **kwargs):
        estado_actual = self.estado()
        if estado_actual is not None and hasattr(estado_actual, accion):
            metodo = getattr(estado_actual, accion)
            estado_nuevo = metodo(self, *args, **kwargs)
            if estado_actual is not None:
                estado_nuevo.usuario = usuario
                estado_nuevo.save()
        elif estado_actual is None:
            Iniciado(tramite=self, usuario=usuario, *args, **kwargs).save()
        else:
            raise Exception("Tramite: La accion solicitada no se pudo realizar")

    def calcular_monto_pagado(self, monto):
        if (self.monto_pagado <= 0):
            self.monto_pagado = monto
        else:
            self.monto_pagado = self.monto_pagado + monto
        self.save()
        return self.monto_pagado


class Estado(models.Model):
    TIPO = 0
    TIPOS = [
        # (0, "Estado"),
        (1, "Iniciado"),
        (2, "Aceptado"),
        (3, "Visado"),
        (4, "Corregido"),
        (5, "Agendado"),
        (6, "Con Inspeccion"),
        (7, "Inspeccionado"),
        (8, "Final de obra solicitado"),
        (9, "Finalizado"),
    ]
    tramite = models.ForeignKey(Tramite, related_name='estados')  # FK related_name=estados
    tipo = models.PositiveSmallIntegerField(choices=TIPOS)
    usuario = models.ForeignKey(Usuario)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'

    def previo(self):
        fecha = self.timestamp
        return self.tramite.estados.filter(timestamp__lt=fecha).last()

    def siguiente(self):
        return self.tramite.estados.filter(timestamp__gt=self.timestamp).first()

    def primero(self):
        fecha = self.timestamp
        return self.tramite.estados.filter(tipo=1).first()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.tipo = self.__class__.TIPO
        super(Estado, self).save(*args, **kwargs)

    def agregar_documentacion(self, documentos_requeridos):
        self.tramite.documentos.add(documento)

    def related(self):
        return self.__class__ != Estado and self or getattr(self, self.get_tipo_display())

    @classmethod
    def register(cls, klass):
        cls.TIPOS.append((klass.TIPO, klass.__name__.lower()))

    def get_usuario(self):
        return self.usuario

    def __str__(self):
        return "{}".format(self.TIPOS[self.tipo - 1][1])


class Iniciado(Estado):
    TIPO = 1
    CADENA_DEFAULT = "En este momento no se poseen observaciones sobre el tramite"
    observacion = models.CharField(max_length=100, default=CADENA_DEFAULT, blank=True)

    def aceptar(self, tramite):
        return Aceptado(tramite=tramite)

    def rechazar(self, tramite, observacion):
        print (observacion)
        return Corregido(tramite=tramite, observacion=observacion)

    def __str__(self):
        return "Iniciado"


class Aceptado(Estado):
    TIPO = 2
    def visar(self, tramite):
        return Visado(tramite=tramite)

    def corregir(self, tramite, observacion):
        return Corregido(tramite=tramite, observacion=observacion)

    def __str__(self):
        return "Aceptado"


class Visado(Estado):
    TIPO = 3

    def agendar(self, tramite, fecha_inspeccion, inspector, rol):
        return Agendado(tramite=tramite, fecha=fecha_inspeccion, inspector=inspector, rol=rol)


class Corregido(Estado):
    TIPO = 4
    CADENA_DEFAULT = "En este momento no se poseen observaciones sobre el tramite"
    observacion = models.CharField(max_length=100, default=CADENA_DEFAULT, blank=True, null=True)

    def corregir(self, tramite, observacion=None):
        # e = Iniciado(tramite=tramite, observacion=observacion)
        # e.agregar_documentacion(documentos_requeridos=documentos)
        # return e
        return Iniciado(tramite=tramite, observacion=observacion)


class Agendado(Estado):
    TIPO = 5
    inspector = models.ForeignKey(Usuario, null=True, blank=True)
    fecha = models.DateTimeField(blank=False)
    rol = models.IntegerField(blank=True, null=True)

    def inspeccionar(self, tramite, inspector=None):
        return ConInspeccion(tramite=tramite, inspector=inspector)


class ConInspeccion(Estado):
    TIPO = 6
    inspector = models.ForeignKey(Usuario, null=True, blank=True)

    def solicitar_final_obra(self, tramite):
        return FinalObraSolicitado(tramite=tramite, final_obra_total=False)

    def agendar(self, tramite, fecha_inspeccion, inspector, rol):
        return Agendado(tramite=tramite, fecha=fecha_inspeccion, inspector=inspector, rol=rol)

    def inspeccionar(self, tramite):
        return Inspeccionado(tramite=tramite)

    def corregir(self, tramite, observacion):
        return Corregido(tramite=tramite, observacion=observacion)

    def __str__(self):
        return str(self.__class__.__name__)


class Inspeccionado(Estado):
    TIPO = 7

    def solicitar_final_obra(self, tramite):  # solicitar final de obra
        if self.tramite.esta_pagado():  # Tramite.objects.get(pk=tramite.pk).pago_completo
            return FinalObraSolicitado(tramite=tramite, final_obra_total=True)
        else:
            return FinalObraSolicitado(tramite=tramite, final_obra_total=False)

    def finalizar(self, tramite):
        if (tramite.monto_pagado+1 >= tramite.monto_a_pagar):  # Tramite.objects.get(pk=tramite.pk).pago_completo
            return Finalizado(tramite=tramite)
        else:
            raise Exception("Todavia no se puede otorgar el final de obra")

class FinalObraSolicitado(Estado):
    TIPO = 8

    final_obra_total = models.BooleanField(blank=True)

    def finalizar(self, tramite):
        if (tramite.monto_pagado >= tramite.monto_a_pagar) and tramite.estados.filter(tipo=7):  # Tramite.objects.get(pk=tramite.pk).pago_completo
            return Finalizado(tramite=tramite)
        else:
            raise Exception("Todavia no se puede otorgar el final de obra")

    def agendar(self, tramite, fecha_inspeccion, inspector, rol):
        return Agendado(tramite=tramite, fecha=fecha_inspeccion, inspector=inspector, rol=rol)


class Finalizado(Estado):
    TIPO = 9


for klass in [Iniciado, Aceptado, Visado, Corregido, Agendado, Inspeccionado, Finalizado, ConInspeccion,
              FinalObraSolicitado]:
    Estado.register(klass)


# class Pago(models.Model):
#     tramite = models.ForeignKey(Tramite)
#     fecha = models.DateField(auto_now=True)
#     monto = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         cabecera = '{0} - {1}'.format(self.tramite.pk, self.fecha)
#         return cabecera
#
#     @classmethod
#     def procesar_pagos(cls, archivo):
#
#         datos = archivo.read()
#
#         #La siguientes linea arma un diccionario para poder recorrer el archivo mejor
#         spliter = lambda datos: [ l.split('"')[:2] for l in datos.splitlines()[1:]]
#
#         datos_diccionario = []
#
#         #Esta linea arma una lista de cadenas de la siguiente forma: {'monto': xxxxxx, 'id': xx}
#         try:
#             for idt, monto in spliter(datos):
#                 datos_diccionario.append({"id": int(idt[:-1]), "monto": Decimal(monto[1:].replace(".","").replace(",", "."))})
#
#             for linea in datos_diccionario:
#                 try:
#                     monto_pagado = linea['monto']
#                     id_tramite = int(linea['id'])
#                     tramite = Tramite.objects.get(pk=id_tramite)
#                     tramite.calcular_monto_pagado(monto_pagado)
#                     p = cls(tramite=tramite, monto=monto_pagado)
#                     p.save()
#                 except Tramite.DoesNotExist:
#                     print 'El tramite con numero: {0}, no existe en el sistema. Se ignora su pago.'.format(id_tramite)
#
#         except ValueError:
#             print('El archivo cargado no tiene el formato correcto.')


@register.filter(is_safe=True)
def es_instancia(estado, cadena):
    if isinstance(estado, cadena):
        return True
    else:
        return False
