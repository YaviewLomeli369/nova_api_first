from datetime import datetime, time
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.db.models import Sum
from ventas.models import Venta
from django.utils import timezone

def ventas_agrupadas_por_fecha(empresa, fecha_inicio, fecha_fin, agrupacion):
    # Convertir fechas a datetime con hora min y max
    # fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)  # 00:00:00
    # fecha_fin_dt = datetime.combine(fecha_fin, time.max)        # 23:59:59.999999
    fecha_inicio_dt = timezone.make_aware(datetime.combine(fecha_inicio, time.min))
    fecha_fin_dt = timezone.make_aware(datetime.combine(fecha_fin, time.max))

    queryset = Venta.objects.filter(
        empresa=empresa,
        fecha__range=[fecha_inicio_dt, fecha_fin_dt],
        estado='COMPLETADA'
    )

    if agrupacion == 'dia':
        trunc_func = TruncDate('fecha')
    elif agrupacion == 'mes':
        trunc_func = TruncMonth('fecha')
    elif agrupacion == 'anio':
        trunc_func = TruncYear('fecha')
    else:
        raise ValueError("Agrupación inválida")

    datos = (
        queryset
        .annotate(fecha_truncada=trunc_func)
        .values('fecha_truncada')
        .annotate(total_ventas=Sum('total'))
        .order_by('fecha_truncada')
    )

    return datos
