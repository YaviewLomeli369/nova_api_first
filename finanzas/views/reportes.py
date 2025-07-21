from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date, timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Avg, F, ExpressionWrapper, DurationField
from rest_framework.exceptions import ValidationError
from finanzas.models import (
    Pago,
    Venta,
    CuentaPorCobrar,
    CuentaPorPagar,
    Compra,
)


class CuentasPorCobrarVencidasView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        sucursal_id = request.query_params.get('sucursal')
        cliente_id = request.query_params.get('cliente')
        fecha_limite = request.query_params.get('fecha_limite') or date.today()

        cuentas = CuentaPorCobrar.objects.filter(estado='PENDIENTE', fecha_vencimiento__lte=fecha_limite)

        if empresa_id:
            cuentas = cuentas.filter(venta__empresa_id=empresa_id)
        if sucursal_id:
            cuentas = cuentas.filter(venta__sucursal_id=sucursal_id)
        if cliente_id:
            cuentas = cuentas.filter(cliente_id=cliente_id)

        total = cuentas.aggregate(total=Sum('monto'))['total'] or 0
        return Response({"cuentas_por_cobrar_vencidas": total})
        

class FlujoDeCajaView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        sucursal_id = request.query_params.get('sucursal')

        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        if fecha_inicio_str and fecha_fin_str:
            try:
                fecha_inicio = parse_date(fecha_inicio_str)
                fecha_fin = parse_date(fecha_fin_str)
                if not fecha_inicio or not fecha_fin:
                    raise ValueError
            except Exception:
                raise ValidationError("Los parámetros 'fecha_inicio' y 'fecha_fin' deben tener formato YYYY-MM-DD.")
        else:
            fecha_inicio = fecha_fin = None

        ingresos = Pago.objects.filter(cuenta_cobrar__isnull=False)
        egresos = Pago.objects.filter(cuenta_pagar__isnull=False)

        if empresa_id:
            ingresos = ingresos.filter(empresa_id=empresa_id)
            egresos = egresos.filter(empresa_id=empresa_id)
        if sucursal_id:
            ingresos = ingresos.filter(sucursal_id=sucursal_id)
            egresos = egresos.filter(sucursal_id=sucursal_id)
        if fecha_inicio and fecha_fin:
            ingresos = ingresos.filter(fecha__range=[fecha_inicio, fecha_fin])
            egresos = egresos.filter(fecha__range=[fecha_inicio, fecha_fin])

        total_ingresos = ingresos.aggregate(total=Sum('monto'))['total'] or 0
        total_egresos = egresos.aggregate(total=Sum('monto'))['total'] or 0

        return Response({
            "ingresos": total_ingresos,
            "egresos": total_egresos,
            "flujo_neto": total_ingresos - total_egresos
        })


class AnalisisPorClienteProveedorView(APIView):
    def get(self, request):
        cliente_id = request.query_params.get('cliente')
        proveedor_id = request.query_params.get('proveedor')

        # Validar que los parámetros de fecha sean strings antes de parsearlos
        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        fecha_inicio = parse_date(fecha_inicio_str) if fecha_inicio_str else None
        fecha_fin = parse_date(fecha_fin_str) if fecha_fin_str else None

        ventas = Venta.objects.all()
        compras = Compra.objects.all()

        if cliente_id:
            ventas = ventas.filter(cliente_id=cliente_id)
        if proveedor_id:
            compras = compras.filter(proveedor_id=proveedor_id)
        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
            compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])

        total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0
        total_compras = compras.aggregate(total=Sum('total'))['total'] or 0

        return Response({
            "ventas_cliente": total_ventas,
            "compras_proveedor": total_compras
        })


class CuentasPorCobrarAvanzadasView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        sucursal_id = request.query_params.get('sucursal')
        cliente_id = request.query_params.get('cliente')

        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        fecha_inicio = parse_date(fecha_inicio_str) if isinstance(fecha_inicio_str, str) else None
        fecha_fin = parse_date(fecha_fin_str) if isinstance(fecha_fin_str, str) else None

        cxc = CuentaPorCobrar.objects.all()

        if empresa_id:
            cxc = cxc.filter(venta__empresa_id=empresa_id)
        if sucursal_id:
            cxc = cxc.filter(venta__sucursal_id=sucursal_id)
        if cliente_id:
            cxc = cxc.filter(cliente_id=cliente_id)
        if fecha_inicio and fecha_fin:
            cxc = cxc.filter(fecha__range=[fecha_inicio, fecha_fin])

        total = cxc.aggregate(total=Sum('monto'))['total'] or 0
        return Response({"cuentas_por_cobrar": total})


class FlujoDeCajaProyectadoView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')

        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        fecha_inicio = parse_date(fecha_inicio_str) if isinstance(fecha_inicio_str, str) else None
        fecha_fin = parse_date(fecha_fin_str) if isinstance(fecha_fin_str, str) else None


        pagos = Pago.objects.all()

        if empresa_id:
            pagos = pagos.filter(empresa_id=empresa_id)
        if fecha_inicio and fecha_fin:
            pagos = pagos.filter(fecha__range=[fecha_inicio, fecha_fin])

        proyeccion = pagos.annotate(mes=TruncMonth('fecha')).values('mes').annotate(total=Sum('monto')).order_by('mes')

        return Response({"flujo_proyectado": proyeccion})



class RentabilidadClienteProveedorView(APIView):
    def get(self, request):
        cliente_id = request.query_params.get('cliente')
        proveedor_id = request.query_params.get('proveedor')

        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        fecha_inicio = parse_date(fecha_inicio_str) if isinstance(fecha_inicio_str, str) else None
        fecha_fin = parse_date(fecha_fin_str) if isinstance(fecha_fin_str, str) else None

        ventas = Venta.objects.all()
        compras = Compra.objects.all()

        if cliente_id:
            ventas = ventas.filter(cliente_id=cliente_id)
        if proveedor_id:
            compras = compras.filter(proveedor_id=proveedor_id)

        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
            compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])

        total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0
        total_compras = compras.aggregate(total=Sum('total'))['total'] or 0
        rentabilidad = total_ventas - total_compras

        return Response({
            "ventas": total_ventas,
            "compras": total_compras,
            "rentabilidad": rentabilidad,
        })



class CicloConversionEfectivoView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        ventas = Venta.objects.all()
        compras = Compra.objects.all()

        if empresa_id:
            ventas = ventas.filter(empresa_id=empresa_id)
            compras = compras.filter(empresa_id=empresa_id)

        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
            compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])

        cxc_qs = CuentaPorCobrar.objects.filter(venta__in=ventas)
        cxc_qs = cxc_qs.annotate(
            dias_para_cobro=ExpressionWrapper(
                F('fecha_vencimiento') - F('venta__fecha'),
                output_field=DurationField()
            )
        )

        cxc_avg = cxc_qs.aggregate(avg=Avg('dias_para_cobro'))['avg']

        if cxc_avg:
            promedio_dias_cobro = cxc_avg.total_seconds() / (60*60*24)
        else:
            promedio_dias_cobro = 0

        cxp_qs = CuentaPorPagar.objects.filter(compra__in=compras)
        cxp_qs = cxp_qs.annotate(
            dias_para_pago=ExpressionWrapper(
                F('fecha_vencimiento') - F('compra__fecha'),
                output_field=DurationField()
            )
        )

        cxp_avg = cxp_qs.aggregate(avg=Avg('dias_para_pago'))['avg']

        if cxp_avg:
            promedio_dias_pago = cxp_avg.total_seconds() / (60*60*24)
        else:
            promedio_dias_pago = 0

        ciclo = round(promedio_dias_cobro - promedio_dias_pago, 2)

        return Response({"ciclo_conversion_efectivo": ciclo})



class LiquidezCorrienteView(APIView):
    """
    Vista para obtener el ratio de liquidez corriente con filtros por fecha, empresa y sucursal.
    """
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        fecha_inicio = parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin = parse_date(request.query_params.get('fecha_fin'))

        cxc = CuentaPorCobrar.objects.filter(estado='PENDIENTE')
        cxp = CuentaPorPagar.objects.filter(estado='PENDIENTE')

        if empresa_id:
            cxc = cxc.filter(venta__empresa_id=empresa_id)
            cxp = cxp.filter(compra__empresa_id=empresa_id)

        if fecha_inicio and fecha_fin:
            cxc = cxc.filter(fecha_vencimiento__range=[fecha_inicio, fecha_fin])
            cxp = cxp.filter(fecha_vencimiento__range=[fecha_inicio, fecha_fin])

        activos_corrientes = cxc.aggregate(total=Sum('monto'))['total'] or 0
        pasivos_corrientes = cxp.aggregate(total=Sum('monto'))['total'] or 0

        if pasivos_corrientes == 0:
            ratio = "N/A"
        else:
            ratio = round(activos_corrientes / pasivos_corrientes, 2)

        return Response({"liquidez_corriente": ratio})
