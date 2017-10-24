from django.conf.urls import include, url
#from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    url(r'^planillaVisado$', views.mostrar_planillaVisado, name="planillaVisado"),
]
