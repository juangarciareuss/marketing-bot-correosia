import os
from dotenv import load_dotenv

print("--- Iniciando prueba de .env ---")

# Cargar el archivo .env desde la carpeta actual
load_dotenv()

# Intentar leer la variable específica
db_url = os.getenv("DATABASE_URL")

if db_url:
    print("✅ ÉXITO: La variable DATABASE_URL fue encontrada.")
    # Por seguridad, solo mostraremos una parte de la URL para confirmar
    print(f"   Valor parcial: {db_url[:30]}...") 
else:
    print("❌ FALLO: La variable DATABASE_URL NO fue encontrada en el archivo .env.")
    print("   Por favor, verifica estos 3 puntos:")
    print("   1. Que el archivo se llame exactamente '.env' (con el punto al principio).")
    print("   2. Que el archivo .env esté en la misma carpeta que este script.")
    print("   3. Que hayas guardado los cambios en el archivo .env.")

print("--- Prueba de .env finalizada ---")