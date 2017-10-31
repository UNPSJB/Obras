from crispy_forms.helper import FormHelper
from django import forms
from django.forms import ValidationError
from crispy_forms.layout import Submit, Field

from .models import *

# class FormularioTipoCategoriaInspeccion(forms.ModelForm):
#     NAME = 'tipo_cat_inspeccicon_form'
#     SUBMIT = 'tipo_cat_inspeccion_submit'
#
#     class Meta:
#         model = TipoCategoriaInspeccion
#         fields = ('nombre',)
#
#     def __init__(self, *args, **kwargs):
#         super(FormularioTipoCategoriaInspeccion, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         # self.helper.form_class = 'form-horizontal'
#         self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
#         self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar descripcion de categoria"
#
#     def clean_descripcion(self):
#         descripcion = self.cleaned_data['descripcion']
#         cargados = TipoCategoriaInspeccion.objects.filter(nombre__icontains=descripcion)
#         if cargados.exists():
#             raise ValidationError("Ya existe {}".format(cargados.first().descripcion))
#         return descripcion

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

class FormularioDocumentoTecnicoInspeccion(forms.ModelForm):
    NAME = 'doc_tecnico_inspeccion_form'
    SUBMIT = 'doc_tecnico_inspeccion_submit'

    class Meta:
        model = DocumentoTecnicoInspeccion
        fields = ('nombre','descripcion','detalles')

    def __init__(self, *args, **kwargs):
        super(FormularioDocumentoTecnicoInspeccion, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar nombre"
        self.fields['descripcion'].widget.attrs['placeholder'] = "Ingresar Descripcion"
        self.fields['detalles'].widget.attrs['placeholder'] = "Ingresar Detalles"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        cargados = DocumentoTecnicoInspeccion.objects.filter(nombre__icontains=nombre)
        if cargados.exists():
            raise ValidationError("Ya existe {}".format(cargados.first().nombre))
        return nombre