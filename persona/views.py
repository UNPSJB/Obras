from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required

from .forms import *
from django.contrib import messages
from pago.forms import *
from tipos.forms import *
from obras_particulares.views import *
from tramite.forms import FormularioIniciarTramite
from documento.forms import FormularioDocumentoSetFactory
from documento.forms import metodo
from tramite.models import *
from django.core.mail import send_mail
from persona.models import *
from tramite.models import Tramite, Estado
from django.views.generic.detail import DetailView
import re
from datetime import datetime, date, time, timedelta
from django.views.generic.base import TemplateView
from openpyxl import Workbook
from django.http.response import HttpResponse
from django.views.generic import View
from django.conf import settings
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Table, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
import time
from datetime import datetime
import collections
from planilla_visado.models import ItemDeVisado
from pago.models import Cuota, Cancelacion,Cancelada,Estado
from datetime import date, timedelta

#-------------------------------------------------------------------------------------------------------------------
#generales ---------------------------------------------------------------------------------------------------------

DATETIME = re.compile("^(\d{4})\-(\d{2})\-(\d{2})\s(\d{2}):(\d{2})$")

def convertidor_de_fechas(fecha):

    return datetime(*[int(n) for n in DATETIME.match(fecha).groups()])

#-------------------------------------------------------------------------------------------------------------------
#propietario -------------------------------------------------------------------------------------------------------

@login_required(login_url="login")
@grupo_requerido('propietario')
def mostrar_propietario(request):
    contexto = {
        "ctxtramitespropietario": listado_tramites_propietario(request),
        "ctxmis_tramites_para_financiar": tramites_para_financiar(request),
    }
    #print(contexto)
    return render(request, 'persona/propietario/propietario.html', contexto)

def listado_tramites_propietario(request):
    tramites = Tramite.objects.all()
    personas = Persona.objects.all()
    usuario = request.user
    lista_de_persona_que_esta_logueada = filter(lambda persona: (persona.usuario is not None and persona.usuario == usuario), personas)
    persona = lista_de_persona_que_esta_logueada.pop()  # Saco de la lista la persona porque no puedo seguir trabajando con una lista
    propietario = persona.get_propietario()  # Me quedo con el atributo propietario de la persona
    tramites_de_propietario = filter(lambda tramite: (tramite.propietario == propietario), tramites)
    return tramites_de_propietario

def propietario_solicita_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(Tramite.SOLICITAR_FINAL_OBRA, request.user)
        messages.add_message(request, messages.SUCCESS, 'final de obra solicitado.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar el final de obra para ese tramite.')
    finally:
        return redirect('propietario')

def ver_historial_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    contexto0 = {'tramite': tramite}
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    contexto1 = {'estados_del_tramite': estados_de_tramite}
    fechas_del_estado = [];
    for est in estados_de_tramite:
        fechas_del_estado.append(est.timestamp.strftime("%d/%m/%Y"));
    return render(request, 'persona/propietario/ver_historial_tramite.html', {"tramite": contexto0, "estadosp": contexto1, "fecha":fechas_del_estado})

def documentos_de_estado(request, pk_estado):
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha}
    return render(request, 'persona/propietario/documentos_de_estado.html', contexto)

def tramites_para_financiar(request):
    tramites = Tramite.objects.all()
    personas = Persona.objects.all()
    usuario = request.user
    lista_de_persona_que_esta_logueada = filter(
        lambda persona: (persona.usuario is not None and persona.usuario == usuario), personas
    )
    persona = lista_de_persona_que_esta_logueada.pop()  # Saco de la lista la persona porque no puedo seguir trabajando con una lista
    propietario = persona.get_propietario()  # Me quedo con el atributo propietario de la persona
    tramites_propietario = Tramite.objects.en_estado(Visado)
    tramites_propietario = filter(lambda tramite: (tramite.propietario == propietario), tramites)
    contexto = {'tramites':tramites_propietario}
    return contexto

def elegir_financiacion(request,pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    print("tramite")
    print(tramite)
    return render(request, 'persona/cajero/elegir_financiacion.html',{'tramite': tramite, 'ctxpago':registrar_pago(request,tramite.id)})

#-------------------------------------------------------------------------------------------------------------------
#profesional -------------------------------------------------------------------------------------------------------

@login_required(login_url="login")
@grupo_requerido('profesional')
def mostrar_profesional(request):
    usuario = request.user
    #raise Exception(usuario.persona.profesional)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.INICIAR)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    tramite_form = FormularioIniciarTramite(initial={'profesional':usuario.persona.profesional.pk})
    propietario_form = FormularioPropietario()
    propietario = None
    #contexto = listado_tramites_de_profesional(request)
    if request.method == "POST":
        personas = Persona.objects.filter(dni=request.POST["propietario"])
        persona = personas.exists() and personas.first() or None
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        propietario_form = FormularioPropietario(request.POST)
        tramite_form = FormularioIniciarTramite(request.POST)
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        propietario = propietario_form.obtener_o_crear(persona)
        if propietario is not None and tramite_form.is_valid() and documento_set.is_valid():
            tramite = tramite_form.save(propietario=propietario, commit=False)
            lista=[]
            for docForm in documento_set:
               lista.append(docForm.save(commit=False))
            Tramite.new(
                usuario,
                propietario,
                usuario.persona.profesional,
                request.POST['tipo_obra'],
                request.POST['medidas'],
                request.POST['domicilio'],
                request.POST['parcela'],
                request.POST['circunscripcion'],
                request.POST['manzana'],
                request.POST['sector'],
                lista
            )
            tramite_form = FormularioIniciarTramite(initial={'profesional':usuario.persona.profesional.pk})
            propietario_form = None
        else:
            messages.add_message(request, messages.WARNING, 'Propietario no existe, debe darlo de alta para iniciar al tramite.')
    else:
        propietario_form = None
    contexto = {
        'documentos_requeridos': tipos_de_documentos_requeridos,
        'ctxtramitesprofesional': listado_tramites_de_profesional(request),
        'tramite_form': tramite_form,
        'propietario_form': propietario_form,
        'documento_set': documento_set,
        'ctxtramcorregidos':tramites_corregidos(request)
    }
    return render(request, 'persona/profesional/profesional.html', contexto)

def listado_tramites_de_profesional(request):
    tramites = Tramite.objects.all()
    personas = Persona.objects.all()
    usuario = request.user
    lista_de_persona_que_esta_logueada = filter(lambda persona: (persona.usuario is not None and persona.usuario == usuario), personas)
    persona = lista_de_persona_que_esta_logueada.pop()  #Saco de la lista la persona porque no puedo seguir trabajando con una lista
    profesional = persona.get_profesional() #Me quedo con el atributo profesional de la persona
    tramites_de_profesional = filter(lambda tramite: (tramite.profesional == profesional), tramites)
    contexto = {'tramites_de_profesional': tramites_de_profesional}
    return contexto

def tramites_corregidos(request):
    tramites = Tramite.objects.all()
    personas = Persona.objects.all()
    usuario = request.user
    lista_de_persona_que_esta_logueada = filter(lambda persona: (persona.usuario is not None and persona.usuario == usuario), personas)
    persona = lista_de_persona_que_esta_logueada.pop()  #Saco de la lista la persona porque no puedo seguir trabajando con una lista
    profesional = persona.get_profesional() #Me quedo con el atributo profesional de la persona
    tramites_de_profesional = filter(lambda tramite: (tramite.profesional == profesional), tramites)
    tipo = 4
    tram_corregidos = filter(lambda tramite: (tramite.estado().tipo == tipo), tramites_de_profesional)
    contexto = {'tramites': tram_corregidos}
    return contexto

def ver_documentos_tramite_profesional(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    contexto0 = {'tramite': tramite}
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    contexto1 = {'estados_del_tramite': estados_de_tramite}
    fechas_del_estado = [];
    for est in estados_de_tramite:
        fechas_del_estado.append(est.timestamp.strftime("%d/%m/%Y"));
    return render(request, 'persona/profesional/vista_de_documentos.html', {"tramite": contexto0, "estadosp": contexto1, "fecha":fechas_del_estado})

def profesional_solicita_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(Tramite.SOLICITAR_FINAL_OBRA, request.user)
        messages.add_message(request, messages.SUCCESS, 'final de obra solicitado.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar el final de obra para ese tramite.')
    finally:
        return redirect('profesional')

def ver_documentos_corregidos(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    if request.method == "POST":
        print ("faltan guardar documentos")
        enviar_correcciones(request, pk_tramite)
    else:
        return render(request, 'persona/profesional/ver_documentos_corregidos.html', {'tramite': tramite})
    return redirect('profesional')

def enviar_correcciones(request, pk_tramite):
    usuario = request.user
    #archivos = request.GET['msg']
    observacion = "Este tramite ya tiene los archivos corregidos cargados"
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(tramite.CORREGIR, request.user, observacion)
    messages.add_message(request, messages.SUCCESS, 'Tramite con documentos corregidos y enviados')
    return redirect('profesional')

def documento_de_estado(request, pk_estado):
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha}
    return render(request, 'persona/profesional/documento_de_estado.html', contexto)

#-------------------------------------------------------------------------------------------------------------------
#administrativo ----------------------------------------------------------------------------------------------------

@login_required(login_url="login")
@grupo_requerido('administrativo')
def mostrar_administrativo(request):

    contexto = {
        "ctxprofesional": profesional_list(request),
        "ctxpropietario": propietario_list(request),
        "ctxtramitesiniciados": listado_de_tramites_iniciados(request),
        "ctxtramitescorregidos": tramite_corregidos_list(request),
        "ctxsolicitudesfinalobra": solicitud_final_obra_list(request),
        "ctxpago": registrar_pago_tramite(request)
    }
    return render(request, 'persona/administrativo/administrativo.html', contexto)

def profesional_list(request):
    personas = Persona.objects.all()
    profesionales = filter(lambda persona: (persona.usuario is None and persona.profesional is not None), personas)
    contexto = {'personas': profesionales}
    return contexto

def propietario_list(request):
    propietarios = Propietario.objects.all()
    propietarios_sin_usuario = filter(lambda propietario: (propietario.persona.usuario is None and propietario.persona is not None ), propietarios)
    contexto = {'propietarios': propietarios_sin_usuario}
    return contexto

def listado_de_tramites_iniciados(request):
    tramites = Tramite.objects.en_estado(Iniciado)
    contexto = {'tramites': tramites}
    return contexto

def tramite_corregidos_list(request):
    tramites = Tramite.objects.en_estado(Corregido)
    contexto = {'tramites': tramites}
    return contexto

def solicitud_final_obra_list(request):
    tramites = Tramite.objects.en_estado(FinalObraSolicitado)
    contexto = {'tramites': tramites}
    return contexto

def registrar_pago_tramite(request):
    print(request.FILES)
    if request.method == "POST":
        print("POST")
        archivo_pago_form = FormularioArchivoPago(request.POST, request.FILES)
        if archivo_pago_form.is_valid():
            Pago.procesar_pagos(request.FILES['pagos'])
    else:
        archivo_pago_form = FormularioArchivoPago()
    #formulario = {'archivo_pago_form' : archivo_pago_form}
    return archivo_pago_form

def crear_usuario(request, pk_persona):
    usuario = request.user
    persona = get_object_or_404(Persona, pk=pk_persona)
    creado, password, usuario_creado = persona.crear_usuario()
    if creado:
        messages.add_message(request, messages.SUCCESS, 'usuario creado.')
        # Mandar correo al  nuevo usuario con su usurio y clave
        print("Mando correo de creado")
        send_mail(
            'Usuario habilitado',
            'Usted ya puede acceder al sistema: Nombre de usuario: '+persona.mail+' password: '+password,
            'infosopunpsjb@gmail.com',
            [persona.mail],
            fail_silently=False,
        )
        print (password)
    else:
        print("Mando correo informando que se cambio algo en su cuenta de usuario")
    return redirect(usuario.get_view_name())

def habilitar_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(tramite.FINALIZAR, request.user)
        messages.add_message(request, messages.SUCCESS, 'final de obra habilitado.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede otorgar final de obra total para ese tramite.')
    finally:
        return redirect('administrativo')

def aceptar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(tramite.ACEPTAR, request.user)
    messages.add_message(request, messages.SUCCESS, "Tramite aceptado")
    return redirect('administrativo')

def rechazar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(tramite.RECHAZAR, request.user, request.GET["msg"])
    messages.add_message(request, messages.WARNING, 'Tramite rechazado.')
    return redirect('administrativo')

class ver_un_certificado(DetailView):
    model = Persona
    template_name = 'persona/administrativo/ver_certificado_profesional.html'
    def dispatch(self, *args, **kwargs):
        return super(ver_un_certificado, self).dispatch(*args, **kwargs)

def ver_documentos_tramite_administrativo(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    return render(request, 'persona/administrativo/vista_de_documentos_administrativo.html', {'tramite': tramite})

#-------------------------------------------------------------------------------------------------------------------
#visador -----------------------------------------------------------------------------------------------------------

@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visador(request):
    contexto = {
        "ctxtramaceptado": tramites_aceptados(request),
        "ctxtramvisados": tramites_visados(request),
    }
    return render(request, 'persona/visador/visador.html', contexto)

def tramites_aceptados(request):
    aceptados = Tramite.objects.en_estado(Aceptado)
    contexto = {'tramites': aceptados}
    return contexto

def tramites_visados(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 3 #es el tipo de visado
    estados_visado = filter(lambda estado: (estado.usuario is not None and estado.usuario == usuario and estado.tipo == tipo), estados)
    contexto = {'estados': estados_visado}
    return contexto

def ver_documentos_para_visado(request, pk_tramite):
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.VISAR)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    return render(request, 'persona/visador/ver_documentos_tramite.html', {'tramite': tramite, 'documentos_requeridos': tipos_de_documentos_requeridos})
'''    if request.method == "POST":

        observacion = request.POST["observaciones"]
        tram = request.POST['tram']
        monto_permiso = request.POST['monto']

        if "Envia Planilla de visado" in request.POST:
            documento_set = FormularioDocumentoSet(request.POST, request.FILES)
            if documento_set.is_valid():
                for docForm in documento_set:
                    docForm.save(tramite=tramite)
            no_aprobar_visado(request, tram, observacion)
        else:
            aprobar_visado(request, tram, monto_permiso)
    else:
        #return render(request, 'persona/visador/ver_documentos_tramite.html', {'tramite': tramite, 'ctxdoc': documento_set, 'documentos_requeridos': tipos_de_documentos_requeridos})
        return render(request, 'persona/visador/ver_documentos_tramite.html', {'tramite': tramite, 'documentos_requeridos': tipos_de_documentos_requeridos})
'''
    #return redirect('visador')

def ver_documentos_visados(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    return render(request, 'persona/visador/ver_documentos_visados.html', {'tramite': tramite})

from planilla_visado.models import FilaDeVisado, ColumnaDeVisado, Elemento_Balance_Superficie

def planilla_visado(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    items = ItemDeVisado.objects.all()
    if request.method == "POST":
        observacion = request.POST["observaciones"]
        tram = request.POST['tram']
        monto_permiso = request.POST['monto']
        if "Envia Planilla de visado" in request.POST:
            no_aprobar_visado(request, tram, observacion)
        else:
            aprobar_visado(request, tram, monto_permiso)
    else:
        filas = FilaDeVisado.objects.all()
        columnas = ColumnaDeVisado.objects.all()
        elementosBalance = Elemento_Balance_Superficie.objects.all()
        return render(request, 'persona/visador/planilla_visado.html', {'tramite': tramite, 'items':items, 'filas':filas, 'columnas':columnas, 'elementosBalance':elementosBalance})
    #return render(request, 'persona/visador/planilla_visado.html', {'tramite': tramite})
    return redirect('visador')

from planilla_visado.models import PlanillaDeVisado

#def aprobar_visado(request, pk_tramite, monto,planilla_visado):
def aprobar_visado(request, pk_tramite, monto):
    usuario = request.user
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(tramite.VISAR, usuario)
    tramite.monto_a_pagar= monto
    tramite.save()
#    planilla_visado.save()
    messages.add_message(request, messages.SUCCESS, 'Tramite visado aprobado')
    return redirect('visador')

def no_aprobar_visado(request, pk_tramite, observacion):
    usuario = request.user
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    obs = observacion
    tramite.hacer(tramite.CORREGIR, usuario, obs)
    messages.add_message(request, messages.SUCCESS, 'Tramite con visado no aprobado')
    return redirect('visador')

class ReporteTramitesAceptadosExcel(TemplateView):

    def get(self, request, *args, **kwargs):
        tramites = Tramite.objects.en_estado(Aceptado)
        wb = Workbook()
        ws = wb.active
        ws['B1'] = 'REPORTE DE TRAMITES ACEPTADOS'
        ws.merge_cells('B1:F1')
        #ws['B2'] = 'FECHA_INICIO'
        ws['C2'] = 'TIPO_DE_OBRA'
        ws['D2'] = 'PROFESIONAL'
        ws['E2'] = 'PROPIETARIO'
        ws['F2'] = 'MEDIDAS'
        cont = 3
        for tramite in tramites:
            #ws.cell(row=cont, column=2).value = convertidor_de_fechas(tramite.estado.timestamp)
            #ws.cell(row=cont, column=2).value = tramite.estado.timestamp
            ws.cell(row=cont, column=3).value = str(tramite.tipo_obra)
            ws.cell(row=cont, column=4).value = str(tramite.profesional)
            ws.cell(row=cont, column=5).value = str(tramite.propietario)
            ws.cell(row=cont, column=6).value = tramite.medidas
            cont = cont + 1
        nombre_archivo = "ReportePersonasExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response

class ReporteTramitesAceptadosPdf(View):

    def get(self, request, *args, **kwargs):

        filename = "Informe de tramites.pdf"
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        doc = SimpleDocTemplate(
            response,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=15,
            bottomMargin=28,
        )
        Story = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Usuario', alignment=TA_RIGHT, fontName='Helvetica', fontSize=8))
        styles.add(ParagraphStyle(name='Titulo', alignment=TA_RIGHT, fontName='Helvetica', fontSize=18))
        styles.add(ParagraphStyle(name='Subtitulo', alignment=TA_RIGHT, fontName='Helvetica', fontSize=12))
        usuario = 'Usuario: ' + request.user.username + ' -  Fecha:' + ' ... aca va la fecha'
        Story.append(Paragraph(usuario, styles["Usuario"]))
        Story.append(Spacer(0, cm * 0.15))
        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=490, height=3)
        im0.hAlign = 'CENTER'
        Story.append(im0)
        titulo = 'SISTEMA OBRAS PARTICULARES'
        Story.append(Paragraph(titulo, styles["Titulo"]))
        Story.append(Spacer(0, cm * 0.20))
        subtitulo = 'Reporte De Tramites Iniciados para visar'
        Story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        Story.append(Spacer(0, cm * 0.15))
        Story.append(im0)
        Story.append(Spacer(0, cm * 0.5))
        encabezados = ('TIPO DE OBRA', 'PROFESIONAL', 'PROPIETARIO', 'MEDIDAS', 'ESTADO')
        detalles = [(tramite.tipo_obra, tramite.profesional, tramite.propietario, tramite.medidas, tramite.estado()) for
                    tramite in
                    Tramite.objects.en_estado(Aceptado)]
        detalle_orden = Table([encabezados] + detalles, colWidths=[4 * cm, 4 * cm, 4 * cm, 3 * cm, 2 * cm])
        detalle_orden.setStyle(TableStyle(
            [
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.gray),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
                ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ]
        ))
        detalle_orden.hAlign = 'CENTER'
        Story.append(detalle_orden)
        doc.build(Story)
        return response

#-------------------------------------------------------------------------------------------------------------------
#inspector ---------------------------------------------------------------------------------------------------------

@login_required(login_url="login")
@grupo_requerido('inspector')
def mostrar_inspector(request):
    contexto = {
        "ctxtramitesvisadosyconinspeccion": tramites_visados_y_con_inspeccion(request),
        "ctxtramitesinspeccionados": tramites_inspeccionados_por_inspector(request),
        "ctxtramitesagendados": tramites_agendados_por_inspector(request)
    }
    return render(request, 'persona/inspector/inspector.html', contexto)

def tramites_visados_y_con_inspeccion(request):
    argumentos = [Visado, ConInspeccion]
    tramites = Tramite.objects.en_estado(argumentos)
    return tramites

def tramites_inspeccionados_por_inspector(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 9
    estados_inspeccionados = filter(lambda estado: (estado.usuario is not None and estado.usuario == usuario and estado.tipo == tipo), estados)
    return estados_inspeccionados

def tramites_agendados_por_inspector(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 5
    #estados_agendados = filter(lambda estado: (estado.usuario is not None and estado.usuario == usuario and estado.tipo == tipo), estados)
    argumentos = [Visado, ConInspeccion]
    tramites = Tramite.objects.en_estado(Agendado)
    tramites_del_inspector = filter(lambda t: t.estado().usuario == usuario, tramites)
    #print (tramites_del_inspector)
    contexto = {"tramites_del_inspector": tramites_del_inspector}
    return tramites_del_inspector

def agendar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    fecha = convertidor_de_fechas(request.GET["msg"])
    tramite.hacer(Tramite.AGENDAR, request.user, fecha) #tramite, fecha_inspeccion, inspector=None
    return redirect('inspector')

def cargar_inspeccion(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.INSPECCIONAR)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
                if "aceptar_tramite" in request.POST:
                    print ("acepte el tramite")
                    aceptar_inspeccion(request, pk_tramite)
                elif "rechazar_tramite" in request.POST:
                    print ("rechace el tramite")
                    rechazar_inspeccion(request, pk_tramite)
        else:
            print("no entre al if")
    return render(request, 'persona/inspector/cargar_inspeccion.html', {'tramite': tramite, 'ctxdocumentoset': documento_set})

def rechazar_inspeccion(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.INSPECCIONAR, request.user)
    tramite.hacer(Tramite.CORREGIR, request.user, request.POST["observaciones"])  #request.POST["observaciones"]
    messages.add_message(request, messages.ERROR, 'Inspeccion rechazada')
    return redirect('inspector')

def aceptar_inspeccion(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.INSPECCIONAR, request.user)
    messages.add_message(request, messages.SUCCESS, 'Inspeccion aprobada')
    return redirect('inspector')

def ver_documentos_tramite_inspector(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    contexto0 = {'tramite': tramite}
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    contexto1 = {'estados_del_tramite': estados_de_tramite}
    fechas_del_estado = [];
    for est in estados_de_tramite:
        fechas_del_estado.append(est.timestamp.strftime("%d/%m/%Y"));
    return render(request, 'persona/inspector/documentos_tramite_inspector.html', {"tramite": contexto0, "estadosp": contexto1, "fechas":fechas_del_estado})

def documentos_inspector_estado(request, pk_estado):
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha}
    return render(request, 'persona/inspector/documentos_del_estado.html', contexto)

#------------------------------------------------------------------------------------------------------------------
#jefeinspector ----------------------------------------------------------------------------------------------------

@login_required(login_url="login")
@grupo_requerido('jefeinspector')
def mostrar_jefe_inspector(request):
    contexto = {
        "ctxtramitesconinspeccion": tramite_con_inspecciones_list(request),
        "ctxtramitesagendados": tramites_agendados_por_inspector(request),
    }
    return render(request, 'persona/jefe_inspector/jefe_inspector.html', contexto)

def tramite_con_inspecciones_list(request):
    tramites = Tramite.objects.en_estado(ConInspeccion)
    contexto = {'tramites': tramites}
    return contexto

def agendar_inspeccion_final(request,pk_tramite):
    tramite = get_object_or_404(Tramite,pk=pk_tramite)
    fecha = convertidor_de_fechas(request.GET["msg"])
    tramite.hacer(Tramite.AGENDAR, usuario=request.user, fecha_inspeccion=fecha, inspector=request.user)
    return redirect('jefe_inspector')

def cargar_inspeccion_final(request,pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    return render(request, 'persona/jefe_inspector/cargar_inspeccion_final.html', {'tramite': tramite})

def aceptar_inspeccion_final(request,pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    u = request.user
    tramite.hacer(Tramite.INSPECCIONAR, usuario=u, inspector=u)#agendado->ConInspeccion
    tramite.hacer(Tramite.INSPECCIONAR, usuario=u)#ConInspeccion->Inspeccionado
    messages.add_message(request, messages.SUCCESS, 'Inspeccion Finalizada')
    return redirect('jefe_inspector')

# ve la inspeccion de un tramite o inspecciones
def ver_inspecciones(request, pk_tramite):
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    estados = filter(lambda e: (e.tipo == 9), estados_de_tramite)
    contexto = {'estados': estados}
    return render(request, 'persona/jefe_inspector/vista_de_inspecciones.html',contexto)

#------------------------------------------------------------------------------------------------------------------
#director ---------------------------------------------------------------------------------------------------------
from planilla_visado import forms as pforms
from planilla_visado import models as pmodels
from planilla_inspeccion.forms import FormularioCategoriaInspeccion
from planilla_inspeccion.forms import FormularioItemInspeccion
from planilla_inspeccion.forms import FormularioDetalleItem
from planilla_inspeccion.models import *
from planilla_inspeccion.models import CategoriaInspeccion, ItemInspeccion, DetalleDeItemInspeccion

@login_required(login_url="login")
@grupo_requerido('director')
def mostrar_director(request):
    usuario = request.user
    items = ItemInspeccion.objects.all()
    detalles = DetalleDeItemInspeccion.objects.all()
    categorias = CategoriaInspeccion.objects.all()
    filas = FilaDeVisado.objects.all()
    columnas = ColumnaDeVisado.objects.all()
    itemsVisados = ItemDeVisado.objects.all()
    balancesSuperficies = Elemento_Balance_Superficie.objects.all()
    values = {"items":items, "categorias":categorias, "detalles":detalles, "filas": filas, "columnas":columnas, "itemsVisados":itemsVisados, "balancesSuperficies":balancesSuperficies}
    FORMS_DIRECTOR.update({(k.NAME, k.SUBMIT): k for k in [
        pforms.PlanillaDeVisadoFormFactory(pmodels.FilaDeVisado.objects.all(), pmodels.ColumnaDeVisado.objects.all()),
          ]})
    for form_name, submit_name in FORMS_DIRECTOR:
        KlassForm = FORMS_DIRECTOR[(form_name, submit_name)]
        if request.method == "POST" and submit_name in request.POST:
            _form = KlassForm(request.POST)
            if _form.is_valid():
                _form.save()
                messages.add_message(request, messages.SUCCESS, "La accion solicitada ha sido ejecutada con exito")
                return redirect(usuario.get_view_name())
            else:
                values["submit_name"] = submit_name
                messages.add_message(request, messages.ERROR, "La accion solicitada no a podido ser ejecutada")
            values[form_name] = _form
        else:
            values[form_name] = KlassForm()
    return render(request, 'persona/director/director.html', values)

FORMS_DIRECTOR = {(k.NAME, k.SUBMIT): k for k in {
    FormularioTipoDocumento,
    FormularioUsuarioPersona,
# este formulario no se necesitaria, solo se dan de alta visador, inspector y administrativo
    FormularioTipoObra,
    FormularioTipoDocumento,
    FormularioTipoPago,
    pforms.FormularioColumnaVisado,
    pforms.FormularioFilaVisado,
    pforms.FormularioItemDeVisado,
    #pforms.PlanillaDeVisadoFormFactory(pmodels.FilaDeVisado.objects.all(), pmodels.ColumnaDeVisado.objects.all()),
    pforms.FormularioElementoBalanceSuperficie,
    FormularioCategoriaInspeccion,
    FormularioItemInspeccion,
    FormularioDetalleItem
}}

def cambiar_usuario_de_grupo(request):
    contexto = {
        "ctxempleados": empleados(request),
        "ctxgrupos": grupos(request),
    }
    return render(request, 'persona/director/cambiar_usuario_de_grupo.html', contexto)

def empleados(request):
    personas = Persona.objects.all()
    #empleado = filter(lambda persona: (persona. == ), personas)
    contexto = {'persona': personas}
    return contexto

def grupos(request):
    grupos = Group.objects.all()
    contexto = {'grupo': grupos}
    return contexto

def ver_listado_todos_tramites(request):
    argumentos = [Iniciado, Aceptado, Visado, Corregido, Agendado, ConInspeccion, Inspeccionado, FinalObraSolicitado]
    tramites = Tramite.objects.en_estado(argumentos)
    estados = []
    for t in tramites:
        estados.append(t.estado().tipo);
    estados_cant = dict(collections.Counter(estados))
    for n in range(1, 9):
        if (not estados_cant.has_key(n)):
            estados_cant.setdefault(n, 0);
    estados_datos = estados_cant.values()
    contexto = {'todos_los_tramites': tramites, "datos_estados":estados_datos, "label_estados":argumentos}
    return render(request, 'persona/director/vista_de_tramites.html', contexto)

def ver_listado_todos_usuarios(request):
    grupos = Group.objects.all()
    label_grupos = []
    for g in grupos:
        label_grupos.append(g.name)
    usuarios = Usuario.objects.all()
    cant_usuarios_grupos = []
    for u in usuarios:
        for gu in u.get_view_groups():
            cant_usuarios_grupos.append(gu)
    total_usuarios_grupos = dict(collections.Counter(cant_usuarios_grupos))
    for lg in grupos:
        if (not total_usuaxrios_grupos.has_key(lg)):
            total_usuarios_grupos.setdefault(lg, 0)
    datos_grupos = total_usuarios_grupos.values()
    return render(request, 'persona/director/vista_de_usuarios.html', {"label_grupos":label_grupos, "datos_grupos":datos_grupos})

def detalle_de_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    contexto0 = {'tramite': tramite}
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    contexto1 = {'estados_del_tramite': estados_de_tramite}
    fechas_del_estado = [];
    for est in estados_de_tramite:
        fechas_del_estado.append(est.timestamp.strftime("%d/%m/%Y"));
    return render(request, 'persona/director/detalle_de_tramite.html', {"tramite": contexto0, "estados": contexto1, "fecha": fechas_del_estado})

def documentos_del_estado(request, pk_estado):
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha}
    return render(request, 'persona/director/documentos_del_estado.html', contexto)

def generar_planilla_visado(request):
     filas = FilaDeVisado.objects.all()
     #raise Exception(filas)
     #print (filas)
     columnas = ColumnaDeVisado.objects.all()
     balancesSuperficies = Elemento_Balance_Superficie.objects.all()
     itemsVisados = ItemDeVisado.objects.all()
     contexto = {'filas': filas, 'columnas':columnas, 'itemsVisados':itemsVisados,'balancesSuperficies':balancesSuperficies}
     #contexto_columnas = {'columnas': columnas}
     return render(request, 'persona/director/item_visado.html', contexto)

def ver_planilla_inspeccion(request):
     items = ItemInspeccion.objects.all()
     detalles = DetalleDeItemInspeccion.objects.all()
     categorias = CategoriaInspeccion.objects.all()     
     contexto = {'items': items}
     #return render(request, 'persona/director/ver_planilla_inspeccion.html', {"items":items, "detalles": detalles, "categorias":categorias})
     return render(request, 'persona/director/ver_planilla_inspeccion.html', contexto)

class ReporteTramitesDirectorExcel(TemplateView):

    def get(self, request, *args, **kwargs):
        tramites = Tramite.objects.all()
        wb = Workbook()
        ws = wb.active
        ws['A1'] = 'REPORTE DE TRAMITES'
        ws.merge_cells('B1:G1')
        #ws['B2'] = 'FECHA_INICIO'
        ws['B2'] = 'NRO'
        ws['C2'] = 'TIPO_DE_OBRA'
        ws['D2'] = 'PROFESIONAL'
        ws['E2'] = 'PROPIETARIO'
        ws['F2'] = 'MEDIDAS'
        cont = 3
        for tramite in tramites:
            #ws.cell(row=cont, column=2).value = convertidor_de_fechas(tramite.estado.timestamp)
            #ws.cell(row=cont, column=2).value = tramite.estado.timestamp
            ws.cell(row=cont, column=2).value = tramite.id
            ws.cell(row=cont, column=3).value = str(tramite.tipo_obra)
            ws.cell(row=cont, column=4).value = str(tramite.profesional)
            ws.cell(row=cont, column=5).value = str(tramite.propietario)
            ws.cell(row=cont, column=6).value = tramite.medidas
            cont = cont + 1
        nombre_archivo = "ReportePersonasExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response

class ReporteTramitesDirectorPdf(View):

    def get(self, request, *args, **kwargs):

        filename = "Informe de tramites.pdf"
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        doc = SimpleDocTemplate(
            response,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=15,
            bottomMargin=28,
        )
        Story = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Usuario', alignment=TA_RIGHT, fontName='Helvetica', fontSize=8))
        styles.add(ParagraphStyle(name='Titulo', alignment=TA_RIGHT, fontName='Helvetica', fontSize=18))
        styles.add(ParagraphStyle(name='Subtitulo', alignment=TA_RIGHT, fontName='Helvetica', fontSize=12))
        usuario = 'Usuario: ' + request.user.username + ' -  Fecha:' + ' ... aca va la fecha'
        Story.append(Paragraph(usuario, styles["Usuario"]))
        Story.append(Spacer(0, cm * 0.15))
        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=490, height=3)
        im0.hAlign = 'CENTER'
        Story.append(im0)
        titulo = 'SISTEMA OBRAS PARTICULARES'
        Story.append(Paragraph(titulo, styles["Titulo"]))
        Story.append(Spacer(0, cm * 0.20))
        subtitulo = 'Reporte de tramites'
        Story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        Story.append(Spacer(0, cm * 0.15))
        Story.append(im0)
        Story.append(Spacer(0, cm * 0.5))
        encabezados = ('NRO', 'TIPO_DE_OBRA', 'PROFESIONAL', 'PROPIETARIO', 'MEDIDAS', 'ESTADO')
        detalles = [
            (tramite.id, tramite.tipo_obra, tramite.profesional, tramite.propietario, tramite.medidas, tramite.estado())
            for tramite in
            Tramite.objects.all()]
        detalle_orden = Table([encabezados] + detalles, colWidths=[1 * cm, 3 * cm, 4 * cm, 4 * cm, 2 * cm, 3 * cm])
        detalle_orden.setStyle(TableStyle(
            [
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.gray),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
                ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ]
        ))
        detalle_orden.hAlign = 'CENTER'
        Story.append(detalle_orden)
        doc.build(Story)
        return response


#-------------------------------------------------------------------------------------------------------------------
#No se de donde son estos------------------------------------------------------------------

def tramite_visados_list(request):
    tramites = Tramite.objects.en_estado(Visado) #cambiar a visados cuando etengas tramites visaddos
    contexto = {'tramites': tramites}
    return contexto

def mostrar_popup_datos_agendar(request,pk_tramite):
    pass

def alta_persona(request):
    if request.method == "POST":
        form = FormularioPersona(request.POST)
        if form.is_valid():
            persona = form.save()
            persona.save()
    else:
        form = FormularioPersona()
    return render(request, 'persona/alta/alta_persona.html', {'form': form})

#------------------------------------------------------------------------------------------------------------------
#cajero ---------------------------------------------------------------------------------------------------------

def mostrar_cajero(request):
    contexto = {
        "ctxtramites_para_financiar": listado_tramites_para_financiar(request),
        "ctxcuotas":listado_cuotas(request)
    }    
    return render(request, 'persona/cajero/cajero.html', contexto)

def listado_tramites_para_financiar(request):
    tramites = Tramite.objects.en_estado(Visado)
    contexto = {'tramites':tramites}
    print ("contexto")
    print(contexto)
    return contexto

def elegir_financiacion(request,pk_tramite):    
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    print("tramite")
    print(tramite)
    return render(request, 'persona/cajero/elegir_financiacion.html',{'tramite': tramite, 'ctxpago':registrar_pago(request,tramite.id)})

def registrar_pago(request,pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    if request.method == "POST":
        form = FormularioPago(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            # pago.valor=pago.guardar_valor()
            print(pago.valor)
            print(pago.cantidadCuotas)
            contador=31
            fms = "%A"
            for i in range(1, pago.cantidadCuotas+1):
                total = pago.importe()
                cuota = Cuota(monto=total,numeroCuota=i)
                print("valor")
                print(i)
                cuota.fechaVencimiento=date.today() + timedelta(days=contador)
                dia=cuota.fechaVencimiento.strftime(fms)
                if (dia=="Sunday"):
                    cuota.fechaVencimiento=date.today() + timedelta(days=contador+1)
                else:
                    if (dia=="Saturday"):
                        cuota.fechaVencimiento = date.today() + timedelta(days=contador + 2)
                contador=contador+31
                cuota.save()
                cuota.hacer("Cancelacion")
            pago.save()
            tramite.pago=pago
            tramite.save()
    else:
        # initial = {'valor':}
        form = FormularioPago(initial = {'valor':tramite.monto_a_pagar})
    return form

def listado_cuotas(request):
    cuotas=Cuota.objects.en_estado(Cancelacion)
    contexto= {'cuotas':cuotas}
    return contexto

def elegir_cuota(request,pk_cuota):
    cuota=get_object_or_404(Cuota,pk=pk_cuota)
    cuota.guardar_fecha()
    cuota.save()
    cuota.hacer("cancelacion")
    messages.add_message(request, messages.SUCCESS, 'Pago Registrado.')
    return redirect('cajero')

#
# def actualizar_cuota(request, pk_cuota):
#     cuota=get_object_or_404(Cuota,pk=pk_cuota)
#     if request.method=="GET":
#         form=FormularioCuota(instance=cuota)
#         try:
#             print (form.errors)
#             fecha = datetime.datetime.now()
#             print(fecha)
#             print(form.errors)
#         except:
#         if form.is_valid():
#             form.save()
#     else:
#         form=FormularioCuota(request.POST,instance=cuota)
#         if form.is_valid():
#             form.save()
#     return redirect('persona/cajero/cajero.html')

#------------------------------------------------------------------------------------------------------------------
#movil ---------------------------------------------------------------------------------------------------------

def movil_login(request):        
    return render(request, 'movil/templates/login.html', contexto)

def movil_inspector(request):
    #return render(request, 'persona/movil/inspector.html')
    return render(request, 'persona/movil/planilla_inspeccion.html')

def frente_o_fachada(request):
    return render(request,'persona/movil/frente_o_fachada.html')    

def paredes(request):    
    return render(request,'persona/movil/paredes.html')    

def cocinas(request):    
    return render(request,'persona/movil/cocinas.html')    

def techos(request):    
    return render(request,'persona/movil/techos.html')                

def mostrar_inspector_movil(request):
    argumentos = [Visado, ConInspeccion]
    tramites = Tramite.objects.en_estado(argumentos)    
    return render(request, 'persona/movil/inspector_movil.html', {'tramites':tramites})

def planilla_inspeccion_movil(request,pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    contexto = {'tramite': tramite}    
    return render(request, 'persona/movil/planilla_inspeccion.html',contexto)

