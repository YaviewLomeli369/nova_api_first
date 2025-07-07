def registrar_auditoria(usuario=None, accion="", tabla="", registro="", username_intentado=None):
    from accounts.models import Auditoria

    if not usuario and not username_intentado:
        raise ValueError("Se debe proporcionar 'usuario' o 'username_intentado' para la auditoría.")

    Auditoria.objects.create(
        usuario=usuario if hasattr(usuario, 'id') else None,
        username_intentado=username_intentado,
        accion=accion,
        tabla_afectada=tabla,
        registro_afectado=str(registro)
    )

# def registrar_auditoria(usuario, accion, tabla, registro):
#   from accounts.models import Auditoria

#   Auditoria.objects.create(
#       usuario=usuario if hasattr(usuario, 'id') else None,
#       accion=accion,
#       tabla_afectada=tabla,
#       registro_afectado=str(registro)
#   )
