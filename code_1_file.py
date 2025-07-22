import os

def combine_output_files(output_dir, final_output_file):
    with open(final_output_file, 'w') as outfile:
        for file_name in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file_name)

            # Verifica que sea un archivo .py
            if os.path.isfile(file_path) and file_path.endswith('.py'):
                print(f"Agregando {file_path} al archivo final")

                # Escribe un comentario para indicar de qué archivo proviene
                outfile.write(f"\n# === Archivo: {file_name} ===\n")

                with open(file_path, 'r') as infile:
                    outfile.write(infile.read())
                    outfile.write("\n\n")  # Separador entre archivos

if __name__ == "__main__":
    # Define la carpeta de salida y el archivo final
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, 'salida')
    final_output_file = os.path.join(current_dir, 'todo_combinado.py')

    combine_output_files(output_dir, final_output_file)
    print(f"\n✅ Todos los archivos combinados en: {final_output_file}")
