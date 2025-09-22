# db_setup.py (Versión Corregida)
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# --- CARGAMOS LAS VARIABLES DE ENTORNO AQUÍ, AL PRINCIPIO DE TODO ---
load_dotenv()

def setup_database():
    """
    Se conecta a la base de datos y crea las tablas necesarias si no existen.
    """
    # Ahora la variable ya debería estar cargada
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        # Este error ya no debería ocurrir
        raise ValueError("No se encontró la DATABASE_URL. Revisa el .env")

    print("🔌 Conectando a la base de datos...")
    engine = create_engine(db_url)

    try:
        with engine.connect() as connection:
            print("✅ Conexión exitosa.")

            # --- Crear la tabla de tweets publicados ---
            print("🏗️  Creando tabla 'tweets_publicados' si no existe...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS tweets_publicados (
                    tweet_id VARCHAR(255) PRIMARY KEY,
                    fecha_publicacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    contenido_texto TEXT,
                    pilar_contenido VARCHAR(100),
                    tema_contenido VARCHAR(255),
                    likes INTEGER DEFAULT 0,
                    retweets INTEGER DEFAULT 0,
                    impresiones INTEGER DEFAULT 0
                );
            """))

            # --- Crear la tabla de usuarios registrados (para el futuro) ---
            print("🏗️  Creando tabla 'usuarios_registrados' si no existe...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS usuarios_registrados (
                    user_id SERIAL PRIMARY KEY,
                    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    tweet_de_origen VARCHAR(255) REFERENCES tweets_publicados(tweet_id),
                    ingreso_generado NUMERIC(10, 2) DEFAULT 0.00
                );
            """))

            connection.commit()
            print("✅ ¡Tablas creadas o ya existentes con éxito!")

    except Exception as e:
        print(f"❌ Error durante la configuración de la base de datos: {e}")

if __name__ == "__main__":
    setup_database()