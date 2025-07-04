# Esquema Completo de Base de Datos Nova ERP Total (con apps asignadas)

| Tabla / Modelo       | Campos Principales                                                                                                 | Tipo de Dato                                             | Clave / Relación                           | Descripción Breve                                     | App Asignada      |
|---------------------|-------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|--------------------------------------------|------------------------------------------------------|-------------------|
| Empresa             | id (PK), nombre, rfc, domicilio_fiscal, regimen_fiscal, creado_en, actualizado_en                                 | Integer, String, DateTime                                 | PK                                         | Información básica de cada empresa registrada         | core              |
| Sucursal            | id (PK), empresa_id (FK), nombre, direccion, creado_en, actualizado_en                                            | Integer, Integer, String, DateTime                        | FK → Empresa.id                            | Ubicaciones físicas o sucursales de la empresa        | core              |
| Usuario             | id (PK), empresa_id (FK), rol_id (FK), username, email, password, activo, fecha_creacion, foto, telefono, direccion, idioma, tema | Integer, Integer, Integer, String, String, String, Boolean, DateTime, String, String, String, String | FK → Empresa.id, FK → Rol.id               | Usuarios del sistema con roles y permisos              | accounts          |
| Rol                 | id (PK), nombre, descripcion                                                                                      | Integer, String                                          | PK                                         | Roles para control de acceso y permisos                | accounts          |
| Cliente             | id (PK), empresa_id (FK), nombre, rfc, correo, telefono, direccion, creado_en, actualizado_en                     | Integer, String, DateTime                                 | FK → Empresa.id                            | Clientes de la empresa                                 | ventas            |
| Proveedor           | id (PK), empresa_id (FK), nombre, rfc, correo, telefono, direccion, creado_en, actualizado_en                     | Integer, String, DateTime                                 | FK → Empresa.id                            | Proveedores de la empresa                             | compras           |
| Categoria           | id (PK), empresa_id (FK), nombre, descripcion                                                                     | Integer, String                                          | FK → Empresa.id                            | Clasificación de productos                             | inventario        |
| Producto            | id (PK), empresa_id (FK), codigo, nombre, descripcion, unidad_medida, categoria_id (FK), precio_compra, precio_venta, stock_minimo, activo | Integer, String, Decimal                                 | FK → Empresa.id, FK → Categoria.id          | Productos y servicios ofrecidos                        | inventario        |
| Inventario          | id (PK), producto_id (FK), sucursal_id (FK), lote, fecha_vencimiento, cantidad                                    | Integer, Integer, Date, Decimal                          | FK → Producto.id, FK → Sucursal.id          | Registro de stock por producto, sucursal y lote       | inventario        |
| MovimientoInventario | id (PK), inventario_id (FK), tipo_movimiento, cantidad, fecha, usuario_id (FK)                                    | Integer, String, Decimal, DateTime                        | FK → Inventario.id, FK → Usuario.id          | Registro histórico de entradas y salidas              | inventario        |
| Venta               | id (PK), empresa_id (FK), cliente_id (FK), fecha, total, estado, usuario_id (FK)                                  | Integer, Integer, DateTime, Decimal                      | FK → Empresa.id, FK → Cliente.id, FK → Usuario.id | Registro de ventas realizadas                          | ventas            |
| DetalleVenta        | id (PK), venta_id (FK), producto_id (FK), cantidad, precio_unitario                                               | Integer, Integer, Decimal                                | FK → Venta.id, FK → Producto.id              | Productos y cantidades por venta                       | ventas            |
| Compra              | id (PK), empresa_id (FK), proveedor_id (FK), fecha, total, estado, usuario_id (FK)                                | Integer, Integer, DateTime, Decimal                      | FK → Empresa.id, FK → Proveedor.id, FK → Usuario.id | Registro de compras realizadas                         | compras           |
| DetalleCompra       | id (PK), compra_id (FK), producto_id (FK), cantidad, precio_unitario                                             | Integer, Integer, Decimal                                | FK → Compra.id, FK → Producto.id             | Productos y cantidades por compra                      | compras           |
| CuentaPorCobrar     | id (PK), venta_id (FK), monto, fecha_vencimiento, estado                                                         | Integer, Decimal, Date, String                           | FK → Venta.id                              | Cuentas pendientes a cobrar de clientes                | finanzas          |
| CuentaPorPagar      | id (PK), compra_id (FK), monto, fecha_vencimiento, estado                                                        | Integer, Decimal, Date, String                           | FK → Compra.id                             | Cuentas pendientes a pagar a proveedores               | finanzas          |
| Pago                | id (PK), cuenta_cobrar_id (FK nullable), cuenta_pagar_id (FK nullable), monto, fecha, metodo_pago                 | Integer, Decimal, DateTime, String                       | FK → CuentaPorCobrar.id, FK → CuentaPorPagar.id | Pagos realizados vinculados a cuentas                  | finanzas          |
| AsientoContable     | id (PK), empresa_id (FK), fecha, concepto, usuario_id (FK), creado_en                                            | Integer, Date, String, Integer, DateTime                | FK → Empresa.id, FK → Usuario.id             | Registro de asientos contables                          | contabilidad      |
| DetalleAsiento      | id (PK), asiento_id (FK), cuenta_contable, debe, haber                                                           | Integer, String, Decimal, Decimal                        | FK → AsientoContable.id                      | Detalle de movimientos contables por asiento           | contabilidad      |
| Empleado            | id (PK), empresa_id (FK), nombre, rfc, puesto, salario                                                           | Integer, String, Decimal                                 | FK → Empresa.id                             | Empleados para nómina y RRHH                            | rrhh              |
| Nomina              | id (PK), empleado_id (FK), periodo, total, estado                                                                | Integer, Integer, String, Decimal, String               | FK → Empleado.id                            | Nóminas generadas                                      | rrhh              |
| Asistencia          | id (PK), empleado_id (FK), fecha, hora_entrada, hora_salida                                                      | Integer, Integer, Date, Time, Time                       | FK → Empleado.id                            | Registro de entradas y salidas                          | rrhh              |
| DocumentoFiscal     | id (PK), tipo_documento, referencia_id, archivo, fecha_emision                                                   | Integer, String, Integer, FileField, Date               | FK a entidades relacionadas                | Almacenamiento de CFDI, XML, PDFs                       | documentos        |
| Auditoria           | id (PK), usuario_id (FK), acción, tabla_afectada, registro_afectado, timestamp                                   | Integer, Integer, String, String, String, DateTime      | FK → Usuario.id                            | Registro histórico de cambios                           | accounts          |

---

# Relaciones Clave Principales

| Tabla Origen        | Campo FK           | Tabla Referenciada | Tipo de Relación           |
|---------------------|--------------------|--------------------|---------------------------|
| Sucursal            | empresa_id         | Empresa            | Muchos a uno              |
| Usuario             | empresa_id         | Empresa            | Muchos a uno              |
| Usuario             | rol_id             | Rol                | Muchos a uno              |
| Cliente             | empresa_id         | Empresa            | Muchos a uno              |
| Proveedor           | empresa_id         | Empresa            | Muchos a uno              |
| Categoria           | empresa_id         | Empresa            | Muchos a uno              |
| Producto            | empresa_id         | Empresa            | Muchos a uno              |
| Producto            | categoria_id       | Categoria          | Muchos a uno              |
| Inventario          | producto_id        | Producto           | Muchos a uno              |
| Inventario          | sucursal_id        | Sucursal           | Muchos a uno              |
| MovimientoInventario | inventario_id      | Inventario         | Muchos a uno              |
| MovimientoInventario | usuario_id         | Usuario            | Muchos a uno              |
| Venta               | empresa_id         | Empresa            | Muchos a uno              |
| Venta               | cliente_id         | Cliente            | Muchos a uno              |
| Venta               | usuario_id         | Usuario            | Muchos a uno              |
| DetalleVenta        | venta_id           | Venta              | Muchos a uno              |
| DetalleVenta        | producto_id        | Producto           | Muchos a uno              |
| Compra              | empresa_id         | Empresa            | Muchos a uno              |
| Compra              | proveedor_id       | Proveedor          | Muchos a uno              |
| Compra              | usuario_id         | Usuario            | Muchos a uno              |
| DetalleCompra       | compra_id          | Compra             | Muchos a uno              |
| DetalleCompra       | producto_id        | Producto           | Muchos a uno              |
| CuentaPorCobrar     | venta_id           | Venta              | Muchos a uno              |
| CuentaPorPagar      | compra_id          | Compra             | Muchos a uno              |
| Pago                | cuenta_cobrar_id   | CuentaPorCobrar    | Muchos a uno / Nullable   |
| Pago                | cuenta_pagar_id    | CuentaPorPagar     | Muchos a uno / Nullable   |
| AsientoContable     | empresa_id         | Empresa            | Muchos a uno              |
| AsientoContable     | usuario_id         | Usuario            | Muchos a uno              |
| DetalleAsiento      | asiento_id         | AsientoContable    | Muchos a uno              |
| Empleado            | empresa_id         | Empresa            | Muchos a uno              |
| Nomina              | empleado_id        | Empleado           | Muchos a uno              |
| Asistencia          | empleado_id        | Empleado           | Muchos a uno              |
| DocumentoFiscal     | referencia_id      | Variable           | Variable según tipo       |
| Auditoria           | usuario_id         | Usuario            | Muchos a uno              |
