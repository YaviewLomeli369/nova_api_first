import os
import django

# Define el archivo de configuración de Django (ajustalo según el nombre de tu archivo de settings)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_erp_total.settings')

django.setup()

# Ahora puedes importar tus modelos
from core.models import Empresa
# Resto del código



#CREAR DATOS PRUEBA VENTAS



# Importamos los modelos necesarios
from core.models import Empresa, Sucursal
from accounts.models import Usuario
from ventas.models import Cliente, Venta, DetalleVenta
from inventario.models import Categoria, Producto, Inventario, MovimientoInventario
from django.utils import timezone

# 1. Crear una empresa
empresa = Empresa.objects.create(
    nombre="Mi Empresa",
    rfc="AAA010101AAA",
    domicilio_fiscal="Av. Siempre Viva 123, Ciudad, País",
    regimen_fiscal="Régimen General de Ley Personas Morales"
)

# 2. Crear una sucursal asociada a la empresa
sucursal = Sucursal.objects.create(
    empresa=empresa,
    nombre="Sucursal Principal",
    direccion="Av. Principal 456, Ciudad"
)

# 3. Crear un usuario asociado a la empresa
usuario = Usuario.objects.create(
    empresa=empresa,
    username="admin_venta",
    email="admin_ventaa@miempresa.com",
    password="password123",  # Recuerda que la contraseña debe ser cifrada
    is_active=True,
    is_superuser=False,
    fecha_creacion=timezone.now()
)

# 4. Crear categorías de productos
categoria1 = Categoria.objects.create(
    empresa=empresa,
    nombre="Electrónica",
    descripcion="Productos electrónicos diversos"
)

categoria2 = Categoria.objects.create(
    empresa=empresa,
    nombre="Ropa",
    descripcion="Ropa y accesorios"
)

# 5. Crear productos
producto1 = Producto.objects.create(
    empresa=empresa,
    codigo="P001",
    nombre="Smartphone",
    descripcion="Smartphone de última generación",
    unidad_medida="Unidad",
    categoria=categoria1,
    precio_compra=500.00,
    precio_venta=800.00,
    stock_minimo=5
)

producto2 = Producto.objects.create(
    empresa=empresa,
    codigo="P002",
    nombre="Camiseta",
    descripcion="Camiseta de algodón",
    unidad_medida="Unidad",
    categoria=categoria2,
    precio_compra=10.00,
    precio_venta=20.00,
    stock_minimo=10
)

# 6. Crear clientes
cliente1 = Cliente.objects.create(
    empresa=empresa,
    nombre="Cliente A",
    rfc="AAA010101AAA",
    correo="cliente_a@correo.com",
    telefono="5551234567",
    direccion="Calle Ficticia 456, Ciudad"
)

cliente2 = Cliente.objects.create(
    empresa=empresa,
    nombre="Cliente B",
    rfc="BBB020202BBB",
    correo="cliente_b@correo.com",
    telefono="5557654321",
    direccion="Calle Real 789, Ciudad"
)

# 7. Crear inventarios para los productos
inventario1 = Inventario.objects.create(
    producto=producto1,
    sucursal=sucursal,
    lote="L001",
    cantidad=50
)

inventario2 = Inventario.objects.create(
    producto=producto2,
    sucursal=sucursal,
    lote="L002",
    cantidad=100
)

# 8. Registrar movimientos de inventario (entradas y salidas)
movimiento1 = MovimientoInventario.objects.create(
    inventario=inventario1,
    tipo_movimiento="entrada",
    cantidad=20,
    usuario=usuario
)

movimiento2 = MovimientoInventario.objects.create(
    inventario=inventario2,
    tipo_movimiento="salida",
    cantidad=5,
    usuario=usuario
)

# 9. Crear ventas y detalles de ventas
# Venta para Cliente A
venta1 = Venta.objects.create(
    empresa=empresa,
    cliente=cliente1,
    total=250.00,  # Total calculado de los productos
    estado="PENDIENTE",
    usuario=usuario
)

# Detalles de la venta 1
detalle1 = DetalleVenta.objects.create(
    venta=venta1,
    producto=producto1,
    cantidad=2,  # Dos unidades del Producto A
    precio_unitario=800.00
)

detalle2 = DetalleVenta.objects.create(
    venta=venta1,
    producto=producto2,
    cantidad=3,  # Tres unidades del Producto B
    precio_unitario=20.00
)

# Venta para Cliente B
venta2 = Venta.objects.create(
    empresa=empresa,
    cliente=cliente2,
    total=320.00,  # Total calculado de los productos
    estado="COMPLETADA",
    usuario=usuario
)

# Detalles de la venta 2
detalle3 = DetalleVenta.objects.create(
    venta=venta2,
    producto=producto2,
    cantidad=4,  # Cuatro unidades del Producto B
    precio_unitario=20.00
)

# Mensaje de éxito
print("Datos de prueba creados con éxito:")
print(f"Empresa: {empresa.nombre}")
print(f"Sucursal: {sucursal.nombre}")
print(f"Usuarios: {usuario.username}")
print(f"Clientes: {cliente1.nombre}, {cliente2.nombre}")
print(f"Productos: {producto1.nombre}, {producto2.nombre}")
print(f"Inventarios: {inventario1.producto.nombre} - {inventario1.cantidad}, {inventario2.producto.nombre} - {inventario2.cantidad}")
print(f"Movimientos de Inventario: Entrada - {movimiento1.cantidad}, Salida - {movimiento2.cantidad}")
print(f"Ventas: Venta 1 (Cliente A), Venta 2 (Cliente B)")

#-------------------------------



# from faker import Faker
# from datetime import datetime, timedelta
# from random import randint, choice
# from django.utils import timezone
# from django.db import transaction
# from nova_erp_total.models import Empresa, Categoria, Producto, Rol, Usuario, Cliente, Venta, DetalleVenta, Movimientoinventario, Sucursal, Inventario, Proveedor

# fake = Faker()

# # Generar Empresas
# def create_empresa():
#     empresa = Empresa.objects.create(
#         nombre=fake.company(),
#         rfc=fake.company_suffix(),
#         domicilio_fiscal=fake.address(),
#         regimen_fiscal=fake.word(),
#         creado_en=timezone.now(),
#         actualizado_en=timezone.now()
#     )
#     return empresa

# # Generar Categorías
# def create_categoria(empresa):
#     categoria = Categoria.objects.create(
#         empresa=empresa,
#         nombre=fake.word(),
#         descripcion=fake.text()
#     )
#     return categoria

# # Generar Productos
# def create_producto(empresa, categoria):
#     producto = Producto.objects.create(
#         empresa=empresa,
#         codigo=fake.uuid4(),
#         nombre=fake.word(),
#         descripcion=fake.text(),
#         unidad_medida='pieza',
#         categoria=categoria,
#         precio_compra=round(randint(10, 500), 2),
#         precio_venta=round(randint(500, 1000), 2),
#         stock_minimo=randint(5, 30),
#         activo=True
#     )
#     return producto

# # Generar Roles
# def create_roles():
#     roles = ['Admin', 'Vendedor', 'Gerente']
#     return [Rol.objects.create(nombre=role, descripcion=f'{role} del sistema') for role in roles]

# # Generar Usuarios
# def create_usuario(empresa, roles):
#     usuario = Usuario.objects.create(
#         username=fake.user_name(),
#         password=fake.password(),
#         email=fake.email(),
#         activo=True,
#         is_active=True,
#         is_staff=True,
#         is_superuser=False,
#         fecha_creacion=timezone.now(),
#         foto=fake.image_url(),
#         telefono=fake.phone_number(),
#         direccion=fake.address(),
#         idioma='es',
#         tema='default',
#         empresa=empresa,
#         rol=choice(roles),
#         last_login=timezone.now(),
#         mfa_enabled=False,
#         mfa_secret='',
#     )
#     return usuario

# # Generar Clientes
# def create_cliente(empresa):
#     cliente = Cliente.objects.create(
#         empresa=empresa,
#         nombre=fake.company(),
#         rfc=fake.ssn(),
#         correo=fake.email(),
#         telefono=fake.phone_number(),
#         direccion=fake.address(),
#         creado_en=timezone.now(),
#         actualizado_en=timezone.now()
#     )
#     return cliente

# # Generar Ventas
# def create_venta(empresa, cliente, usuario):
#     venta = Venta.objects.create(
#         empresa=empresa,
#         cliente=cliente,
#         fecha=timezone.now(),
#         total=round(randint(100, 1000), 2),
#         estado='Completada',
#         usuario=usuario
#     )
#     return venta

# # Generar Detalles de Venta
# def create_detalleventa(venta, producto):
#     detalle = DetalleVenta.objects.create(
#         venta=venta,
#         producto=producto,
#         cantidad=randint(1, 5),
#         precio_unitario=producto.precio_venta
#     )
#     return detalle

# # Generar Movimientos de Inventario
# def create_movimientoinventario(inventario, usuario):
#     movimiento = MovimientoInventario.objects.create(
#         inventario=inventario,
#         tipo_movimiento='Ingreso',
#         cantidad=randint(1, 10),
#         fecha=timezone.now(),
#         usuario=usuario
#     )
#     return movimiento

# # Generar Sucursales
# def create_sucursal(empresa):
#     sucursal = Sucursal.objects.create(
#         empresa=empresa,
#         nombre=fake.city(),
#         direccion=fake.address(),
#         creado_en=timezone.now(),
#         actualizado_en=timezone.now()
#     )
#     return sucursal

# # Generar Inventarios
# def create_inventario(producto, sucursal):
#     inventario = Inventario.objects.create(
#         producto=producto,
#         sucursal=sucursal,
#         lote=fake.uuid4(),
#         fecha_vencimiento=timezone.now() + timedelta(days=365),
#         cantidad=randint(10, 100)
#     )
#     return inventario

# # Generar Proveedores
# def create_proveedor(empresa):
#     proveedor = Proveedor.objects.create(
#         empresa=empresa,
#         nombre=fake.company(),
#         rfc=fake.ssn(),
#         correo=fake.email(),
#         telefono=fake.phone_number(),
#         direccion=fake.address(),
#         creado_en=timezone.now(),
#         actualizado_en=timezone.now()
#     )
#     return proveedor

# # Crear los datos
# def generate_data():
#     with transaction.atomic():
#         # Creación de empresas
#         empresa = create_empresa()

#         # Creación de categorías
#         categoria = create_categoria(empresa)

#         # Creación de productos
#         producto = create_producto(empresa, categoria)

#         # Crear roles
#         roles = create_roles()

#         # Crear usuario
#         usuario = create_usuario(empresa, roles)

#         # Crear clientes
#         cliente = create_cliente(empresa)

#         # Crear ventas y detalles de venta
#         venta = create_venta(empresa, cliente, usuario)
#         create_detalleventa(venta, producto)

#         # Crear sucursal
#         sucursal = create_sucursal(empresa)

#         # Crear inventario
#         inventario = create_inventario(producto, sucursal)

#         # Crear movimientos de inventario
#         create_movimientoinventario(inventario, usuario)

#         # Crear proveedores
#         proveedor = create_proveedor(empresa)

#     print("Datos de prueba generados con éxito.")

# # Ejecutar la función
# generate_data()
