from rest_framework import viewsets, permissions, filters
from accounts.models import Usuario
from accounts.serializers.user_serializers import UsuarioCreateSerializer, UsuarioDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers

# # accounts/views/users.py

# from rest_framework import viewsets, permissions, filters
# from accounts.models import Usuario
# from accounts.serializers import UsuarioCreateSerializer, UsuarioDetailSerializer
# from django_filters.rest_framework import DjangoFilterBackend

class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Usuario.objects.select_related('empresa', 'rol').all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'email']
    filterset_fields = ['activo', 'empresa', 'rol']

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioDetailSerializer

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save()
