import django_filters
from core.models import Sucursal
from inventario.models import Categoria

class StockActualFilter(django_filters.FilterSet):
    sucursal = django_filters.ModelChoiceFilter(
        queryset=Sucursal.objects.all(),
        label="Sucursal",
        required=False
    )
    categoria = django_filters.ModelChoiceFilter(
        queryset=Categoria.objects.all(),
        label="Categoría",
        field_name='producto__categoria',
        required=False
    )
    minimo_stock = django_filters.BooleanFilter(
        field_name='stock_actual',
        method='filter_minimo_stock',
        label="Solo productos con stock > 0",
        required=False
    )

    class Meta:
        model = None  # No es un modelo directo, es un queryset de dicts
        fields = ['sucursal', 'categoria', 'minimo_stock']

    def filter_minimo_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_actual__gt=0)
        return queryset
