# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2019-12-22 23:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planilla_visado', '0006_planilladevisado_fecha'),
    ]

    operations = [
        migrations.RenameField(
            model_name='planilladevisado',
            old_name='observacion',
            new_name='observaciones',
        ),
    ]
