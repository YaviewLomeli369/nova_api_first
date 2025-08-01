from compras.models import Compra, PagoCompra
from datetime import timedelta

def calcular_dias_promedio_pago_proveedores():
    compras_pagadas = Compra.objects.filter(pagos__isnull=False).distinct()

    total_dias = 0
    total_pagos = 0

    for compra in compras_pagadas:
        fecha_compra = compra.fecha.date() if hasattr(compra.fecha, 'date') else compra.fecha
        pagos = PagoCompra.objects.filter(compra=compra)

        for pago in pagos:
            fecha_pago = pago.fecha_pago.date() if hasattr(pago.fecha_pago, 'date') else pago.fecha_pago
            dias = (fecha_pago - fecha_compra).days
            if dias >= 0:
                total_dias += dias
                total_pagos += 1

    if total_pagos == 0:
        return 0

    promedio = total_dias / total_pagos
    return round(promedio, 2)