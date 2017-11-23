from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from . import views
from tramite.models import *
from persona.views import *
from pago.views import *

urlpatterns = [

    #No me acuerdo de donde son - Acomodar esto!!!! -------------------------------------------------------------------

    url(r'^altapersona$', views.alta_persona, name="alta_persona"),
    url(r'^crearusuario/(?P<pk_persona>\d+)/$', views.crear_usuario, name="crear_usuario"),
    url(r'^habilitar_final_obra/(?P<pk_tramite>\d+)/$', views.habilitar_final_obra, name="habilitar_final_obra"),
    url(r'^aceptar_tramite/(?P<pk_tramite>\d+)/$', views.aceptar_tramite, name="aceptar_tramite"),

    # propietario ---------------------------------------------------------------------------------------------------
    url(r'^propietario$', views.mostrar_propietario, name="propietario"),
    url(r'^ver_historial_tramite/(?P<pk_tramite>\d+)/$', views.ver_historial_tramite, name="ver_historial_tramite"),
    url(r'^solicitud_final_obra_propietario/(?P<pk_tramite>\d+)/$', views.propietario_solicita_final_obra, name="propietario_solicita_final_obra"),
    url(r'^documentos_de_estado/(?P<pk_estado>\d+)/$', views.documentos_de_estado, name="documentos_de_estado"),
    url(r'^cajero/tramites_para_financiar$', views.tramites_para_financiar, name="tramites_para_financiar"),
    url(r'^cajero/elegir_financiacion/(?P<pk_tramite>\d+)/$', views.elegir_financiacion, name="financiar"),

    # profesional ---------------------------------------------------------------------------------------------------
    url(r'^profesional$', views.mostrar_profesional, name="profesional"),
    url(r'^ver_documentos_tramite_profesional/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_profesional, name="ver_documentos_tramite_profesional"),
    url(r'^ver_documentos_corregidos/(?P<pk_tramite>\d+)/$', views.ver_documentos_corregidos, name="ver_documentos_corregidos"),
    url(r'^solicitud_final_obra/(?P<pk_tramite>\d+)/$', views.profesional_solicita_final_obra, name="profesional_solicita_final_obra"),
    url(r'^enviar_correcciones/(?P<pk_tramite>\d+)/$', views.enviar_correcciones, name="enviar_correcciones"),
    url(r'^profesional/estado_tramite$', views.listado_tramites_de_profesional, name="estado_tramite"),
    url(r'^documento_de_estado/(?P<pk_estado>\d+)/$', views.documento_de_estado, name="documento_de_estado"),

    # administrativo ------------------------------------------------------------------------------------------------
    url(r'^administrativo$', views.mostrar_administrativo, name="administrativo"),
    url(r'^crearusuario/(?P<pk_propietario>\d+)/$', views.crear_usuario, name="crear_usuario"),
    url(r'^administrativo/tramite_listar$', views.listado_de_tramites_iniciados, name="tramite_listar"),
    url(r'^ver_certificado/(?P<pk>\d+)/$', ver_un_certificado.as_view(), name="ver_certificado"),
    url(r'^documentos_tramite_administrativo/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_administrativo, name="ver_documentos_tramite_administrativo"),
    url(r'^rechazar_tramite/(?P<pk_tramite>\d+)/$', views.rechazar_tramite, name="rechazar_tramite"),
    url(r'^aceptar_tramite/(?P<pk_tramite>\d+)/$', views.aceptar_tramite, name="aceptar_tramite"),

    # visador -------------------------------------------------------------------------------------------------------
    url(r'^visador$', views.mostrar_visador, name="visador"),
    url(r'^ver_documentos_para_visado/(?P<pk_tramite>\d+)/$', views.ver_documentos_para_visado, name="ver_documentos_para_visado"),
    url(r'^aprobar_visado/(?P<pk_tramite>\d+)/$', views.aprobar_visado, name="aprobar_visado"),
    url(r'^no_aprobar_visado/(?P<pk_tramite>\d+)/$', views.no_aprobar_visado, name="no_aprobar_visado"),
    url(r'^ver_documentos_visados/(?P<pk_tramite>\d+)/$', views.ver_documentos_visados, name="ver_documentos_visados"),
    url(r'^reporte_tramites_aceptados_excel/', ReporteTramitesAceptadosExcel.as_view(), name="reporte_tramites_aceptados_excel"),
    url(r'^reporte_tramites_aceptados_pdf/$', login_required(ReporteTramitesAceptadosPdf.as_view()), name="reporte_tramites_aceptados_pdf"),
    url(r'^visador/planilla_visado/(?P<pk_tramite>\d+)/$', views.planilla_visado, name="planilla_visado"),    
    #url(r'^visador/ver_planilla_visado/', views.ver_planilla_visado, name="ver_planilla_visado"),    

    # inspector -----------------------------------------------------------------------------------------------------
    url(r'^inspector$', views.mostrar_inspector, name="inspector"),
    url(r'^vista_de_inspecciones/(?P<pk_tramite>\d+)/$', views.ver_inspecciones, name="ver_inspecciones"),
    url(r'^cargar_inspeccion/(?P<pk_tramite>\d+)/$', views.cargar_inspeccion, name="cargar_inspeccion"),
    url(r'^agendar_tramite/(?P<pk_tramite>\d+)/$', views.agendar_tramite, name="agendar_tramite"),
    url(r'^rechazar_inspeccion/(?P<pk_tramite>\d+)/$', views.rechazar_inspeccion, name="rechazar_inspeccion"),
    url(r'^aceptar_inspeccion/(?P<pk_tramite>\d+)/$', views.aceptar_inspeccion, name="aceptar_inspeccion"),
    url(r'^documentos_tramite_inspector/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_inspector, name="documentos_tramite_inspector"),
    url(r'^documentos_inspector_estado/(?P<pk_estado>\d+)/$', views.documentos_inspector_estado, name="documentos_inspector_estado"),

    #jefeinspector --------------------------------------------------------------------------------------------------
    url(r'^jefeinspector$', views.mostrar_jefe_inspector, name="jefe_inspector"),
    url(r'^cargar_inspeccion_final/(?P<pk_tramite>\d+)/$', views.cargar_inspeccion_final, name="cargar_inspeccion_final"),
    url(r'^agendar_inspeccion_final/(?P<pk_tramite>\d+)/$', views.agendar_inspeccion_final, name="agendar_inspeccion_final"),
    url(r'^aceptar_inspeccion_final/(?P<pk_tramite>\d+)/$', views.aceptar_inspeccion_final, name="aceptar_inspeccion_final"),

    #director -------------------------------------------------------------------------------------------------------
    url(r'^director$', views.mostrar_director, name="director"),
    url(r'^cambiar_usuario_de_grupo/(?P<pk_persona>\d+)/$', views.cambiar_usuario_de_grupo, name="cambiar_usuario_de_grupo"),
    url(r'^vista_de_tramites$', views.ver_listado_todos_tramites, name="vista_de_tramites"),
    url(r'^detalle_de_tramite/(?P<pk_tramite>\d+)/$', views.detalle_de_tramite, name="detalle_de_tramite"),
    url(r'^documentos_del_estado/(?P<pk_estado>\d+)/$', views.documentos_del_estado, name="documentos_del_estado"),
    url(r'^reporte_tramites_director_excel/', ReporteTramitesDirectorExcel.as_view(), name="reporte_tramites_director_excel"),
    url(r'^reporte_tramites_director_pdf/$', login_required(ReporteTramitesDirectorPdf.as_view()), name="reporte_tramites_director_pdf"),
    url(r'^vista_de_usuarios$', views.ver_listado_todos_usuarios, name="vista_de_usuarios"),
    url(r'^listado_planilla_visado', views.generar_planilla_visado, name="listado_planilla_visado"),
    url(r'^ver_planilla_inspeccion$', views.ver_planilla_inspeccion, name="ver_planilla_inspeccion"),
    
    #cajero -------------------------------------------------------------------------------------------------------
    url(r'^cajero$', views.mostrar_cajero, name="cajero"),
    url(r'^cajero/tramites_para_financiar$', views.listado_tramites_para_financiar, name="tramites_para_financiar"),
    url(r'^elegir_financiacion/(?P<pk_tramite>\d+)/$', views.elegir_financiacion, name="financiar"),

    url(r'^cajero/registrar_cuota/$', views.elegir_tramite, name="registrar_cuota"),
    url(r'^cajero/listado_tramites_a_pagar', views.listado_tramites_a_pagar, name="listado_tramites_a_pagar"),
    url(r'^cajero/actualizar_cuota/(?P<pk_cuota>\d+)$', views.elegir_cuota, name="actualizar_cuota"),
    url(r'^cajero/elegir_tramite/(?P<pk_tramite>\d+)$', views.elegir_tramite, name="elegir_tramite"),
    #TODO como hacer para no acceder a las otras cuotas?
    url(r'^cajero/registrar_pago.html/(?P<pk_tramite>\d+)/$', views.registrar_pago, name="registrar_pago"),

    #movil -------------------------------------------------------------------------------------------------------
    url(r'^movil$', views.movil_inspector, name="movil_inspector"),    
    url(r'^inspector_movil$', views.mostrar_inspector_movil, name="inspector_movil"),
    url(r'^planilla_inspeccion_movil/(?P<pk_tramite>\d+)/$', views.planilla_inspeccion_movil, name="planilla_inspeccion_movil"),
    #url(r'^vista_de_inspecciones/(?P<pk_tramite>\d+)/$', views.ver_inspecciones_movil, name="ver_inspecciones_movil"),
    url(r'^cargar_inspeccion/(?P<pk_tramite>\d+)/$', views.cargar_inspeccion_movil, name="cargar_inspeccion_movil"),

]
