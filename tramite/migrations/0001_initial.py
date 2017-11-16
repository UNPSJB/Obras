# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-16 22:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('planilla_visado', '0001_initial'),
        ('persona', '0001_initial'),
        ('planilla_inspeccion', '0001_initial'),
        ('tipos', '0001_initial'),
        ('pago', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.PositiveSmallIntegerField(choices=[(0, 'Estado'), (1, b'iniciado'), (2, b'aceptado'), (3, b'visado'), (4, b'corregido'), (5, b'agendado'), (7, b'inspeccionado'), (9, b'finalizado'), (6, b'coninspeccion'), (8, b'finalobrasolicitado')])),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'get_latest_by': 'timestamp',
            },
        ),
        migrations.CreateModel(
            name='Tramite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medidas', models.IntegerField()),
                ('domicilio', models.CharField(blank=True, max_length=50)),
                ('parcela', models.CharField(max_length=20)),
                ('circunscripcion', models.CharField(max_length=20)),
                ('manzana', models.CharField(max_length=20)),
                ('sector', models.CharField(max_length=20)),
                ('monto_a_pagar', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('monto_pagado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('pago', models.ForeignKey(blank=True, default=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pago.Pago')),
                ('planillaInspeccion', models.ForeignKey(default=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='planilla_inspeccion.PlanillaDeInspeccion')),
                ('planillaVisado', models.ForeignKey(default=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='planilla_visado.PlanillaDeVisado')),
                ('profesional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persona.Profesional')),
                ('propietario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='persona.Propietario')),
                ('tipo_obra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tipos.TipoObra')),
            ],
        ),
        migrations.CreateModel(
            name='Aceptado',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tramite.Estado')),
            ],
            bases=('tramite.estado',),
        ),
        migrations.CreateModel(
            name='Agendado',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tramite.Estado')),
                ('fecha', models.DateTimeField()),
                ('inspector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=('tramite.estado',),
        ),
        migrations.CreateModel(
            name='ConInspeccion',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tramite.Estado')),
                ('inspector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=('tramite.estado',),
        ),
        migrations.CreateModel(
            name='Corregido',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tramite.Estado')),
                ('observacion', models.CharField(blank=True, default='En este momento no se poseen observaciones sobre el tramite', max_length=100, null=True)),
            ],
            bases=('tramite.estado',),
        ),
        migrations.CreateModel(
            name='Finalizado',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tramite.Estado')),
            ],
            bases=('tramite.estado',),
        ),
        migrations.CreateModel(
            name='FinalObraSolicitado',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tramite.Estado')),
                ('final_obra_total', models.BooleanField()),
            ],
            bases=('tramite.estado',),
        ),
        migrations.CreateModel(
            name='Iniciado',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tramite.Estado')),
                ('observacion', models.CharField(blank=True, default='En este momento no se poseen observaciones sobre el tramite', max_length=100)),
            ],
            bases=('tramite.estado',),
        ),
        migrations.CreateModel(
            name='Inspeccionado',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tramite.Estado')),
            ],
            bases=('tramite.estado',),
        ),
        migrations.CreateModel(
            name='Visado',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tramite.Estado')),
            ],
            bases=('tramite.estado',),
        ),
        migrations.AddField(
            model_name='estado',
            name='tramite',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estados', to='tramite.Tramite'),
        ),
        migrations.AddField(
            model_name='estado',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
