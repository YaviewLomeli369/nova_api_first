from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Auditoria
from accounts.serializers import AuditoriaSerializer

class ActivityLogView(APIView):
    permission_classes = [IsAuthenticated]

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
