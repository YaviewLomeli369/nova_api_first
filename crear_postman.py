import json

# Definir estructura de la colección
collection = {
    "info": {
        "name": "NOVA API-FIRST",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "GET - Obtener usuarios",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "https://miapi.com/usuarios",
                    "protocol": "https",
                    "host": ["fca3faea-e64a-4f83-a448-762fa6e71df4-00-1kkfg9j97gplb", "spock", "replit", "dev"],
                    "path": ["usuarios"]
                }
            }
        },
        {
            "name": "POST - Crear usuario",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "nombre": "Juan",
                        "correo": "juan@correo.com"
                    }, indent=2)
                },
                "url": {
                    "raw": "https://miapi.com/usuarios",
                    "protocol": "https",
                    "host": ["fca3faea-e64a-4f83-a448-762fa6e71df4-00-1kkfg9j97gplb", "spock", "replit", "dev"],
                    "path": ["usuarios"]
                }
            }
        }
    ]
}

# Guardar el archivo JSON
with open("collection.json", "w", encoding="utf-8") as f:
    json.dump(collection, f, indent=2, ensure_ascii=False)

print("✅ Archivo 'collection.json' generado correctamente.")
