# reportes/services/reportes_compras.py
from compras.models import PagoCompra
from django.db.models import F, ExpressionWrapper, DurationField
from collections import defaultdict

def obtener_dias_promedio_pago_proveedores(empresa):
    """
    Retorna una lista con proveedor, cantidad de pagos y promedio de días entre compra y pago.
    """
    pagos = PagoCompra.objects.filter(compra__empresa=empresa).annotate(
        dias_pago=ExpressionWrapper(
            F('fecha_pago') - F('compra__fecha'),
            output_field=DurationField()
        )
    )

    resumen = defaultdict(lambda: {'proveedor': '', 'cantidad_pagos': 0, 'suma_dias': 0})

    for pago in pagos:
        proveedor = pago.compra.proveedor.nombre
        dias = pago.dias_pago.days
        resumen[proveedor]['proveedor'] = proveedor
        resumen[proveedor]['cantidad_pagos'] += 1
        resumen[proveedor]['suma_dias'] += dias

    resultado = []
    for proveedor, data in resumen.items():
        promedio = round(data['suma_dias'] / data['cantidad_pagos'], 2)
        resultado.append({
            'proveedor': data['proveedor'],
            'cantidad_pagos': data['cantidad_pagos'],
            'dias_promedio_pago': promedio
        })

    return resultado
