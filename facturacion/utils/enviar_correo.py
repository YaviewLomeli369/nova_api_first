from django.core.mail import EmailMessage
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

def enviar_cfdi_por_correo(email_destino, comprobante):
    """
    Envía el CFDI (PDF + XML) como adjuntos al email del cliente.
    """
    if not email_destino:
        raise ValueError("El cliente no tiene un correo electrónico válido.")

    asunto = f"Factura electrónica {comprobante.serie or ''}-{comprobante.folio or ''}".strip("- ")
    cuerpo = (
        f"Estimado cliente,\n\nAdjuntamos su factura electrónica.\n\n"
        f"Gracias por su preferencia.\n\nSaludos,\nNova ERP"
    )

    email = EmailMessage(
        asunto,
        cuerpo,
        settings.DEFAULT_FROM_EMAIL,
        [email_destino],
    )

    try:
        # Adjuntar PDF leyendo contenido directamente
        if comprobante.pdf and comprobante.pdf.path and os.path.exists(comprobante.pdf.path):
            with open(comprobante.pdf.path, 'rb') as f:
                email.attach(f'cfdi_{comprobante.id}.pdf', f.read(), 'application/pdf')
        else:
            logger.warning(f"Archivo PDF no encontrado para comprobante {comprobante.id}")

        # Adjuntar XML leyendo contenido directamente
        if comprobante.xml and comprobante.xml.path and os.path.exists(comprobante.xml.path):
            with open(comprobante.xml.path, 'rb') as f:
                email.attach(f'cfdi_{comprobante.id}.xml', f.read(), 'application/xml')
        else:
            logger.warning(f"Archivo XML no encontrado para comprobante {comprobante.id}")

        email.send(fail_silently=False)
        logger.info(f"Correo enviado a {email_destino} con comprobante {comprobante.id}")

        # 🔥 Marcar como enviado si todo fue bien
        comprobante.correo_enviado = True
        comprobante.save(update_fields=['correo_enviado'])

    except Exception as e:
        logger.error(f"Error enviando correo con comprobante {comprobante.id}: {e}")
        raise
