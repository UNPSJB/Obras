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
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"
        self.fields['descripcion'].widget.attrs['placeholder'] = "Ingresar Descripcion"

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
        model = Elemento_Balance_Superficie
        fields = ('nombre','descripcion')

    def __init__(self, *args, **kwargs):
        super(FormularioElementoBalanceSuperficie, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"
        self.fields['descripcion'].widget.attrs['placeholder'] = "Ingresar Descripcion"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = Elemento_Balance_Superficie.objects.filter(nombre__icontains=nombre)
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
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"

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
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioFilaVisado, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = FilaDeVisado.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

from django.utils.safestring import mark_safe

class HorizontalCheckboxRenderer(forms.CheckboxSelectMultiple):
    def __init__(self, *args, **kwargs):
        super(HorizontalCheckboxRenderer, self).__init__(*args, **kwargs)
        print("index")
        css_style = 'style="display: inline-block; margin-right: 10px;"'

        self.renderer.inner_html = '<li ' + css_style + '>{choice_value}{sub_widgets}</li>'

def PlanillaDeVisadoFormFactory(filas, columnas):
    COL_CHOICES = []
    for columna in columnas:
        COL_CHOICES.append((columna.pk, columna.nombre))
    fields = {
        'NAME': 'planilla_de_visado_form',
        'SUBMIT': 'planilla_de_visado_submit'
    }
    for index, fila in enumerate(filas):
        fields["fila" + str(index)] = forms.MultipleChoiceField(
            label=fila.nombre,
            required=False,
            widget= forms.CheckboxSelectMultiple(attrs={
                'display': 'inline-block'
            }),
            choices=COL_CHOICES,
        )
    class PlanillaDeVisadoMixin(forms.Form):
        NAME = 'planilla_de_visado_form'
        SUBMIT = 'planilla_de_visado_submit'
     
        def save(self, *args, **kwargs):
            print(self.cleaned_data)
            return "pepe"
    
        def __init__(self, *args, **kwargs):
            super(PlanillaDeVisadoMixin, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            # self.helper.form_class = 'form-horizontal'
            self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))

    return type("PlanillaDeVisadoForm", (PlanillaDeVisadoMixin, ), fields)

class FormularioItemDeVisado(forms.ModelForm):
    NAME = 'item_visado_form'
    SUBMIT = 'item_visado_submit'

    class Meta:
        model = ItemDeVisado
        fields = ('columna_de_visado','fila_de_visado','activo')

    def __init__(self, *args, **kwargs):
        super(FormularioItemDeVisado, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['columna_de_visado'].widget.attrs['placeholder'] = "Ingresar columna"
        self.fields['fila_de_visado'].widget.attrs['placeholder'] = "Ingresar fila"
        self.fields['activo'].widget.attrs['placeholder'] = "Ingresar si es activo"

    def clean_nombre(self): #aca iria validacion de columna valida y fila valida
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

