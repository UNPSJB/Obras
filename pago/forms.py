#from pago.models import *
from crispy_forms.helper import FormHelper
from django import forms
from django.forms import ValidationError
from crispy_forms.layout import Submit, Field

from .models import *


class FormularioTipoPago(forms.ModelForm):
    NAME = 'tipo_pago_form'
    SUBMIT = 'tipo_de_pago_submit'

    class Meta:
        model = Tipo_Pago
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioTipoPago, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = Tipo_Pago.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioPago(forms.ModelForm):
    NAME = 'pago_form'
    SUBMIT = 'pago_submit'

    class Meta:
        model = Pago
        fields = (
            'tipoPago',
            'cuota',
            'valor',
            'cantidadCuotas',
            'fecha',
        )

    def __init__(self, *args, **kwargs):
        super(FormularioPago, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.add_input(Submit(self.SUBMIT, 'Guardar Tramite'))
       # self.helper.form_tag = False
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['tipoPago'].widget.attrs['placeholder'] = "Ingresar Tipo de Pago"
        self.fields['cuota'].widget.attrs['placeholder'] = "cuota"
        self.fields['valor'].widget.attrs['placeholder'] = "Importe"
        self.fields['cantidadCuotas'].widget.attrs['placeholder'] = "Ingresar cantidad de cuotas"
        self.fields['fecha'].widget.attrs['placeholder'] = "Ingresar fecha"

        # -------------------------------------------------------------------------------------

    def save(self, commit=True, pago=None):
        FormularioPago, self.save(commit=False)
        pago.save()
        return pago


class FormularioCuota(forms.ModelForm):
    NAME = 'cuota_form'
    SUBMIT = 'cuota_submit'

    class Meta:
        model = Cuota
        fields = (
            'fechaVencimiento',
            'fechaPago',
            'monto',
        )

    def __init__(self, *args, **kwargs):
        super(FormularioCuota, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.add_input(Submit(self.SUBMIT, 'Guardar Tramite'))
        self.helper.form_tag = False
        self.fields['fechaVencimiento'].widget.attrs['placeholder'] = "fecha de vencimiento"
        self.fields['fechaPago'].widget.attrs['placeholder'] = "fecha de pago"
        self.fields['monto'].widget.attrs['placeholder'] = "monto"

