# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2020-09-14 20:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planilla_visado', '0011_auto_20200914_0300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemdevisado',
            name='enUso',
        ),
    ]
