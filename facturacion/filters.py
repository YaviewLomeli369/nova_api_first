import django_filters
from facturacion.models import ComprobanteFiscal
import django_filters
from facturacion.models import EnvioCorreoCFDI

class EnvioCorreoCFDIFilter(django_filters.FilterSet):
    destinatario = django_filters.CharFilter(lookup_expr='icontains')
    enviado_por = django_filters.NumberFilter()
    comprobante = django_filters.NumberFilter()
    fecha_envio_inicio = django_filters.DateTimeFilter(field_name='fecha_envio', lookup_expr='gte')
    fecha_envio_fin = django_filters.DateTimeFilter(field_name='fecha_envio', lookup_expr='lte')

    class Meta:
        model = EnvioCorreoCFDI
        fields = ['destinatario', 'enviado_por', 'comprobante']

class ComprobanteFiscalFilter(django_filters.FilterSet):
    uuid = django_filters.CharFilter(lookup_expr='icontains')
    estado = django_filters.CharFilter()
    tipo = django_filters.CharFilter()
    serie = django_filters.CharFilter(lookup_expr='icontains')
    folio = django_filters.NumberFilter()
    venta__cliente__nombre = django_filters.CharFilter(field_name='venta__cliente__nombre', lookup_expr='icontains')
    empresa = django_filters.NumberFilter()

    fecha_timbrado_inicio = django_filters.DateFilter(field_name='fecha_timbrado', lookup_expr='gte')
    fecha_timbrado_fin = django_filters.DateFilter(field_name='fecha_timbrado', lookup_expr='lte')

    class Meta:
        model = ComprobanteFiscal
        fields = [
            'uuid', 'estado', 'tipo', 'serie', 'folio', 'empresa', 'venta__cliente__nombre']