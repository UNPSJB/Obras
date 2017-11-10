from crispy_forms.helper import FormHelper
from django import forms
from django.forms import ValidationError
from crispy_forms.layout import Submit, Field

from .models import *

class FormularioCategoriaInspeccion(forms.ModelForm):
    NAME = 'cat_inspeccion_form'
    SUBMIT = 'cat_inspeccion_submit'

    class Meta:
        model = CategoriaInspeccion
        fields = ('nombre','descripcion','tipo')

    def __init__(self, *args, **kwargs):
        super(FormularioCategoriaInspeccion, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar nombre"
        self.fields['descripcion'].widget.attrs['placeholder'] = "Ingresar Descripcion"
        self.fields['tipo'].widget.attrs['placeholder'] = "Ingresar tipo"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = CategoriaInspeccion.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioItemInspeccion(forms.ModelForm):
    NAME = 'item_inspeccion_form'
    SUBMIT = 'item_inspeccion_submit'

    class Meta:
        model = ItemInspeccion
        fields = ('nombre', )
        fields = ('nombre','categorias')

    def __init__(self, *args, **kwargs):
        super(FormularioItemInspeccion, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar nombre"
        self.fields['categorias'].widget.attrs['placeholder'] = "Ingresar Categoria"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = ItemInspeccion.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

class FormularioDetalleItem(forms.ModelForm):
    NAME = 'detalle_item_inspeccion_form'
    SUBMIT = 'detalle_item_inspeccion_submit'

    class Meta:
        model = DetalleDeItemInspeccion
        fields = ('item_inspeccion','categoria_inspeccion','nombre')

    def __init__(self, *args, **kwargs):
        super(FormularioDetalleItem, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['item_inspeccion'].widget.attrs['placeholder'] = "Ingresar item inspeccion"
        self.fields['categoria_inspeccion'].widget.attrs['placeholder'] = "Ingresar Categoria"
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar nombre"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = ItemInspeccion.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre

 # class FormularioDocumentoTecnicoInspeccion(forms.ModelForm):
 #     NAME = 'doc_tecnico_inspeccion_form'
 #     SUBMIT = 'doc_tecnico_inspeccion_submit'
 #
 #     class Meta:
 #         model = DocumentoTecnicoInspeccion
 #         fields = ('nombre','descripcion','detalles')
 #
 #     def __init__(self, *args, **kwargs):
 #         super(FormularioDocumentoTecnicoInspeccion, self).__init__(*args, **kwargs)
 #         self.helper = FormHelper()
 #         # self.helper.form_class = 'form-horizontal'
 #         self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
 #         self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar nombre"
 #         self.fields['descripcion'].widget.attrs['placeholder'] = "Ingresar Descripcion"
 #         self.fields['detalles'].widget.attrs['placeholder'] = "Ingresar Detalles"
 #
 #     def clean_nombre(self):
 #         nombre = self.cleaned_data['nombre']
 #         cargados = DocumentoTecnicoInspeccion.objects.filter(nombre__icontains=nombre)
 #         if cargados.exists():
 #             raise ValidationError("Ya existe {}".format(cargados.first().nombre))
 #         return nombre

from django.utils.safestring import mark_safe

class HorizontalCheckboxRenderer(forms.CheckboxSelectMultiple):
    def __init__(self, *args, **kwargs):
        super(HorizontalCheckboxRenderer, self).__init__(*args, **kwargs)
        print("index")
        css_style = 'style="display: inline-block; margin-right: 10px;"'

        self.renderer.inner_html = '<li ' + css_style + '>{choice_value}{sub_widgets}</li>'

def PlanillaDeInspeccionFormFactory(categorias, items):
    CAT_CHOICES = []
    for categoria in categorias:
        CAT_CHOICES.append((categoria.pk, categoria.nombre))
    fields = {
        'NAME': 'planilla_de_inspeccion_form',
        'SUBMIT': 'planilla_de_inspeccion_submit'
    }

    for item in items:
        detalle = DetalleDeItemInspeccion.objects.filter(item_de_inspeccion=item)
        initial = [str(i.categoria.pk) for i in items]
        fields["item-" + str(categoria.pk)] = forms.MultipleChoiceField(
            label=categoria.nombre,
            required=False,
            initial=initial,
            widget=forms.CheckboxSelectMultiple(),
            choices=CAT_CHOICES,
        )

    class PlanillaDeInspeccionMixin(forms.Form):
        NAME = 'planilla_de_inspeccion_form'
        SUBMIT = 'planilla_de_inspeccion_submit'

        def save(self, *args, **kwargs):
            datos = self.cleaned_data
            for field, values in datos.detalles():
                pk = int(field.split("-")[1])
                item = filter(lambda f: f.pk == pk, items).pop()
                cats = filter(lambda c: str(c.pk) in values, categorias)
                DetalleDeItemInspeccion.objects.filter(item_de_inspeccion=item).delete()
                item.relacionar_con_columnas(cats)
            print datos
            return

        def __init__(self, *args, **kwargs):
            super(PlanillaDeInspeccionMixin, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            # self.helper.form_class = 'form-horizontal'
            self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))

    return type("PlanillaDeInspeccionForm", (PlanillaDeInspeccionMixin, ), fields)