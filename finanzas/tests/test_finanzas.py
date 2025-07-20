
from django.core.exceptions import ValidationError

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from accounts.models import Usuario
from core.models import Empresa
from compras.models import Proveedor, Compra
from ventas.models import Venta, Cliente
from finanzas.models import CuentaPorCobrar, CuentaPorPagar, Pago, MetodoPagoChoices
from decimal import Decimal

class FinanzasTests(TestCase):
    def setUp(self):
        # Crear una empresa sin especificar el ID (se asignará automáticamente)
        self.empresa = Empresa.objects.create(
            nombre="Mi Empresa",
            razon_social="Razón Social",
            rfc="ABC1234567890",
            domicilio_fiscal="Calle Ficticia 123",
            regimen_fiscal="General"
        )

        self.fecha_venc = timezone.now().date() + timedelta(days=7)

        # Crear un usuario de prueba usando el modelo 'Usuario' personalizado
        self.usuario = Usuario.objects.create_user(
            username='testuser', 
            password='testpassword', 
            empresa=self.empresa
        )

        # Crear un proveedor antes de la compra
        self.proveedor = Proveedor.objects.create(
            nombre="Proveedor de prueba",
            empresa=self.empresa
        )

        # Crear un cliente antes de la venta (soluciona el problema de clave foránea)
        self.cliente = Cliente.objects.create(
            nombre="Cliente de prueba",
            empresa=self.empresa
        )


        # Simulamos venta y compra con el usuario asignado
        self.venta = Venta.objects.create(cliente_id=self.cliente.id, total=1000, empresa=self.empresa, usuario=self.usuario)
        self.compra = Compra.objects.create(proveedor=self.proveedor, total=500, empresa=self.empresa)

        # Cuentas
        self.cxc = CuentaPorCobrar.objects.create(
            empresa=self.empresa, venta=self.venta, monto=1000, fecha_vencimiento=self.fecha_venc
        )
        self.cxp = CuentaPorPagar.objects.create(
            empresa=self.empresa, compra=self.compra, monto=500, fecha_vencimiento=self.fecha_venc
        )

    def test_crear_cuenta_por_pagar(self):
        self.assertEqual(self.cxp.monto, Decimal('500.00'))
        self.assertEqual(self.cxp.estado, "PENDIENTE")

    def test_crear_cuenta_por_cobrar(self):
        self.assertEqual(self.cxc.monto, Decimal('1000.00'))
        self.assertEqual(self.cxc.estado, "PENDIENTE")

    def test_pago_parcial_cuenta_por_cobrar(self):
        Pago.objects.create(cuenta_cobrar=self.cxc, monto=400, fecha=timezone.now(), metodo_pago=MetodoPagoChoices.EFECTIVO, empresa=self.empresa)
        self.cxc.refresh_from_db()
        self.assertEqual(self.cxc.estado, "PENDIENTE")
        self.assertEqual(self.cxc.saldo_pendiente, Decimal('600.00'))

    def test_pago_total_cuenta_por_pagar(self):
        Pago.objects.create(cuenta_pagar=self.cxp, monto=500, fecha=timezone.now(), metodo_pago=MetodoPagoChoices.TRANSFERENCIA, empresa=self.empresa)
        self.cxp.refresh_from_db()
        self.assertEqual(self.cxp.estado, "PAGADO")
        self.assertEqual(self.cxp.saldo_pendiente, Decimal('0.00'))


    def test_pago_excesivo_lanza_error(self):
        # Intentamos crear un pago cuyo monto excede el saldo pendiente
        with self.assertRaises(ValidationError):  # Aseguramos que se lance una ValidationError
            pago = Pago.objects.create(
                cuenta_pagar=self.cxp,
                monto=600,
                fecha=timezone.now(),
                metodo_pago=MetodoPagoChoices.CHEQUE,
                empresa=self.empresa
            )
            pago.full_clean()  # Esto ejecuta la validación manualmente antes de guardar

