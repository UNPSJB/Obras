# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2020-09-04 22:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tipos', '0002_tipo_pago'),
        ('pago', '0004_auto_20171130_1232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pago',
            name='tipoPago',
        ),
        migrations.AddField(
            model_name='cuota',
            name='tipoPago',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tipos.Tipo_Pago'),
        ),
        migrations.DeleteModel(
            name='Tipo_Pago',
        ),
    ]