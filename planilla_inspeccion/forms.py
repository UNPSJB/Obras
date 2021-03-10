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
        categorias = CategoriaInspeccion.objects.filter(nombre=nombre)
        if categorias.exists():
            for c in categorias:
                if c.nombre == nombre and c.activo == 0:
                    return c
            raise ValidationError("Ya existe {}".format(categorias.first().nombre))
        return nombre

class FormularioCategoriaInspeccionModificada(forms.ModelForm):
    NAME = 'cat_inspeccion_modificado_form'
    SUBMIT = 'cat_inspeccion_submit'

    class Meta:
        model = CategoriaInspeccion
        fields = ('nombre','descripcion','tipo')

    def __init__(self, *args, **kwargs):
        super(FormularioCategoriaInspeccionModificada, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar nombre"
        self.fields['descripcion'].widget.attrs['placeholder'] = "Ingresar Descripcion"
        self.fields['tipo'].widget.attrs['placeholder'] = "Ingresar tipo"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        categorias = CategoriaInspeccion.objects.filter(nombre=nombre)
        if categorias.exists():
            raise ValidationError("Ya existe {}".format(categorias.first().nombre))
        return nombre

class FormularioItemInspeccion(forms.ModelForm):
    NAME = 'item_inspeccion_form'
    SUBMIT = 'item_inspeccion_submit'

    class Meta:
        model = ItemInspeccion
        fields = ('nombre', )

    def __init__(self, *args, **kwargs):
        super(FormularioItemInspeccion, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar nombre"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        items = ItemInspeccion.objects.filter(nombre=nombre)
        if items.exists():
            for i in items:
                if i.nombre == nombre and i.activo == 0:
                    return i
            raise ValidationError("Ya existe {}".format(items.first().nombre))
        return nombre

class FormularioItemInspeccionModificado(forms.ModelForm):
    NAME = 'item_inspeccion_modificado_form'
    SUBMIT = 'item_inspeccion_submit'

    class Meta:
        model = ItemInspeccion
        fields = ('nombre', )

    def __init__(self, *args, **kwargs):
        super(FormularioItemInspeccionModificado, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar nombre"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        items = ItemInspeccion.objects.filter(nombre=nombre)
        if items.exists():
            raise ValidationError("Ya existe {}".format(items.first().nombre))
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
        self.fields['item_inspeccion'].queryset = ItemInspeccion.objects.all()
        self.fields['categoria_inspeccion'].queryset = CategoriaInspeccion.objects.all()
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar nombre"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        categoria = self.cleaned_data['categoria_inspeccion']
        item=self.cleaned_data['item_inspeccion']
        detalles = DetalleDeItemInspeccion.objects.filter(nombre=nombre, categoria_inspeccion = categoria,item_inspeccion=item)
        if detalles.exists():
            for d in detalles:
                if d.nombre == nombre and d.activo == 0:
                    return d
            raise ValidationError("Ya existe {}".format(nombre))
        return nombre

class FormularioDetalleItemModificado(forms.ModelForm):
    NAME = 'detalle_item_inspeccion_modificado_form'
    SUBMIT = 'detalle_item_inspeccion_submit'

    class Meta:
        model = DetalleDeItemInspeccion
        fields = ('item_inspeccion','categoria_inspeccion','nombre')

    def __init__(self, *args, **kwargs):
        super(FormularioDetalleItemModificado, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['item_inspeccion'].queryset = ItemInspeccion.objects.all()
        self.fields['categoria_inspeccion'].queryset = CategoriaInspeccion.objects.all()
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar nombre"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        categoria = self.cleaned_data['categoria_inspeccion']
        item = self.cleaned_data['item_inspeccion']
        detalles = DetalleDeItemInspeccion.objects.filter(nombre=nombre, categoria_inspeccion=categoria, item_inspeccion=item)
        print(nombre)
        print(detalles)
        print(categoria)
        if detalles.exists():
            raise ValidationError("Ya existe {}".format(detalles.first().nombre))
        return nombre