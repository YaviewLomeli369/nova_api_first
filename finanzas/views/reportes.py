from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, F  # Faltan estos dos
from datetime import date, timedelta
from django.db.models.functions import TruncMonth
from finanzas.models import (
    Pago,
    Venta,
    CuentaPorCobrar,
    CuentaPorPagar,
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
        
# class CuentasPorCobrarVencidasView(APIView):
#     """
#     Vista para obtener las cuentas por cobrar vencidas o próximas a vencer.
#     """
#     def get(self, request):
#         hoy = now().date()
#         limite = hoy + timedelta(days=3)
#         cuentas_vencidas = CuentaPorCobrar.objects.filter(fecha_vencimiento__lte=hoy, estado='PENDIENTE')
#         cuentas_proximas = CuentaPorCobrar.objects.filter(fecha_vencimiento__range=(hoy, limite), estado='PENDIENTE')

#         cuentas = list(cuentas_vencidas) + list(cuentas_proximas)

#         return Response({"cuentas": [str(cuenta.id) for cuenta in cuentas]})


class FlujoDeCajaView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        sucursal_id = request.query_params.get('sucursal')
        # fecha_inicio = request.query_params.get('fecha_inicio')
        # fecha_fin = request.query_params.get('fecha_fin')
        fecha_inicio = parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin = parse_date(request.query_params.get('fecha_fin'))


        ingresos = Pago.objects.filter(tipo='INGRESO')
        egresos = Pago.objects.filter(tipo='EGRESO')

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
# class FlujoDeCajaView(APIView):
#     """
#     Vista para obtener el flujo de caja por fecha.
#     """
#     def get(self, request):
#         pagos = Pago.objects.filter(fecha__year=2025).values('fecha__month').annotate(total=Sum('monto'))
#         return Response({"flujos": pagos})

class AnalisisPorClienteProveedorView(APIView):
    def get(self, request):
        cliente_id = request.query_params.get('cliente')
        proveedor_id = request.query_params.get('proveedor')
        # fecha_inicio = request.query_params.get('fecha_inicio')
        # fecha_fin = request.query_params.get('fecha_fin')
        fecha_inicio = parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin = parse_date(request.query_params.get('fecha_fin'))


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


# class AnalisisPorClienteProveedorView(APIView):
#     """
#     Vista para obtener un análisis de pagos por cliente o proveedor.
#     """
#     def get(self, request):
#         pagos_cliente = Pago.objects.filter(cuenta_cobrar__venta__cliente_id=1).values('fecha__month').annotate(total=Sum('monto'))
#         pagos_proveedor = Pago.objects.filter(cuenta_pagar__compra__proveedor_id=1).values('fecha__month').annotate(total=Sum('monto'))

#         return Response({
#             "pagos_cliente": pagos_cliente,
#             "pagos_proveedor": pagos_proveedor,
#         })


class CuentasPorCobrarAvanzadasView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        sucursal_id = request.query_params.get('sucursal')
        cliente_id = request.query_params.get('cliente')
        # fecha_inicio = request.query_params.get('fecha_inicio')
        # fecha_fin = request.query_params.get('fecha_fin')
        fecha_inicio = parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin = parse_date(request.query_params.get('fecha_fin'))


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
        
# class CuentasPorCobrarAvanzadasView(APIView):
#     """
#     Vista para obtener un análisis avanzado de cuentas por cobrar.
#     """
#     def get(self, request):
#         hoy = now().date()
#         limite = hoy + timedelta(days=3)

#         cuentas_vencidas = CuentaPorCobrar.objects.filter(fecha_vencimiento__lte=hoy, estado='PENDIENTE')
#         cuentas_proximas = CuentaPorCobrar.objects.filter(fecha_vencimiento__range=(hoy, limite), estado='PENDIENTE')

#         result = {
#             "cuentas_vencidas": cuentas_vencidas.values('venta__cliente__nombre', 'monto', 'fecha_vencimiento', 'estado'),
#             "cuentas_proximas": cuentas_proximas.values('venta__cliente__nombre', 'monto', 'fecha_vencimiento', 'estado'),
#         }
#         return Response(result)


class FlujoDeCajaProyectadoView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        # fecha_inicio = request.query_params.get('fecha_inicio')
        # fecha_fin = request.query_params.get('fecha_fin')
        fecha_inicio = parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin = parse_date(request.query_params.get('fecha_fin'))


        pagos = Pago.objects.all()

        if empresa_id:
            pagos = pagos.filter(empresa_id=empresa_id)
        if fecha_inicio and fecha_fin:
            pagos = pagos.filter(fecha__range=[fecha_inicio, fecha_fin])

        proyeccion = pagos.annotate(mes=TruncMonth('fecha')).values('mes').annotate(total=Sum('monto')).order_by('mes')

        return Response({"flujo_proyectado": proyeccion})

# class FlujoDeCajaProyectadoView(APIView):
#     """
#     Vista para obtener el flujo de caja proyectado por mes.
#     """
#     def get(self, request):
#         pagos = Pago.objects.values('fecha__month').annotate(total=Sum('monto'))
#         return Response({"flujo_de_caja": pagos})



class RentabilidadClienteProveedorView(APIView):
    def get(self, request):
        cliente_id = request.query_params.get('cliente')
        # fecha_inicio = request.query_params.get('fecha_inicio')
        # fecha_fin = request.query_params.get('fecha_fin')
        fecha_inicio = parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin = parse_date(request.query_params.get('fecha_fin'))


        ventas = Venta.objects.all()
        cobros = Pago.objects.filter(tipo='INGRESO')

        if cliente_id:
            ventas = ventas.filter(cliente_id=cliente_id)
            # cobros = cobros.filter(cliente_id=cliente_id)
            cobros = cobros.filter(cuenta_cobrar__venta__cliente_id=cliente_id)
        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
            cobros = cobros.filter(fecha__range=[fecha_inicio, fecha_fin])

        total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0
        total_cobros = cobros.aggregate(total=Sum('monto'))['total'] or 0

        return Response({
            "ventas": total_ventas,
            "cobros": total_cobros,
            "rentabilidad": round(total_cobros - total_ventas, 2)
        })

# class RentabilidadClienteProveedorView(APIView):
#     """
#     Vista para obtener el análisis de rentabilidad por cliente/proveedor.
#     """
#     def get(self, request):
#         ventas_cliente = Venta.objects.values('cliente__nombre').annotate(total_ventas=Sum('total'))
#         cuentas_cliente = CuentaPorCobrar.objects.values('venta__cliente__nombre').annotate(total_cobrado=Sum('monto'))

#         rentabilidad = []
#         for cliente in ventas_cliente:
#             ventas = cliente['total_ventas']
#             cuentas = next((item for item in cuentas_cliente if item['venta__cliente__nombre'] == cliente['cliente__nombre']), None)
#             cuentas_cobrar = cuentas['total_cobrado'] if cuentas else 0
#             rentabilidad.append({
#                 'cliente': cliente['cliente__nombre'],
#                 'ventas': ventas,
#                 'cuentas_por_cobrar': cuentas_cobrar,
#                 'rentabilidad': ventas - cuentas_cobrar
#             })

#         return Response({"rentabilidad_cliente": rentabilidad})

class CicloConversionEfectivoView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        # fecha_inicio = request.query_params.get('fecha_inicio')
        # fecha_fin = request.query_params.get('fecha_fin')
        fecha_inicio = parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin = parse_date(request.query_params.get('fecha_fin'))


        ventas = Venta.objects.filter(fecha__isnull=False)
        compras = Compra.objects.filter(fecha__isnull=False)

        if empresa_id:
            ventas = ventas.filter(empresa_id=empresa_id)
            compras = compras.filter(empresa_id=empresa_id)
        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
            compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])

        dias_prom_cobro = ventas.aggregate(avg=Avg(F('cuenta_por_cobrar__dias_para_cobro')))['avg'] or 0
        dias_prom_pago = compras.aggregate(avg=Avg(F('cuenta_por_pagar__dias_para_pago')))['avg'] or 0

        ciclo = round(dias_prom_cobro - dias_prom_pago, 2)

        return Response({"ciclo_conversion_efectivo": ciclo})
        
# class CicloConversiónEfectivoView(APIView):
#     """
#     Vista para calcular y mostrar el ciclo de conversión de efectivo.
#     """
#     def get(self, request):
#         hoy = now().date()

#         dias_inventario = 30  # Este dato puede venir de un modelo más adelante

#         cuentas_por_cobrar = CuentaPorCobrar.objects.filter(fecha_vencimiento__lte=hoy, estado='PENDIENTE')
#         dias_cobro = sum((hoy - cuenta.fecha_vencimiento).days for cuenta in cuentas_por_cobrar) / len(cuentas_por_cobrar) if cuentas_por_cobrar else 0

#         cuentas_por_pagar = CuentaPorPagar.objects.filter(fecha_vencimiento__lte=hoy, estado='PENDIENTE')
#         dias_pago = sum((hoy - cuenta.fecha_vencimiento).days for cuenta in cuentas_por_pagar) / len(cuentas_por_pagar) if cuentas_por_pagar else 0

#         ccc = dias_inventario + dias_cobro - dias_pago
#         return Response({"ciclo_conversion_efectivo": ccc})


class LiquidezCorrienteView(APIView):
    """
    Vista para obtener el ratio de liquidez corriente con filtros por fecha, empresa y sucursal.
    """

    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        # sucursal_id = request.query_params.get('sucursal')
        # fecha_inicio = request.query_params.get('fecha_inicio')
        # fecha_fin = request.query_params.get('fecha_fin')
        # fecha_inicio = parse_date(request.query_params.get('fecha_inicio'))
        # fecha_fin = parse_date(request.query_params.get('fecha_fin'))


        cxc = CuentaPorCobrar.objects.filter(estado='PENDIENTE')
        cxp = CuentaPorPagar.objects.filter(estado='PENDIENTE')

        if empresa_id:
            cxc = cxc.filter(venta__empresa_id=empresa_id)
            cxp = cxp.filter(compra__empresa_id=empresa_id)

        # if sucursal_id:
        #     cxc = cxc.filter(venta__sucursal_id=sucursal_id)
        #     cxp = cxp.filter(compra__sucursal_id=sucursal_id)

        if fecha_inicio and fecha_fin:
            fecha_inicio = parse_date(fecha_inicio)
            fecha_fin = parse_date(fecha_fin)
            cxc = cxc.filter(fecha_vencimiento__range=[fecha_inicio, fecha_fin])
            cxp = cxp.filter(fecha_vencimiento__range=[fecha_inicio, fecha_fin])

        activos_corrientes = cxc.aggregate(total=Sum('monto'))['total'] or 0
        pasivos_corrientes = cxp.aggregate(total=Sum('monto'))['total'] or 0

        if pasivos_corrientes == 0:
            ratio = "N/A"
        else:
            ratio = round(activos_corrientes / pasivos_corrientes, 2)

        return Response({"liquidez_corriente": ratio})
