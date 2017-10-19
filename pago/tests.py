# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from .models import Pago,Cuota, Cancelacion, Cancelada

# Create your tests here.
from django.test import TestCase

class PermisoEstadosTests(TestCase):
    def setUp(self):
        self.cuota = Cuota.new(1)

    def test_permiso_iniciado(self):
        estado = self.cuota.estado()
        self.assertTrue(isinstance(estado, Cancelacion))
        self.assertEqual(Cuota.objects.en_estado(Cancelacion).count(), 1)
