from django import forms
from django.forms import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import *

class FormularioIniciarTramite(forms.ModelForm):
    NAME = 'tramite_form'
    SUBMIT = 'tramite_submit'
    propietario = forms.CharField()

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
        self.fields['tipo_obra'].widget.attrs['placeholder'] = "Ingresar Tipo de Obra"
        self.fields['medidas'].widget.attrs['placeholder'] = "Ingresar Medidas en m2"
        self.fields['profesional'].widget.attrs['placeholder'] = "Ingresar DNI del Profesional"
        #-------------------------------------------------------------------------------------        
        self.fields['parcela'].widget.attrs['placeholder'] = "Datos catastrales"
        self.fields['circunscripcion'].widget.attrs['placeholder'] = "Datos catastrales"
        self.fields['manzana'].widget.attrs['placeholder'] = "Datos catastrales"
        self.fields['sector'].widget.attrs['placeholder'] = "Datos catastrales"
        #-------------------------------------------------------------------------------------


    def save(self, commit=True, propietario=None):
        tramite = super(FormularioIniciarTramite, self).save(commit=False)
        if propietario is not None:
            tramite.propietario = propietario
        if commit:
            tramite.save()
        return tramite
