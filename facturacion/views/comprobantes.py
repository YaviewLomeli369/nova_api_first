# views/comprobantes.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from facturacion.models import ComprobanteFiscal
from facturacion.utils.build_facturama_payload import build_facturama_payload
from facturacion.services.facturama import FacturamaService

class TimbrarComprobanteAPIView(APIView):
    def post(self, request, pk):
        comprobante = get_object_or_404(ComprobanteFiscal, pk=pk)
        payload = build_facturama_payload(comprobante)

        try:
            respuesta = FacturamaService.timbrar_comprobante(payload)
            # Aquí podrías guardar en el comprobante la respuesta o UUID recibido
            return Response(respuesta, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)