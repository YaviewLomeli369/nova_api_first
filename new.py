import os
import django
from datetime import datetime
import sqlite3
from datetime import timezone as dt_timezone

# Configura la variable de entorno para indicar dónde están los settings de tu proyecto Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_erp_total.settings')  # Ajusta esta ruta

# Inicializa Django
django.setup()

from accounts.models import Rol, Usuario
from core.models import Empresa, Sucursal
from inventario.models import (
    ClaveSATUnidad, ClaveSATProducto,
    Categoria, Producto,
    Inventario, MovimientoInventario
)
from compras.models import Proveedor, Compra, DetalleCompra
from accounts.models import Empresa, Usuario
from core.models import Sucursal

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

def limpiar_tablas_y_crear_empresa_sucursal():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = OFF;")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    tables_to_delete = [t for t in tables if t not in EXCLUDE_TABLES]

    print("Tablas que serán limpiadas:")
    for table in tables_to_delete:
        print(f" - {table}")
        cursor.execute(f"DELETE FROM {table};")

    now = datetime.now().isoformat(sep=' ', timespec='seconds')

    cursor.execute("SELECT id FROM core_empresa WHERE id = 4;")
    if not cursor.fetchone():
        print("Empresa ID 4 no existe. Creando...")
        cursor.execute("""
            INSERT INTO core_empresa (
                id, nombre, rfc, domicilio_fiscal, regimen_fiscal, creado_en, actualizado_en, razon_social
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (4, "Empresa del Superusuario", "XAXX010101000", "Domicilio demo", "Régimen General", now, now, "Razón Social Demo"))
    else:
        print("Empresa ID 4 ya existe.")

    cursor.execute("SELECT id FROM core_sucursal WHERE id = 2;")
    if not cursor.fetchone():
        print("Sucursal ID 2 no existe. Creando...")
        cursor.execute("""
            INSERT INTO core_sucursal (
                id, empresa_id, nombre, direccion, creado_en, actualizado_en
            ) VALUES (?, ?, ?, ?, ?, ?);
        """, (2, 4, "Sucursal Principal", "Dirección demo", now, now))
    else:
        print("Sucursal ID 2 ya existe.")

    cursor.execute("PRAGMA foreign_keys = ON;")

    conn.commit()
    conn.close()
    print("\n¡Limpieza completada, empresa y sucursal aseguradas!")

def crear_actualizar_roles():
    datos_roles = [
        #... tus roles aquí ...
    ]

    for rol_data in datos_roles:
        rol, creado = Rol.objects.update_or_create(
            nombre=rol_data['nombre'],
            defaults={
                'descripcion': rol_data['descripcion'],
                'grupo': None
            }
        )
        print(f"{'🟢 Creado' if creado else '🟡 Actualizado'}: {rol.nombre}")

def crear_actualizar_superusuario():
    empresa, _ = Empresa.objects.get_or_create(
        id=4,
        defaults={"nombre": "Mi Empresa"}
    )

    sucursal, _ = Sucursal.objects.get_or_create(
        id=2,
        defaults={"nombre": "Sucursal Central", "empresa": empresa}
    )

    rol, _ = Rol.objects.get_or_create(
        id=2,
        defaults={"nombre": "Administrador"}
    )

    admin_user, created = Usuario.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@empresa.com",
            "empresa": empresa,
            "sucursal_actual": sucursal,
            "rol": rol,
            "activo": True,
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "idioma": "es",
            "tema": "claro",
            "fecha_creacion": datetime(2025, 7, 15, 21, 35, 57, 332198, tzinfo=dt_timezone.utc),
            "foto": None,
            "telefono": None,
            "direccion": None
        }
    )

    if not created:
        # Actualiza campos si ya existía el usuario
        admin_user.id = 9
        admin_user.email = "admin@empresa.com"
        admin_user.empresa = empresa
        admin_user.sucursal_actual = sucursal
        admin_user.rol = rol
        admin_user.activo = True
        admin_user.is_active = True
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.idioma = "es"
        admin_user.tema = "claro"
        admin_user.fecha_creacion = datetime(2025, 7, 15, 21, 35, 57, 332198, tzinfo=dt_timezone.utc)
        admin_user.foto = None
        admin_user.telefono = None
        admin_user.direccion = None

    admin_user.set_password("admin1234")  # Encripta la contraseña
    admin_user.save()

    print(f"Superusuario {'creado' if created else 'actualizado'}: {admin_user.username} ({admin_user.email})")




def cargar_claves_sat():
    from inventario.models import ClaveSATProducto, ClaveSATUnidad

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

    unidades_existentes = {}

    for clave_prod, desc_prod, clave_uni, desc_uni in datos_sat:
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

        ClaveSATProducto.objects.get_or_create(
            clave=clave_prod,
            defaults={"descripcion": desc_prod}
        )

    print("✅ Claves SAT cargadas correctamente.")

def cargar_claves_sat_unidad():
    from inventario.models import ClaveSATUnidad

    datos_unidades = [
        ("H87", "Pieza"),
        ("E48", "Metro"),
        ("LTR", "Litro"),
        ("KGM", "Kilogramo"),
        ("GRM", "Gramo"),
        ("MTS", "Metro cuadrado"),
        ("MTK", "Metro cúbico"),
        ("ACT", "Actividad"),
        ("C62", "Unidad de servicio"),
        ("EA", "Ea (Cada uno)"),
        ("HUR", "Horas"),
        ("MIN", "Minutos"),
        ("DAY", "Días"),
        ("MO", "Meses"),
        ("ANN", "Años"),
        ("CM", "Centímetro"),
        ("MM", "Milímetro"),
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




def crear_productos_ejemplo():
    empresa = Empresa.objects.get(id=4)

    # Crear unidades SAT necesarias
    unidades = {
        "EA": "Ea (Cada uno)",
        "H87": "Pieza",
        "E48": "Metro"
    }
    for clave, desc in unidades.items():
        ClaveSATUnidad.objects.get_or_create(clave=clave, defaults={"descripcion": desc})

    # Crear claves SAT producto
    claves_sat = {
        "01010101": "Por definir",
        "01010104": "Equipo de computo",
        "01010108": "Ropa"
    }
    for clave, desc in claves_sat.items():
        ClaveSATProducto.objects.get_or_create(clave=clave, defaults={"descripcion": desc})

    # Crear categorías
    categorias = [
        ("Equipos", "Equipos de computo y accesorios"),
        ("Ropa", "Prendas y accesorios de vestir"),
    ]
    categoria_objs = {}
    for nombre, desc in categorias:
        cat, _ = Categoria.objects.get_or_create(empresa=empresa, nombre=nombre, defaults={"descripcion": desc})
        categoria_objs[nombre] = cat

    # Obtener unidades y claves SAT para asignar
    unidad_ea = ClaveSATUnidad.objects.get(clave="EA")
    unidad_h87 = ClaveSATUnidad.objects.get(clave="H87")

    clave_equipo = ClaveSATProducto.objects.get(clave="01010104")
    clave_ropa = ClaveSATProducto.objects.get(clave="01010108")

    # Crear productos de ejemplo
    productos_info = [
        {
            "codigo": "PROD-001",
            "nombre": "Laptop XYZ",
            "descripcion": "Laptop de alta gama para oficina",
            "unidad_medida": unidad_ea,
            "categoria": categoria_objs["Equipos"],
            "precio_compra": Decimal("12000.00"),
            "precio_venta": Decimal("15000.00"),
            "stock_minimo": Decimal("3"),
            "activo": True,
            "clave_sat": clave_equipo,
        },
        {
            "codigo": "PROD-002",
            "nombre": "Camisa Formal",
            "descripcion": "Camisa para oficina talla M",
            "unidad_medida": unidad_h87,
            "categoria": categoria_objs["Ropa"],
            "precio_compra": Decimal("200.00"),
            "precio_venta": Decimal("350.00"),
            "stock_minimo": Decimal("10"),
            "activo": True,
            "clave_sat": clave_ropa,
        },
        {
            "codigo": "PROD-003",
            "nombre": "Mouse Inalámbrico",
            "descripcion": "Mouse inalámbrico para laptop",
            "unidad_medida": unidad_ea,
            "categoria": categoria_objs["Equipos"],
            "precio_compra": Decimal("150.00"),
            "precio_venta": Decimal("250.00"),
            "stock_minimo": Decimal("5"),
            "activo": True,
            "clave_sat": clave_equipo,
        },
    ]

    for info in productos_info:
        prod, creado = Producto.objects.get_or_create(
            empresa=empresa,
            codigo=info["codigo"],
            defaults=info
        )
        if creado:
            print(f"✅ Producto creado: {prod.nombre}")
        else:
            print(f"ℹ️ Producto ya existe: {prod.nombre}")

def crear_compras_y_actualizar_inventario():
    empresa = Empresa.objects.get(id=4)
    sucursal = Sucursal.objects.get(id=2)
    usuario = Usuario.objects.get(username="admin")

    proveedor, _ = Proveedor.objects.get_or_create(
        empresa=empresa,
        rfc="XAXX010101000",
        defaults={"nombre": "Proveedor Genérico S.A. de C.V."}
    )

    productos = list(Producto.objects.filter(empresa=empresa)[:3])

    compra, creada = Compra.objects.get_or_create(
        empresa=empresa,
        proveedor=proveedor,
        fecha=timezone.now(),
        defaults={
            "estado": "pendiente",
            "usuario": usuario,
            "total": Decimal("0.00"),
        }
    )
    if creada:
        print(f"✅ Compra creada (ID: {compra.id})")
    else:
        print(f"ℹ️ Compra ya existía (ID: {compra.id})")

    total_compra = Decimal("0.00")

    for i, producto in enumerate(productos):
        lote = f"LOTE-{i+1:03d}"
        fecha_vencimiento = timezone.now().date() + timedelta(days=30 * (i + 1))
        cantidad = Decimal(10 + i*5)  # cantidades ejemplo: 10, 15, 20
        precio_unitario = producto.precio_compra

        detalle, creado = DetalleCompra.objects.get_or_create(
            compra=compra,
            producto=producto,
            lote=lote,
            fecha_vencimiento=fecha_vencimiento,
            defaults={
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "cantidad_recibida": Decimal("0.00"),
            }
        )

        if creado:
            print(f"✅ DetalleCompra creado para producto '{producto.nombre}' lote '{lote}'")
        else:
            print(f"ℹ️ DetalleCompra ya existía para producto '{producto.nombre}' lote '{lote}'")

        # Actualizar inventario: obtener o crear registro para ese producto, sucursal, lote y fecha venc.
        inventario, _ = Inventario.objects.get_or_create(
            producto=producto,
            sucursal=sucursal,
            lote=lote,
            fecha_vencimiento=fecha_vencimiento,
            defaults={"cantidad": Decimal("0.00")}
        )
        # Sumar cantidad recibida (simulamos que ya fue recibida toda la compra)
        inventario.cantidad += cantidad
        inventario.save()

        # Registrar movimiento de inventario
        MovimientoInventario.objects.create(
            inventario=inventario,
            tipo_movimiento='entrada',
            cantidad=cantidad,
            usuario=usuario
        )
        total_compra += cantidad * precio_unitario

    # Actualizar total de compra
    compra.total = total_compra
    compra.estado = 'recibida'
    compra.save()

    print(f"💰 Total compra actualizado a: {total_compra}")

if __name__ == "__main__":
    crear_productos_ejemplo()
    crear_compras_y_actualizar_inventario()


def crear_ejemplos_compras():
    from compras.models import Proveedor, Compra, DetalleCompra
    from inventario.models import Producto
    from accounts.models import Empresa, Usuario
    from django.utils import timezone
    from decimal import Decimal
    import random

    empresa = Empresa.objects.get(id=4)
    usuario = Usuario.objects.get(username="admin")

    # Crear proveedor de ejemplo
    proveedor, creado = Proveedor.objects.get_or_create(
        empresa=empresa,
        rfc="XAXX010101000",
        defaults={
            "nombre": "Proveedor Genérico S.A. de C.V.",
            "correo": "proveedor@ejemplo.com",
            "telefono": "555-123-4567",
            "direccion": "Calle Ficticia 123, CDMX",
        }
    )
    if creado:
        print("✅ Proveedor creado.")
    else:
        print("ℹ️ Proveedor ya existía.")

    # Obtener hasta 5 productos
    productos = Producto.objects.filter(empresa=empresa)[:5]
    if not productos.exists():
        print("❌ No hay productos en la base de datos. Crea productos primero.")
        return

    # Crear compra
    compra, creada = Compra.objects.get_or_create(
        empresa=empresa,
        proveedor=proveedor,
        fecha=timezone.now(),
        total=Decimal("0.00"),
        defaults={
            "estado": "pendiente",
            "usuario": usuario,
        }
    )
    if creada:
        print(f"✅ Compra creada (ID: {compra.id})")
    else:
        print("ℹ️ Compra ya existía.")

    total_compra = Decimal("0.00")

    for i, producto in enumerate(productos):
        lote = f"LOTE-{i+1:03d}"
        fecha_vencimiento = timezone.now().date() + timezone.timedelta(days=30 * (i + 1))
        cantidad = Decimal(random.randint(5, 20))
        precio_unitario = Decimal(random.randint(50, 200))

        detalle, creado = DetalleCompra.objects.get_or_create(
            compra=compra,
            producto=producto,
            lote=lote,
            fecha_vencimiento=fecha_vencimiento,
            defaults={
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
            }
        )

        if creado:
            print(f"✅ Detalle creado para '{producto.nombre}' (lote {lote})")
            total_compra += cantidad * precio_unitario
        else:
            print(f"ℹ️ Ya existía detalle para '{producto.nombre}' (lote {lote})")

    # Actualizar total y guardar compra
    compra.total = total_compra
    compra.save()
    print(f"💰 Total de la compra actualizado: ${total_compra}")




if __name__ == "__main__":
    limpiar_tablas_y_crear_empresa_sucursal()
    crear_actualizar_roles()
    crear_actualizar_superusuario()
    cargar_claves_sat()
    cargar_claves_sat_unidad()
    crear_productos_ejemplo()
    crear_compras_y_actualizar_inventario()
    crear_ejemplos_compras()
