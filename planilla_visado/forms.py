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
        fields = ('nombre','descripcion')

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
        fields = ('nombre','descripcion')

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

class FormularioColumnaVisado(forms.ModelForm):
    NAME = 'columna_visado_form'
    SUBMIT = 'columna_visado_submit'

    class Meta:
        model = ColumnaDeVisado
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioColumnaVisado, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre de columna"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = ColumnaDeVisado.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioFilaVisado(forms.ModelForm):
    NAME = 'fila_visado_form'
    SUBMIT = 'fila_visado_submit'

    class Meta:
        model = FilaDeVisado
        fields = ('nombre','items')

    def __init__(self, *args, **kwargs):
        super(FormularioFilaVisado, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre de fila"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = FilaDeVisado.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioItemDeVisado(forms.ModelForm):
    NAME = 'item_vista_elementoform'
    SUBMIT = 'item_vista_elemento_submit'

    class Meta:
        model = ItemDeVisado
        fields = ('columna_de_visado','fila_de_visado','activo')

    def __init__(self, *args, **kwargs):
        super(FormularioItemDeVisado, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre de elemento de vista"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = ItemDeVisado.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre
#
# class FormularioPlanillaDeLocales(forms.ModelForm):
#     NAME = 'planilla_de_localesform'
#     SUBMIT = 'planilla_de_locales_submit'
#
#     class Meta:
#         model = PlanillaLocales
#         fields = ('planillaLocales')

