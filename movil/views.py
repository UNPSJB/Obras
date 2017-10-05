# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required
from obras_particulares.views import *
from django.views.generic import TemplateView

def mostrar_movil(request):
    return render(request, 'login.html')
    
def movil_inspector(request):	
	return render(request, 'inspector.html')

class MovilView(TemplateView):
    template_name = "movil/inspector.html"