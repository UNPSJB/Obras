from django import forms
from django.forms import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import *

class FormularioIniciarTramite(forms.ModelForm):
    NAME = 'tramite_form'
    SUBMIT = 'tramite_submit'
    propietario = forms.IntegerField()

    class Meta:
        model = Tramite
        fields = (
            'tipo_obra',
            'medidas', 
            'profesional',
            'domicilio',
            'parcela',
            'circunscripcion',
            'manzana',
            'sector'
        )
        widgets = {
            "profesional": forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(FormularioIniciarTramite, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.add_input(Submit(self.SUBMIT, 'Guardar Tramite'))
        self.helper.form_tag = False
        self.fields['tipo_obra'].queryset = TipoObra.objects.filter(activo=True)
        self.fields['medidas'].widget.attrs['placeholder'] = "Ingresar Medidas en m2"
        self.fields['medidas'].widget.attrs['max'] = "100000"
        self.fields['medidas'].widget.attrs['min'] = "1"
        self.fields['profesional'].widget.attrs['placeholder'] = "Ingresar DNI del Profesional"
        self.fields['parcela'].widget.attrs['placeholder'] = "Ingresar numero de Parcela"
        self.fields['parcela'].widget.attrs['max'] = "500000"
        self.fields['parcela'].widget.attrs['min'] = "1"
        self.fields['circunscripcion'].widget.attrs['placeholder'] = "Ingresar numero de Circunscripcion"
        self.fields['circunscripcion'].widget.attrs['max'] = "500000"
        self.fields['circunscripcion'].widget.attrs['min'] = "1"
        self.fields['manzana'].widget.attrs['placeholder'] = "Ingresar numero de Manzana"
        self.fields['manzana'].widget.attrs['max'] = "500000"
        self.fields['manzana'].widget.attrs['min'] = "1"
        self.fields['sector'].widget.attrs['placeholder'] = "Ingresar numero de Sector"
        self.fields['sector'].widget.attrs['max'] = "500000"
        self.fields['sector'].widget.attrs['min'] = "1"
        self.fields['domicilio'].widget.attrs['title'] = "Ingresar Domicilio ej calle 11111"
        self.fields['domicilio'].widget.attrs['placeholder'] = "Ingresar Domicilio ej calle 1111"
        self.fields['domicilio'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z ]{3,50} [0-9]{2,5}$"
        self.fields['propietario'].widget.attrs['placeholder'] = "Ingresar Dni de propietario"
        self.fields['propietario'].widget.attrs['max'] = "99999999"
        self.fields['propietario'].widget.attrs['min'] = "9999999"
        #-------------------------------------------------------------------------------------


    def save(self, commit=True, propietario=None):
        tramite = super(FormularioIniciarTramite, self).save(commit=False)
        if propietario is not None:
            tramite.propietario = propietario
        if commit:
            tramite.save()
        return tramite
