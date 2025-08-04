from compras.models import Compra
from django.db.models import Sum
from datetime import datetime

def calcular_eficiencia_compras(empresa_id, fecha_inicio, fecha_fin):
    compras = Compra.objects.filter(
        empresa_id=empresa_id,
        fecha__range=[fecha_inicio, fecha_fin],
        estado__in=["aprobada", "recibida", "pagada"] #"pendiente" solo pruebas si aun no hay forma de camabiar estatuds
    )

    total_compras = compras.count()
    planificadas = compras.filter(planificada=True).count()
    no_planificadas = total_compras - planificadas
    urgentes = compras.filter(urgente=True).count()

    presupuesto_total = compras.aggregate(pres=Sum("presupuesto_total"))['pres'] or 0
    costo_real_total = compras.aggregate(real=Sum("total"))['real'] or 0

    eficiencia = (planificadas / total_compras) * 100 if total_compras > 0 else 0
    ahorro = ((presupuesto_total - costo_real_total) / presupuesto_total * 100) if presupuesto_total > 0 else 0

    return {
        "planificadas": planificadas,
        "no_planificadas": no_planificadas,
        "urgentes": urgentes,
        "total_compras": total_compras,
        "costo_real_total": float(costo_real_total),
        "presupuesto_total": float(presupuesto_total),
        "eficiencia": eficiencia,
        "ahorro": ahorro,
    }
