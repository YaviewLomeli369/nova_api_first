import sqlite3
from datetime import datetime

DB_PATH = "db.sqlite3"
EXCLUDE_TABLES = {
    'accounts_auditoria',
    'accounts_rol',
    'accounts_usuario',
    'accounts_usuario_groups',
    'accounts_usuario_user_permissions',
    'core_empresa',
    'core_sucursal'
}

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Desactivar claves foráneas para evitar errores al borrar
    cursor.execute("PRAGMA foreign_keys = OFF;")

    # Obtener todas las tablas excepto las que queremos excluir
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    tables_to_delete = [t for t in tables if t not in EXCLUDE_TABLES]

    print("Tablas que serán limpiadas:")
    for table in tables_to_delete:
        print(f" - {table}")
        cursor.execute(f"DELETE FROM {table};")

    now = datetime.now().isoformat(sep=' ', timespec='seconds')

    # Crear empresa ID=4 si no existe
    print("\nVerificando existencia de empresa con ID 4...")
    cursor.execute("SELECT id FROM core_empresa WHERE id = 4;")
    result = cursor.fetchone()

    if not result:
        print("Empresa ID 4 no existe. Creando...")
        cursor.execute("""
            INSERT INTO core_empresa (
                id, nombre, rfc, domicilio_fiscal, regimen_fiscal, creado_en, actualizado_en, razon_social
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            4,
            "Empresa del Superusuario",
            "XAXX010101000",  # RFC genérico válido
            "Domicilio demo",
            "Régimen General",
            now,
            now,
            "Razón Social Demo"
        ))
    else:
        print("Empresa ID 4 ya existe.")

    # Crear sucursal ID=2 si no existe
    print("\nVerificando existencia de sucursal con ID 2...")
    cursor.execute("SELECT id FROM core_sucursal WHERE id = 2;")
    result = cursor.fetchone()

    if not result:
        print("Sucursal ID 2 no existe. Creando...")
        cursor.execute("""
            INSERT INTO core_sucursal (
                id, empresa_id, nombre, direccion, creado_en, actualizado_en
            )
            VALUES (?, ?, ?, ?, ?, ?);
        """, (
            2,
            4,  # empresa_id
            "Sucursal Principal",
            "Dirección demo",
            now,
            now
        ))
    else:
        print("Sucursal ID 2 ya existe.")

    # Reactivar claves foráneas
    cursor.execute("PRAGMA foreign_keys = ON;")

    conn.commit()
    conn.close()
    print("\n¡Limpieza completada, empresa y sucursal aseguradas!")

if __name__ == "__main__":
    main()