from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required,user_passes_test
import easygui as eg
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
from django.views.generic.base import TemplateView
from openpyxl import Workbook
from django.http.response import HttpResponse
from django.views.generic import View
from django.conf import settings
from io import BytesIO
from datetime import date

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Table, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.validators import Auto
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String
import base64;
import time
import collections
from planilla_visado.models import ItemDeVisado
from pago.models import Cuota, Cancelacion,Cancelada,Estado
from datetime import datetime, date, time, timedelta
from documento.models import Documento

#-------------------------------------------------------------------------------------------------------------------
#generales ---------------------------------------------------------------------------------------------------------


DATETIME = re.compile("^(\d{4})\-(\d{2})\-(\d{2})\s(\d{2}):(\d{2})$")

def convertidor_de_fechas(fecha):
    return datetime.datetime(*[int(n) for n in DATETIME.match(fecha).groups()])    

#-------------------------------------------------------------------------------------------------------------------
#propietario -------------------------------------------------------------------------------------------------------

@login_required(login_url="login")
@grupo_requerido('propietario')
def mostrar_propietario(request):
    estilos = ''
    usuario = request.user
    propietario = get_object_or_404(Propietario, pk=usuario.persona.propietario.pk)
    if request.method == "POST":
        if "Aceptar" in request.POST:
            estilos = request.POST.get('estilo')
            usuario = request.user
            propietario = Propietario.objects.filter(id=usuario.persona.propietario.pk).update(estilo=estilos)
    else:
        if propietario.estilo:
            estilos = propietario.estilo
    contexto = {
        "ctxtramitespropietario": listado_tramites_propietario(request),
        "ctxmis_tramites_para_financiar": tramites_para_financiar(request),
        'estilos': estilos,
    }
    return render(request, 'persona/propietario/propietario.html', contexto)

def elegir_financiacion_propietario(request,pk_tramite):
    estilos = ''
    usuario = request.user
    propietario = get_object_or_404(Propietario, pk=usuario.persona.propietario.pk)
    if propietario.estilo:
        estilos = propietario.estilo
    tramite = get_object_or_404(Tramite, pk=pk_tramite)        
    if request.method == "POST":
        if "Guardar" in request.POST: 
            pago = Pago()  
            contador = 31
            fms = "%A"              
            for name, value in request.POST.items():
                if name.startswith('cantidadCuotas'):                                        
                    pago.cantidadCuotas=value                                 
            total = tramite.monto_a_pagar/int(pago.cantidadCuotas)
            pago.save()
            for i in range(1, int(pago.cantidadCuotas)+1):
                cuota = Cuota(monto=total, numeroCuota=i, pago=pago)                
                cuota.fechaVencimiento=date.today() + timedelta(days=contador)
                dia=cuota.fechaVencimiento.strftime(fms)
                if dia=="Sunday":
                    cuota.fechaVencimiento==date.today() + timedelta(days=contador+1)
                else:
                    if dia=="Saturday":
                        cuota.fechaVencimiento = date.today() + timedelta(days=contador +2)
                contador=contador+31
                cuota.save()
                cuota.hacer("Cancelacion")
            messages.add_message(request, messages.SUCCESS, 'Financiacion registrada')
            tramite.pago = pago
            tramite.save()
        return redirect('propietario')                              
    return render(request, 'persona/propietario/elegir_financiacion_propietario.html',{'tramite': tramite, 'ctxpago':registrar_pago(request,tramite.id),'estilos':estilos})

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
    tramites = filter(lambda tramite: (tramite.propietario == propietario and tramite.pago is  None), tramites_propietario)
    return tramites

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
    estilos = ''
    usuario = request.user
    propietario = get_object_or_404(Propietario, pk=usuario.persona.propietario.pk)
    if propietario.estilo:
        estilos = propietario.estilo
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    contexto0 = {'tramite': tramite}
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    contexto1 = {'estados_del_tramite': estados_de_tramite}
    fechas_del_estado = [];
    for est in estados_de_tramite:
        fechas_del_estado.append(est.timestamp.strftime("%d/%m/%Y"));
    return render(request, 'persona/propietario/ver_historial_tramite.html', {"tramite": contexto0, "estadosp": contexto1, "fecha":fechas_del_estado,'estilos':estilos})

def documentos_de_estado(request, pk_estado):
    estilos = ''
    usuario = request.user
    propietario = get_object_or_404(Propietario, pk=usuario.persona.propietario.pk)
    if propietario.estilo:
        estilos = propietario.estilo
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = date.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(date.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)    
    contexto = {'documentos_de_fecha': documentos_fecha,'estilos':estilos}
    planillas = []
    inspecciones = []
    if (estado.tipo >2 and estado.tipo <5):
        for p in PlanillaDeVisado.objects.all():
            if (p.tramite.pk == estado.tramite.pk):
                planillas.append(p)
        filas = FilaDeVisado.objects.all()
        columnas = ColumnaDeVisado.objects.all()
        #elementos = planilla.elementos.all()
        contexto = {
            'documentos_de_fecha': documentos_fecha,
            'planillas':planillas,
            'filas': filas,
            'columnas': columnas,
            'estilos':estilos
            #'items': items,
            #'elementos': elementos,
        }    
    if (estado.tipo >5 and estado.tipo <8):                        
        for p in PlanillaDeInspeccion.objects.all():
            if (p.tramite.pk == estado.tramite.pk):
                inspecciones.append(p)              
        items = ItemInspeccion.objects.all()
        categorias = CategoriaInspeccion.objects.all()
        #detalles = inspeccion.detalles.all()
        contexto = {
            'inspecciones': inspecciones,
            'items': items,
            'categorias': categorias,
            'estilos':estilos
            #'detalles': detalles,
        }
    return render(request, 'persona/propietario/documentos_de_estado.html', contexto)

#-------------------------------------------------------------------------------------------------------------------
#profesional -------------------------------------------------------------------------------------------------------

from planilla_inspeccion.models import PlanillaDeInspeccion

@login_required(login_url="login")
@grupo_requerido('profesional')
def mostrar_profesional(request):
    usuario = request.user
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
        'ctxtramcorregidos':tramites_corregidos(request),
       # 'ctxvisadosprofesional':visados_del_profesional(request),
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
    if request.method == "POST":
        print ("faltan guardar documentos")
        documentos = Documento.objects.filter(tramite_id=pk_tramite)
        enviar_correccioness(request, pk_tramite)
    else:
        tramite = get_object_or_404(Tramite, pk=pk_tramite)
        planillas = PlanillaDeVisado.objects.filter(
            tramite_id=tramite.id)  # busca las planillas que tengan el id del tramite
        if (len(planillas) > 1):
            aux = planillas[0]
            for p in planillas:
                if (p.id > aux.id):  # obtiene el ultimo visado del tramite
                    plan = p
                else:
                    plan = aux
            planilla = get_object_or_404(PlanillaDeVisado,
                                         id=plan.id)  # PlanillaDeVisado.objects.filter(tramite_id=tramite.id)# busca las planillas que tengan el id del tramite
        else:
            planilla = get_object_or_404(PlanillaDeVisado,
                                         tramite_id=pk_tramite)  # PlanillaDeVisado.objects.filter(tramite_id=tramite.id)# busca las planillas que tengan el id del tramite
        filas = FilaDeVisado.objects.all()
        columnas = ColumnaDeVisado.objects.all()
        obs = planilla.observacion
        try:
            elementos = planilla.elementos.all()
            items = planilla.items.all()
            contexto = {
                'tramite': tramite,
                'planilla': planilla,
                'filas': filas,
                'columnas': columnas,
                'items': items,
                'elementos': elementos,
                'obs': obs,
            }
            return render(request, 'persona/profesional/ver_documentos_corregidos.html', contexto, {'tramite': tramite})
        except:
            contexto = {
                'tramite': tramite,
                'planilla': planilla,
                'filas': filas,
                'columnas': columnas,
                'obs': obs,
            }

    return redirect('profesional')


def enviar_correccioness(request, pk_tramite):
    usuario = request.user
    #archivos = request.GET['msg']
    observacion = "Este tramitzzzzzzzzzzzzzzze ya tiene los archivos corregidos cargados"
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    documento = Documento(file=request.FILES['documento'])
    tipo_documento = get_object_or_404(TipoDocumento, pk=3)
    documento.tipo_documento = tipo_documento
    documento.tramite = tramite
    print documento
    documento.save()
    tramite.hacer(tramite.CORREGIR, request.user, observacion)
    messages.add_message(request, messages.SUCCESS, 'Tramite con documentos corregidos y enviados')
    return redirect('profesional')

def enviar_correcciones(request, pk_tramite):
    usuario = request.user
    #archivos = request.GET['msg']
    observacion = "Este tramite ya tiene los archivos corregidos cargados"
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    documento = Documento(file=request.FILES['documento'])
    documento.tramite = tramite
    print documento
    documento.save()
    tramite.hacer(tramite.CORREGIR, request.user, observacion)
    messages.add_message(request, messages.SUCCESS, 'Tramite con documentos corregidos y enviados')
    return redirect('profesional')

def obtener_documentos_de_estado(request, pk_estado):
    estado = get_object_or_404(Estado, pk=pk_estado)
    documentos = estado.tramite.documentacion_para_estado(estado)
    print documentos
    return render(request, 'persona/profesional/documento_de_estado.html', documentos)
    #return render(request, 'persona/profesional/documento_de_estado.html', { 'documentos': documentos } )

def documento_de_estado(request, pk_estado):
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = date.strftime(fecha, '%d/%m/%Y %H:%M')
    # documentos = estado.tramite.documentacion_para_estado(estado)
    # documentos = estado.tramite.documentos.all()
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e: (date.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto = {'documentos_de_fecha': documentos_fecha}
    planillas = []
    inspecciones = []
    if (estado.tipo > 2 and estado.tipo < 5):
        for p in PlanillaDeVisado.objects.all():
            if (p.tramite.pk == estado.tramite.pk):
                planillas.append(p)
        #items = planilla.items.all()
        filas = FilaDeVisado.objects.all()
        columnas = ColumnaDeVisado.objects.all()
        #elementos = planilla.elementos.all()
        contexto = {
            'documentos_de_fecha': documentos_fecha,
            'planillas': planillas,
            'filas': filas,
            'columnas': columnas,
            #'items': items,
            #'elementos': elementos,
        }
    if (estado.tipo >5 and estado.tipo <8):                        
        for p in PlanillaDeInspeccion.objects.all():
            if (p.tramite.pk == estado.tramite.pk):
                inspecciones.append(p)              
        items = ItemInspeccion.objects.all()
        categorias = CategoriaInspeccion.objects.all()
        #detalles = inspeccion.detalles.all()
        contexto = {
            'inspecciones': inspecciones,
            'items': items,
            'categorias': categorias,
            #'detalles': detalles,                        
        }    
    return render(request, 'persona/profesional/documento_de_estado.html', contexto)

# def visados_profesional(request):
#     usuario = request.user
#     estados = Estado.objects.all()
#     tipo = 3 #visado
#     argumentos = [Visado]
#     tramites = Tramite.objects.en_estado(Visado)
#     visados_del_profesional = filter(lambda t: t.estado().usuario == usuario, tramites)
#     contexto = {"visados_del_profesional": visados_del_profesional}
#     return contexto

def planilla_visado_impresa(request, pk_tramite):
    planilla = get_object_or_404(PlanillaDeVisado,id=pk_tramite)
    tramite = get_object_or_404(Tramite, pk=planilla.tramite_id)
    filas = FilaDeVisado.objects.all()
    columnas = ColumnaDeVisado.objects.all()
    try:
        elementos = planilla.elementos.all()
        items = planilla.items.all()
        obs = planilla.observacion
        contexto={'tramite': tramite,
                  'planilla': planilla,
                  'filas': filas,
                  'columnas': columnas,
                  'elementos': elementos,
                  'items': items,
                  'obs': obs,
                  }
        return render(request, 'persona/profesional/planilla_visado_impresa.html',contexto)
    except:
         contexto = {
             'tramite': tramite,
             'planilla': planilla,
             'filas': filas,
             'columnas': columnas,
             'obs': obs,
         }
         return render(request, 'persona/profesional/planilla_visado_impresa.html', contexto)

def planilla_inspeccion_impresa(request, pk_tramite):
    planilla = get_object_or_404(PlanillaDeInspeccion, id=pk_tramite)
    tramite=get_object_or_404(Tramite, id=planilla.tramite_id)
    items = ItemInspeccion.objects.all()
    categorias = CategoriaInspeccion.objects.all()
    try:
        detalles = planilla.detalles.all()
        contexto = {
            'tramite': tramite,
            'planilla': planilla,
            'items': items,
            'categorias': categorias,
            'detalles': detalles,
        }
        return render(request, 'persona/profesional/planilla_inspeccion_impresa.html', contexto)

    except:
        contexto = {
            'tramite':tramite,
            'planilla': planilla,
            'items': items,
            'categorias': categorias,
        }
        return render(request, 'persona/profesional/planilla_inspeccion_impresa.html', contexto)


class ReporteTramitesProfesionalPdf(View):

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
        encabezados = ('PLANILLA DE VISADO')
        detalles = [(columna, fila, '*')
            # for columna in
            # ColumnaDeVisado.objects.all()
           for fila in
             FilaDeVisado.objects.all()
                    for columna in ColumnaDeVisado.objects.all()
                        for item in ItemDeVisado.objects.all()
                            if fila == item.fila_de_visado and columna == item.columna_de_visado]
            # for item in
            # ItemDeVisado.objects.all()]
        detalle_orden = Table([encabezados] + detalles, colWidths=[5 * cm, 7 * cm, 6 * cm, 6 * cm, 4 * cm, 4 * cm])
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
        "ctxpago": registrar_pago_tramite(request),
        "ctxlistprofesional": listado_profesionales(request)
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

def listado_profesionales(request):
    tramites = Tramite.objects.all()  # puse con inspeccion solo para fines de mostrar algo
    profesionales = Profesional.objects.all()
    personas = []
    for t in tramites:
        for p in profesionales:
            if t.profesional.id == p.id:
                if p not in personas:
                    personas.append(p)
    contexto = {
        "profesionales": personas}
    return contexto

def lista_profesionales_imprimible(request):
    personas = Profesional.objects.all()
    profesionales = filter(lambda persona: (persona is not None), personas)
    contexto = {'profesionales': personas}
    return render(request, 'persona/administrativo/lista_profesionales_imprimible.html', contexto)


#from datetime import date, time
class ReporteProfesionalExcel(TemplateView):
    def get(self, request, *args, **kwargs):
        profesionales = Profesional.objects.all()
        wb = Workbook()
        ws = wb.active
        ws['A1'] = 'REPORTE DE TRAMITES'
        ws.merge_cells('B1:G1')
        # ws['B2'] = 'FECHA_INICIO'
        ws['B2'] = 'NOMBRE'
        ws['C2'] = 'APELLIDO'
        ws['D2'] = 'DNI'
        ws['E2'] = 'TELEFONO'
        ws['F2'] = 'PROFESION'
        ws['G2'] = 'CATEGORIA'
        ws['H2'] = 'MATRICULA'
        ws['I2'] = 'DOMICILIO'
        ws['J2'] = 'MAIL'
        cont = 3
        for profesional in profesionales:
            # ws.cell(row=cont, column=2).value = convertidor_de_fechas(tramite.estado.timestamp)
            # ws.cell(row=cont, column=2).value = tramite.estado.timestamp
            ws.cell(row=cont, column=2).value = str(profesional.persona.nombre)
            ws.cell(row=cont, column=3).value = str(profesional.persona.apellido)
            ws.cell(row=cont, column=4).value = str(profesional.persona.dni)
            ws.cell(row=cont, column=5).value = str(profesional.persona.telefono)
            ws.cell(row=cont, column=6).value = str(profesional.profesion)
            ws.cell(row=cont, column=7).value = profesional.categoria
            ws.cell(row=cont, column=8).value = profesional.matricula
            ws.cell(row=cont, column=9).value = str(profesional.persona.domicilio)
            ws.cell(row=cont, column=10).value = str(profesional.persona.mail)
            cont = cont + 1
        nombre_archivo = "ReportePersonasExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response

class ReporteProfesionalesPdf(View):

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
        fecha = timezone.now().strftime('%Y-%m-%d')
        usuario = 'Usuario: ' + request.user.username + ' -  Fecha:' + str(fecha)
        Story.append(Paragraph(usuario, styles["Usuario"]))
        Story.append(Spacer(0, cm * 0.1))
        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=490, height=3)
        im0.hAlign = 'CENTER'
        Story.append(im0)
        titulo = 'SISTEMA OBRAS PARTICULARES'
        Story.append(Paragraph(titulo, styles["Titulo"]))
        Story.append(Spacer(0, cm * 0.20))
        subtitulo = 'Listado de Profesionales activos'
        Story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        Story.append(Spacer(0, cm * 0.15))
        Story.append(im0)
        Story.append(Spacer(0, cm * 0.5))
        encabezados = ('Nombre', 'Apellido', 'Telefono','Profesion',
                       'Matricula','Domicilio','correo')
        detalles = [(profesional.persona.nombre, profesional.persona.apellido,
                     profesional.persona.dni,
                     profesional.persona.telefono, profesional.profesion,
                     profesional.matricula,
                     profesional.persona.domicilio,
                     profesional.persona.mail) for
                    profesional in
                    Profesional.objects.all()
                    #
                    # persona.nombre, persona.apellido, persona.dni, persona.cuil,
                    # persona.telefono, persona.domicilio, persona.mail) for
                    # persona in
                    # Persona.objects.all()

                    ]
        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm,
                                                                   4 * cm, 6 * cm])
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

#reporte tramites iniciados

class ReporteTramitesIniciadosExcel(TemplateView):
    def get(self, request, *args, **kwargs):
        tramites = Tramite.objects.en_estado(Iniciado)
        wb = Workbook()
        ws = wb.active
        ws['B1'] = 'REPORTE DE TRAMITES INICIADOS'
        ws.merge_cells('B1:F1')
            # ws['B2'] = 'FECHA_INICIO'
        ws['B2'] = 'NRO'
        ws['C2'] = 'PROPIETARIO'
        ws['D2'] = 'PROFESIONAL'
        ws['E2'] = 'MEDIDAS'
        ws['F2'] = 'TIPO'
        #ws['G2'] = 'ESTADO'
        cont = 3
        for tramite in tramites:
                # ws.cell(row=cont, column=2).value = convertidor_de_fechas(tramite.estado.timestamp)
                # ws.cell(row=cont, column=2).value = tramite.estado.timestamp
            ws.cell(row=cont, column=2).value = str(tramite.id)
            ws.cell(row=cont, column=3).value = str(tramite.propietario)
            ws.cell(row=cont, column=4).value = str(tramite.profesional)
            ws.cell(row=cont, column=5).value = str(tramite.medidas)
            ws.cell(row=cont, column=6).value = str(tramite.tipo_obra)
            #ws.cell(row=cont, column=7).value = str(tramite.estado)
            cont = cont + 1
        nombre_archivo = "ReportePersonasExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response

class ReporteTramitesIniciadosPdf(View):
    def get(self, request, *args, **kwargs):
        filename = "Informe de tramites iniciados " + datetime.datetime.now().strftime("%d/%m/%Y") + " .pdf"
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
        usuario = 'Usuario: ' + request.user.username + ' - Fecha: ' + datetime.datetime.now().strftime("%Y/%m/%d")
        Story.append(Paragraph(usuario, styles["Usuario"]))
        Story.append(Spacer(0, cm * 0.15))
        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=490, height=3)
        im0.hAlign = 'CENTER'
        Story.append(im0)
        titulo = 'SISTEMA OBRAS PARTICULARES'
        Story.append(Paragraph(titulo, styles["Titulo"]))
        Story.append(Spacer(0, cm * 0.20))
        subtitulo = 'Reporte De Tramites Iniciados'
        Story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        Story.append(Spacer(0, cm * 0.15))
        Story.append(im0)
        Story.append(Spacer(0, cm * 0.5))
        encabezados = ('NRO', 'PROPIETARIO', 'PROFESIONAL', 'MEDIDAS', 'TIPO')
        detalles = [(tramite.id, tramite.propietario, tramite.profesional, tramite.medidas,
                        tramite.tipo_obra)
                    for
                    tramite in
                    Tramite.objects.en_estado(Iniciado)]
        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 3 * cm, 3 * cm, 3 * cm])
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

#reporte tramites corregidos

class ReporteTramitesCorregidosExcel(TemplateView):
    def get(self, request, *args, **kwargs):
        tramites = Tramite.objects.en_estado(Corregido)
        wb = Workbook()
        ws = wb.active
        ws['B1'] = 'REPORTE DE TRAMITES CORREGIDOS'
        ws.merge_cells('B1:F1')
            # ws['B2'] = 'FECHA_INICIO'
        ws['B2'] = 'NRO'
        ws['C2'] = 'PROPIETARIO'
        ws['D2'] = 'PROFESIONAL'
        ws['E2'] = 'MEDIDAS'
        ws['F2'] = 'TIPO'
        #ws['G2'] = 'ESTADO'
        cont = 3
        for tramite in tramites:
                # ws.cell(row=cont, column=2).value = convertidor_de_fechas(tramite.estado.timestamp)
                # ws.cell(row=cont, column=2).value = tramite.estado.timestamp
            ws.cell(row=cont, column=2).value = str(tramite.id)
            ws.cell(row=cont, column=3).value = str(tramite.propietario)
            ws.cell(row=cont, column=4).value = str(tramite.profesional)
            ws.cell(row=cont, column=5).value = str(tramite.medidas)
            ws.cell(row=cont, column=6).value = str(tramite.tipo_obra)
            #ws.cell(row=cont, column=7).value = str(tramite.estado)
            cont = cont + 1
        nombre_archivo = "ReportePersonasExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response

class ReporteTramitesCorregidosPdf(View):
    def get(self, request, *args, **kwargs):
        filename = "Informe de tramites corregidos " + datetime.datetime.now().strftime("%d/%m/%Y") + " .pdf"
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
        usuario = 'Usuario: ' + request.user.username + ' - Fecha: ' + datetime.datetime.now().strftime("%Y/%m/%d")
        Story.append(Paragraph(usuario, styles["Usuario"]))
        Story.append(Spacer(0, cm * 0.15))
        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=490, height=3)
        im0.hAlign = 'CENTER'
        Story.append(im0)
        titulo = 'SISTEMA OBRAS PARTICULARES'
        Story.append(Paragraph(titulo, styles["Titulo"]))
        Story.append(Spacer(0, cm * 0.20))
        subtitulo = 'Reporte De Tramites Corregidos'
        Story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        Story.append(Spacer(0, cm * 0.15))
        Story.append(im0)
        Story.append(Spacer(0, cm * 0.5))
        encabezados = ('NRO', 'PROPIETARIO', 'PROFESIONAL', 'MEDIDAS', 'TIPO')
        detalles = [(tramite.id, tramite.propietario, tramite.profesional, tramite.medidas,
                        tramite.tipo_obra)
                    for
                    tramite in
                    Tramite.objects.en_estado(Visado)]
        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 3 * cm, 3 * cm, 3 * cm])
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

    #reporte listado profesionales activos

class ReporteProfesionalesActivosExcel(TemplateView):
    def get(self, request, *args, **kwargs):
        tramites = Tramite.objects.all()  # puse con inspeccion solo para fines de mostrar algo
        personas = Profesional.objects.all()
        profesionales = []
        for t in tramites:
            for p in personas:
                if t.profesional.id == p.id:
                    if p not in profesionales:
                        profesionales.append(p)
        wb = Workbook()
        ws = wb.active
        ws['A1'] = 'REPORTE DE PROFESIONALES ACTIVOS'
        ws.merge_cells('B1:G1')
        # ws['B2'] = 'FECHA_INICIO'
        ws['B2'] = 'NOMBRE'
        ws['C2'] = 'APELLIDO'
        ws['D2'] = 'TELEFONO'
        ws['E2'] = 'PROFESION'
        ws['F2'] = 'MATRICULA'
        ws['G2'] = 'DOMICILIO'
        ws['H2'] = 'MAIL'
        cont = 3
        for profesional in profesionales:
            # ws.cell(row=cont, column=2).value = convertidor_de_fechas(tramite.estado.timestamp)
            # ws.cell(row=cont, column=2).value = tramite.estado.timestamp
            ws.cell(row=cont, column=2).value = str(profesional.persona.nombre)
            ws.cell(row=cont, column=3).value = str(profesional.persona.apellido)
            ws.cell(row=cont, column=4).value = str(profesional.persona.telefono)
            ws.cell(row=cont, column=5).value = str(profesional.profesion)
            ws.cell(row=cont, column=6).value = profesional.matricula
            ws.cell(row=cont, column=7).value = profesional.persona.domicilio
            ws.cell(row=cont, column=8).value = str(profesional.persona.mail)
            cont = cont + 1
        nombre_archivo = "ReportePersonasExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response

class ReporteProfesionalesActivosPdf(View):

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
        fecha = timezone.now().strftime('%Y-%m-%d')
        usuario = 'Usuario: ' + request.user.username + ' - Fecha: ' + datetime.datetime.now().strftime("%Y/%m/%d")
        Story.append(Paragraph(usuario, styles["Usuario"]))
        Story.append(Spacer(0, cm * 0.1))
        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=490, height=3)
        im0.hAlign = 'CENTER'
        Story.append(im0)
        titulo = 'SISTEMA OBRAS PARTICULARES'
        Story.append(Paragraph(titulo, styles["Titulo"]))
        Story.append(Spacer(0, cm * 0.20))
        subtitulo = 'Listado de Profesionales activos'
        Story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        Story.append(Spacer(0, cm * 0.15))
        Story.append(im0)
        Story.append(Spacer(0, cm * 0.5))
        encabezados = ('NOMBRE', 'APELLIDO', 'TELEFONO','PROFESION',
                       'MATRICULA','DOMICILIO','MAIL')
        tramites = Tramite.objects.all()  # puse con inspeccion solo para fines de mostrar algo
        personas = Profesional.objects.all()
        profesionales = []
        for t in tramites:
            for p in personas:
                if t.profesional.id == p.id:
                    if p not in profesionales:
                        profesionales.append(p)
        detalles = [(profesional.persona.nombre, profesional.persona.apellido,
                     profesional.persona.telefono,
                     profesional.profesion,
                     profesional.matricula,
                     profesional.persona.domicilio,
                     profesional.persona.mail) for
                    profesional in
                    profesionales
                    ]
        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm,
                                                                   4 * cm])
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

#reporte tramites con final de obra solicitado

class ReporteSolicitudFinalObraExcel(TemplateView):
    def get(self, request, *args, **kwargs):
        tramites = Tramite.objects.en_estado(FinalObraSolicitado)
        wb = Workbook()
        ws = wb.active
        ws['A1'] = 'REPORTE DE TRAMITES FINAL OBRA SOLICITADO'
        ws.merge_cells('B1:G1')
        # ws['B2'] = 'FECHA_INICIO'
        ws['B2'] = 'NUMERO'
        ws['C2'] = 'MEDIDAS'
        ws['D2'] = 'TIPO'
        ws['E2'] = 'ESTADO'
        ws['F2'] = 'PROFESIONAL'
        ws['G2'] = 'PROPIETARIO'
        cont = 3
        for tramite in tramites:
            # ws.cell(row=cont, column=2).value = convertidor_de_fechas(tramite.estado.timestamp)
            # ws.cell(row=cont, column=2).value = tramite.estado.timestamp
            ws.cell(row=cont, column=2).value = tramite.id
            ws.cell(row=cont, column=3).value = tramite.medidas
            ws.cell(row=cont, column=4).value = str(tramite.tipo_obra)
            ws.cell(row=cont, column=5).value = str(tramite.estado())
            ws.cell(row=cont, column=6).value = str(tramite.profesional)
            ws.cell(row=cont, column=7).value = str(tramite.propietario)
            cont = cont + 1
        nombre_archivo = "ReportePersonasExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response

class ReporteSolicitudFinalObraPdf(View):

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
        fecha = timezone.now().strftime('%Y-%m-%d')
        usuario = 'Usuario: ' + request.user.username + ' - Fecha: ' + datetime.datetime.now().strftime("%Y/%m/%d")
        Story.append(Paragraph(usuario, styles["Usuario"]))
        Story.append(Spacer(0, cm * 0.1))
        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=490, height=3)
        im0.hAlign = 'CENTER'
        Story.append(im0)
        titulo = 'SISTEMA OBRAS PARTICULARES'
        Story.append(Paragraph(titulo, styles["Titulo"]))
        Story.append(Spacer(0, cm * 0.20))
        subtitulo = 'Listado de tramites con solicitud final de obra'
        Story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        Story.append(Spacer(0, cm * 0.15))
        Story.append(im0)
        Story.append(Spacer(0, cm * 0.5))
        encabezados = ('NUMERO', 'MEDIDAS', 'TIPO','ESTADO',
                       'PROFESIONAL','PROPIETARIO')
        detalles = [(tramite.id, tramite.medidas, tramite.tipo_obra, tramite.estado(),
                     tramite.profesional, tramite.propietario)
                    for
                    tramite in
                    Tramite.objects.en_estado(FinalObraSolicitado)]
        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 2 * cm, 4 * cm, 3 * cm, 3 * cm,
                                                                   3 * cm])
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
#visador -----------------------------------------------------------------------------------------------------------
from planilla_visado import forms as pforms
from planilla_visado import models as pmodels

@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visador(request):
    contexto = {
        "ctxtramaceptado": tramites_aceptados(request),
        "ctxtramvisados": tramites_visados(request),
        "ctxmis_visados": mis_visados(request),
        "ctxtramvisadosnoaprobados": visados_noaproabados(request)
    }
    return render(request, 'persona/visador/visador.html', contexto)

def mis_visados(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 3 #visado    
    tramites = Tramite.objects.en_estado(Visado)
    tramites_del_visador = filter(lambda t: t.estado().usuario == usuario, tramites)
    contexto = {"tramites_del_visador": tramites_del_visador}    
    return tramites_del_visador

def tramites_aceptados(request):
    aceptados = Tramite.objects.en_estado(Aceptado)
    contexto = {'tramites': aceptados}
    return contexto

def tramites_visados(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 3 #visado    
    argumentos = [Visado]
    tramites = Tramite.objects.en_estado(Visado)
    tramites_del_visador = filter(lambda t: t.estado().usuario == usuario, tramites)
    contexto = {"tramites_del_visador": tramites_del_visador}  
    return contexto

def visados_noaproabados(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 4
    argumentos = [Corregido]
    tramites = Tramite.objects.en_estado(Corregido)
    tramites_del_visador = filter(lambda t: t.estado().usuario == usuario, tramites)
    contexto = {"tramites_del_visador": tramites_del_visador}
    return contexto

def ver_documentos_para_visado(request, pk_tramite):
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.VISAR)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    return render(request, 'persona/visador/ver_documentos_tramite.html', {'tramite': tramite, 'documentos_requeridos': tipos_de_documentos_requeridos})

def ver_documentos_visados(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    planilla = get_object_or_404(PlanillaDeVisado, pk=tramite.id)
    items = planilla.items.all()
    filas = FilaDeVisado.objects.all()
    columnas = ColumnaDeVisado.objects.all()
    elementos = planilla.elementos.all()
    contexto = {
        'planilla':planilla,
        'filas': filas,
        'columnas': columnas,
        'items': items,
        'elementos': elementos,
    }
    return render(request, 'persona/visador/ver_documentos_visados.html', {'tramite': tramite, 'planilla':planilla, 'filas':filas, 'columnas':columnas, 'elementos':elementos, 'items':items})

from planilla_visado.models import FilaDeVisado, ColumnaDeVisado

def ver_planilla_visado(request):    
    items = ItemDeVisado.objects.all()    
    filas = FilaDeVisado.objects.all()
    columnas = ColumnaDeVisado.objects.all()
    elementos = Elemento_Balance_Superficie.objects.all()        
    return render(request, 'persona/visador/ver_planilla_visado.html', {'tramite': tramite, 'items':items, 'filas':filas, 'columnas':columnas, 'elementos':elementos})    


def generar_planilla_impresa(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    planillas=PlanillaDeVisado.objects.filter(tramite_id=tramite.id)# busca las planillas que tengan el id del tramite

    if (len(planillas) > 1):
        aux = planillas[0]
        for p in planillas:
            if (p.id > aux.id):  #obtiene el ultimo visado del tramite
                plan = p
            else:
                plan= aux
        planilla = get_object_or_404(PlanillaDeVisado,id=plan.id)  # PlanillaDeVisado.objects.filter(tramite_id=tramite.id)# busca las planillas que tengan el id del tramite
        obs = planilla.observacion
    else:
        planilla = get_object_or_404(PlanillaDeVisado,tramite_id=pk_tramite)  # PlanillaDeVisado.objects.filter(tramite_id=tramite.id)# busca las planillas que tengan el id del tramite
        filas = FilaDeVisado.objects.all()
        columnas = ColumnaDeVisado.objects.all()
        obs = planilla.observacion
    try:
        filas = FilaDeVisado.objects.all()
        columnas = ColumnaDeVisado.objects.all()
        elementos = planilla.elementos.all()
        items = planilla.items.all()
        obs = planilla.observacion
        contexto = {
            'tramite': tramite,
            'planilla': planilla,
            'filas': filas,
            'columnas': columnas,
            'items': items,
            'elementos': elementos,
            'obs': obs,
        }
        return render(request, 'persona/visador/generar_planilla_impresa.html', contexto)
    except:
        contexto = {
            'tramite': tramite,
            'planilla': planilla,
            'filas': filas,
            'columnas': columnas,
            'obs': obs,
        }
        return render(request, 'persona/visador/generar_planilla_impresa.html', contexto)


def mostrar_visados_noaprobados(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    planillas=PlanillaDeVisado.objects.filter(tramite_id=tramite.id)# busca las planillas que tengan el id del tramite
    if (len(planillas) > 1):
        aux = planillas[0]
        for p in planillas:
            if (p.id > aux.id):  #obtiene el ultimo visado del tramite
                plan = p
            else:
                plan= aux
        planilla = get_object_or_404(PlanillaDeVisado,id=plan.id)  # PlanillaDeVisado.objects.filter(tramite_id=tramite.id)# busca las planillas que tengan el id del tramite
        obs = planilla.observacion
    else:
        planilla = get_object_or_404(PlanillaDeVisado,tramite_id=pk_tramite)  # PlanillaDeVisado.objects.filter(tramite_id=tramite.id)# busca las planillas que tengan el id del tramite
    filas = FilaDeVisado.objects.all()
    columnas = ColumnaDeVisado.objects.all()
    obs = planilla.observacion
    try:
        elementos = planilla.elementos.all()
        items = planilla.items.all()
        obs = planilla.observacion
        contexto = {
            'tramite': tramite,
            'planilla': planilla,
            'filas': filas,
            'columnas': columnas,
            'items': items,
            'elementos': elementos,
            'obs': obs,
        }
        return render(request, 'persona/visador/mostrar_visados_noaprobados.html', contexto)
    except:
        contexto = {
            'tramite': tramite,
            'planilla': planilla,
            'filas': filas,
            'columnas': columnas,
            'obs': obs,
        }
        return render(request, 'persona/visador/mostrar_visador_noaprobados.html', contexto)


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
        elementos = Elemento_Balance_Superficie.objects.all()
        return render(request, 'persona/visador/planilla_visado.html', {'tramite': tramite, 'items':items, 'filas':filas, 'columnas':columnas, 'elementos':elementos})
    return redirect('visador')


from planilla_visado.models import PlanillaDeVisado

def aprobar_visado(request, pk_tramite, monto):
    list_items = []
    list_elementos = []
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    planilla = PlanillaDeVisado()
    planilla.tramite = tramite
    planilla.save()
    for name, value in request.POST.items():
        if name.startswith('item'):
            ipk= name.split('-')[1]
            list_items.append(ipk)            
    items = ItemDeVisado.objects.all()        
    for item in items:        
        for i in list_items:            
            if (item.id == int(i)):                                
                planilla.agregar_item(item)                                                                                
    planilla.save()
    for name, value in request.POST.items():
        print request.POST.items()
        if name.startswith('elemento'):
            ipk= name.split('-')[1]
            list_elementos.append(ipk)
    elementos = Elemento_Balance_Superficie.objects.all()        
    for elemento in elementos:        
        for i in list_elementos:
            if (elemento.id == int(i)):                                                
                planilla.agregar_elemento(elemento)
                planilla.save()
    planilla.save()                
    usuario = request.user    
    tramite.hacer(tramite.VISAR, usuario)
    tramite.monto_a_pagar= monto        
    tramite.save()    
    messages.add_message(request, messages.SUCCESS, 'Tramite visado aprobado')        
    return redirect('visador')

def no_aprobar_visado(request, pk_tramite, observacion):
    list_items = []
    list_elementos = []
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    planilla = PlanillaDeVisado()
    planilla.tramite = tramite
    planilla.observacion = observacion
    planilla.save()
    for name, value in request.POST.items():
        if name.startswith('item'):
            ipk= name.split('-')[1]
            list_items.append(ipk)
    items = ItemDeVisado.objects.all()        
    for item in items:        
        for i in list_items:            
            if (item.id == int(i)):                                
                planilla.agregar_item(item)
    planilla.save()
    for name, value in request.POST.items():
        if name.startswith('elemento'):
            ipk= name.split('-')[1]
            list_elementos.append(ipk)
    elementos = Elemento_Balance_Superficie.objects.all()        
    for elemento in elementos:        
        for i in list_elementos:
            if (elemento.id == int(i)):                                                
                planilla.agregar_elemento(elemento)
                planilla.save()
    planilla.save()
    usuario = request.user            
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    planilla.save()
    tramite.hacer(tramite.CORREGIR, usuario, observacion)
    messages.add_message(request, messages.SUCCESS, 'Tramite con visado no aprobado')
    return redirect('visador')

def tramites_visados_imprimible(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 3  # visado
    argumentos = [Visado]
    tramites = Tramite.objects.en_estado(Visado)
    tramites_del_visador = filter(lambda t: t.estado().usuario == usuario, tramites)
    contexto = {"tramites_del_visador": tramites_del_visador}
    return render(request, 'persona/visador/tramites_visados_imprimible.html', contexto)


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

        filename = "Informe de tramites Aceptados " + datetime.datetime.now().strftime("%d/%m/%Y") + ".pdf"
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
        usuario = 'Usuario: ' + request.user.username + ' - Fecha: ' + datetime.datetime.now().strftime("%Y/%m/%d")
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

  #  reporte_tramites_visados_pdf

class ReporteTramitesVisadosExcel(TemplateView):
    def get(self, request, *args, **kwargs):
        tramites = Tramite.objects.en_estado(Visado)
        wb = Workbook()
        ws = wb.active
        ws['B1'] = 'REPORTE DE TRAMITES VISADOS'
        ws.merge_cells('B1:F1')
            # ws['B2'] = 'FECHA_INICIO'
        ws['B2'] = 'NRO'
        ws['C2'] = 'MEDIDAS'
        ws['D2'] = 'TIPO'
        ws['E2'] = 'PROFESIONAL'
        ws['F2'] = 'PROPIETARIO'
        ws['G2'] = 'DOMICILIO'
        cont = 3
        for tramite in tramites:
                # ws.cell(row=cont, column=2).value = convertidor_de_fechas(tramite.estado.timestamp)
                # ws.cell(row=cont, column=2).value = tramite.estado.timestamp
            ws.cell(row=cont, column=2).value = str(tramite.id)
            ws.cell(row=cont, column=3).value = str(tramite.medidas)
            ws.cell(row=cont, column=4).value = str(tramite.tipo_obra)
            ws.cell(row=cont, column=5).value = str(tramite.profesional)
            ws.cell(row=cont, column=6).value = str(tramite.propietario)
            ws.cell(row=cont, column=7).value = str(tramite.domicilio)
            cont = cont + 1
        nombre_archivo = "ReportePersonasExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response

class ReporteTramitesVisadosPdf(View):
    def get(self, request, *args, **kwargs):
        filename = "Informe de tramites visados " + datetime.datetime.now().strftime("%d/%m/%Y") + " .pdf"
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
        usuario = 'Usuario: ' + request.user.username + ' - Fecha: ' + datetime.datetime.now().strftime("%Y/%m/%d")
        Story.append(Paragraph(usuario, styles["Usuario"]))
        Story.append(Spacer(0, cm * 0.15))
        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=490, height=3)
        im0.hAlign = 'CENTER'
        Story.append(im0)
        titulo = 'SISTEMA OBRAS PARTICULARES'
        Story.append(Paragraph(titulo, styles["Titulo"]))
        Story.append(Spacer(0, cm * 0.20))
        subtitulo = 'Reporte De Tramites Visados'
        Story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        Story.append(Spacer(0, cm * 0.15))
        Story.append(im0)
        Story.append(Spacer(0, cm * 0.5))
        encabezados = ('NRO', 'MEDIDAS', 'TIPO','PROFESIONAL', 'PROPIETARIO', 'DOMICILIO')
        detalles = [(tramite.id, tramite.medidas, tramite.tipo_obra, tramite.profesional, tramite.propietario, tramite.domicilio)
                    for
                    tramite in
                    Tramite.objects.en_estado(Visado)]
        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 2 * cm, 3 * cm, 3 * cm, 4 * cm])
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
from django_user_agents.utils import get_user_agent
from planilla_inspeccion.models import *

@login_required(login_url="login")
@grupo_requerido('inspector')
def mostrar_inspector(request):    
    if (request.user_agent.is_mobile): # returns True
        return redirect('movil_')
    contexto = {
        "ctxtramitesvisadosyconinspeccion": tramites_visados_y_con_inspeccion(request),
        "ctxtramitesinspeccionados": tramites_inspeccionados_por_inspector(request),
        "ctxtramitesagendados": tramites_agendados_por_inspector(request),
        "ctxtramis_inspecciones": mis_inspecciones(request),
        "ctxlistado_inspector": listado_inspector_movil(request),
    }
    return render(request, 'persona/inspector/inspector.html', contexto)

def mis_inspecciones(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 6 #visado    
    argumentos = [ConInspeccion]
    tramites = Tramite.objects.en_estado(ConInspeccion)
    return tramites

def tramites_visados_y_con_inspeccion(request):
    argumentos = [Visado, ConInspeccion]
    tramites = Tramite.objects.en_estado(argumentos)
    return tramites

def tramites_inspeccionados_por_inspector(request):   
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 7 #7
    tramites = Tramite.objects.en_estado(ConInspeccion)
    tramites_del_inspector = filter(lambda t: t.estado().usuario == usuario, tramites)
    estados_inspeccionados = filter(lambda estado: (estado.usuario is not None and estado.usuario == usuario and estado.tipo == tipo), estados)    
    contexto = {"tramites_del_inspector": tramites_del_inspector}
    return estados_inspeccionados

def tramites_agendados_por_inspector(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 5
    #estados_agendados = filter(lambda estado: (estado.usuario is not None and estado.usuario == usuario and estado.tipo == tipo), estados)
    argumentos = [Visado, ConInspeccion]
    tramites = Tramite.objects.en_estado(Agendado)
    tramites_del_inspector = filter(lambda t: t.estado().usuario == usuario, tramites)
    contexto = {"tramites_del_inspector": tramites_del_inspector}
    return tramites_del_inspector

def agendar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)    
    usuario = request.user    
    fecha = convertidor_de_fechas(request.GET["msg"])        
    tramite.hacer(Tramite.AGENDAR, request.user, fecha) #tramite, fecha_inspeccion, inspector=None
    messages.add_message(request, messages.SUCCESS, "Inspeccion agendada")
    return redirect('inspector')

def cargar_inspeccion(request, pk_tramite):        
    if request.method == "POST":
        if "Agendar" in request.POST: 
            tramite = get_object_or_404(Tramite, pk=pk_tramite)
            id_tramite = int(pk_tramite)
            planilla = PlanillaDeInspeccion()
            planilla.tramite = tramite
            planilla.save()
            list_detalles=[] 
            for name,value in request.POST.items():        
                if name.startswith('detalle'):
                    ipk=name.split('-')[1]
                    detalle = DetalleDeItemInspeccion.objects.get(id=ipk)
                    list_detalles.append(detalle)
            for detalle in list_detalles:
                planilla.agregar_detalle(detalle)
            planilla.save()
            usuario = request.user        
            tramite.hacer(tramite.INSPECCIONAR, usuario)
            tramite.save()
            messages.add_message(request,messages.SUCCESS,"Inspeccion cargada")        
        else:        
            messages.add_message(request,messages.ERROR,"No se cargo la inspeccion")
    return redirect('inspector')

def rechazar_inspeccion(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.INSPECCIONAR, request.user)
    tramite.hacer(Tramite.CORREGIR, request.user, request.POST["observaciones"])  #request.POST["observaciones"]
    messages.add_message(request, messages.ERROR, 'Inspeccion rechazada')
    return redirect('inspector')

# def aceptar_inspeccion(request, pk_tramite):
#     list_detalles = []
#     tramite = get_object_or_404(Tramite, pk=pk_tramite)
#     planilla = PlanillaDeInspeccion()
#     planilla.tramite = tramite
#     planilla.save()
#     for name, value in request.POST.detalles():
#         if name.startswith('detalle'):
#             ipk= name.split('-')[1]
#             list_detalles.append(ipk)
#     detalles = DetalleDeItemInspeccion.objects.all()
#     for detalle in detalles:
#         for i in list_detalles:
#             if (detalle.id == int(i)):
#                 planilla.agregar_detalle(detalle)
#     planilla.save()
#     usuario = request.user
#     tramite.hacer(Tramite.INSPECCIONAR, request.user)
#     tramite.save()
#     messages.add_message(request, messages.SUCCESS, 'Tramite inspeccionado')
#     return redirect('inspector')
def aceptar_inspeccion(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.INSPECCIONAR, request.user)
    messages.add_message(request, messages.SUCCESS, 'Inspeccion aprobada')
    return redirect('inspector')

# def ver_documentos_tramite_inspector(request, pk_tramite):
#     tramite = get_object_or_404(Tramite, pk=pk_tramite)
#     contexto0 = {'tramite': tramite}
#     pk = int(pk_tramite)
#     estados = Estado.objects.all()
#     estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
#     contexto1 = {'estados_del_tramite': estados_de_tramite}
#     fechas_del_estado = [];
#     for est in estados_de_tramite:
#         fechas_del_estado.append(est.timestamp.strftime("%d/%m/%Y"));
#     return render(request, 'persona/inspector/documentos_tramite_inspector.html', {"tramite": contexto0, "estadosp": contexto1, "fechas":fechas_del_estado})

def ver_documentos_tramite_inspector(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    planilla = get_object_or_404(PlanillaDeInspeccion, pk=pk_tramite)
    items = ItemInspeccion.objects.all()
    categorias = CategoriaInspeccion.objects.all()
    detalles = planilla.detalles.all()
    contexto = {'planilla': planilla,'items':items,'categorias':categorias,'detalles':detalles}
    return render(request, 'persona/inspector/documentos_del_estado_inspector.html', {"tramite": tramite,
                                                                                   'planilla': planilla, 'items': items,
                                                                                   'categorias': categorias,
                                                                                   'detalles': detalles})

def documentos_inspector_estado(request, pk_estado):
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = date.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(date.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    if (estado.tipo >5):
        planilla = None
        for p in PlanillaDeInspeccion.objects.all():
            if (p.tramite.pk == estado.tramite.pk):
                planilla = p        
        items = ItemInspeccion.objects.all()
        categorias = CategoriaInspeccion.objects.all()
        detalles = planilla.detalles.all()
        contexto = {'documentos_de_fecha': documentos_fecha, 'items': items, 'categorias': categorias, 'detalles': detalles, 'planilla':planilla}
    else:
        contexto = {'documentos_de_fecha': documentos_fecha}
    return render(request,'persona/inspector/documentos_del_estado_inspector.html', contexto)

def generar_planilla_impresa_inspeccion(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    planillas = PlanillaDeInspeccion.objects.filter(tramite_id=tramite.id) #busca las planillas que tengan el id del tramite
    if (len(planillas)>1):
        aux=planillas[0]
        for p in planillas:
            if (p.id>aux.id):
                plan=p
            else:
                plan=aux
        planilla=get_object_or_404(PlanillaDeInspeccion, id=plan.id)
    else:
        planilla=get_object_or_404(PlanillaDeInspeccion, tramite_id=tramite.id)
    items = ItemInspeccion.objects.all()
    categorias = CategoriaInspeccion.objects.all()
    try:
        detalles = planilla.detalles.all()
        contexto = {
            'tramite': tramite,
            'planilla': planilla,
            'items': items,
            'categorias': categorias,
            'detalles': detalles,
        }
        return render(request, 'persona/inspector/generar_planilla_impresa_inspeccion.html', contexto)

    except:
        contexto = {
            'tramite':tramite,
            'planilla': planilla,
            'items': items,
            'categorias': categorias,
        }
        return render(request, 'persona/inspector/generar_planilla_impresa_inspeccion.html', contexto)

#REPORTES INSPECTOR //DE TODOS LOS LISTADOS HICE REPORTES


class ReporteTramitesAgendarInspeccionExcel(TemplateView):
    def get(self, request, *args, **kwargs):
        tramites = Tramite.objects.all()
        tramites_aagendar = filter(lambda t: t.estado == 3 or t.estado == 6, tramites)
        wb = Workbook()
        ws = wb.active
        ws['B1'] = 'REPORTE DE TRAMITES VISADOS'
        ws.merge_cells('B1:F1')
            # ws['B2'] = 'FECHA_INICIO'
        ws['B2'] = 'NRO'
        ws['C2'] = 'MEDIDAS'
        ws['D2'] = 'TIPO'
        ws['E2'] = 'PROFESIONAL'
        ws['F2'] = 'PROPIETARIO'
        ws['G2'] = 'DOMICILIO'
        cont = 3
        for tramite in tramites:
                # ws.cell(row=cont, column=2).value = convertidor_de_fechas(tramite.estado.timestamp)
                # ws.cell(row=cont, column=2).value = tramite.estado.timestamp
            ws.cell(row=cont, column=2).value = str(tramite.id)
            ws.cell(row=cont, column=3).value = str(tramite.medidas)
            ws.cell(row=cont, column=4).value = str(tramite.tipo_obra)
            ws.cell(row=cont, column=5).value = str(tramite.profesional)
            ws.cell(row=cont, column=6).value = str(tramite.propietario)
            ws.cell(row=cont, column=7).value = str(tramite.domicilio)
            cont = cont + 1
        nombre_archivo = "ReportePersonasExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response

class ReporteTramitesAgendarInspeccionPdf(View):
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
        usuario = 'Usuario: ' + request.user.username + ' - Fecha: ' + datetime.datetime.now().strftime("%Y/%m/%d")
        Story.append(Paragraph(usuario, styles["Usuario"]))
        Story.append(Spacer(0, cm * 0.15))
        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=490, height=3)
        im0.hAlign = 'CENTER'
        Story.append(im0)
        titulo = 'SISTEMA OBRAS PARTICULARES'
        Story.append(Paragraph(titulo, styles["Titulo"]))
        Story.append(Spacer(0, cm * 0.20))
        subtitulo = 'Reporte De Tramites Visados'
        Story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        Story.append(Spacer(0, cm * 0.15))
        Story.append(im0)
        Story.append(Spacer(0, cm * 0.5))
        encabezados = ('NRO', 'MEDIDAS', 'TIPO','PROFESIONAL', 'PROPIETARIO', 'DOMICILIO')
        detalles = [(tramite.id, tramite.medidas, tramite.tipo_obra, tramite.profesional, tramite.propietario, tramite.domicilio)
                    for
                    tramite in
                    Tramite.objects.en_estado(Visado)]
        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 2 * cm, 3 * cm, 3 * cm, 4 * cm])
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


#------------------------------------------------------------------------------------------------------------------
#jefeinspector ----------------------------------------------------------------------------------------------------

@login_required(login_url="login")
@grupo_requerido('jefeinspector')
def mostrar_jefe_inspector(request):
    contexto = {
        "ctxtramitesconinspeccion": tramite_con_inspecciones_list(request),
        "ctxtramitesagendados": tramites_agendados_por_inspector(request),
        "ctxlistadosinspecciones":listado_inspecciones(request),
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

def inspeccion_final(request,pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    detalles = DetalleDeItemInspeccion.objects.all()        
    items = ItemInspeccion.objects.all()
    categorias = CategoriaInspeccion.objects.all()
    contexto = {"tramite":tramite, "items":items,"detalles":detalles,"categorias":categorias}
    return render(request, 'persona/jefe_inspector/cargar_inspeccion_final.html', contexto)

def completar_inspeccion_final(request,pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
   # id_tramite = int(pk_tramite)
    planilla = PlanillaDeInspeccion()
    planilla.tramite = tramite
    planilla.save()
    list_detalles=[]                    
    for name,value in request.POST.items():        
        if name.startswith('detalle'):
            ipk=name.split('-')[1]
            list_detalles.append(ipk)
    detalles = DetalleDeItemInspeccion.objects.all()
    for detalle in detalles:
        for i in list_detalles:
            if (detalle.id == int(i)):
                planilla.agregar_detalle(detalle)
    planilla.save()
    u = request.user        
    try:        
        tramite.hacer(Tramite.INSPECCIONAR, usuario=u)#ConInspeccion->Inspeccionado    
        tramite.save()
        messages.add_message(request, messages.SUCCESS, 'Inspeccion Finalizada') 
    except:   
        messages.add_message(request, messages.WARNING, "La inspeccion ya fue cargada")
    return redirect('jefe_inspector')
    #return render(request, 'persona/jefe_inspector/cargar_inspeccion_final.html', {'tramite': tramite})

def aceptar_inspeccion_final(request,pk_tramite):
    u = request.user
    tramite.hacer(Tramite.INSPECCIONAR, usuario=u, inspector=u)#agendado->ConInspeccion
    tramite.hacer(Tramite.INSPECCIONAR, usuario=u)#ConInspeccion->Inspeccionado
    messages.add_message(request, messages.SUCCESS, 'Inspeccion Finalizada')
    return redirect('jefe_inspector')

# ve la inspeccion de un tramite o inspecciones
def ver_inspecciones(request, pk_tramite):
    tramite = get_object_or_404(Tramite,pk=pk_tramite)
    inspecciones = []
    for p in PlanillaDeInspeccion.objects.all():
        if (p.tramite.pk == int(pk_tramite)):
            inspecciones.append(p)
    items = ItemInspeccion.objects.all()
    categorias = CategoriaInspeccion.objects.all()
    contexto = {
        'tramite': tramite,
        'inspecciones':inspecciones,
        'inspecciones': inspecciones,
        'items': items,
        'categorias': categorias
    }
    return render(request, 'persona/jefe_inspector/vista_de_inspecciones.html',contexto)

def listado_inspecciones(request):
    tramites=Tramite.objects.en_estado(ConInspeccion)
    contexto={'tramites':tramites}
    return contexto
#------------------------------------------------------------------------------------------------------------------
#director ---------------------------------------------------------------------------------------------------------
from planilla_visado import forms as pforms
from planilla_visado import models as pmodels
from planilla_visado.models import *
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
    elementos = Elemento_Balance_Superficie.objects.all()
    values = {"items":items, "categorias":categorias, "detalles":detalles, "filas": filas, "columnas":columnas, "itemsVisados":itemsVisados, "elementos":elementos, "ctxtramites_anuales":inspecciones_realizadas_durante_el_anio(request),
}
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
        if (not total_usuarios_grupos.has_key(lg)):
            total_usuarios_grupos.setdefault(lg, 0)
    datos_grupos = total_usuarios_grupos.values()
    return render(request, 'persona/director/vista_de_usuarios.html', {"label_grupos":label_grupos, "datos_grupos":datos_grupos})

def ver_tipos_de_obras_mas_frecuentes(request):
    tramites = Tramite.objects.all()
    tipos_obras = TipoObra.objects.all()
    list = []
    list_obras = []
    # for o in tipos_obras:
    #     l = [o,0]
    #     list.append(l)
    # for t in tramites:
    #     for o in tipos_obras:
    #         if t.tipo_obra.id == o.id:
    #             list_obras.append(o)
    datos=[]
    nombres=[]
    for t in tipos_obras:
        cant = Tramite.objects.filter(tipo_obra_id=t.id).exclude(tipo_obra_id__isnull=True).count()
        l = [t, cant]
        list.append(l)
        if cant!=0:
            datos.append(cant)
            nombres.append(t.nombre)
        cant=None
    # for name,value in list:
    #     aux = 0
    #     for o in list_obras:
    #         if name.id == o.id:
    #             l = [name,aux]
    #             i = list.index(l)
    #             aux += 1
    #             l = [name,aux]
    #             list[i] = l
    titulo = "Tipos de obras mas frecuentes"
    grafico = pie_chart_with_legend(datos, nombres, titulo)
    imagen = base64.b64encode(grafico.asString("png"))
    contexto = {"tipos_obras": list, "grafico":imagen}
    return render(request,'persona/director/tipos_de_obras_mas_frecuentes.html',contexto)

def add_legend(draw_obj, chart, data):
    legend = Legend()
    legend.alignment = 'right'
    legend.x = 10
    legend.y = 50
    legend.colorNamePairs = Auto(obj=chart)
    draw_obj.add(legend)


def pie_chart_with_legend(datos, nombres,titulo):
    drawing = Drawing(width=500, height=200)
    my_title = String(150, 180, titulo, fontSize=18)
    pie = Pie()
    pie.sideLabels = True
    pie.x = 150
    pie.y = 65
    pie.data = datos
    pie.labels = [cat for cat in nombres]
    pie.slices.strokeWidth = 0.5
    drawing.add(my_title)
    drawing.add(pie)
    add_legend(drawing, pie, datos)
    return drawing

def ver_categorias_mas_frecuentes(request):
    planillas = PlanillaDeInspeccion.objects.all()    
    #tramites_inspeccionados = Tramite.objects.en_estado(Inspeccionado)
    tramites = Tramite.objects.all()    
    tipos_categorias = CategoriaInspeccion.objects.all()
    detalles = DetalleDeItemInspeccion.objects.all()
    list = []
    for p in planillas:
        for t in tramites:            
            if t.id == p.tramite.id:
                list.append(p)                
    a = 0
    b = 0
    c = 0
    nombres=[]
    for cat in tipos_categorias:
        nombres.append(cat.nombre)
    for l in list:
        list_categorias = l.detalles.values_list('categoria_inspeccion_id')
        for i in list_categorias:
            if 1 in i:
                a+=1
            if 2 in i:
                b+=1
            if 3 in i:
                c+=1
    datos=[a,b,c]
    titulo="Categorias mas frecuentes"
    grafico=pie_chart_with_legend(datos,nombres,titulo)
    imagen=base64.b64encode(grafico.asString("png"))
    contexto = {
        "tipos_categorias":tipos_categorias,
        "detalles":detalles,
        "totala":a,
        "totalb":b,
        "totalc":c,
        "grafico": imagen,
    }
    return render(request,'persona/director/categorias_mas_frecuentes.html',contexto)

def ver_profesionales_mas_requeridos(request):
    planillas = PlanillaDeInspeccion.objects.all()
    tramites_inspeccionados = Tramite.objects.en_estado(ConInspeccion) #aca deberia ir estado Finalizado
   # tramites = Tramite.objects.all()                #puse con inspeccion solo para fines de mostrar algo
    profesionales = Profesional.objects.all()
    list = []
    list_profesionales = []
    # for p in profesionales:
    #     m = [p,0]
    #     list.append(m)
    #for t in tramites:
    #     for p in profesionales:
    #         if t.profesional.id == p.id:
    #             list_profesionales.append(p)
    datos=[]
    nombres=[]
    for p in profesionales:
        cant=Tramite.objects.filter(profesional_id=p.id).exclude(profesional_id__isnull=True).count()
        m=[p,cant]
        list.append(m)
        if cant!=0:
            datos.append(cant)
            nombres.append(str(p.id)+" "+p.persona.nombre+" "+p.persona.apellido)
        cant=None
    # for name,value in list:
    #     aux = 0
    #     for p in list_profesionales:
    #         if name.id == p.id:
    #             m = [name,aux]
    #             i = list.index(m)
    #             aux +=1
    #             m = [name,aux]
    #             list[i] = m
    titulo = "Profesionales mas requeridos"
    grafico = pie_chart_with_legend(datos, nombres, titulo)
    imagen = base64.b64encode(grafico.asString("png"))
    contexto = {
        "profesionales": list,
        "grafico":imagen
    }
    return render(request, 'persona/director/profesionales_mas_requeridos.html',contexto)

def ver_barra_materiales(request):
    items = ItemInspeccion.objects.all()    
    planillas = PlanillaDeInspeccion.objects.all()
    contexto = {
        "items":items,
    }             
    if "Guardar" in request.POST:              
        for name, value in request.POST.items():
            if name.startswith('item'):              
                detalles = __busco_item__(value)                                                                           
                return render(request, 'persona/director/materiales_mas_usados.html',{"detalles":detalles,"tipo_item":value})
    if "Volver" in request.POST: 
        pass
    return render(request,'persona/director/barra_materiales.html',contexto)    

def __busco_item__(item):    
    detalles = DetalleDeItemInspeccion.objects.all()
    planillas = PlanillaDeInspeccion.objects.all()                   
    i = get_object_or_404(ItemInspeccion, nombre=item)
    list = []
    for d in detalles:                    
        if i == d.item_inspeccion:            
            m = [d.nombre,0]
            list.append(m)            
    list_detalles = []
    for p in planillas:
        for d in p.detalles.all():
            list_detalles.append(d.nombre)    
    for l in list_detalles:
        aux = 0
        for name,value in list:
            if l == name:
                aux += value +1
                i = list.index([name,value])
                list[i] = [name,aux]
    return list

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
    fecha_str = date.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(date.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha}
    return render(request, 'persona/director/documentos_del_estado.html', contexto)

def generar_planilla_visado(request):
    filas = FilaDeVisado.objects.all()
    columnas = ColumnaDeVisado.objects.all()
    contexto = {'filas': filas}
    contexto_columnas = {'columnas': columnas}
    balancesSuperficies = Elemento_Balance_Superficie.objects.all()
    itemsVisados = ItemDeVisado.objects.all()
    contexto = {'filas': filas, 'columnas':columnas, 'itemsVisados':itemsVisados,'balancesSuperficies':balancesSuperficies}    
    return render(request, 'persona/director/item_visado.html', contexto)

def ver_planilla_inspeccion(request):
     items = ItemInspeccion.objects.all()
     detalles = DetalleDeItemInspeccion.objects.all()
     categorias = CategoriaInspeccion.objects.all()     
     contexto = {'items': items}
     #return render(request, 'persona/director/ver_planilla_inspeccion.html', {"items":items, "detalles": detalles, "categorias":categorias})
     return render(request, 'persona/director/ver_planilla_inspeccion.html', contexto)

def ver_filtro_obra_fechas(request):
    listado_tramites = []
    list_estados_fechas = []
    if "Guardar" in request.POST:
        tipos = TipoObra.objects.all()
        tramites = Tramite.objects.all()
        estados = Estado.objects.all()
      #  tramites_estados = Tramite.objects.en_estado(Aceptado)
        list = []
        list_obras = []
        for name, value in request.POST.items():
             if name == 'fechaInicial':
                 fechaInicial = value
             if name == 'fechaFinal':
                 fechaFinal = value
        for t in tramites:
            if (str(t.estado().timestamp) >= fechaInicial) and (str(t.estado().timestamp) <= fechaFinal):
                list_estados_fechas.append(t)
        for o in tipos:
            l = [o, 0]
            list.append(l)
        for t in tramites:
            for o in tipos:
                if t.tipo_obra.id == o.id:
                    list_obras.append(o)
        for name, value in list:
            aux = 0
            for o in list_obras:
                if name.id == o.id:
                    l = [name, aux]
                    i = list.index(l)
                    aux += 1
                    l = [name, aux]
                    list[i] = l
        contexto = {"tipos_obras": list}
        return render(request, 'persona/director/tipos_obras_periodo_fechas.html', contexto)
    else:
        pass
    return render(request,'persona/director/filtro_obra_fechas.html')

def ver_sectores_con_mas_obras(request):
    tramites = Tramite.objects.all()
    sectores = []
    list = []
    for t in tramites:
        if not t.sector in sectores:
            sectores.append(t.sector)

    for s in sectores:
        list.append([s, 0])

    sectores = list
    list_sectores = []

    for name, value in sectores:
        v = 0
        for t in tramites:
            if t.sector == name:
                v += 1
        list_sectores.append([name, v])
    contexto = {
        "sectores": list_sectores,
        "nombres": list
    }
    return render(request,'persona/director/ver_sectores_con_mas_obras.html',contexto)

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
        nombre_archivo = "ReporteTramites.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response

class ReporteTramitesDirectorPdf(View):

    def get(self, request, *args, **kwargs):
        filename = "Informe de tramites " + datetime.datetime.now().strftime("%d/%m/%Y") + ".pdf"
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
@login_required(login_url="login")
@grupo_requerido('cajero')
def mostrar_cajero(request):
    contexto = {
        "ctxtramites_para_financiar": listado_tramites_para_financiar(request),
        "ctxcuotas":listado_tramites_a_pagar(request),
        "ctxlistado":listado_tramites(request),
    }
    return render(request, 'persona/cajero/cajero.html', contexto)

def listado_tramites_para_financiar(request):
    tramite = Tramite.objects.en_estado(Visado)
    listado=[]
    for tramites in tramite:
        if tramites.pago is None:
           listado.append(tramites)
    contexto = {'tramites':listado}
    return contexto

def elegir_financiacion(request,pk_tramite):        
    tramite = get_object_or_404(Tramite, pk=pk_tramite)        
    if request.method == "POST":
        if "Guardar" in request.POST: 
            pago = Pago()  
            contador = 31
            fms = "%A"              
            for name, value in request.POST.items():
                if name.startswith('cantidadCuotas'):                                        
                    pago.cantidadCuotas=value                         
            total = tramite.monto_a_pagar/int(pago.cantidadCuotas)
            pago.save()
            for i in range(1, int(pago.cantidadCuotas)+1):
                cuota = Cuota(monto=total, numeroCuota=i, pago=pago)                
                cuota.fechaVencimiento=date.today() + timedelta(days=contador)
                dia=cuota.fechaVencimiento.strftime(fms)
                if dia=="Sunday":
                    cuota.fechaVencimiento==date.today() + timedelta(days=contador+1)
                else:
                    if dia=="Saturday":
                        cuota.fechaVencimiento = date.today() + timedelta(days=contador +2)
                contador=contador+31
                cuota.save()
                cuota.hacer("Cancelacion")
            messages.add_message(request, messages.SUCCESS, 'Todo bien =)')                    
            tramite.pago = pago
            tramite.save()
        return redirect('cajero')                          
    return render(request, 'persona/cajero/elegir_financiacion.html',{'tramite': tramite})

def registrar_pago(request,pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    if request.method == "POST":
        form = FormularioPago(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            contador=31
            fms = "%A"
            if tramite.pago is None:
                pago.save()
                tramite.pago = pago
                tramite.save()
                total=tramite.monto_a_pagar/pago.cantidadCuotas
                for i in range(1, pago.cantidadCuotas+1):
                    cuota = Cuota(monto=total,numeroCuota=i,pago=pago)
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
            else:
                messages.add_message(request, messages.ERROR, 'El tramite ya tiene un pago registrado.')
    else:
        form = FormularioPago()
    return form

def listado_tramites_a_pagar(request):
    objetos=Tramite.objects.all()
    tramites=[]
    for tramite in objetos:
        if ((tramite.pago is not None) and (tramite.esta_pagado()==False)):
            tramites.append(tramite)
    contexto={'tramites':tramites}
    return contexto

def listado_cuotas(request):
    cuotas=Cuota.objects.en_estado(Cancelacion)
    contexto= {'cuotas':cuotas}
    return contexto

def elegir_tramite(request, pk_tramite):
    tramite=get_object_or_404(Tramite,pk=pk_tramite)
    pago=tramite.pago
    cuotas=[]
    objetos=Cuota.objects.en_estado(Cancelacion)
    for cuota in objetos:
        if cuota.fechaPago is None and cuota.pago==pago:
            cuotas.append(cuota)
    return render(request, 'persona/cajero/registrar_cuota.html', {'cuotas':cuotas})

def elegir_cuota(request,pk_cuota):
    cuota=get_object_or_404(Cuota,pk=pk_cuota)
    cuota.guardar_fecha()
    cuota.save()
    cuota.hacer("cancelacion")
    pago = cuota.pago
    tramite = get_object_or_404(Tramite, pago=pago)
    tramite.calcular_monto_pagado(cuota.monto)
    tramite.save()
    messages.add_message(request, messages.SUCCESS, 'Pago Registrado.')
    return render(request, 'persona/cajero/actualizar_cuota.html',{'cuota':cuota})

def comprobante_pago_cuota(request,pk_cuota):
    cuota=get_object_or_404(Cuota,pk=pk_cuota)
    pago = cuota.pago
    tramite = get_object_or_404(Tramite, pago=pago)
    return render(request, 'persona/cajero/comprobante.html',{'cuota': cuota, 'pago':pago,'tramite':tramite})

def registrar_el_pago_tramite(request, pk_cuota):
    cuota = get_object_or_404(Cuota, pk=pk_cuota)
    pago=cuota.pago
    tramite = get_object_or_404(Tramite, pago=pago)
    contexto = {'tramite': tramite,'pago':pago, 'cuota': cuota}
    return render ( request,'persona/cajero/registrar_pago_tramite.html', contexto)

def listado_tramites(request):
    objetos=Tramite.objects.all()
    tramites=[]
    for tramite in objetos:
        if (tramite.pago is not None):
            tramites.append(tramite)
    contexto={'tramites':tramites}
    return contexto

def listado_comprobantes(request,pk_tramite):
    tramite=get_object_or_404(Tramite,pk=pk_tramite)
    pago=tramite.pago
    canceladas=[]
    cuotas=Cuota.objects.en_estado(Cancelada)
    for cuota in cuotas:
        if cuota.pago==pago:
                canceladas.append(cuota)
    if canceladas is None:
        messages.add_message(request, messages.WARNING, 'No hay pagos registrados para el tramite seleccionado.')
    return render (request, 'persona/cajero/listado_comprobantes.html', {'cuotas':canceladas})

#------------------------------------------------------------------------------------------------------------------
#movil ---------------------------------------------------------------------------------------------------------
#
# def movil_login(request):
#     return render(request, 'movil/templates/login.html', contexto)
def es_inspector(usuario):
    return usuario.groups.filter(name='inspector' or 'jefeinspector').exists()

@user_passes_test(es_inspector)
def mostrar_inspector_movil(request):
    if (request.user_agent.is_mobile):
        contexto = {
            "ctxlistado_inspector":listado_inspector_movil(request)
        }
    else:
        return redirect('inspector')
    return render(request, 'persona/movil/inspector_movil.html',contexto)

def movil_inspector(request):
    #return render(request, 'persona/movil/inspector.html')
    return render(request, 'persona/movil/inspector_movil.html')

def frente_o_fachada(request):
    return render(request,'persona/movil/frente_o_fachada.html')    

def paredes(request):    
    return render(request,'persona/movil/paredes.html')    

def cocinas(request):    
    return render(request,'persona/movil/cocinas.html')    

def techos(request):    
    return render(request,'persona/movil/techos.html')                

def listado_inspector_movil(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 5 #Agendados
    argumentos = [Visado, ConInspeccion]
    tramites_del_inspector = Tramite.objects.en_estado(Agendado)
    tramites = filter(lambda t: t.estado().usuario == usuario, tramites_del_inspector)
    contexto={'tramites':tramites}
    return contexto

def planilla_inspeccion_movil(request,pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    movil=es_movil(request)
    contexto = {'tramite': tramite}
    detalles = DetalleDeItemInspeccion.objects.all()        
    items = ItemInspeccion.objects.all()
    categorias = CategoriaInspeccion.objects.all()
    contexto = {"tramite":tramite, "items":items,"detalles":detalles,"categorias":categorias,"movil":movil}
    return render(request, 'persona/movil/planilla_inspeccion.html', contexto)

def es_movil(request):
    if (request.user_agent.is_mobile):
        return True
    else:
        return False

def inspecciones_realizadas_durante_el_anio(request):
    year=date.today()
    tramites1=Tramite.objects.all()
    tramitesEstado=Estado.objects.filter(timestamp__range=(datetime.date(year.year,01,01), datetime.date(year.year,12,12)), tipo=(6))
    tramites=[]
    for i in range(0, len(tramitesEstado)):
        aux=tramites1.filter(id=tramitesEstado[i].tramite_id).exclude(id__isnull=True)
        tramites.append({"tramite": aux, "fecha": tramitesEstado[i].timestamp})
    return {"tramites":tramites}
