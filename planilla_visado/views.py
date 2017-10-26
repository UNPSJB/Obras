from django.shortcuts import render
from .models import *
from .forms import *

# Create your views here.
# def alta_elemento_balance(request):
#     if request.method == "POST":
#         form = FormularioElementoBalanceSuperficie(request.POST)
#         if form.is_valid():
#             elemento_balanceSuperficie = form.save()
#     else:
#         form = FormularioElementoBalanceSuperficie()
#     return render(request, 'elementoBalance/elemento_balanceSuperficie.html', {'form': form})
#
# def mostrar_elemento_balance(request):
#     form= FormularioElementoBalanceSuperficie()
#     return render(request,'elementoBalance/elemento_balanceSuperficie.html',{'form':form})
#
# def alta_columna_visado(request):
#     if request.method == "POST":
#         form = FormularioColumnaVisado(request.POST)
#         if form.is_valid():
#             columna_planillaVisado = form.save()
#     else:
#         form = FormularioColumnaVisado()
#     return render(request, 'columnaPlanilla/columna_planillaVisado.html', {'form': form})
#
# def mostrar_columna_visado(request):
#     form= FormularioColumnaVisado()
#     return render(request,'columnaPlanilla/columna_planillaVisado.html',{'form':form})
#
# def alta_fila_visado(request):
#     if request.method == "POST":
#         form = FormularioFilaVisado(request.POST)
#         if form.is_valid():
#             fila_planillaVisado = form.save()
#     else:
#         form = FormularioFilaVisado()
#     return render(request, 'filaPlanilla/fila_planillaVisado.html', {'form': form})
#
# def mostrar_fila_visado(request):
#     form = FormularioFilaVisado()
#     return render(request, 'filaPlanilla/fila_planillaVisado.html', {'form': form})
#
#
# def alta_item_visado(request):
#     if request.method == "POST":
#         form = FormularioItemDeVisado(request.POST)
#         if form.is_valid():
#             item_visado = form.save()
#     else:
#         form = FormularioItemDeVisado()
#     return render(request, 'itemPlanilla/item_visado.html', {'form': form})
#
# def mostrar_item_visado(request):
#     form = FormularioItemDeVisado()
#     return render(request, 'itemPlanilla/item_visado.html', {'form': form})