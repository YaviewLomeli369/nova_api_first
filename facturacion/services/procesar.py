from facturacion.models import ComprobanteFiscal
from facturacion.helpers.facturama import timbrar_cfdi_venta

def procesar_timbrado_venta(venta):
    try:
        cfdi = timbrar_cfdi_venta(venta)

        if "error" in cfdi:
            return ComprobanteFiscal.objects.create(
                empresa=venta.empresa,
                venta=venta,
                estado="ERROR",
                error_mensaje=cfdi["error"],
            )

        comprobante = ComprobanteFiscal.objects.create(
            empresa=venta.empresa,
            venta=venta,
            uuid=cfdi["Complement"]["TimbreFiscalDigital"]["Uuid"],
            xml=cfdi.get("Xml"),
            pdf=cfdi.get("Pdf"),
            serie=cfdi.get("Serie", "A"),
            folio=int(cfdi.get("Folio", 0)),
            estado="TIMBRADO",
            fecha_timbrado=cfdi.get("FechaTimbrado"),
        )
        return comprobante

    except Exception as e:
        return ComprobanteFiscal.objects.create(
            empresa=venta.empresa,
            venta=venta,
            estado="ERROR",
            error_mensaje=str(e),
        )

