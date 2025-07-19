# compras/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from accounts.models import Usuario, Empresa
from compras.models import Compra, DetalleCompra
from inventario.models import Producto
from datetime import date

class CompraTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.empresa = Empresa.objects.create(nombre="Empresa Test")
        self.usuario = Usuario.objects.create_user(username="user1", password="pass123", empresa=self.empresa)
        self.producto1 = Producto.objects.create(nombre="Producto 1", activo=True)
        self.producto2 = Producto.objects.create(nombre="Producto 2", activo=True)

        self.client.force_authenticate(user=self.usuario)

    def test_crear_compra_con_detalles_y_total(self):
        url = reverse('compra-list')  # O el nombre correcto de tu ruta
        data = {
            "proveedor": 1,  # crea un proveedor antes o usa uno válido
            "detalles": [
                {"producto": self.producto1.id, "cantidad": 10, "precio_unitario": "5.00"},
                {"producto": self.producto2.id, "cantidad": 2, "precio_unitario": "20.00"}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['total'], '90.00')  # 10*5 + 2*20

    def test_actualizar_compra_y_recalcular_total(self):
        compra = Compra.objects.create(
            empresa=self.empresa,
            proveedor_id=1,  # igual, un proveedor válido
            usuario=self.usuario,
            total=0
        )
        DetalleCompra.objects.create(compra=compra, producto=self.producto1, cantidad=1, precio_unitario=10)
        url = reverse('compra-detail', args=[compra.id])

        data = {
            "detalles": [
                {"producto": self.producto1.id, "cantidad": 3, "precio_unitario": "15.00"}
            ],
            "estado": "pendiente"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], '45.00')  # 3*15

    def test_subtotal_detalle(self):
        compra = Compra.objects.create(empresa=self.empresa, proveedor_id=1, usuario=self.usuario, total=0)
        detalle = DetalleCompra.objects.create(compra=compra, producto=self.producto1, cantidad=4, precio_unitario=7.5)
        self.assertEqual(detalle.subtotal, 30.0)
