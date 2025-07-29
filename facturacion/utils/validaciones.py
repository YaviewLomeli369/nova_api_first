# facturacion/utils/validaciones.py

import re

def validar_rfc(rfc):
    return bool(re.match(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$", rfc or ""))

def validar_clave_unidad(clave):
    return bool(re.match(r"^[A-Z0-9]{1,5}$", clave or ""))

def validar_datos_fiscales(comprobante):
    errores = {}

    cliente = comprobante.venta.cliente
    empresa = comprobante.empresa
    detalles = comprobante.venta.detalles.all()

    # Cliente
    cliente_errores = {}
    if not validar_rfc(cliente.rfc):
        cliente_errores['rfc'] = "RFC inválido o ausente"
    if not cliente.direccion_codigo_postal:
        cliente_errores['direccion_codigo_postal'] = "Código postal faltante"
    if not cliente.uso_cfdi:
        cliente_errores['uso_cfdi'] = "Uso CFDI no definido"

    if cliente_errores:
        errores['cliente'] = cliente_errores

    # Empresa
    empresa_errores = {}
    if not empresa.rfc or not validar_rfc(empresa.rfc):
        empresa_errores['rfc'] = "RFC inválido o ausente"
    if not empresa.regimen_fiscal:
        empresa_errores['regimen_fiscal'] = "Régimen fiscal faltante"

    if empresa_errores:
        errores['empresa'] = empresa_errores

    # Productos
    productos_errores = []
    for d in detalles:
        p = d.producto
        if not p.clave_sat:
            productos_errores.append({
                "id": p.id,
                "error": "Producto sin clave SAT"
            })
        if not p.unidad_medida or not validar_clave_unidad(p.unidad_medida.clave):
            productos_errores.append({
                "id": p.id,
                "error": "Unidad de medida ausente o inválida"
            })

    if productos_errores:
        errores['productos'] = productos_errores

    # Método y forma de pago
    if not comprobante.metodo_pago:
        errores['metodo_pago'] = "Método de pago no definido"
    if not comprobante.forma_pago:
        errores['forma_pago'] = "Forma de pago no definida"

    if errores:
        return {"ok": False, "errores": errores}
    return {"ok": True}
