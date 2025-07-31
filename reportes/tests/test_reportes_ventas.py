import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from ventas.models import Venta
from core.models import Empresa
from ventas.models import Cliente
from django.contrib.auth import get_user_model
from datetime import datetime
from decimal import Decimal
from ventas.models import DetalleVenta
from inventario.models import Producto
from django.utils import timezone
from inventario.models import Producto, ClaveSATUnidad, Categoria, ClaveSATProducto


@pytest.mark.django_db
def test_reporte_ventas_agrupado():
    client = APIClient()

    empresa = Empresa.objects.create(nombre="Mi empresa")
    user = get_user_model().objects.create_user(
        username="testuser",
        password="password123",
        empresa=empresa
    )
    user.save()
    client.force_authenticate(user=user)

    cliente = Cliente.objects.create(nombre="Cliente X", empresa=empresa)
    fecha_manual = timezone.make_aware(datetime(2025, 7, 15, 12, 0))

    unidad_medida = ClaveSATUnidad.objects.create(clave="H87", descripcion="Pieza")

    # Crear una ClaveSATProducto que referencia a la unidad creada
    clave_sat_producto = ClaveSATProducto.objects.create(
        clave="01010101",
        descripcion="Producto genérico",
        unidad=unidad_medida
    )


    # Crea o obtiene una Categoria válida para la empresa
    categoria = Categoria.objects.create(empresa=empresa, nombre="Equipos", descripcion="Equipos de oficina")

    producto1 = Producto.objects.create(
        empresa=empresa,
        codigo="PROD-001",
        nombre="Laptop XYZ",
        descripcion="Laptop de alta gama para oficina",
        unidad_medida=unidad_medida,  
        categoria=categoria,
        precio_compra=12000,
        precio_venta=15000,
        stock_minimo=3,
        activo=True,
        clave_sat=clave_sat_producto
    )

    producto2 = Producto.objects.create(
        empresa=empresa,
        codigo="PROD-003",
        nombre="Mouse Inalámbrico",
        descripcion="Mouse inalámbrico para laptop",
        unidad_medida=unidad_medida,  
        categoria=categoria,
        precio_compra=150,
        precio_venta=250,
        stock_minimo=5,
        activo=True,
        clave_sat=clave_sat_producto
    )

    venta1 = Venta.objects.create(
        empresa=empresa,
        cliente=cliente,
        total=Decimal('0.00'),  # opcional, si se calcula después
        estado='COMPLETADA',
        usuario=user,
        fecha=fecha_manual
    )
    # Crear detalles para venta1
    DetalleVenta.objects.create(
        venta=venta1,
        producto_id=1,  # asumiendo producto con id=1 existe
        cantidad=1,
        precio_unitario=Decimal('150.00'),
    )

    venta2 = Venta.objects.create(
        empresa=empresa,
        cliente=cliente,
        total=Decimal('0.00'),
        estado='COMPLETADA',
        usuario=user,
        fecha=fecha_manual
    )
    # Crear detalles para venta2
    DetalleVenta.objects.create(
        venta=venta2,
        producto_id=1,
        cantidad=1,
        precio_unitario=Decimal('250.00'),
    )

    # Si tu lógica calcula el total automáticamente, actualiza total en ventas
    venta1.total = Decimal('150.00')
    venta1.save()
    venta2.total = Decimal('250.00')
    venta2.save()

    url = reverse('reporte-ventas')
    params = {
        'fecha_inicio': datetime(2025, 7, 1).date().isoformat(),    # '2025-07-01T00:00:00+00:00'
        'fecha_fin': datetime(2025, 7, 31).date().isoformat(),  # '2025-07-31T23:59:59+00:00'
        'agrupacion': 'mes',
    }
    response = client.get(url, params)

    print("RESPONSE DATA:", response.data)

    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert Decimal(response.data[0]['total_ventas']) == Decimal('400.00')
