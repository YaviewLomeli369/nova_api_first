from django.core.management.base import BaseCommand
from facturacion.models import ComprobanteFiscal
from facturacion.services.consultar_estado_cfdi import consultar_estado_cfdi
from django.utils import timezone

class Command(BaseCommand):
    help = 'Consulta el estado SAT de los CFDIs timbrados y actualiza el modelo'

    def handle(self, *args, **options):
        comprobantes = ComprobanteFiscal.objects.filter(estado='TIMBRADO', uuid__isnull=False)

        for c in comprobantes:
            try:
                if not (c.empresa.rfc and c.venta.cliente.rfc and c.venta.total):
                    self.stdout.write(f"⚠️ Saltando comprobante {c.id}: datos incompletos.")
                    continue

                estado_info = consultar_estado_cfdi(
                    uuid=c.uuid,
                    issuer_rfc=c.empresa.rfc,
                    receiver_rfc=c.venta.cliente.rfc,
                    total=c.venta.total
                )

                estado_sat = estado_info.get("Estado", "SIN RESPUESTA")
                c.estado_sat = estado_sat
                c.fecha_estado_sat = timezone.now()
                c.save(update_fields=["estado_sat", "fecha_estado_sat"])

                self.stdout.write(f"✅ {c.uuid} → Estado SAT: {estado_sat}")

            except Exception as e:
                mensaje_error = str(e)
                if "pruebacfdiconsultaqr.cloudapp.net" in mensaje_error:
                    # Error típico del sandbox de Facturama
                    c.estado_sat = "NO DISPONIBLE (SANDBOX)"
                    c.fecha_estado_sat = timezone.now()
                    c.save(update_fields=["estado_sat", "fecha_estado_sat"])
                    self.stdout.write(f"🟡 {c.uuid} → Estado no disponible en sandbox.")
                else:
                    self.stderr.write(f"[ERROR] {c.uuid}: {mensaje_error}")
# from django.core.management.base import BaseCommand
# from facturacion.models import ComprobanteFiscal
# from facturacion.services.consultar_estado_cfdi import consultar_estado_cfdi
# from django.utils import timezone

# class Command(BaseCommand):
#     help = 'Consulta el estado SAT de los CFDIs timbrados y actualiza el modelo'

#     def handle(self, *args, **options):
#         comprobantes = ComprobanteFiscal.objects.filter(estado='TIMBRADO', uuid__isnull=False)
    
#         for c in comprobantes:
#             try:
#                 if not (c.empresa.rfc and c.venta.cliente.rfc and c.venta.total):
#                     self.stdout.write(f"⚠️ Saltando comprobante {c.id}: datos incompletos.")
#                     continue
    
#                 estado_info = consultar_estado_cfdi(
#                     uuid=c.uuid,
#                     issuer_rfc=c.empresa.rfc,
#                     receiver_rfc=c.venta.cliente.rfc,
#                     total=c.venta.total
#                 )
    
#                 c.estado_sat = estado_info.get("Estado")
#                 c.fecha_estado_sat = timezone.now()
#                 c.save(update_fields=["estado_sat", "fecha_estado_sat"])
    
#                 self.stdout.write(f"✅ {c.uuid} → Estado SAT: {c.estado_sat}")
    
#             except Exception as e:
#                 self.stderr.write(f"[ERROR] {c.uuid}: {str(e)}")

   