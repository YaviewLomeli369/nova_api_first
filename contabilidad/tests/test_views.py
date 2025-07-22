import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from contabilidad.models import AsientoContable, DetalleAsiento

@pytest.mark.django_db
def test_list_asientos_autenticado(usuario, empresa, asiento_creado):
    client = APIClient()
    client.force_authenticate(usuario)
    url = reverse('asiento-list')
    response = client.get(url)
    assert response.status_code == 200
    # Debe mostrar solo asientos de la empresa del usuario
    for item in response.data['results']:
        assert item['empresa'] == empresa.id

@pytest.mark.django_db
def test_update_bloqueado_si_conciliado(usuario, asiento_conciliado):
    client = APIClient()
    client.force_authenticate(usuario)
    url = reverse('asiento-detail', args=[asiento_conciliado.id])
    response = client.put(url, {'fecha': '2025-07-30'})
    assert response.status_code == 400
    assert 'No se puede modificar un asiento contable ya conciliado.' in response.data['detail']

@pytest.mark.django_db
def test_accion_conciliar(usuario, asiento_creado, cuenta_contable_1, cuenta_contable_2):
    DetalleAsiento.objects.create(asiento=asiento_creado, cuenta_contable=cuenta_contable_1, debe=100, haber=0)
    DetalleAsiento.objects.create(asiento=asiento_creado, cuenta_contable=cuenta_contable_2, debe=0, haber=100)

    client = APIClient()
    client.force_authenticate(usuario)
    url = reverse('asiento-conciliar', args=[asiento_creado.id])
    response = client.patch(url)
    assert response.status_code == 200
    assert response.data['detail'] == "Asiento conciliado correctamente."
    
# @pytest.mark.django_db
# def test_accion_conciliar(usuario, asiento_creado):
#     client = APIClient()
#     client.force_authenticate(usuario)
#     url = reverse('asiento-conciliar', args=[asiento_creado.id])
#     response = client.patch(url)
#     assert response.status_code == 200
#     assert response.data['detail'] == "Asiento conciliado correctamente."

@pytest.mark.django_db
def test_accion_conciliar_ya_conciliado(usuario, asiento_conciliado):
    client = APIClient()
    client.force_authenticate(usuario)
    url = reverse('asiento-conciliar', args=[asiento_conciliado.id])
    response = client.patch(url)
    assert response.status_code == 400
    assert response.data['detail'] == "Este asiento ya está conciliado."
