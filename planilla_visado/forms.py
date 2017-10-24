from crispy_forms.helper import FormHelper
from django import forms
from django.forms import ValidationError
from crispy_forms.layout import Submit, Field

from .models import *


class FormularioDocBalanceSuperficie(forms.ModelForm):
    NAME = 'doc_balance_superficie_form'
    SUBMIT = 'doc_balance_superficie_submit'

    class Meta:
        model = Doc_Balance_Superficie
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioDocBalanceSuperficie, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre de documento de balance"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = Doc_Balance_Superficie.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioElementoBalanceSuperficie(forms.ModelForm):
    NAME = 'elemento_balance_form'
    SUBMIT = 'elemento_balance_submit'

    class Meta:
        model = Doc_Balance_Superficie
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioElementoBalanceSuperficie, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre de documento de balance"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = Doc_Balance_Superficie.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre


class FormulariotTipoVista(forms.ModelForm):
    NAME = 'tipo_vista_form'
    SUBMIT = 'tipo_vista_submit'

    class Meta:
        model = Tipo_De_Vista
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormulariotTipoVista, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre de tipo de vista"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = Tipo_De_Vista.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioElementoDeVista(forms.ModelForm):
    NAME = 'elemento_vista_form'
    SUBMIT = 'elemento_vista_submit'

    class Meta:
        model = Elemento_De_Vista
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioElementoDeVista, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre de elemento de vista"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = Elemento_De_Vista.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre


class FormularioItemDeVistaElemento(forms.ModelForm):
    NAME = 'item_vista_elementoform'
    SUBMIT = 'item_vista_submit'

    class Meta:
        model = Elemento_De_Vista
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioItemDeVistaElemento, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre de elemento de vista"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = Elemento_De_Vista.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre