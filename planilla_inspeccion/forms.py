from crispy_forms.helper import FormHelper
from django import forms
from django.forms import ValidationError
from crispy_forms.layout import Submit, Field

from .models import *

class FormularioTipoCategoriaInspeccion(forms.ModelForm):
    NAME = 'tipo_cat_inspeccicon_form'
    SUBMIT = 'tipo_cat_inspeccion_submit'

    class Meta:
        model = TipoCategoriaInspeccion
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioTipoCategoriaInspeccion, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar descripcion de categoria"

    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion']
        cargados = TipoCategoriaInspeccion.objects.filter(nombre__icontains=descripcion)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().descripcion))
        return descripcion

class FormularioCategoriaInspeccion(forms.ModelForm):
    NAME = 'cat_inspeccicon_form'
    SUBMIT = 'cat_inspeccion_submit'

    class Meta:
        model = TipoCategoriaInspeccion
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioCategoriaInspeccion, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar descripcion de categoria"

    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion']
        cargados = TipoCategoriaInspeccion.objects.filter(nombre__icontains=descripcion)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return descripcion

class FormularioItemInspeccion(forms.ModelForm):
    NAME = 'item_inspeccicon_form'
    SUBMIT = 'item_inspeccion_submit'

    class Meta:
        model = ItemInspeccion
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioItemInspeccion, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar descripcion de categoria"

    def clean_descripcion(self):
        nombre = self.cleaned_data['descripcion']
        cargados = ItemInspeccion.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre