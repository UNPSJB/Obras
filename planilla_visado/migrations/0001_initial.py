# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ColumnaDeVisado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Doc_Balance_Superficie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Elemento_Balance_Superficie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='FilaDeVisado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ItemDeVisado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activo', models.BooleanField(default=True)),
                ('columna_de_visado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planilla_visado.ColumnaDeVisado')),
                ('fila_de_visado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planilla_visado.FilaDeVisado')),
            ],
            options={
                'ordering': ['columna_de_visado__nombre', 'fila_de_visado__nombre'],
            },
        ),
        migrations.CreateModel(
            name='PlanillaDeVisado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('items', models.ManyToManyField(related_name='planillas', to='planilla_visado.ItemDeVisado')),
            ],
        ),
        migrations.CreateModel(
            name='PlanillaLocales',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('planillaLocales', models.CharField(max_length=2)),
            ],
        ),
        migrations.AddField(
            model_name='filadevisado',
            name='items',
            field=models.ManyToManyField(related_name='items', through='planilla_visado.ItemDeVisado', to='planilla_visado.ColumnaDeVisado'),
        ),
    ]
