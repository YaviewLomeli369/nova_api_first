# core/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from core.models import Empresa
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Empresa)
def log_empresa_save(sender, instance, created, **kwargs):
    accion = "Creada" if created else "Actualizada"
    # Aquí puedes usar instance.modified_by si guardas usuario en el modelo Empresa
    # O dejar "desconocido" si no tienes
    usuario = getattr(instance, 'modified_by', None)
    usuario_str = usuario.username if usuario else 'desconocido'
    print(f"Empresa {accion}: {instance.razon_social} por usuario {usuario_str} en {now()}")

@receiver(post_delete, sender=Empresa)
def log_empresa_delete(sender, instance, **kwargs):
    print(f"Empresa Eliminada: {instance.razon_social} en {now()}")
