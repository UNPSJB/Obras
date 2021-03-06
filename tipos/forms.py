from django import forms
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Submit, Field
from django.forms import ValidationError
import datetime

from .models import *
from documento import *
from tipos import *

class FormularioTipoDocumento(forms.ModelForm):
    NAME = 'tipo_documento_form'
    SUBMIT = 'tipo_documento_submit'
    class Meta:
        model = TipoDocumento
        fields = ('nombre', 'descripcion', 'activo', 'fecha_alta')

    #Esto es para el crispy
    def __init__(self, *args, **kwargs):
        super(FormularioTipoDocumento, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.helper.layout = Layout(
            Field('nombre', placeholder='Ingresar Nombre'),
            Field('descripcion', placeholder='Ingresar Descripcion'),
            Field('activo', placeholder='Ingresar Activo'),
            Field('fecha_alta', placeholder='Ingresar Fecha de Alta', css_class='datepicker'),
        )
        #self.fields['requerido'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,


    def clean_requerido(self):
        flags = [int(e) for e in self.cleaned_data['requerido']]
        return sum(flags)

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = TipoDocumento.objects.filter(nombre__iexact=nombre)
        if cargados.exists():
             for t in cargados:
                if nombre == t.nombre and t.activo == 0:
                    return t
             raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioTipoObra(forms.ModelForm):
    NAME = 'tipo_obra_form'
    SUBMIT = 'tipo_obra_submit'
    class Meta:
        model = TipoObra
        fields = ('nombre','descripcion','categorias')

    def __init__(self, *args, **kwargs):
        super(FormularioTipoObra, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('tipo_obra_submit', 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"
        self.fields['descripcion'].widget.attrs['placeholder'] = "Ingresar Descripcion"
        self.fields['categorias'].widget.attrs['placeholder'] = "Ingresar Categoria/s"

    def clean_tipoObra(self):
        tipoObra = self.cleaned_data['tipoObra']
        if tipoObra is None:
            raise ValidationError("Seleccione un tipo de Obra")
        return tipoObra

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = TipoObra.objects.filter(nombre__iexact=nombre)
        if cargados.exists():
            for i in cargados:
                if nombre == i.nombre and i.activo == 0:
                    return i
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

#agrego tipo pago

class FormularioTipoPago(forms.ModelForm):
    NAME = 'tipo_pago_form'
    SUBMIT = 'tipo_de_pago_submit'

    class Meta:
        model = Tipo_Pago
        fields = ('nombre',)
        #cuota = forms.ChoiceField(choices=Pago.CUOTAS)

    def __init__(self, *args, **kwargs):
        super(FormularioTipoPago, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"

    def clean_nombre(self):
        tipoPago = self.cleaned_data['nombre']
        cargados = Tipo_Pago.objects.filter(nombre__iexact=tipoPago)
        if cargados.exists():
              for i in cargados:
                   if tipoPago == i.nombre and i.activo == 0:
                       return i
              raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return tipoPago

class FormularioTipoObraModificada(forms.ModelForm):
    NAME = 'tipo_obra_form_modificada'
    SUBMIT = 'tipo_obra_submit'
    class Meta:
        model = TipoObra
        fields = ('nombre','descripcion','categorias')

    def __init__(self, *args, **kwargs):
        super(FormularioTipoObraModificada, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('tipo_obra_submit', 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"
        self.fields['descripcion'].widget.attrs['placeholder'] = "Ingresar Descripcion"
        self.fields['categorias'].widget.attrs['placeholder'] = "Ingresar Categoria/s"

    def clean_tipoObra(self):
        tipoObra = self.cleaned_data['tipoObra']
        if tipoObra is None:
            raise ValidationError("Seleccione un tipo de Obra")
        return tipoObra

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = TipoObra.objects.filter(nombre__iexact=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioTipoPagoModificado(forms.ModelForm):
    NAME = 'tipo_pago_form'
    SUBMIT = 'tipo_de_pago_submit'

    class Meta:
        model = Tipo_Pago
        fields = ('nombre',)
        #cuota = forms.ChoiceField(choices=Pago.CUOTAS)

    def __init__(self, *args, **kwargs):
        super(FormularioTipoPagoModificado, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"

    def clean_nombre(self):
        tipoPago = self.cleaned_data['nombre']
        cargados = Tipo_Pago.objects.filter(nombre__iexact=tipoPago)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return tipoPago