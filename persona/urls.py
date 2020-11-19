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
    url(r'^aceptar_tramite/(?P<pk_tramite>\d+)/$', views.aceptar_tramite, name="aceptar_tramite"),

    # propietario ---------------------------------------------------------------------------------------------------
    url(r'^propietario$', views.mostrar_propietario, name="propietario"),
    url(r'^ver_historial_tramite/(?P<pk_tramite>\d+)/$', views.ver_historial_tramite, name="ver_historial_tramite"),
    url(r'^solicitud_final_obra_propietario/(?P<pk_tramite>\d+)/$', views.propietario_solicita_final_obra,name="propietario_solicita_final_obra"),
    url(r'^propietario/documentos_de_estado/(?P<pk_estado>\d+)/$', views.documentos_de_estado, name="documentos_de_estado"),
    url(r'^propietario/financiar', views.tramites_para_financiar, name="financiar"),
    url(r'^propietario/elegir_financiacion_propietario/(?P<pk_tramite>\d+)/$', views.elegir_financiacion_propietario, name="financiar_propietario"),

    # profesional ---------------------------------------------------------------------------------------------------
    url(r'^profesional$', views.mostrar_profesional, name="profesional"),
    url(r'^ver_documentos_tramite_profesional/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_profesional, name="ver_documentos_tramite_profesional"),
    url(r'^ver_documentos_corregidos/(?P<pk_tramite>\d+)/$', views.ver_documentos_corregidos, name="ver_documentos_corregidos"),
    url(r'^solicitud_final_obra/(?P<pk_tramite>\d+)/$', views.profesional_solicita_final_obra, name="profesional_solicita_final_obra"),
    url(r'^enviar_correcciones/(?P<pk_tramite>\d+)/$', views.enviar_correcciones, name="enviar_correcciones"),
    url(r'^profesional/estado_tramite$', views.listado_tramites_de_profesional, name="estado_tramite"),
    url(r'^documento_de_estado/(?P<pk_estado>\d+)/$', views.documento_de_estado, name="documento_de_estado"),
    #url(r'^obtener_documentos_de_estado/(?P<pk_estado>\d+)/$', views.obtener_documentos_de_estado, name="obtener_documentos_de_estado"),
    url(r'^reporte_tramites_profesional_pdf/$', login_required(ReporteTramitesProfesionalPdf.as_view()), name="reporte_tramites_profesional_pdf"),
    url(r'^planilla_inspeccion_impresa/(?P<pk_tramite>\d+)/$', views.planilla_inspeccion_impresa, name="planilla_inspeccion_impresa"),
    url(r'^planilla_visado_impresa/(?P<pk_tramite>\d+)/$', views.planilla_visado_impresa, name="planilla_visado_impresa"),

    # administrativo ------------------------------------------------------------------------------------------------
    url(r'^administrativo$', views.mostrar_administrativo, name="administrativo"),
    url(r'^crearusuario/(?P<pk_propietario>\d+)/$', views.crear_usuario, name="crear_usuario"),
    url(r'^administrativo/tramite_listar$', views.listado_de_tramites_iniciados, name="tramite_listar"),
    url(r'^ver_certificado/(?P<pk>\d+)/$', ver_un_certificado.as_view(), name="ver_certificado"),
    url(r'^documentos_tramite_administrativo/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_administrativo, name="ver_documentos_tramite_administrativo"),
    url(r'^rechazar_tramite/(?P<pk_tramite>\d+)/$', views.rechazar_tramite, name="rechazar_tramite"),
    url(r'^aceptar_tramite/(?P<pk_tramite>\d+)/$', views.aceptar_tramite, name="aceptar_tramite"),
    url(r'^habilitar_final_obra/(?P<pk_tramite>\d+)/$', views.habilitar_final_obra, name="habilitar_final_obra"),
    url(r'^listado_profesionales$', views.listado_profesionales, name="listado_profesionales"),
    url(r'^reporte_listado_profesional_pdf/$', login_required(ReporteProfesionalesPdf.as_view()), name="reporte_listado_profesional_pdf"),
    url(r'^lista_profesionales_imprimible', views.lista_profesionales_imprimible, name="lista_profesionales_imprimible"),

    url(r'^reporte_tramites_corregidos_excel/', ReporteTramitesCorregidosExcel.as_view(),
        name="reporte_tramites_corregidos_excel"),
    url(r'^reporte_tramites_corregidos_pdf/$', login_required(ReporteTramitesCorregidosPdf.as_view()),
        name="reporte_tramites_corregidos_pdf"),

    url(r'^reporte_tramites_iniciados_excel/', ReporteTramitesIniciadosExcel.as_view(),
        name="reporte_tramites_iniciados_excel"),
    url(r'^reporte_tramites_iniciados_pdf/$', login_required(ReporteTramitesIniciadosPdf.as_view()),
        name="reporte_tramites_iniciados_pdf"),

    url(r'^reporte_profesionales_activos_excel/', ReporteProfesionalesActivosExcel.as_view(),
        name="reporte_profesionales_activos_excel"),
    url(r'^reporte_profesionales_activos_pdf/$', login_required(ReporteProfesionalesActivosPdf.as_view()),
        name="reporte_profesionales_activos_pdf"),

    url(r'^reporte_solicitud_final_obra_excel/', ReporteSolicitudFinalObraExcel.as_view(),
        name="reporte_solicitud_final_obra_excel"),
    url(r'^reporte_solicitud_final_obra_pdf/$', login_required(ReporteSolicitudFinalObraPdf.as_view()),
        name="reporte_solicitud_final_obra_pdf"),

    # visador -------------------------------------------------------------------------------------------------------
    url(r'^visador$', views.mostrar_visador, name="visador"),
    url(r'^ver_documentos_para_visado/(?P<pk_tramite>\d+)/$', views.ver_documentos_para_visado, name="ver_documentos_para_visado"),
    url(r'^aprobar_visado/(?P<pk_tramite>\d+)/$', views.aprobar_visado, name="aprobar_visado"),
    url(r'^no_aprobar_visado/(?P<pk_tramite>\d+)/$', views.no_aprobar_visado, name="no_aprobar_visado"),
    url(r'^ver_documentos_visados/(?P<pk_tramite>\d+)/$', views.ver_documentos_visados, name="ver_documentos_visados"),
    url(r'^reporte_tramites_aceptados_excel/', ReporteTramitesAceptadosExcel.as_view(), name="reporte_tramites_aceptados_excel"),
    url(r'^reporte_tramites_aceptados_pdf/$', login_required(ReporteTramitesAceptadosPdf.as_view()), name="reporte_tramites_aceptados_pdf"),
    url(r'^visador/cargar_planilla_visado/(?P<pk_tramite>\d+)/$', views.cargar_planilla_visado, name="cargar_planilla_visado"),
    url(r'^visador/planilla_visado/(?P<pk_tramite>\d+)/$', views.planilla_visado, name="planilla_visado"),
    url(r'^generar_planilla_impresa/(?P<pk_tramite>\d+)/$', views.generar_planilla_impresa, name="generar_planilla_impresa"),

    url(r'^tramites_visados_imprimible', views.tramites_visados_imprimible, name="tramites_visados_imprimible"),

    url(r'^reporte_tramites_visados_excel/', ReporteTramitesVisadosExcel.as_view(),
        name="reporte_tramites_visados_excel"),
    url(r'^reporte_tramites_visados_pdf/$', login_required(ReporteTramitesVisadosPdf.as_view()),
        name="reporte_tramites_visados_pdf"),
    url(r'^mostrar_visados_noaprobados/(?P<pk_tramite>\d+)/$', views.mostrar_visados_noaprobados, name="mostrar_visados_noaprobados"),

    # inspector -----------------------------------------------------------------------------------------------------
    url(r'^inspector$', views.mostrar_inspector, name="inspector"),
    url(r'^vista_de_inspecciones/(?P<pk_tramite>\d+)/$', views.ver_inspecciones, name="ver_inspecciones"),
    url(r'^cargar_inspeccion/(?P<pk_tramite>\d+)/$', views.cargar_inspeccion, name="cargar_inspeccion"),
    url(r'^agendar_tramite/(?P<pk_tramite>\d+)/$', views.agendar_tramite, name="agendar_tramite"),
    url(r'^rechazar_inspeccion/(?P<pk_tramite>\d+)/$', views.rechazar_inspeccion, name="rechazar_inspeccion"),
    url(r'^aceptar_inspeccion/(?P<pk_tramite>\d+)/$', views.aceptar_inspeccion, name="aceptar_inspeccion"),
    url(r'^documentos_tramite_inspector/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_inspector, name="documentos_tramite_inspector"),
    url(r'^inspector/documentos_del_estado_inspector/(?P<pk_estado>\d+)/$', views.documentos_inspector_estado, name="documentos_del_estado_inspector"),
    url(r'^generar_planilla_impresa_inspeccion/(?P<pk_tramite>\d+)/$', views.generar_planilla_impresa_inspeccion, name="generar_planilla_impresa_inspeccion"),

    url(r'^reporte_tramites_agendar_excel/', ReporteTramitesAgendarInspeccionExcel.as_view(),
        name="reporte_tramites_agendar_excel"),
    url(r'^reporte_tramites_agendar_pdf/$', login_required(ReporteTramitesAgendarInspeccionPdf.as_view()),
        name="reporte_tramites_agendar_pdf"),
    #jefeinspector --------------------------------------------------------------------------------------------------
    url(r'^jefeinspector$', views.mostrar_jefe_inspector, name="jefe_inspector"),
    url(r'^inspeccion_final/(?P<pk_tramite>\d+)/$', views.inspeccion_final, name="inspeccion_final"),
    url(r'^agendar_inspeccion_final/(?P<pk_tramite>\d+)/$', views.agendar_inspeccion_final, name="agendar_inspeccion_final"),
    url(r'^aceptar_inspeccion_final/(?P<pk_tramite>\d+)/$', views.aceptar_inspeccion_final, name="aceptar_inspeccion_final"),
    url(r'^listados_inspecciones/$', views.listado_inspecciones, name="listado_inspecciones"),
    url(r'^completar_inspeccion_final/(?P<pk_tramite>\d+)/$', views.completar_inspeccion_final, name="completar_inspeccion_final"),
    url(r'^ver_inspecciones/(?P<pk_tramite>\d+)/$', views.ver_inspecciones, name="todas_las_inspecciones"),

    #director -------------------------------------------------------------------------------------------------------
    url(r'^director$', views.mostrar_director, name="director"),
    url(r'^seleccionar_fecha_item_inspeccion$', views.seleccionar_fecha_item_inspeccion, name="selecionar_fecha_item_inspeccion"),
    url(r'^seleccionar_fecha$', views.tramites_iniciados_finalizados, name="tramites_iniciados_finalizados"),
    url(r'^cambiar_usuario_de_grupo/(?P<pk_persona>\d+)/c', views.cambiar_usuario_de_grupo, name="cambiar_usuario_de_grupo"),
    url(r'^vista_de_tramites$', views.ver_listado_todos_tramites, name="vista_de_tramites"),
    url(r'^detalle_de_tramite/(?P<pk_tramite>\d+)/$', views.detalle_de_tramite, name="detalle_de_tramite"),
    url(r'^documentos_del_estado/(?P<pk_estado>\d+)/$', views.documentos_del_estado, name="documentos_del_estado"),
    url(r'^reporte_tramites_director_excel/', ReporteTramitesDirectorExcel.as_view(), name="reporte_tramites_director_excel"),
    url(r'^reporte_tramites_director_pdf/$', login_required(ReporteTramitesDirectorPdf.as_view()), name="reporte_tramites_director_pdf"),
    url(r'^vista_de_usuarios$', views.ver_listado_todos_usuarios, name="vista_de_usuarios"),
    url(r'^listado_planilla_visado', views.generar_planilla_visado, name="listado_planilla_visado"),
    url(r'^ver_planilla_inspeccion$', views.ver_planilla_inspeccion, name="ver_planilla_inspeccion"),
    url(r'^categorias_mas_frecuentes', views.ver_categorias_mas_frecuentes, name="categorias_mas_frecuentes"),
    url(r'^tipos_de_obras_mas_frecuentes', views.ver_tipos_de_obras_mas_frecuentes, name="tipos_de_obras_mas_frecuentes"),
    url(r'^profesionales_mas_requeridos', views.ver_profesionales_mas_requeridos, name="profesionales_mas_requeridos"),
    url(r'^ver_barra_materiales', views.ver_barra_materiales, name="ver_barra_materiales"),
    url(r'^reporte_inspeccionesDirector_excel/', ReporteInspeccionesDirectorExcel.as_view(), name="reporte_inspeccionesDirector_excel"),
    url(r'^reporte_inspeccionesDirector_pdf/', ReporteInspeccionesDirectorPdf.as_view(), name="reporte_inspeccionesDirector_pdf"),
    url(r'^ver_filtro_obra_fechas', views.ver_filtro_obra_fechas, name="ver_filtro_obra_fechas"),
    url(r'^ver_sectores_con_mas_obras', views.ver_sectores_con_mas_obras, name="ver_sectores_con_mas_obras"),
#    url(r'^tipos_obras_periodo_fechas', views.ver_filtro_obra_fechas, name="tipos_obras_periodo_fechas"),
    url(r'^director/inspecciones_realizadas_durante_el_anio', views.inspecciones_realizadas_durante_el_anio, name="inspecciones_realizadas_durante_el_anio"),
    url(r'^vista_de_todos_tramites$', views.ver_todos_tramites, name="vista_de_todos_tramites"),
    url(r'^listado_de_usuarios_segun_grupo', views.ver_listado_usuarios, name="listado_de_usuarios_segun_grupo"),
    url(r'^tiempo_aprobacion_visados', views.tiempo_aprobacion_visados, name="tiempo_aprobacion_visados"),

    #url(r'^baja_fila_visado', views.baja_fila_visado, name="baja_fila_visado"),
    #url(r'^eliminar_fila_visado', views.eliminar_fila_visado, name="eliminar_fila_visado"),
    #url(r'^baja_columna_visado', views.baja_columna_visado, name="baja_columna_visado"),
    #url(r'^eliminar_columna_visado', views.eliminar_columna_visado, name="eliminar_columna_visado"),
    #url(r'^baja_elemento_visado', views.baja_elemento_visado, name="baja_elemento_visado"),
    #url(r'^eliminar_elemento_visado', views.eliminar_elemento_visado, name="eliminar_elemento_visado"),
    #url(r'^baja_categoria_inspeccion', views.baja_categoria_inspeccion, name="baja_categoria_inspeccion"),
    #url(r'^eliminar_categoria_inspeccion', views.eliminar_categoria_inspeccion, name="eliminar_categoria_inspeccion"),
    #url(r'^baja_item_inspeccion', views.baja_item_inspeccion, name="baja_item_inspeccion"),
    #url(r'^eliminar_item_inspeccion', views.eliminar_item_inspeccion, name="eliminar_item_inspeccion"),
    #url(r'^baja_detalle_inspeccion', views.baja_detalle_inspeccion, name="baja_detalle_inspeccion"),
    #url(r'^eliminar_detalle_inspeccion', views.eliminar_detalle_inspeccion, name="eliminar_detalle_inspeccion"),
    #url(r'^baja_tipo_pago', views.baja_tipo_pago, name="baja_tipo_pago"),
    #url(r'^eliminar_tipo_pago', views.eliminar_tipo_pago, name="eliminar_tipo_pago"),

    url(r'^edit_tipoObra/(?P<pk_tipoObra>\d+)$', views.edit_tipoObra, name="edit_tipoObra"),
    url(r'^delete_tipoObra/(?P<pk_tipoObra>\d+)$', views.delete_tipoObra, name="delete_tipoObra"),

    url(r'^edit_fila_visado/(?P<pk_fila>\d+)$', views.edit_fila_visado, name="edit_fila_visado"),
    url(r'^delete_fila_visado/(?P<pk_fila>\d+)$', views.delete_fila_visado, name="delete_fila_visado"),

    #url(r'^listado_tiposPago', views.listado_tiposPago, name="listado_tiposPago"),
    url(r'^editar_tipoPago/(?P<pk_tipoPago>\d+)$', views.editar_tipoPago, name="editar_tipoPago"),
    url(r'^delete_tipo_pago/(?P<pk_tipoPago>\d+)$', views.delete_tipo_pago, name="delete_tipo_pago"),

    url(r'^edit_columna_visado/(?P<pk_columna>\d+)$', views.edit_columna_visado, name="edit_columna_visado"),
    url(r'^delete_columna_visado/(?P<pk_columna>\d+)$', views.delete_columna_visado, name="delete_columna_visado"),

    url(r'^edit_elemento_visado/(?P<pk_elemento>\d+)$', views.edit_elemento_visado, name="edit_elemento_visado"),
    url(r'^delete_elemento_visado/(?P<pk_elemento>\d+)$', views.delete_elemento_visado, name="delete_elemento_visado"),

    url(r'^edit_item_inspeccion/(?P<pk_item>\d+)$', views.edit_item_inspeccion, name="edit_item_inspeccion"),
    url(r'^delete_item_inspeccion/(?P<pk_item>\d+)$', views.delete_item_inspeccion, name="delete_item_inspeccion"),

    url(r'^edit_categoria_inspeccion/(?P<pk_categoria>\d+)$', views.edit_categoria_inspeccion, name="edit_categoria_inspeccion"),
    url(r'^delete_categoria_inspeccion/(?P<pk_categoria>\d+)$', views.delete_categoria_inspeccion, name="delete_categoria_inspeccion"),

    url(r'^edit_detalle_inspeccion/(?P<pk_detalle>\d+)$', views.edit_detalle_inspeccion, name="edit_detalle_inspeccion"),
    url(r'^delete_detalle_inspeccion/(?P<pk_detalle>\d+)$', views.delete_detalle_inspeccion, name="delete_detalle_inspeccion"),

    url(r'^seleccionar_tipoObra_sector', views.seleccionar_tipoObra_sector, name="seleccionar_tipoObra_sector"),

    #cajero -------------------------------------------------------------------------------------------------------
    url(r'^cajero$', views.mostrar_cajero, name="cajero"),
    url(r'^cajero/tramites_para_financiar$', views.listado_tramites_para_financiar, name="tramites_para_financiar"),
    url(r'^cajero/elegir_financiacion/(?P<pk_tramite>\d+)/$', views.elegir_financiacion, name="financiar"),
    url(r'^cajero/listado_tramites_a_pagar', views.listado_tramites_a_pagar, name="listado_tramites_a_pagar"),
    url(r'^cajero/registrar_pago$', views.pagar, name="pagar"),
    url(r'^cajero/actualizar_cuota/(?P<pk_cuota>\d+)$', views.elegir_cuota, name="elegir_cuota"),
    url(r'^cajero/elegir_tramite/(?P<pk_tramite>\d+)$', views.elegir_tramite, name="elegir_tramite"),
    url(r'^cajero/registrar_pago_tramite$', views.registrar_el_pago_tramite, name="registrar_pago_tramite"),
    url(r'^cajero/registrar_pago_tramite.html(?P<pk_cuota>\d+)$', views.registrar_el_pago_tramite,
        name="registrar_pago_tramite"),
    url(r'^cajero/relizar_pago.html/(?P<pk_cuota>\d+)/$', views.pagar1, name="pagar1"),
    url(r'^cajero/registrar_pago.html/(?P<pk_cuota>\d+)/$', views.comprobante_pago_cuota,  name="comprobante_pago_cuota"),
    # url(r'^cajero/registrar_pago.html/$', views.comprobante_pago_cuota, name="comprobante_pago_cuota"),
    url(r'^cajero/listado_de_comprobantes/(?P<pk_tramite>\d+)$', views.listado_de_comprobantes,
        name="listado_de_comprobantes"),
    url(r'^cajero/listado_tramites$', views.listado_tramites, name="listado_tramites"),
    url(r'^cajero/listado_tramites_comprobantes$', views.listado_tramites, name="listado_tramites"),
    url(r'^cajero/listado_comprobantes/(?P<pk_tramite>\d+)$', views.listado_comprobantes, name="listado_comprobantes"),
    url(r'^cajero/pagar_cuota.html/(?P<pk_cuota>\d+)/$', views.pagar_cuota, name="pagar_cuota"),
    #movil -------------------------------------------------------------------------------------------------------
    url(r'^movil$', views.mostrar_inspector_movil_jefe, name="movil_jefe"),

    url(r'^movil$', views.mostrar_inspector_movil, name="movil_"),

    #url(r'^movil$', views.movil_inspector, name="movil_inspector"),
    #url(r'^inspector_movil$', views.mostrar_inspector_movil, name="inspector_movil"),
    url(r'^listado_inspector_movil$', views.listado_inspector_movil, name="listado_inspector_movil"),
    url(r'^planilla_inspeccion/(?P<pk_tramite>\d+)$', views.planilla_inspeccion_movil, name="planilla_inspeccion_movil"),
    #url(r'^vista_de_inspecciones/(?P<pk_tramite>\d+)/$', views.ver_inspecciones_movil, name="ver_inspecciones_movil"),

]
