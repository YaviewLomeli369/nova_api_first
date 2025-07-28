def tipo_cfdi_desde_tipo_comprobante(tipo):
  """
  Convierte el tipo interno del comprobante ('FACTURA', 'NOTA_CREDITO', etc.)
  al tipo de CFDI que Facturama espera: 'I', 'E', 'N', etc.
  """
  mapeo = {
      "FACTURA": "I",           # Ingreso
      "NOTA_CREDITO": "E",      # Egreso
      "RECIBO_NOMINA": "N",     # Nómina
  }
  return mapeo.get(tipo, "I")  # Valor por defecto: Ingreso
