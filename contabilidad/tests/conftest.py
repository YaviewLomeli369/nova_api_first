import pytest
from contabilidad.models import AsientoContable, CuentaContable
from accounts.models import Usuario
from core.models import Empresa

@pytest.fixture
def empresa(db):
    return Empresa.objects.create(nombre="Empresa Test")

@pytest.fixture
def usuario(db, empresa):
    return Usuario.objects.create(username="user1", empresa=empresa)

@pytest.fixture
def cuenta_contable_1(db, empresa):
    return CuentaContable.objects.create(
        codigo="001",  # código único dentro de la empresa
        nombre="Cuenta 1",
        clasificacion="activo",  # debe estar dentro de las opciones válidas
        empresa=empresa
    )

@pytest.fixture
def cuenta_contable_2(db, empresa):
    return CuentaContable.objects.create(
        codigo="002",  # código único dentro de la empresa
        nombre="Cuenta 2",
        clasificacion="activo",  # debe estar dentro de las opciones válidas
        empresa=empresa
    )    

@pytest.fixture
def asiento_data(empresa, usuario, cuenta_contable_1, cuenta_contable_2):
    return {
        "fecha": "2025-07-21",
        "usuario": usuario.id,
        "concepto": "Concepto de prueba",
        "detalles": [
            {"cuenta_contable": cuenta_contable_1.id, "debe": 100, "haber": 0},
            {"cuenta_contable": cuenta_contable_2.id, "debe": 0, "haber": 100},
        ],
    }

@pytest.fixture
def asiento_creado(db, empresa, usuario):
    return AsientoContable.objects.create(
        fecha="2025-07-21",
        empresa=empresa,
        usuario=usuario,
        conciliado=False,
        concepto="test"
    )

@pytest.fixture
def asiento_conciliado(db, empresa, usuario, cuenta_contable_1, cuenta_contable_2):
    asiento = AsientoContable.objects.create(
        fecha="2025-07-21",
        empresa=empresa,
        usuario=usuario,
        conciliado=True,
        concepto="test"
    )
    # Añadir detalles válidos
    from contabilidad.models import DetalleAsiento
    DetalleAsiento.objects.create(
        asiento=asiento,
        cuenta_contable=cuenta_contable_1,
        debe=100,
        haber=0
    )
    DetalleAsiento.objects.create(
        asiento=asiento,
        cuenta_contable=cuenta_contable_2,
        debe=0,
        haber=100
    )
    return asiento