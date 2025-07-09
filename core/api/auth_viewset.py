from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse
from rest_framework import viewsets

@extend_schema_view(
    post=extend_schema(
        summary="Login",
        description="Autenticación con JWT",
        responses={
            200: OpenApiResponse(description="Login exitoso"),
            400: OpenApiResponse(description="Datos inválidos"),
            401: OpenApiResponse(description="Credenciales incorrectas"),
            500: OpenApiResponse(description="Error interno"),
        },
    ),
    get=extend_schema(
        summary="Ver perfil",
        description="Datos del usuario autenticado",
        responses={
            200: OpenApiResponse(description="Datos del usuario"),
            401: OpenApiResponse(description="Token inválido o no enviado"),
        },
    ),
)
class AuthViewSet(viewsets.ViewSet):
    pass
