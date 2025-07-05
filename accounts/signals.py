# accounts/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from accounts.models import Auditoria, Usuario
from django.conf import settings
import threading

# Hilo-local para almacenar temporalmente el usuario
_local = threading.local()

def set_audit_user(user):
    _local.user = user

def get_audit_user():
    return getattr(_local, 'user', None)


def registrar_auditoria(instance, accion):
    modelo = instance.__class__.__name__
    usuario = get_audit_user()
    if not usuario or not isinstance(usuario, Usuario):
        return

    Auditoria.objects.create(
        usuario=usuario,
        accion=accion,
        tabla_afectada=modelo,
        registro_afectado=str(instance)
    )

# --- Señales globales ---

@receiver(post_save)
def auditoria_crear_modificar(sender, instance, created, **kwargs):
    if sender._meta.app_label in ['accounts', 'ventas', 'compras', 'inventario']:
        accion = "CREADO" if created else "MODIFICADO"
        registrar_auditoria(instance, accion)

@receiver(post_delete)
def auditoria_eliminar(sender, instance, **kwargs):
    if sender._meta.app_label in ['accounts', 'ventas', 'compras', 'inventario']:
        registrar_auditoria(instance, "ELIMINADO")
