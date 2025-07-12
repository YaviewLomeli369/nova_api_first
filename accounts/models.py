# accounts/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from core.models import Empresa
from django.conf import settings


# accounts/models.py

from django.core.exceptions import ValidationError


from django.db import models

from django.core.exceptions import ValidationError
from django.db import models

from django.contrib.auth.models import Group

class Auditoria(models.Model):
    usuario = models.ForeignKey(
        'Usuario', 
        null=True, blank=True,  # ← Permitir que sea opcional
        on_delete=models.SET_NULL,  # ← No eliminar auditorías si se borra el usuario
        related_name="auditorias"
    )
    username_intentado = models.CharField(
        max_length=150, 
        null=True, blank=True, 
        help_text="Nombre de usuario usado en caso de login fallido"
    )
    accion = models.CharField(max_length=255)
    tabla_afectada = models.CharField(max_length=255)
    registro_afectado = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.usuario or self.username_intentado} - {self.accion} ({self.timestamp})"

    def clean(self):
        if not self.usuario and not self.username_intentado:
            raise ValidationError("Debe proporcionarse 'usuario' o 'username_intentado'.")
        if not self.accion:
            raise ValidationError("El campo 'acción' es obligatorio.")
        if not self.tabla_afectada:
            raise ValidationError("El campo 'tabla_afectada' es obligatorio.")
        if not self.registro_afectado:
            raise ValidationError("El campo 'registro_afectado' es obligatorio.")




class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    grupo = models.OneToOneField(Group, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


from django.contrib.auth.models import BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, empresa=None, **extra_fields):
        if not empresa:
            raise ValueError("El campo empresa es obligatorio")
        if not username:
            raise ValueError('El usuario debe tener un nombre de usuario')
        email = self.normalize_email(email)

        # Aseguramos valores por defecto para los flags de estado
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('activo', True)  # Si usas este campo personalizado
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        user = self.model(
            username=username,
            email=email,
            empresa=empresa,
            **extra_fields  # Pasa todos los campos extra para asignarlos directo
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, empresa=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('activo', True)

        if empresa is None:
            raise ValueError("El superusuario debe tener una empresa asignada")

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(username, email, password, empresa=empresa, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='usuarios')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    # password = models.CharField(max_length=128)

    activo = models.BooleanField(default=True)  # si quieres mantenerlo aparte
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(default=timezone.now)
    foto = models.URLField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    idioma = models.CharField(max_length=10, default='es')
    tema = models.CharField(max_length=50, default='claro')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UsuarioManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
        indexes = [
            models.Index(fields=['empresa', 'username']),
            models.Index(fields=['rol', 'activo']),
        ]

    # def __str__(self):
    #     return self.username

    def __str__(self):
        empresa_nombre = self.empresa.nombre if self.empresa else "Sin empresa"
        return f"{self.username} ({self.email}) - {empresa_nombre}"

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

