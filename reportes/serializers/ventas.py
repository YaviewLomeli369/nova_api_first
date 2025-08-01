from rest_framework import serializers

class PromedioTicketVentaSerializer(serializers.Serializer):
    total_tickets = serializers.IntegerField()
    total_ingresos = serializers.DecimalField(max_digits=14, decimal_places=2)
    promedio_ticket = serializers.DecimalField(max_digits=14, decimal_places=2)
