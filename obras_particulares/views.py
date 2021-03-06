from persona import *
from persona.forms import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from . import forms

def registrarse (request):
        if request.method == "POST":
            if "profesional_submit" in request.POST:
                form = FormularioProfesional(request.POST, request.FILES)
                if form.is_valid():
                    profesional = form.save()
                    profesional.save()
                    messages.add_message(request, messages.SUCCESS, "Solicitud de Registro Enviada")
                    return redirect('home1')
                else:
                    messages.add_message(request, messages.ERROR,
                                         "Solicitud de Registro No Enviada - Comuniquese con el administrador")
        else:
            form = FormularioProfesional()
        return render(request, "registrarse.html", {'form': form})

def login_view(request):
    if request.method == 'POST':
        if (request.POST["username"] is not None and request.POST['password'] is not None):
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            movil=es_movil(request)
            if user is not None and user.is_active :
                if not movil or (movil and user.groups.filter(name='inspector').exists() or  user.groups.filter(name='jefeinspector').exists()):
                    login(request, user)
                    return redirect(user.get_view_name())
                else:
                    logout_view(request)
                    messages.add_message(request, messages.WARNING, 'Acceso no autorizado')
            else:
                messages.add_message(request, messages.WARNING, 'Clave o usuario incorrecto.')
    return redirect("home")


def logout_view(request):
    logout(request)
    return redirect("home")

def ayuda(request):
    return render(request, "documentacion/_build/html/ayudaUsuario.html", {})

def home1(request):
    usuario = request.user
    if usuario is not None and not usuario.is_anonymous:
        return redirect('inspector_movil')
    else:
        form = FormularioProfesional()
        return render(request, 'homeMovil.html',{'login_usuario_form': forms.FormularioLogin(),'form':form})

def home(request):
    movil= es_movil(request)
    if movil:
        usuario= request.user
        if usuario is not None and not usuario.is_anonymous:
            return redirect('inspector_movil')
        else:
            return redirect('home1')
    else :
        if request.method == "POST":
            form = FormularioProfesional(request.POST, request.FILES)
            if form.is_valid():
                profesional = form.save()
                profesional.save()
                messages.add_message(request, messages.SUCCESS, "Solicitud de Registro Enviada")
                return redirect('home')
            else:
                messages.add_message(request, messages.SUCCESS, "Solicitud de NO Registro Enviada - Comuniquese con el administrador")
        else:
            form = FormularioProfesional()
        return render(request, 'home.html',{'login_usuario_form': forms.FormularioLogin(),'form':form})


def grupo_requerido(*grupos):
    def view_funct(f):
        def func_wrapped(request, *args, **kwargs):
            usuario = request.user
            if bool(usuario.groups.filter(name__in=grupos)) | usuario.is_superuser:
                return f(request, *args, **kwargs)
            else:
                return redirect(usuario.get_view_name())
        return func_wrapped
    return view_funct

def es_movil(request):
    if (request.user_agent.is_mobile):
        return True
    else:
        return False