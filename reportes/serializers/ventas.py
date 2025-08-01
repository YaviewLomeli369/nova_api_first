from rest_framework import serializers

class PromedioTicketVentaSerializer(serializers.Serializer):
    total_tickets = serializers.IntegerField()
    total_ingresos = serializers.DecimalField(max_digits=14, decimal_places=2)
    promedio_ticket = serializers.DecimalField(max_digits=14, decimal_places=2)



class ProductoMasVendidoSerializer(serializers.Serializer):
    id_producto = serializers.IntegerField()
    nombre = serializers.CharField()
    codigo = serializers.CharField()
    total_vendido = serializers.DecimalField(max_digits=10, decimal_places=2)