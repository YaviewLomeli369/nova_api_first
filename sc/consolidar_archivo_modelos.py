import os

# Nombre del archivo de salida
archivo_salida = 'todos_los_modelos_combinados.py'

# Extensión del archivo a buscar
archivo_objetivo = 'models.py'  # cambia a 'models.py' si es lo que querías

# Carpeta raíz del proyecto (desde donde ejecutas el script)
raiz_proyecto = '.'

# Lista para almacenar las rutas encontradas
rutas_models = []

# Buscar recursivamente todos los archivos models1.py
for carpeta, _, archivos in os.walk(raiz_proyecto):
    for archivo in archivos:
        if archivo == archivo_objetivo:
            ruta_completa = os.path.join(carpeta, archivo)
            rutas_models.append(ruta_completa)

# Escribir los contenidos en el archivo combinado
with open(archivo_salida, 'w', encoding='utf-8') as salida:
    for ruta in rutas_models:
        salida.write(f"# === Contenido de: {ruta} ===\n\n")
        with open(ruta, 'r', encoding='utf-8') as f:
            salida.write(f.read())
        salida.write("\n\n# === Fin de: {ruta} ===\n\n\n")

print(f"Modelos combinados guardados en '{archivo_salida}'. Total archivos encontrados: {len(rutas_models)}")