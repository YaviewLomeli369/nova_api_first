from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ventas.models import Venta
from facturacion.models import ComprobanteFiscal  # Importa el modelo
from facturacion.services.procesar import procesar_timbrado_venta

class FacturarVentaAPIView(APIView):
    def get(self, request, id):
        try:
            venta = Venta.objects.get(pk=id)
        except Venta.DoesNotExist:
            return Response({'error': 'Venta no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        # Verificar si ya existe un comprobante para esta venta
        comprobante_existente = ComprobanteFiscal.objects.filter(venta=venta).first()

        if comprobante_existente:
            # Ya existe un comprobante, devolver info sin crear uno nuevo
            if comprobante_existente.estado == "TIMBRADO":
                return Response({
                    "message": "Factura ya generada anteriormente",
                    "uuid": comprobante_existente.uuid,
                    "venta": venta.id,
                    "comprobante_id": comprobante_existente.id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "message": "Comprobante existente con error",
                    "error": comprobante_existente.error_mensaje
                }, status=status.HTTP_400_BAD_REQUEST)

        # No existe comprobante, proceder a timbrar y crear uno nuevo
        comprobante = procesar_timbrado_venta(venta)

        if comprobante.estado == "TIMBRADO":
            return Response({
                "message": "Factura generada correctamente",
                "uuid": comprobante.uuid,
                "venta": venta.id,
                "comprobante_id": comprobante.id
            }, status=status.HTTP_200_OK) 
        else:
            return Response({
                "message": "Error al timbrar",
                "error": comprobante.error_mensaje
            }, status=status.HTTP_400_BAD_REQUEST)