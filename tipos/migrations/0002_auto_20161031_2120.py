# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-31 21:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tipos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipoobra',
            name='nombre',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]