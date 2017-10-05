from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    url(r'^tipoPago/new$', views.alta_tipoPago),
    url(r'^tipoPago', views.mostrar_TipoPago(), name='mostrar_tipoPago'),
    url(r'^pago/new$', views.mostrar_Pago(), name='mostrar_Pago'),

]
