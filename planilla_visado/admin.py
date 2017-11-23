# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import FilaDeVisado, PlanillaDeVisado, ColumnaDeVisado, ItemDeVisado, Elemento_Balance_Superficie

# Register your models here.

admin.site.register(FilaDeVisado)
admin.site.register(PlanillaDeVisado)
admin.site.register(ColumnaDeVisado)
admin.site.register(ItemDeVisado)
admin.site.register(Elemento_Balance_Superficie)