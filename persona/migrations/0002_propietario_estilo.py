# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-07-14 17:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='propietario',
            name='estilo',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
