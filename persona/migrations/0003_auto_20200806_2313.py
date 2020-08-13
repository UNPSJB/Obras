# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2020-08-06 23:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0002_propietario_estilo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profesional',
            name='matricula',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='profesional',
            name='profesion',
            field=models.CharField(choices=[('Ingeniero Civil', 'Ingeniero Civil'), ('Arquitecto', 'Arquitecto'), ('Maestro Mayor de Obra', 'Maestro Mayor de Obra')], max_length=21),
        ),
    ]