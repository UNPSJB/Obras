# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import CategoriaInspeccion, ItemInspeccion, DetalleDeItemInspeccion

# Register your models here.
admin.site.register(CategoriaInspeccion)
admin.site.register(ItemInspeccion)
admin.site.register(DetalleDeItemInspeccion)
#admin.site.register(DocumentoTecnicoInspeccion)
