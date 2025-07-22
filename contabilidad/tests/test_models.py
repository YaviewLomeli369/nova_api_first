import pytest
from django.core.exceptions import ValidationError
from contabilidad.models import AsientoContable

@pytest.mark.django_db
def test_no_modificar_conciliado(empresa, usuario):
    asiento = AsientoContable.objects.create(
        fecha="2025-07-21",
        empresa=empresa,
        usuario=usuario,
        conciliado=True,
        concepto="Concepto de prueba"
    )
    with pytest.raises(ValidationError):
        asiento.conciliado = True
        asiento.full_clean()  # dispara validaciones