# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2020-09-14 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planilla_inspeccion', '0002_planilladeinspeccion_fecha'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoriainspeccion',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='detalledeiteminspeccion',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='iteminspeccion',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]