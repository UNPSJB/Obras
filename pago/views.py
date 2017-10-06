# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from .models import *
from .forms import *
# Create your views here.
def mostrar_Pago(request):
    form= FormularioPago()
    return render(request,'pago/pago.html',{'form':form})

def mostrar_TipoPago(request):
     form= FormularioTipoPago()
     return render(request,'tipoPago/alta_tipo_de_pago.html',{'form':form})

def alta_tipoPago(request):
    if request.method == "POST":
        form = FormularioTipoPago(request.POST)
        if form.is_valid():
            tipo_pago = form.save(commit=False)
            tipo_pago.save()
    else:
        form = FormularioTipoPago()

    return render(request, 'tipoPago/alta_tipo_de_pago.html', {'form': form})

def alta_Cuota(request):
    if request.method == "POST":
        form = FormularioCuota(request.POST)
        if form.is_valid():
            cuota = form.save(commit=False)
            cuota.save()
    else:
        form = FormularioCuota()

    return render(request, 'tipoPago/alta_tipo_de_pago.html', {'form': form})
