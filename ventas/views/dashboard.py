from rest_framework.views import APIView
from rest_framework.response import Response
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto, Inventario, MovimientoInventario
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from datetime import timedelta
from django.utils import timezone

class VentaDashboardAPIView(APIView):
    """
    Vista para obtener estadísticas del dashboard de ventas.
    """

    def get(self, request, *args, **kwargs):
        # Obtener los parámetros 'fecha' y 'periodo' de la URL
        fecha_param = request.query_params.get('fecha')
        periodo_param = request.query_params.get('periodo', 'diario')  # El valor predeterminado es 'diario'

        # Si el parámetro 'fecha' es 'hoy', usamos la fecha actual
        if fecha_param == 'hoy':
            fecha_param = timezone.now().date()
        elif fecha_param:  # Si 'fecha_param' no es None o vacío
            # Intentamos usar la fecha proporcionada en formato 'YYYY-MM-DD'
            try:
                fecha_param = timezone.datetime.strptime(fecha_param, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Fecha no válida. Usa el formato YYYY-MM-DD o 'hoy'."})
        else:
            # Si no se pasa ninguna fecha, usamos la fecha actual
            fecha_param = timezone.now().date()

        # Filtramos las ventas por la fecha proporcionada
        ventas_filtradas = Venta.objects.filter(fecha__date=fecha_param)

        # Total de ventas
        total_ventas = ventas_filtradas.aggregate(total=Sum('total'))['total'] or 0

        # Ventas agrupadas por estado
        ventas_por_estado = ventas_filtradas.values('estado').annotate(total=Sum('total'))

        # Ventas por vendedor
        ventas_por_vendedor = ventas_filtradas.values('usuario__username').annotate(total=Sum('total'))

        # Promedio de ventas por transacción
        promedio_venta = ventas_filtradas.aggregate(promedio=Sum('total') / Count('id'))['promedio'] or 0

        # Ventas de los últimos 30 días
        fecha_limite = timezone.now() - timedelta(days=30)
        ventas_ultimos_30_dias = ventas_filtradas.filter(fecha__gte=fecha_limite).aggregate(total=Sum('total'))['total'] or 0

        # Top 5 productos más vendidos (en base a las ventas por detalle)
        top_productos = DetalleVenta.objects.filter(venta__fecha__date=fecha_param).values('producto__nombre').annotate(
            total_ventas=Sum(F('cantidad') * F('precio_unitario'))
        ).order_by('-total_ventas')[:5]

        # Ingresos y margen por producto (basado en costo y precio)
        ingresos_y_margen = DetalleVenta.objects.filter(venta__fecha__date=fecha_param).values('producto__nombre').annotate(
            total_ingresos=Sum(F('cantidad') * F('precio_unitario')),
            margen=Sum(F('cantidad') * (F('precio_unitario') - F('producto__precio_compra')))  # Cambio de costo a precio_compra
        ).order_by('-total_ingresos')[:5]

        # Ventas por cliente
        ventas_por_cliente = ventas_filtradas.values('cliente__nombre').annotate(total=Sum('total')).order_by('-total')[:5]

        # Calcular el stock disponible por producto
        stock_disponible = Inventario.objects.filter(
            producto__empresa__in=ventas_filtradas.values('empresa')
        ).values('producto__nombre').annotate(
            total_stock=Sum(F('cantidad')),
            stock_minimo=F('producto__stock_minimo')
        ).order_by('producto__nombre')

        # Identificar productos con bajo stock
        productos_bajo_stock = stock_disponible.filter(
            total_stock__lte=F('stock_minimo')
        ).order_by('total_stock')

        # Promedio de precio de venta y precio de compra por producto
        precios_promedio = Producto.objects.values('nombre').annotate(
            promedio_precio_venta=Sum('precio_venta') / Count('id'),
            promedio_precio_compra=Sum('precio_compra') / Count('id')
        )

        # Agrupación de ventas por periodo
        if periodo_param == 'semanal':
            ventas_por_periodo = ventas_filtradas.annotate(
                semana=TruncWeek('fecha')
            ).values('semana').annotate(total=Sum('total')).order_by('semana')

        elif periodo_param == 'mensual':
            ventas_por_periodo = ventas_filtradas.annotate(
                mes=TruncMonth('fecha')
            ).values('mes').annotate(total=Sum('total')).order_by('mes')

        else:  # Por defecto, agrupamos por día
            ventas_por_periodo = ventas_filtradas.annotate(
                dia=TruncDate('fecha')
            ).values('dia').annotate(total=Sum('total')).order_by('dia')

        # Devolviendo los resultados con stock y precios promedios
        return Response({
            "total_ventas": total_ventas,
            "ventas_por_estado": ventas_por_estado,
            "ventas_por_vendedor": ventas_por_vendedor,
            "promedio_venta": promedio_venta,
            "ventas_ultimos_30_dias": ventas_ultimos_30_dias,
            "top_productos": top_productos,
            "ingresos_y_margen": ingresos_y_margen,
            "ventas_por_cliente": ventas_por_cliente,
            "stock_disponible": stock_disponible,
            "productos_bajo_stock": productos_bajo_stock,
            "precios_promedio": precios_promedio,
            "ventas_por_periodo": ventas_por_periodo
        })











# from rest_framework.views import APIView
# from rest_framework.response import Response
# from ventas.models import Venta, DetalleVenta
# from inventario.models import Producto, Inventario, MovimientoInventario
# from django.db.models import Sum, F, Count, ExpressionWrapper, DecimalField
# from datetime import timedelta
# from django.utils import timezone


# class VentaDashboardAPIView(APIView):
#     """
#     Vista para obtener estadísticas del dashboard de ventas.
#     """

#     def get(self, request, *args, **kwargs):
#         # Obtener el parámetro 'fecha' de la URL, por ejemplo, "fecha__date=hoy"
#         fecha_param = request.query_params.get('fecha')

#         # Si el parámetro 'fecha' es 'hoy', usamos la fecha actual
#         if fecha_param == 'hoy':
#             fecha_param = timezone.now().date()
#         else:
#             # Si no, intentamos usar la fecha proporcionada en formato 'YYYY-MM-DD'
#             try:
#                 fecha_param = timezone.datetime.strptime(fecha_param, '%Y-%m-%d').date()
#             except ValueError:
#                 return Response({"error": "Fecha no válida. Usa el formato YYYY-MM-DD o 'hoy'."})

#         # Filtramos las ventas por la fecha proporcionada
#         ventas_filtradas = Venta.objects.filter(fecha__date=fecha_param)

#         # Total de ventas
#         total_ventas = ventas_filtradas.aggregate(total=Sum('total'))['total'] or 0

#         # Ventas agrupadas por estado
#         ventas_por_estado = ventas_filtradas.values('estado').annotate(total=Sum('total'))

#         # Ventas por vendedor
#         ventas_por_vendedor = ventas_filtradas.values('usuario__username').annotate(total=Sum('total'))

#         # Promedio de ventas por transacción
#         promedio_venta = ventas_filtradas.aggregate(promedio=Sum('total') / Count('id'))['promedio'] or 0

#         # Ventas de los últimos 30 días
#         fecha_limite = timezone.now() - timedelta(days=30)
#         ventas_ultimos_30_dias = ventas_filtradas.filter(fecha__gte=fecha_limite).aggregate(total=Sum('total'))['total'] or 0

#         # Top 5 productos más vendidos (en base a las ventas por detalle)
#         top_productos = DetalleVenta.objects.filter(venta__fecha__date=fecha_param).values('producto__nombre').annotate(
#             total_ventas=Sum(F('cantidad') * F('precio_unitario'))
#         ).order_by('-total_ventas')[:5]

#         # Ingresos y margen por producto (basado en costo y precio)
#         ingresos_y_margen = DetalleVenta.objects.filter(venta__fecha__date=fecha_param).values('producto__nombre').annotate(
#             total_ingresos=Sum(F('cantidad') * F('precio_unitario')),
#             margen=Sum(F('cantidad') * (F('precio_unitario') - F('producto__precio_compra')))  # Cambio de costo a precio_compra
#         ).order_by('-total_ingresos')[:5]

#         # Ventas por cliente
#         ventas_por_cliente = ventas_filtradas.values('cliente__nombre').annotate(total=Sum('total')).order_by('-total')[:5]

#         # Calcular el stock disponible por producto
#         stock_disponible = Inventario.objects.filter(
#             producto__empresa__in=ventas_filtradas.values('empresa')
#         ).values('producto__nombre').annotate(
#             total_stock=Sum(F('cantidad')),
#             stock_minimo=F('producto__stock_minimo')
#         ).order_by('producto__nombre')

#         # Identificar productos con bajo stock
#         productos_bajo_stock = stock_disponible.filter(
#             total_stock__lte=F('stock_minimo')
#         ).order_by('total_stock')

#         # Promedio de precio de venta y precio de compra por producto
#         precios_promedio = Producto.objects.values('nombre').annotate(
#             promedio_precio_venta=Sum('precio_venta') / Count('id'),
#             promedio_precio_compra=Sum('precio_compra') / Count('id')
#         )

#         # Devolviendo los resultados con stock y precios promedios
#         return Response({
#             "total_ventas": total_ventas,
#             "ventas_por_estado": ventas_por_estado,
#             "ventas_por_vendedor": ventas_por_vendedor,
#             "promedio_venta": promedio_venta,
#             "ventas_ultimos_30_dias": ventas_ultimos_30_dias,
#             "top_productos": top_productos,
#             "ingresos_y_margen": ingresos_y_margen,
#             "ventas_por_cliente": ventas_por_cliente,
#             "stock_disponible": stock_disponible,
#             "productos_bajo_stock": productos_bajo_stock,
#             "precios_promedio": precios_promedio
#         })





#from rest_framework.views import APIView
# from rest_framework.response import Response
# from ventas.models import Venta, DetalleVenta
# from django.db.models import Sum, Count
# from datetime import timedelta
# from django.utils import timezone

# class VentaDashboardAPIView(APIView):
#     """
#     Vista para obtener estadísticas del dashboard de ventas
#     """
#     def get(self, request, *args, **kwargs):
#         # Total de ventas
#         total_ventas = Venta.objects.aggregate(total=Sum('total'))['total'] or 0

#         # Ventas agrupadas por estado
#         ventas_por_estado = Venta.objects.values('estado').annotate(total=Sum('total'))

#         # Ventas por vendedor
#         ventas_por_vendedor = Venta.objects.values('usuario__username').annotate(total=Sum('total'))

#         # Promedio de ventas por transacción
#         promedio_venta = Venta.objects.aggregate(promedio=Sum('total') / Count('id'))['promedio'] or 0

#         # Ventas de los últimos 30 días
#         fecha_limite = timezone.now() - timedelta(days=30)
#         ventas_ultimos_30_dias = Venta.objects.filter(fecha__gte=fecha_limite).aggregate(total=Sum('total'))['total'] or 0

#         # Top 5 productos más vendidos (en base a las ventas por detalle)
#         top_productos = DetalleVenta.objects.values('producto__nombre').annotate(total_ventas=Sum('total')).order_by('-total_ventas')[:5]

#         # Ingresos y margen por producto (basado en costo y precio)
#         ingresos_y_margen = DetalleVenta.objects.values('producto__nombre').annotate(
#             total_ingresos=Sum('total'),
#             margen=Sum('total') - Sum('producto__costo')  # Suponiendo que cada detalle tiene un campo de costo
#         ).order_by('-total_ingresos')[:5]

#         # Ventas por cliente
#         ventas_por_cliente = Venta.objects.values('cliente__nombre').annotate(total=Sum('total')).order_by('-total')[:5]

#         # Ventas diarias (Ventas por día)
#         hoy = timezone.now().date()
#         ventas_diarias = Venta.objects.filter(fecha__date=hoy).aggregate(total=Sum('total'))['total'] or 0

#         # Ventas mensuales (Ventas del mes actual)
#         inicio_mes = hoy.replace(day=1)
#         ventas_mensuales = Venta.objects.filter(fecha__gte=inicio_mes).aggregate(total=Sum('total'))['total'] or 0

#         # Devolviendo los resultados
#         return Response({
#             "total_ventas": total_ventas,
#             "ventas_por_estado": ventas_por_estado,
#             "ventas_por_vendedor": ventas_por_vendedor,
#             "promedio_venta": promedio_venta,
#             "ventas_ultimos_30_dias": ventas_ultimos_30_dias,
#             "top_productos": top_productos,
#             "ingresos_y_margen": ingresos_y_margen,
#             "ventas_por_cliente": ventas_por_cliente,
#             "ventas_diarias": ventas_diarias,
#             "ventas_mensuales": ventas_mensuales
#         })


# from rest_framework import viewsets, permissions, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from ventas.models import Venta
# from ventas.serializers import VentaSerializer
# from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsVendedor
# import django_filters
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response


# # Filtros personalizados para las ventas
# class VentaFilter(django_filters.FilterSet):
#     # Filtro para el RFC del cliente
#     rfc_cliente = django_filters.CharFilter(field_name='cliente__rfc', lookup_expr='icontains', label='RFC del Cliente')

#     # Filtro para el nombre del producto (en los detalles de la venta)
#     nombre_producto = django_filters.CharFilter(field_name='detalles__producto__nombre', lookup_expr='icontains', label='Nombre del Producto')

#     # Filtros de fecha (rango de fechas)
#     fecha_inicio = django_filters.DateFilter(field_name='fecha', lookup_expr='gte', label='Fecha desde')
#     fecha_fin = django_filters.DateFilter(field_name='fecha', lookup_expr='lte', label='Fecha hasta')

#     # Filtro para el vendedor
#     vendedor = django_filters.CharFilter(field_name='usuario__username', lookup_expr='icontains', label='Vendedor')

#     # Filtro para el estado de la venta
#     estado = django_filters.ChoiceFilter(choices=Venta.ESTADO_CHOICES, label='Estado')

#     class Meta:
#         model = Venta
#         fields = ['empresa', 'estado', 'cliente', 'fecha_inicio', 'fecha_fin', 'rfc_cliente', 'nombre_producto', 'vendedor']


# # Clase de paginación personalizada
# class VentaPagination(PageNumberPagination):
#     page_size = 10  # Número de resultados por página
#     page_size_query_param = 'page_size'
#     max_page_size = 100  # Máximo número de resultados por página


# class VentaViewSet(viewsets.ModelViewSet):
#     """
#     CRUD para Ventas, con detalles anidados.
#     """
#     queryset = Venta.objects.all().select_related('cliente', 'usuario', 'empresa').prefetch_related('detalles__producto')
#     serializer_class = VentaSerializer
#     permission_classes = [permissions.IsAuthenticated & (IsSuperAdmin | IsEmpresaAdmin | IsVendedor)]
#     filter_backends = [filters.SearchFilter, DjangoFilterBackend]
#     search_fields = ['cliente__nombre', 'usuario__username', 'estado']
#     filterset_class = VentaFilter  # Usamos el filtro personalizado aquí

#     # Configuramos la paginación
#     pagination_class = VentaPagination

#     # Ordenamiento por fecha o total
#     ordering_fields = ['fecha', 'total']  # Permite ordenar por fecha y total
#     ordering = ['-fecha']  # Orden por defecto: por fecha descendente

#     def get_queryset(self):
#         user = self.request.user
#         if user.rol.nombre == "Superadministrador":
#             return self.queryset
#         return self.queryset.filter(empresa=user.empresa)

#     def perform_create(self, serializer):
#         serializer.save(usuario=self.request.user)

#     def get_latest_sales(self):
#         """
#         Devuelve las últimas n ventas con filtros aplicados.
#         """
#         n = self.request.query_params.get('n', 10)  # Número de ventas a devolver
#         try:
#             n = int(n)
#         except ValueError:
#             n = 10  # Si no se pasa un número válido, devolver las últimas 10 ventas

#         # Filtrar las ventas según los parámetros de búsqueda
#         filtered_sales = self.filter_queryset(self.queryset.order_by('-fecha')[:n])

#         # Devuelve las ventas filtradas y limitadas
#         return filtered_sales

#     def list(self, request, *args, **kwargs):
#         """
#         Sobrescribimos el método `list` para agregar soporte para obtener las últimas 'n' ventas.
#         """
#         # Si se pasa el parámetro 'latest', devolver solo las últimas 'n' ventas
#         if 'latest' in self.request.query_params:
#             latest_sales = self.get_latest_sales()
#             page = self.paginate_queryset(latest_sales)
#             if page is not None:
#                 serializer = self.get_serializer(page, many=True)
#                 return self.get_paginated_response(serializer.data)
#             return Response(self.get_serializer(latest_sales, many=True).data)

#         # Si no se pide 'latest', proceder con la lógica predeterminada
#         return super().list(request, *args, **kwargs)
