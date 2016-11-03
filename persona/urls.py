from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [

    url(r'^profesional$', views.mostrar_profesional,name="profesional"),
    url(r'^inspector$', views.mostrar_inspector,name="inspector"),
    url(r'^jefeinspector$', views.mostrar_jefe_inspector,name="jefe_inspector"),
    url(r'^propietario$', views.mostrar_propietario,name="propietario"),
    url(r'^visador$', views.mostrar_visador,name="visador"),
    url(r'^visar$', views.mostrar_visar,name="visar"),
    url(r'^altapersona$', views.alta_persona,name="alta_persona"),
    url(r'^director$', views.mostrar_director,name="director"),
    url(r'^administrativo$', views.mostrar_administrativo,name="administrativo"),


    url(r'^administrativo/habilitado$', views.habilitar,name="habilitar"),
    # la que manda el correo

    #url( r'^run/(?P<pk>\d+)/$', views.PerfRunView.as_view( ))

]
