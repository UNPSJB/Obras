from django.shortcuts import render
from .models import *
from .forms import *

def mostrar_tipoDocumento(request):
    form = FormularioTipoDocumento()
    return render(request, 'tipos/tipo_documento/tipoDocumento.html',{'form':form})

def alta_tipoObra(request):
    if request.method == "POST":
        form = FormularioTipoObra(request.POST)
        if form.is_valid():
            tipo_obra = form.save()
    else:
        form = FormularioTipoObra()
    return render(request, 'tipos/tipo_obra/tipoObra.html', {'form': form})


def alta_tipoDocumento(request):
    if request.method == "POST":
        form = FormularioTipoDocumento(request.POST)
        if form.is_valid():
            tipo_documento = form.save(commit=False)
            tipo_documento.save()
    else:
        form = FormularioTipoDocumento()

    return render(request, 'tipos/tipo_documento/tipoDocumento.html', {'form': form})
