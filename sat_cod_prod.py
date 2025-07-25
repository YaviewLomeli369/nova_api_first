import os
import django

# Configura Django antes de cualquier otra cosa
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_erp_total.settings')  # ← CAMBIA ESTO
django.setup()

# Ahora importa modelos (después de configurar Django)
from inventario.models import ClaveSATProducto, ClaveSATUnidad


# Lista con los datos (puedes reemplazar esto por lectura desde un archivo CSV si prefieres)
datos_sat = [
    ("01010101", "Por definir", "H87", "Pieza"),
    ("01010102", "Material eléctrico", "E48", "Metro"),
    ("01010103", "Servicios de construcción", "ACT", "Actividad"),
    ("01010104", "Equipo de computo", "EA", "Ea"),
    ("01010105", "Electrodomésticos", "EA", "Ea"),
    ("01010106", "Mobiliario", "EA", "Ea"),
    ("01010107", "Equipo de oficina", "EA", "Ea"),
    ("01010108", "Ropa", "EA", "Ea"),
    ("01010109", "Calzado", "EA", "Ea"),
    ("01010110", "Alimentos", "EA", "Ea"),
    ("01010111", "Bebidas", "EA", "Ea"),
    ("01010112", "Juguetes", "EA", "Ea"),
    ("01010113", "Herramientas", "EA", "Ea"),
    ("01010114", "Material de limpieza", "EA", "Ea"),
    ("01010115", "Productos farmacéuticos", "EA", "Ea"),
    ("01010116", "Servicios de consultoría", "ACT", "Actividad"),
    ("01010117", "Servicios legales", "ACT", "Actividad"),
    ("01010118", "Servicios contables", "ACT", "Actividad"),
    ("01010119", "Servicios médicos", "ACT", "Actividad"),
    ("01010120", "Servicios educativos", "ACT", "Actividad"),
    ("01010121", "Transporte terrestre", "E48", "Metro"),
    ("01010122", "Servicios de hospedaje", "ACT", "Actividad"),
    ("01010123", "Servicios de telecomunicaciones", "ACT", "Actividad"),
    ("01010124", "Software", "ACT", "Actividad"),
    ("01010125", "Servicios de publicidad", "ACT", "Actividad"),
    ("01010126", "Servicios financieros", "ACT", "Actividad"),
    ("01010127", "Servicios de mantenimiento", "ACT", "Actividad"),
    ("01010128", "Servicios de seguridad", "ACT", "Actividad"),
    ("01010129", "Servicios de limpieza", "ACT", "Actividad"),
    ("01010130", "Servicios de alimentación", "ACT", "Actividad"),
    ("01010131", "Servicios de entretenimiento", "ACT", "Actividad"),
    ("01010132", "Servicios de salud mental", "ACT", "Actividad"),
    ("01010133", "Servicios veterinarios", "ACT", "Actividad"),
    ("01010134", "Servicios de diseño gráfico", "ACT", "Actividad"),
    ("01010135", "Servicios de traducción", "ACT", "Actividad"),
    ("01010136", "Servicios de transporte aéreo", "EA", "Ea"),
    ("01010137", "Servicios de transporte marítimo", "EA", "Ea"),
    ("01010138", "Servicios de transporte ferroviario", "EA", "Ea"),
    ("01010139", "Servicios de paquetería", "EA", "Ea"),
    ("01010140", "Servicios de mensajería", "EA", "Ea"),
    ("01010141", "Servicios de reparación", "ACT", "Actividad"),
    ("01010142", "Servicios de consultoría tecnológica", "ACT", "Actividad"),
    ("01010143", "Servicios de desarrollo web", "ACT", "Actividad"),
    ("01010144", "Servicios de fotografía", "ACT", "Actividad"),
    ("01010145", "Servicios de impresión", "ACT", "Actividad"),
    ("01010146", "Servicios de auditoría", "ACT", "Actividad"),
    ("01010147", "Servicios de ingeniería", "ACT", "Actividad"),
    ("01010148", "Servicios de arquitectura", "ACT", "Actividad"),
    ("01010149", "Servicios de marketing", "ACT", "Actividad"),
    ("01010150", "Servicios de recursos humanos", "ACT", "Actividad"),
]

# Evitar duplicados en unidades
unidades_existentes = {}

for clave_prod, desc_prod, clave_uni, desc_uni in datos_sat:
    # Crear unidad si no existe
    if clave_uni not in unidades_existentes:
        unidad_obj, created = ClaveSATUnidad.objects.get_or_create(
            clave=clave_uni,
            defaults={"descripcion": desc_uni}
        )
        if not created and unidad_obj.descripcion != desc_uni:
            unidad_obj.descripcion = desc_uni
            unidad_obj.save()
        unidades_existentes[clave_uni] = unidad_obj
    else:
        unidad_obj = unidades_existentes[clave_uni]

    # Crear producto SAT (sin relación directa con unidad según tu modelo)
    ClaveSATProducto.objects.get_or_create(
        clave=clave_prod,
        defaults={"descripcion": desc_prod}
    )

print("✅ Claves SAT cargadas correctamente.")


from inventario.models import ClaveSATUnidad

# Datos proporcionados
datos_unidades = [
    ("H87", "Pieza"),
    ("E48", "Metro"),
    ("LTR", "Litro"),
    ("KGM", "Kilogramo"),
    ("GRM", "Gramo"),
    ("MTS", "Metro cuadrado"),
    ("MTK", "Metro cúbico"),  # corregido acento
    ("ACT", "Actividad"),
    ("C62", "Unidad de servicio"),
    ("EA", "Ea (Cada uno)"),
    ("HUR", "Horas"),
    ("MIN", "Minutos"),
    ("DAY", "Días"),          # corregido acento
    ("MO", "Meses"),
    ("ANN", "Años"),          # corregido acento
    ("CM", "Centímetro"),     # corregido acento
    ("MM", "Milímetro"),      # corregido acento
]

for clave, descripcion in datos_unidades:
    unidad, created = ClaveSATUnidad.objects.get_or_create(
        clave=clave,
        defaults={"descripcion": descripcion}
    )
    if not created and unidad.descripcion != descripcion:
        unidad.descripcion = descripcion
        unidad.save()

print("✅ Claves SAT Unidad cargadas correctamente.")