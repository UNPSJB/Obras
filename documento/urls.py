from django.conf.urls import include, url
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^alta/$', views.alta_documento, name='alta_docuemto'),
]
