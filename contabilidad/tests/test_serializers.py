import pytest
from contabilidad.serializers.asiento_contable import AsientoContableSerializer
from contabilidad.models import AsientoContable, DetalleAsiento

@pytest.mark.django_db
def test_serializer_valido_creacion(asiento_data, empresa, usuario):
    # asiento_data debe ser un dict válido para crear asiento
    serializer = AsientoContableSerializer(data=asiento_data, context={'empresa': empresa})
    assert serializer.is_valid(), serializer.errors
    asiento = serializer.save()
    assert asiento.empresa == empresa

@pytest.mark.django_db
def test_serializer_error_faltan_campos():
    serializer = AsientoContableSerializer(data={})
    assert not serializer.is_valid()
    assert 'fecha' in serializer.errors or 'detalles' in serializer.errors

@pytest.mark.django_db
def test_serializer_no_modificar_conciliado(asiento_conciliado, cuenta_contable_1, cuenta_contable_2):
    # Agregamos detalles válidos
    DetalleAsiento.objects.create(asiento=asiento_conciliado, cuenta_contable=cuenta_contable_1, debe=100, haber=0)
    DetalleAsiento.objects.create(asiento=asiento_conciliado, cuenta_contable=cuenta_contable_2, debe=0, haber=100)

    # ⚠️ Refrescamos el objeto desde la BD para que tenga los detalles correctamente cargados
    asiento_conciliado.refresh_from_db()

    serializer = AsientoContableSerializer(asiento_conciliado, data={'fecha': '2025-07-22'}, partial=True)
    assert not serializer.is_valid()
    assert 'No se puede modificar un asiento contable ya conciliado.' in str(serializer.errors)

# @pytest.mark.django_db
# def test_serializer_no_modificar_conciliado(asiento_conciliado):
#     serializer = AsientoContableSerializer(asiento_conciliado, data={'fecha': '2025-07-22'}, partial=True)
#     assert not serializer.is_valid()
#     assert 'No se puede modificar un asiento contable ya conciliado.' in str(serializer.errors)
