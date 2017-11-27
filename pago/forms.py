#from pago.models import *
from crispy_forms.helper import FormHelper
from django import forms
from django.forms import ValidationError
from crispy_forms.layout import Submit, Field

from .models import *

class FormularioCuota(forms.ModelForm):
    NAME = 'cuota_form'
    SUBMIT = 'cuota_submit'

    class Meta:
        model = Cuota
        fields = (
            'fechaVencimiento',
            'fechaPago',
            'monto',
            'numeroCuota',
            'pago',
        )
        labels={
            'fechaVencimiento': "Fecha Vencimiento",
            'monto': "Monto",
            'numeroCuota':"Numero de Cuota",
        }
        widgets = {
            'fechaVencimiento': forms.DateInput(attrs={'class': 'datepicker'}),
            'monto': forms.TextInput(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(FormularioCuota, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['fechaVencimiento'].widget.attrs['placeholder'] = "fecha de vencimiento"
        self.fields['fechaPago'].widget.attrs['placeholder'] = "fecha de pago"
        self.fields['fechaPago'].required = False
        self.fields['monto'].widget.attrs['placeholder'] = "monto"
        self.fields['numeroCuota'].widget.attrs['placeholder'] = "cuota"
        self.fields['pago'].widget.attrs['placeholder'] = "ingresar pago"

class FormularioTipoPago(forms.ModelForm):
    NAME = 'tipo_pago_form'
    SUBMIT = 'tipo_de_pago_submit'

    class Meta:
        model = Tipo_Pago
        fields = ('nombre',)
        cuota = forms.ChoiceField(choices=Pago.CUOTAS)

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
        fields = ('tipoPago','cantidadCuotas',)
    def __init__(self, *args, **kwargs):
        super(FormularioPago, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('pago_submit', 'Guardar'))
        self.fields['tipoPago'].widget.attrs['placeholder'] = "Ingresar Tipo de Pago"
        self.fields['cantidadCuotas'].widget.attrs['placeholder'] = "Ingresar cantidad de cuotas"

    def clean_cantidadCuotas(self):
        cantidadCuotas = self.cleaned_data['cantidadCuotas']
        if cantidadCuotas is None:
            raise ValidationError("Seleccione el numero de cuotas ")
        return cantidadCuotas

    def clean_tipoPago(self):
        tipoPago = self.cleaned_data['tipoPago']
        if tipoPago is None:
            raise ValidationError("Seleccione un tipo de Pago")
        return tipoPago




