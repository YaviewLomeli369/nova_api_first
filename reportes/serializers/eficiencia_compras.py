from compras.models import Compra
from datetime import datetime
from django.db.models import Sum, Count, Q

def calcular_eficiencia_compras(empresa_id, fecha_inicio, fecha_fin):
    compras = Compra.objects.filter(
        empresa_id=empresa_id,
        fecha__range=[fecha_inicio, fecha_fin]
    )

    total_compras = compras.count()

    compras_planificadas = compras.filter(planificada=True).count()
    compras_urgentes = compras.filter(urgente=True).count()

    # Costo total de compras reales
    costo_real = compras.aggregate(total=Sum('total'))['total'] or 0

    # Costo presupuestado (si hay campo `presupuesto` o similar)
    # Aquí asumimos que existe un campo "presupuesto_total" en Compra (ajusta si tienes un modelo separado)
    costo_presupuestado = compras.aggregate(total=Sum('presupuesto_total'))['total'] or 0

    eficiencia = 0
    ahorro = 0

    if costo_presupuestado > 0:
        eficiencia = (costo_real / costo_presupuestado) * 100
        ahorro = ((costo_presupuestado - costo_real) / costo_presupuestado) * 100

    return {
        "planificadas": compras_planificadas,
        "urgentes": compras_urgentes,
        "total_compras": total_compras,
        "eficiencia": round(eficiencia, 2),
        "ahorro": round(ahorro, 2)
    }
