from crispy_forms.helper import FormHelper
from django import forms
from django.forms import ValidationError
from crispy_forms.layout import Submit, Field
from planilla_visado.models import *

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
        balance = Doc_Balance_Superficie.objects.filter(nombre__iexact=nombre)
        if balance.exists():
            for b in balance:
                if b.activo == 0 and b.nombre == nombre:
                    return b
            raise ValidationError("Ya existe {}".format(balance.first().nombre))
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
        cargados = Elemento_Balance_Superficie.objects.filter(nombre__iexact=nombre)
        if cargados.exists():
            if cargados.exists():
                for col in cargados:
                    if nombre == col.nombre and col.activo == 0:
                        return col
                raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioElementoBalanceSuperficieModificado(forms.ModelForm):
    NAME = 'elemento_balance_form_modificado'
    SUBMIT = 'elemento_balance_submit'

    class Meta:
        model = Elemento_Balance_Superficie
        fields = ('nombre','descripcion')

    def __init__(self, *args, **kwargs):
        super(FormularioElementoBalanceSuperficieModificado, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"
        self.fields['descripcion'].widget.attrs['placeholder'] = "Ingresar Descripcion"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = Elemento_Balance_Superficie.objects.filter(nombre__iexact=nombre)
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
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre columna"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = ColumnaDeVisado.objects.filter(nombre__iexact=nombre)
        if cargados.exists():
            for col in cargados:
                if nombre== col.nombre and  col.activo == 0:
                    return col
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioColumnaVisadoModificada(forms.ModelForm):
    NAME = 'columna_visado_form_modificada'
    SUBMIT = 'columna_visado_submit'

    class Meta:
        model = ColumnaDeVisado
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioColumnaVisadoModificada, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre columna"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = ColumnaDeVisado.objects.filter(nombre__iexact=nombre)
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
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre fila"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = FilaDeVisado.objects.filter(nombre__iexact=nombre)
        if cargados.exists():
            for col in cargados:
                if nombre == col.nombre and col.activo == 0:
                    return col
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioFilaVisadoModificada(forms.ModelForm):
    NAME = 'fila_visado_form_modificada'
    SUBMIT = 'fila_visado_submit'

    class Meta:
        model = FilaDeVisado
        fields = ('nombre',)

    def __init__(self, *args, **kwargs):
        super(FormularioFilaVisadoModificada, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre fila"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = FilaDeVisado.objects.filter(nombre__iexact=nombre)
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
        if columna.activo == True:
            COL_CHOICES.append((columna.pk, columna.nombre))
        fields = {
            'NAME': 'planilla_de_visado_form',
            'SUBMIT': 'planilla_de_visado_submit'
        }

    for fila in filas:
        if fila.activo == True:
            items = ItemDeVisado.objects.filter(fila_de_visado=fila,activo=True)
            initial = [str(i.columna_de_visado.pk) for i in items]
            fields[str(fila.pk)] = forms.MultipleChoiceField(
                label=fila.nombre,
                required=False,
                initial=initial,
                widget=forms.CheckboxSelectMultiple(),
                choices=COL_CHOICES,
            )

    class PlanillaDeVisadoMixin(forms.Form):
        NAME = 'planilla_de_visado_form'
        SUBMIT = 'planilla_de_visado_submit'
        print("planilla visado mixin")
        def save(self, *args, **kwargs):
            datos = self.cleaned_data
            cols=[]
            lista=[]
            for field, values in datos.items():
                pk = int(field)
                fila = filter(lambda f: f.pk == pk, filas).pop()
                cols = filter(lambda c: str(c.pk) in values, columnas)
                #  ItemDeVisado.objects.filter(fila_de_visado=fila).delete()
                for i in cols:
                    aux={"fila":fila, "columna": i}
                    lista.append(aux)
            fila.relacionar_con_columnas(lista)
                # ItemDeVisado.objects.create(coumna_de_visado=columna, fila_de_visado=fila)
            return

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

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        items = ItemDeVisado.objects.filter(nombre__iexact=nombre)
        if items.exists():
            for i in items:
                if i.activo == 0 and i.nombre == nombre:
                    return i
            raise ValidationError("Ya existe {}".format(items.first().nombre))
        return nombre

