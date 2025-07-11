from rest_framework import viewsets, permissions, filters
from accounts.models import Usuario
from accounts.serializers.user_serializers import UsuarioCreateSerializer, UsuarioDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied

class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'email']
    filterset_fields = ['activo', 'empresa', 'rol']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Usuario.objects.select_related('empresa', 'rol').all()
        return Usuario.objects.filter(empresa=user.empresa)

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioDetailSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_superuser:
            # Solo admin puede crear usuarios fuera de su empresa
            serializer.save(empresa=user.empresa)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save()

# # accounts/views/user_viewset.py

# from rest_framework import viewsets, permissions, filters
# from accounts.models import Usuario
# from accounts.serializers.user_serializers import UsuarioCreateSerializer, UsuarioDetailSerializer
# from django_filters.rest_framework import DjangoFilterBackend

# class UsuarioViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Usuario.objects.select_related('empresa', 'rol').all()
#     filter_backends = [filters.SearchFilter, DjangoFilterBackend]
#     search_fields = ['username', 'email']
#     filterset_fields = ['activo', 'empresa', 'rol']

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_superuser:
#             return Usuario.objects.all()
#         return Usuario.objects.filter(empresa=user.empresa)

#     def get_serializer_class(self):
#         if self.action == 'create':
#             return UsuarioCreateSerializer
#         return UsuarioDetailSerializer

#     def perform_create(self, serializer):
#         user = self.request.user
#         if not user.is_superuser:
#             serializer.save(empresa=user.empresa)
#         else:
#             serializer.save()

#     def perform_destroy(self, instance):
#         instance.activo = False
#         instance.save()

# from rest_framework import viewsets, permissions, filters
# from accounts.models import Usuario
# from accounts.serializers.user_serializers import UsuarioCreateSerializer, UsuarioDetailSerializer
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import serializers



# class UsuarioViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Usuario.objects.select_related('empresa', 'rol').all()
#     filter_backends = [filters.SearchFilter, DjangoFilterBackend]
#     search_fields = ['username', 'email']
#     filterset_fields = ['activo', 'empresa', 'rol']

#     def get_serializer_class(self):
#         if self.action == 'create':
#             return UsuarioCreateSerializer
#         return UsuarioDetailSerializer

#     def perform_destroy(self, instance):
#         instance.activo = False
#         instance.save()
