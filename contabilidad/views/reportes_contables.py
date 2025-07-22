from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
from django.db.models import Sum, Q


class ReportesContablesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa = getattr(request.user, 'empresa_actual', None)
        tipo = request.query_params.get('tipo')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        if not empresa:
            raise ValidationError("El usuario no tiene empresa_actual definida.")
        if tipo not in ['journal', 'trial_balance', 'income_statement', 'balance_sheet']:
            raise ValidationError("Invalid report type.")

        if tipo == 'journal':
            return self.libro_diario(empresa, fecha_inicio, fecha_fin)
        elif tipo == 'trial_balance':
            return self.balance_comprobacion(empresa, fecha_inicio, fecha_fin)
        elif tipo == 'income_statement':
            return self.estado_resultados(empresa, fecha_inicio, fecha_fin)
        elif tipo == 'balance_sheet':
            return self.balance_general(empresa, fecha_inicio, fecha_fin)

    def libro_diario(self, empresa, fecha_inicio, fecha_fin):
        filtros = Q(empresa=empresa)
        if fecha_inicio:
            filtros &= Q(fecha__gte=fecha_inicio)
        if fecha_fin:
            filtros &= Q(fecha__lte=fecha_fin)

        asientos = AsientoContable.objects.filter(filtros).prefetch_related('detalles')
        resultado = []
        for asiento in asientos:
            resultado.append({
                'id': asiento.id,
                'fecha': asiento.fecha,
                'concepto': asiento.concepto,
                'detalles': [
                    {
                        'cuenta': d.cuenta_contable.codigo,
                        'nombre': d.cuenta_contable.nombre,
                        'debe': float(d.debe),
                        'haber': float(d.haber),
                        'descripcion': d.descripcion
                    } for d in asiento.detalles.all()
                ]
            })
        return Response({'libro_diario': resultado})

    def balance_comprobacion(self, empresa, fecha_inicio, fecha_fin):
        filtros = Q(asiento__empresa=empresa)
        if fecha_inicio:
            filtros &= Q(asiento__fecha__gte=fecha_inicio)
        if fecha_fin:
            filtros &= Q(asiento__fecha__lte=fecha_fin)

        detalles = DetalleAsiento.objects.filter(filtros).values(
            'cuenta_contable__codigo',
            'cuenta_contable__nombre'
        ).annotate(
            total_debe=Sum('debe'),
            total_haber=Sum('haber')
        ).order_by('cuenta_contable__codigo')
        return Response({'balance_comprobacion': list(detalles)})

    def estado_resultados(self, empresa, fecha_inicio, fecha_fin):
        cuentas = CuentaContable.objects.filter(
            empresa=empresa,
            clasificacion__in=['ingreso', 'gasto']
        )
        resultado = []
        total_ingresos = 0
        total_gastos = 0

        for cuenta in cuentas:
            movimientos = cuenta.movimientos.all()
            if fecha_inicio:
                movimientos = movimientos.filter(asiento__fecha__gte=fecha_inicio)
            if fecha_fin:
                movimientos = movimientos.filter(asiento__fecha__lte=fecha_fin)

            debe = movimientos.aggregate(s=Sum('debe'))['s'] or 0
            haber = movimientos.aggregate(s=Sum('haber'))['s'] or 0
            saldo = haber - debe if cuenta.clasificacion == 'ingreso' else debe - haber

            resultado.append({
                'codigo': cuenta.codigo,
                'nombre': cuenta.nombre,
                'clasificacion': cuenta.clasificacion,
                'saldo': float(saldo)
            })

            if cuenta.clasificacion == 'ingreso':
                total_ingresos += saldo
            else:
                total_gastos += saldo

        utilidad_neta = total_ingresos - total_gastos
        return Response({
            'estado_resultados': resultado,
            'totales': {
                'ingresos': float(total_ingresos),
                'gastos': float(total_gastos),
                'utilidad_neta': float(utilidad_neta)
            }
        })

    def balance_general(self, empresa, fecha_inicio, fecha_fin):
        cuentas = CuentaContable.objects.filter(
            empresa=empresa,
            clasificacion__in=['activo', 'pasivo', 'patrimonio']
        )
        resultado = []
        totales = {'activo': 0, 'pasivo': 0, 'patrimonio': 0}

        for cuenta in cuentas:
            movimientos = cuenta.movimientos.all()
            if fecha_inicio:
                movimientos = movimientos.filter(asiento__fecha__gte=fecha_inicio)
            if fecha_fin:
                movimientos = movimientos.filter(asiento__fecha__lte=fecha_fin)

            debe = movimientos.aggregate(s=Sum('debe'))['s'] or 0
            haber = movimientos.aggregate(s=Sum('haber'))['s'] or 0
            saldo = debe - haber if cuenta.clasificacion == 'activo' else haber - debe

            resultado.append({
                'codigo': cuenta.codigo,
                'nombre': cuenta.nombre,
                'clasificacion': cuenta.clasificacion,
                'saldo': float(saldo)
            })

            totales[cuenta.clasificacion] += saldo

        return Response({
            'balance_general': resultado,
            'totales': {k: float(v) for k, v in totales.items()}
        })
