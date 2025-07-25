import os
import django
from datetime import datetime
import sqlite3
from datetime import timezone as dt_timezone
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

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
from contabilidad.models import CuentaContable
from compras.models import Proveedor

DB_PATH = "db.sqlite3"
EXCLUDE_TABLES = {
    'l'
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
        {
            "nombre": "Superadministrador",
            "descripcion": (
                "Acceso completo al sistema, configuración técnica, gestión global de empresas, usuarios y permisos.\n"
                "- Acceso total (todas las apps)\n"
                "- Ver, crear, editar y borrar cualquier registro\n"
                "- Configuración de seguridad, backups, monitoreo"
            ),
            "grupo": None
        },
        {
            "nombre": "Administrador de Empresa",
            "descripcion": (
                "Administra una empresa específica, incluyendo empleados, inventario, ventas, finanzas, etc.\n"
                "- Ver y gestionar solo datos de su empresa\n"
                "- CRUD en empleados, usuarios, sucursales, ventas, compras, etc.\n"
                "- Ver reportes financieros\n"
                "- No puede tocar configuraciones globales ni otras empresas"
            ),
            "grupo": None
        },
        {
            "nombre": "Contador",
            "descripcion": (
                "Encargado de la contabilidad, asientos, reportes fiscales y conciliaciones.\n"
                "- Acceso completo a módulo de contabilidad y finanzas\n"
                "- Ver ventas y compras\n"
                "- Exportar datos\n"
                "- No puede modificar stock o ventas"
            ),
            "grupo": None
        },
        {
            "nombre": "Tesorero / Finanzas",
            "descripcion": (
                "Administra bancos, pagos, conciliaciones, deudas.\n"
                "- Ver cuentas por pagar/cobrar\n"
                "- Manejar pagos y bancos\n"
                "- Conciliar transacciones"
            ),
            "grupo": None
        },
        {
            "nombre": "Administrador de Compras / Proveedores",
            "descripcion": (
                "Encargado de compras y gestión de proveedores.\n"
                "- Crear órdenes y registrar compras\n"
                "- Ver productos y stock\n"
                "- Ver historial de proveedores"
            ),
            "grupo": None
        },
        {
            "nombre": "Almacén / Inventario",
            "descripcion": (
                "Administra entradas y salidas de productos, lotes, ubicaciones.\n"
                "- Ver productos, registrar movimientos\n"
                "- Crear y modificar inventario, alertas\n"
                "- No puede ver ventas ni modificar precios"
            ),
            "grupo": None
        },
        {
            "nombre": "Vendedor",
            "descripcion": (
                "Crea ventas y clientes. Puede aplicar devoluciones si tiene permiso.\n"
                "- Ver clientes\n"
                "- Crear ventas\n"
                "- Generar facturas\n"
                "- No puede modificar productos ni ver reportes contables"
            ),
            "grupo": None
        },
        {
            "nombre": "Auditor / Legal",
            "descripcion": (
                "Solo lectura de logs, documentos, movimientos contables y fiscales.\n"
                "- Lectura completa del sistema\n"
                "- Exportar CSV y PDF\n"
                "- No puede editar"
            ),
            "grupo": None
        },
        {
            "nombre": "Recursos Humanos",
            "descripcion": (
                "Administra empleados, asistencia y nómina.\n"
                "- Ver y modificar datos de empleados\n"
                "- Calcular y timbrar nóminas\n"
                "- Exportar registros de asistencia"
            ),
            "grupo": None
        },
        {
            "nombre": "Cliente externo",
            "descripcion": (
                "En el futuro: acceso limitado para consultar facturas, pagos o tickets.\n"
                "- Ver sus propias facturas y estado de cuenta\n"
                "- Ver historial de pagos\n"
                "- No puede ver otros módulos"
            ),
            "grupo": None
        }
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

    admin_user.set_password("admin1234")
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
    sucursal = Sucursal.objects.get(id=2)
    usuario = Usuario.objects.get(username="admin")

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

    # --- Crear stock inicial en Inventario y registrar movimientos ---
    cantidades_stock = {
        "PROD-001": Decimal("10"),
        "PROD-002": Decimal("20"),
        "PROD-003": Decimal("15"),
    }

    for info in productos_info:
        producto = Producto.objects.get(empresa=empresa, codigo=info["codigo"])
        cantidad = cantidades_stock.get(info["codigo"], Decimal("0"))

        if cantidad > 0:
            inventario, creado_inv = Inventario.objects.get_or_create(
                producto=producto,
                sucursal=sucursal,
                lote=None,
                fecha_vencimiento=None,
                defaults={"cantidad": cantidad}
            )
            if not creado_inv:
                inventario.cantidad += cantidad
                inventario.save()

            MovimientoInventario.objects.create(
                inventario=inventario,
                tipo_movimiento="entrada",
                cantidad=cantidad,
                usuario=usuario
            )

            print(f"✅ Stock inicial asignado para {producto.nombre}: {cantidad} unidades")


def crear_clientes_prueba():
    from ventas.models import Cliente
    empresa = Empresa.objects.get(id=4)

    clientes_demo = [
        {
            "nombre": "Cliente Demo 1",
            "rfc": "XAXX010101000",
            "correo": "cliente1@demo.com",
            "telefono": "5551234567",
            "direccion": "Calle Demo 123, Ciudad Demo",
        },
        {
            "nombre": "Cliente Demo 2",
            "rfc": "BADD010203AB1",
            "correo": "cliente2@demo.com",
            "telefono": "5559876543",
            "direccion": "Avenida Falsa 456, Ciudad Falsa",
        },
        {
            "nombre": "Cliente Demo 3",
            "rfc": None,
            "correo": "cliente3@demo.com",
            "telefono": None,
            "direccion": None,
        },
    ]

    for datos in clientes_demo:
        cliente, creado = Cliente.objects.update_or_create(
            empresa=empresa,
            nombre=datos["nombre"],
            defaults={
                "rfc": datos["rfc"],
                "correo": datos["correo"],
                "telefono": datos["telefono"],
                "direccion": datos["direccion"],
            }
        )
        print(f"{'🟢 Creado' if creado else '🟡 Actualizado'} cliente: {cliente.nombre}")


def crear_plan_contable_completo():
    empresa = Empresa.objects.get(id=4)
    cuentas_base = [
        {'codigo': '1010', 'nombre': 'Caja', 'clasificacion': 'activo', 'es_auxiliar': True},
        {'codigo': '1020', 'nombre': 'Bancos', 'clasificacion': 'activo', 'es_auxiliar': True},
        {'codigo': '2010', 'nombre': 'Proveedores', 'clasificacion': 'pasivo', 'es_auxiliar': True},
        {'codigo': '4010', 'nombre': 'Ventas', 'clasificacion': 'ingreso', 'es_auxiliar': True},
        {'codigo': '5010', 'nombre': 'Compras', 'clasificacion': 'gasto', 'es_auxiliar': True},

        # Cuentas faltantes para asientos de venta y compra:
        {'codigo': '1050', 'nombre': 'Clientes por cobrar', 'clasificacion': 'activo', 'es_auxiliar': True},
        {'codigo': '2080', 'nombre': 'IVA por pagar', 'clasificacion': 'pasivo', 'es_auxiliar': True},
        {'codigo': '1180', 'nombre': 'IVA por acreditar', 'clasificacion': 'activo', 'es_auxiliar': True},
    ]

    for cuenta in cuentas_base:
        cuenta_obj, creado = CuentaContable.objects.get_or_create(
            codigo=cuenta['codigo'],
            empresa=empresa,
            defaults={
                'nombre': cuenta['nombre'],
                'clasificacion': cuenta['clasificacion'],
                'es_auxiliar': cuenta['es_auxiliar'],
            }
        )
        if creado:
            print(f"✅ Cuenta creada: {cuenta_obj.codigo} - {cuenta_obj.nombre}")
        else:
            print(f"ℹ️ Cuenta ya existe: {cuenta_obj.codigo} - {cuenta_obj.nombre}")

def crear_proveedores_prueba():
    empresa = Empresa.objects.get(id=4)
    # Crear proveedores de prueba
    proveedores_prueba = [
        {
            'nombre': 'Proveedor Uno S.A. de C.V.',
            'rfc': 'PROV800101XXX',
            'correo': 'contacto@proveedoruno.com',
            'telefono': '5512345678',
            'direccion': 'Calle Falsa 123, Ciudad, País',
        },
        {
            'nombre': 'Distribuciones Globales S.A.',
            'rfc': 'DIST900202YYY',
            'correo': 'ventas@disglobal.com',
            'telefono': '5587654321',
            'direccion': 'Av. Principal 456, Ciudad, País',
        },
        {
            'nombre': 'Importaciones y Exportaciones del Norte',
            'rfc': 'IMPX700303ZZZ',
            'correo': 'info@importxnorte.mx',
            'telefono': '5543219876',
            'direccion': 'Blvd. Industrial 789, Ciudad, País',
        }
    ]

    for prov_data in proveedores_prueba:
        prov_obj, creado = Proveedor.objects.get_or_create(
            empresa=empresa,
            rfc=prov_data['rfc'],
            defaults={
                'nombre': prov_data['nombre'],
                'correo': prov_data['correo'],
                'telefono': prov_data['telefono'],
                'direccion': prov_data['direccion'],
            }
        )
        if creado:
            print(f"✅ Proveedor creado: {prov_obj.nombre} ({prov_obj.rfc})")
        else:
            print(f"ℹ️ Proveedor ya existe: {prov_obj.nombre} ({prov_obj.rfc})")





if __name__ == "__main__":
    limpiar_tablas_y_crear_empresa_sucursal()
    crear_actualizar_roles()
    crear_actualizar_superusuario()
    cargar_claves_sat()
    cargar_claves_sat_unidad()
    crear_productos_ejemplo()
    # crear_compras_y_actualizar_inventario()
    crear_clientes_prueba()  # << aquí la llamas
    crear_plan_contable_completo()
    crear_proveedores_prueba()