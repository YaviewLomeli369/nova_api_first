import os

def dividir_texto_por_caracteres(texto, max_caracteres=15000):
    partes = []
    inicio = 0
    texto_len = len(texto)

    while inicio < texto_len:
        fin = inicio + max_caracteres
        if fin >= texto_len:
            partes.append(texto[inicio:])
            break
        espacio = texto.rfind(' ', inicio, fin)
        if espacio == -1 or espacio <= inicio:
            espacio = fin
        parte = texto[inicio:espacio]
        partes.append(parte)
        inicio = espacio + 1
    return partes

def guardar_partes(partes, carpeta_salida="salida", base_nombre="parte"):
    os.makedirs(carpeta_salida, exist_ok=True)
    for idx, parte in enumerate(partes, 1):
        nombre_archivo = os.path.join(carpeta_salida, f"{base_nombre}_{idx}.txt")
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(parte)
        print(f"✅ Guardado: {nombre_archivo}")

def guardar_resumen(partes, carpeta_salida="salida", nombre_resumen="resumen_dividido.txt"):
    os.makedirs(carpeta_salida, exist_ok=True)
    ruta_resumen = os.path.join(carpeta_salida, nombre_resumen)
    with open(ruta_resumen, "w", encoding="utf-8") as f:
        for idx, parte in enumerate(partes, 1):
            f.write(parte)
            if idx != len(partes):
                f.write("\n---------------------------------\n")
    print(f"✅ Archivo resumen guardado: {ruta_resumen}")

if __name__ == "__main__":
    nombre_archivo_entrada = "texto_largo.txt"
    max_caracteres_por_parte = 15000
    carpeta_destino = "salida"

    if not os.path.isfile(nombre_archivo_entrada):
        print(f"❌ Archivo no encontrado: {nombre_archivo_entrada}")
        print("Verifica que el archivo exista y esté en la misma carpeta.")
        exit()

    with open(nombre_archivo_entrada, "r", encoding="utf-8") as f:
        texto = f.read()

    partes = dividir_texto_por_caracteres(texto, max_caracteres=max_caracteres_por_parte)

    guardar_partes(partes, carpeta_salida=carpeta_destino)
    guardar_resumen(partes, carpeta_salida=carpeta_destino)
