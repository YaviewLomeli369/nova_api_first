import os
import re

def parse_dot_file(dot_path):
    with open(dot_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tables = re.findall(r'(\w+)\s+\[label=<\s*<TABLE.*?>(.*?)</TABLE>', content, re.DOTALL)
    dbd_output = []

    for table_name, table_body in tables:
        cleaned_table_name = table_name.split('_')[-1]  # simplificar nombre

        dbd_output.append(f'Table {cleaned_table_name} {{')

        # buscar cada fila del campo
        rows = re.findall(r'<TR>(.*?)</TR>', table_body, re.DOTALL)
        for row in rows:
            cols = re.findall(r'<TD.*?>(.*?)</TD>', row, re.DOTALL)
            if len(cols) != 2:
                continue

            raw_name = re.sub(r'<.*?>', '', cols[0]).strip()
            raw_type = re.sub(r'<.*?>', '', cols[1]).strip()

            if not raw_name or not raw_type:
                continue

            # dbd_output.append(f'  {raw_name} {map_field_type(raw_type)}')
            dbd_output.append(f'  {raw_name} {map_field_type(raw_type, raw_name)}')

        dbd_output.append('}\n')

    return '\n'.join(dbd_output)

def camel_case(snake_str):
    """Convierte 'usuario' o 'user_profile' a 'Usuario' o 'UserProfile'"""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

custom_foreign_keys = {
    'user': 'Usuario',
    'usuario': 'Usuario',
    'sucursal_actual': 'Sucursal',
    'unidad': 'ClaveSATUnidad',
    'clave_sat': 'ClaveSATProducto',
    'unidad_medida': 'ClaveSATUnidad',
    'cuenta_cobrar': 'CuentaPorCobrar',
    'cuenta_pagar': 'CuentaPorPagar',
    'padre': 'CuentaContable',
    'asiento': 'AsientoContable',
    'comprobante': 'ComprobanteFiscal',
    'enviado_por': 'Usuario',
    'generado_por': 'Usuario',
}

def map_field_type(ftype, field_name=None):
    mapping = {
        'AutoField': 'int [pk]',
        'BigAutoField': 'bigint [pk]',
        'CharField': 'varchar',
        'TextField': 'text',
        'DateTimeField': 'datetime',
        'PositiveSmallIntegerField': 'smallint',
        'JSONField': 'json',
        'BooleanField': 'boolean',
        'IntegerField': 'int',
        'DecimalField': 'decimal',
        'FloatField': 'float',
    }

    if 'ForeignKey' in ftype and field_name:
        if field_name in custom_foreign_keys:
            related_table = custom_foreign_keys[field_name]
        else:
            related_table = camel_case(field_name)
        return f'int [ref: > {related_table}.id]'

    return mapping.get(ftype, 'varchar')


def save_output(output_str, out_path='output.dbd'):
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output_str)
    print(f'[✔] Archivo generado: {out_path}')


# ---------- MAIN ----------
if __name__ == "__main__":
    ruta_dot = "myapp_models.dot"

    salida = "output.dbd"

    resultado = parse_dot_file(ruta_dot)
    save_output(resultado, salida)
