from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, ButtonHolder
from django.contrib.admin.helpers import Fieldset

from .models import *
from tramite.models import *
from django.forms import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.contrib import messages

class FormularioPersona(forms.ModelForm):
    NAME = 'persona_form'
    SUBMIT = 'persona_submit'

    class Meta:
        model = Persona
        fields = ('dni', 'nombre', 'apellido', 'telefono', 'domicilio', 'cuil', 'mail')

    def __init__(self, *args, **kwargs):
        super(FormularioPersona, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(self.SUBMIT, 'Enviar Solicitud'))
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    field.widget = forms.TextInput(attrs={'placeholder': "Ingresar " + str(field.label)})

        self.fields['dni'].widget.attrs['placeholder'] = "Ingresar Dni"
        self.fields['dni'].widget.attrs['max'] = "99999999"
        self.fields['dni'].widget.attrs['min'] = "9999999"
        self.fields['dni'].widget.attrs['title'] = "Ingresar Nro de documento"
        self.fields['cuil'].widget.attrs['pattern'] = "^[0-9]{2}-[0-9]{8}/[0-9]$"
        self.fields['cuil'].widget.attrs['title'] = "Ingresar Cuil con formato xx-xxxxxxxx/x"
        self.fields['cuil'].widget.attrs['placeholder'] = "Ingresar Cuil con Formato: xx-xxxxxxxx/x"
        self.fields['nombre'].widget.attrs['title'] = "Ingresar Nombre no menor a 3 (tres) letras"
        self.fields['nombre'].widget.attrs['pattern'] = "^[A-Za-z]{3,50}"
        self.fields['apellido'].widget.attrs['title'] = "Ingresar Apellido no menor a 3 (tres) letras"
        self.fields['apellido'].widget.attrs['pattern'] = "^[A-Za-z]{3,50}"
        self.fields['telefono'].widget.attrs['title'] = "Ingresar Nro de Telefono con codigo de area ej 280154565788"
        self.fields['telefono'].widget.attrs['placeholder'] = "Ingresar Nro de Telefono con codigo de area ej 280154565788"
        self.fields['telefono'].widget.attrs['pattern'] = "^[0-9]{7,15}"
        self.fields['domicilio'].widget.attrs['title'] = "Ingresar Domicilio ej calle 11111"
        self.fields['domicilio'].widget.attrs['placeholder'] = "Ingresar Domicilio ej calle 11111"
        self.fields['domicilio'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z ]{3,50} [0-9]{2,5}$"
        self.fields['mail'].widget.attrs['title'] = "Ingresar Mail- Formato: xxxxxxx@xxx.xxx"
        self.fields['mail'].widget.attrs['placeholder'] = "Ingresar Mail - Formato: xxxxxxx@xxx.xxx"

    def clean_dni(self):
        dato = self.cleaned_data['dni']
        if Persona.objects.filter(dni=dato).exists():
            raise ValidationError('La persona ya existe en el sistema')
        return dato

    def clean_mail(self):
        dato_mail = self.cleaned_data['mail']
        if Persona.objects.filter(mail=dato_mail).exists():
            raise ValidationError('El mail ya pertenece a otra persona registrada en el sistema')
        return dato_mail

    def clean_cuil(self):
        dato_cuil = self.cleaned_data['cuil']
        if Persona.objects.filter(cuil=dato_cuil).exists():
            raise ValidationError('El cuil ya pertenece a otra persona registrada en el sistema')
        return dato_cuil

class FormularioProfesional(FormularioPersona):
    NAME = 'profesional_form'
    SUBMIT = 'profesional_submit'
    matricula = forms.IntegerField()
    profesion = forms.ChoiceField(choices=Profesional.PROFESIONES)
    categorias = forms.ChoiceField(choices=Profesional.CATEGORIAS)
    certificado = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(FormularioProfesional, self).__init__(*args, **kwargs)
        self.fields['matricula'].widget.attrs['placeholder'] = "Ingresar Matricula"
        self.fields['matricula'].widget.attrs['max'] = "100000"
        self.fields['matricula'].widget.attrs['min'] = "1"

    def save(self, commit=False):
        persona = super(FormularioProfesional, self).save(commit=commit)
        datos = self.cleaned_data
        p = Profesional(
            profesion= datos['profesion'],
            matricula= datos['matricula'],
            categoria= datos['categorias'],
            certificado = datos['certificado'])
        p.save()
        persona.profesional= p
        persona.save()
        return p

    def clean_matricula(self):
        dato = self.cleaned_data['matricula']
        if Profesional.objects.filter(matricula=dato).exists():
            raise ValidationError('Matricula repetida')
        return dato

class FormularioPropietario(FormularioPersona):
    NAME = 'propietario_form'
    SUBMIT = 'propietario_submit'

    def __init__(self, *args, **kwargs):
        super(FormularioPropietario, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def save(self, commit=False):
        persona = super(FormularioPropietario, self).save(commit=commit)
        p = Propietario()
        p.save()
        persona.propietario = p
        persona.save()
        return p

    def crear(self, persona=None):
        if persona:
           propietario = Propietario()
           propietario.save()
           persona.propietario = propietario
           grupo = Group.objects.get(name="propietario")
           persona.usuario.groups.add(grupo)
           persona.save()
           return persona.propietario

        elif self.is_valid():
            return self.save()

class FormularioUsuario(AuthenticationForm):
    NAME = 'usuario_form'
    SUBMIT = 'usuario_submit'

    def __init__(self, *args, **kwargs):
        super(FormularioUsuario, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit', css_class="btn btn-default"))

class FormularioUsuarioPersona(FormularioPersona):
    NAME = 'usuario_persona_form'
    SUBMIT = 'usuario_persona_submit'
    usuario = forms.CharField()
    password = forms.CharField()
    grupos = {
        ('1', 'director'),
        ('2', 'administrativo'),
        ('3', 'visador'),
        ('4', 'inspector'),
        ('7', 'jefeinspector'),
        ('8', 'cajero')}

    grupo = forms.TypedMultipleChoiceField(grupos)

    def __init__(self, *args, **kwargs):
        super(FormularioUsuarioPersona, self).__init__(*args, **kwargs)
        self.fields['usuario'].widget.attrs['placeholder'] = "Ingresar Nombre Usuario"
        self.fields['usuario'].widget.attrs['pattern'] = ".{5,}"
        self.fields['password'].widget.attrs['placeholder'] = "Ingresar Contrasena"
        self.fields['password'].widget.attrs['pattern'] = ".{6,}"
        self.fields['usuario'].widget.attrs['title'] = "Ingresar Usuario"
        self.fields['password'].widget.attrs['title'] = "Ingresar password"

    def clean_usuario(self):
        dato = self.cleaned_data['usuario']
        if Usuario.objects.filter(username=dato).exists():
            raise ValidationError('Nombre de usuario registrado en el sistema, ingrese otro nombre de usuario')
        return dato

    def save(self, commit=False):
        persona = super(FormularioUsuarioPersona, self).save(commit=False)
        datos = self.cleaned_data
        try:
            persona.usuario = Usuario.objects.create_user(username=datos['usuario'], email=datos['mail'], password=datos['password'],)
            grupos = {
                '1': 'director',
                '2':'administrativo',
                '3': 'visador',
                '4': 'inspector',
                '7': 'jefeinspector',
                '8': 'cajero'}
            grupo_post = datos['grupo']
            grupo=grupos[grupo_post[0]]
            if grupo:
                persona.usuario.save()
                persona.save()
                usuario = persona.usuario
                usuario.groups.add(int(grupo_post[0]))
            return usuario
        except:
            clean_usuario(self)
            pass

class FormularioArchivoPago(forms.Form):

    NAME = 'archivo_pago_form'
    SUBMIT = 'archivo_pago_submit'
    pagos = forms.FileField()

    class Meta:
        fields= ('file', 'pagos')

    def __init__(self, *args, **kwargs):
        super(FormularioArchivoPago, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enviar', css_class="btn btn-default"))

