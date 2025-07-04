import os
import django

# Inicializa Django (esto es importante si necesitas cargar configuraciones de tu proyecto Django)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_erp_total.settings')  # Asegúrate de que este sea el nombre correcto del módulo de configuración
django.setup()

def combine_files(app_path, output_file):
    with open(output_file, 'w') as outfile:
        # Recorre todos los archivos dentro de la app
        for root, dirs, files in os.walk(app_path):
            for file in files:
                # Solo archivos .py, no archivos .pyc
                if file.endswith('.py') and not file.endswith('.pyc'):
                    file_path = os.path.join(root, file)
                    print(f"Procesando {file_path}")

                    # Agregar un comentario con el nombre del archivo
                    outfile.write(f"\n# --- {file_path} ---\n")

                    # Leer el contenido del archivo y escribirlo en el archivo de salida
                    with open(file_path, 'r') as infile:
                        outfile.write(infile.read())
                        outfile.write("\n\n")  # Separador entre archivos

def process_all_apps(project_root):
    # Buscar todas las carpetas de apps dentro del directorio raíz del proyecto
    for app_name in os.listdir(project_root):
        app_path = os.path.join(project_root, app_name)

        # Verificar si es una carpeta y si contiene un archivo __init__.py, lo que indica que es una app de Django
        if os.path.isdir(app_path) and os.path.exists(os.path.join(app_path, '__init__.py')):
            output_file = f"{app_name}_combined.py"
            print(f"Combinando archivos para la app: {app_name}")
            combine_files(app_path, output_file)
            print(f"Archivos de la app '{app_name}' combinados en '{output_file}'")

if __name__ == "__main__":
    project_root = os.getcwd()  # Obtiene el directorio actual del proyecto
    process_all_apps(project_root)
