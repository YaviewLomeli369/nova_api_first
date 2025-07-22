import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from accounts.models import Usuario
from contabilidad.models import CuentaContable, AsientoContable, DetalleAsiento
from core.models import Empresa
from datetime import date


@pytest.fixture
def setup_contabilidad(db):
    empresa = Empresa.objects.create(nombre="Nova Corp")
    usuario = Usuario.objects.create_user(
        username="testuser", password="1234", empresa=empresa
    )

    cuenta_activo = CuentaContable.objects.create(
        empresa=empresa, codigo="1001", nombre="Caja", clasificacion="activo"
    )
    cuenta_ingreso = CuentaContable.objects.create(
        empresa=empresa, codigo="4001", nombre="Ventas", clasificacion="ingreso"
    )

    asiento = AsientoContable.objects.create(
        empresa=empresa, fecha=date(2025, 7, 1), concepto="Venta inicial", usuario=usuario
    )

    DetalleAsiento.objects.create(
        asiento=asiento, cuenta_contable=cuenta_activo, debe=1000, haber=0, descripcion="Ingreso en caja"
    )
    DetalleAsiento.objects.create(
        asiento=asiento, cuenta_contable=cuenta_ingreso, debe=0, haber=1000, descripcion="Venta realizada"
    )

    return usuario


@pytest.mark.django_db
def test_journal_report(setup_contabilidad):
    client = APIClient()
    client.force_authenticate(user=setup_contabilidad)

    url = reverse('reportes-contables') + '?tipo=journal'
    response = client.get(url)

    assert response.status_code == 200
    assert 'libro_diario' in response.data
    assert isinstance(response.data['libro_diario'], list)


@pytest.mark.django_db
def test_trial_balance_report(setup_contabilidad):
    client = APIClient()
    client.force_authenticate(user=setup_contabilidad)

    url = reverse('reportes-contables') + '?tipo=trial_balance'
    response = client.get(url)

    assert response.status_code == 200
    assert 'balance_comprobacion' in response.data
    assert isinstance(response.data['balance_comprobacion'], list)


@pytest.mark.django_db
def test_income_statement_report(setup_contabilidad):
    client = APIClient()
    client.force_authenticate(user=setup_contabilidad)

    url = reverse('reportes-contables') + '?tipo=income_statement'
    response = client.get(url)

    assert response.status_code == 200
    assert 'estado_resultados' in response.data
    assert 'totales' in response.data


@pytest.mark.django_db
def test_balance_sheet_report(setup_contabilidad):
    client = APIClient()
    client.force_authenticate(user=setup_contabilidad)

    url = reverse('reportes-contables') + '?tipo=balance_sheet'
    response = client.get(url)

    assert response.status_code == 200
    assert 'balance_general' in response.data
    assert 'totales' in response.data
