def serializar_filtros(validated_data):
  """
  Convierte los valores de validated_data a tipos compatibles con JSON,
  como string o número. Especialmente útil para fechas.
  """
  def serializar_valor(val):
      if hasattr(val, "isoformat"):
          return val.isoformat()
      elif isinstance(val, list):
          return [serializar_valor(v) for v in val]
      elif isinstance(val, dict):
          return {k: serializar_valor(v) for k, v in val.items()}
      return val

  return {k: serializar_valor(v) for k, v in validated_data.items()}
