#!/bin/bash

# === CONFIGURACIÓN ===
URL_BASE="http://localhost:8000/api/auth"  # Cambia esto a tu URL real
USUARIO="yaview.lomeli@gmail.com"
PASSWORD="tu_contraseña"  # Modifica si es necesario

# === PASO 1: Login para obtener temp_token ===
echo "🔐 Haciendo login para obtener temp_token..."
RESPONSE=$(curl -s -X POST "$URL_BASE/login/" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USUARIO\", \"password\": \"$PASSWORD\"}")

echo "📨 Respuesta completa:"
echo "$RESPONSE"
echo

# === PASO 2: Pegas el temp_token manualmente ===
read -p "✏️  Copia y pega aquí el temp_token recibido: " TEMP_TOKEN

# === PASO 3: Ingresar código de Google Authenticator ===
read -p "📲 Ingresa el código TOTP actual de 6 dígitos: " MFA_CODE

# === PASO 4: Verificar el login con MFA ===
RESPONSE2=$(curl -s -X POST "$URL_BASE/2fa/verify-login/" \
  -H "Content-Type: application/json" \
  -d "{\"temp_token\": \"$TEMP_TOKEN\", \"code\": \"$MFA_CODE\"}")

echo "🔁 Respuesta final:"
echo "$RESPONSE2"
