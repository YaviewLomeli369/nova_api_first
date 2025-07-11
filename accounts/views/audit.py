# Standard library
import csv

# Django
from django.http import HttpResponse

# Django REST Framework
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.pagination import PageNumberPagination

# Filtros de terceros
from django_filters.rest_framework import DjangoFilterBackend

# Local apps
from accounts.models import Auditoria
from accounts.serializers.auditoria_serializers import AuditoriaSerializer
from accounts.filters import AuditoriaFilter

from rest_framework import serializers

# # accounts/views/audit.py
# from rest_framework import generics, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.permissions import IsAdminUser
# from rest_framework.pagination import PageNumberPagination
# from accounts.models import Auditoria
# from accounts.serializers import AuditoriaSerializer
# from accounts.filters import AuditoriaFilter
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from accounts.models import Auditoria
# from accounts.serializers import AuditoriaSerializer
# from django.http import HttpResponse
# import csv

# from rest_framework.generics import GenericAPIView
# from rest_framework.response import Response
# from rest_framework import serializers

class EmptySerializer(serializers.Serializer):
    pass

class AuditLogExportCSV(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = EmptySerializer

    def get(self, request):
        # Aplicar filtros con el mismo filtro set
        filtro = AuditoriaFilter(request.GET, queryset=Auditoria.objects.all())

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit_log.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Usuario', 'Acción', 'Tabla', 'Registro Afectado', 'Fecha/Hora'])

        for entry in filtro.qs.order_by('-timestamp'):
            writer.writerow([
                entry.id,
                str(entry.usuario),
                entry.accion,
                entry.tabla_afectada,
                entry.registro_afectado,
                entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return response

class ActivityLogView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer

    def get(self, request):
        logs = Auditoria.objects.filter(usuario_id=request.user.id).order_by('-timestamp')[:50]
        data = AuditoriaSerializer(logs, many=True).data
        return Response(data)

class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]  # ¿solo admins?

    def get(self, request):
        logs = Auditoria.objects.all().order_by('-timestamp')[:200]
        data = AuditoriaSerializer(logs, many=True).data
        return Response(data)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

class AuditLogListView(generics.ListAPIView):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AuditoriaFilter
    ordering_fields = ['timestamp', 'usuario__username', 'accion', 'tabla_afectada']
    ordering = ['-timestamp']
    pagination_class = StandardResultsSetPagination