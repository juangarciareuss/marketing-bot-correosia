# marketer_bot.py (V6.0 - Con Memoria en Base de Datos)
import os
import json
import random
import google.generativeai as genai
from dotenv import load_dotenv
import tweepy
from datetime import datetime
from sqlalchemy import create_engine, text # <-- NUEVO IMPORT

# ... la función configurar_api() no cambia ...
def configurar_api():
    load_dotenv()
    # ... (código existente es el mismo)
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key:
        raise ValueError("No se encontró la GOOGLE_API_KEY en el archivo .env")
    genai.configure(api_key=gemini_api_key)
    twitter_keys = {
        "api_key": os.getenv("API_KEY_X"), "api_key_secret": os.getenv("API_KEY_SECRET_X"),
        "access_token": os.getenv("ACCESS_TOKEN_X"), "access_token_secret": os.getenv("ACCESS_TOKEN_SECRET_X")
    }
    if not all(twitter_keys.values()):
        raise ValueError("Faltan una o más claves de la API de X en el archivo .env")
    return twitter_keys

# ... la función leer_estrategia() no cambia ...
def leer_estrategia():
    print("📖 Leyendo el plan estratégico desde strategy.json...")
    try:
        with open("strategy.json", "r", encoding="utf-8") as f:
            estrategia = json.load(f)
        return estrategia["plan_semanal"]
    except Exception as e:
        raise ValueError(f"No se pudo leer o procesar strategy.json: {e}")

# ... El PROMPT_REDACCION_FINAL no cambia ...
PROMPT_REDACCION_FINAL = """
Actúa como un Social Media Manager de clase mundial, experto en contenido de valor que se siente auténtico y humano.
Tu única tarea es tomar la siguiente directriz estratégica y convertirla en un post de alta calidad para X (Twitter).

**Directriz Estratégica para Hoy:**
---
{directriz_del_dia}
---

**Tipo de Llamado a la Acción (CTA) para hoy:** {tipo_cta}

**Reglas de Estilo y Estrategia:**
1.  Elabora la idea de la directriz para crear un post que aporte valor real. El tono debe ser natural y conversacional.
2.  El límite de X es de 280 caracteres. Sé breve y potente.
3.  **Estrategia de Hashtags:** Basado en el contenido del post, decide estratégicamente cómo usar los hashtags para que se vea natural. No tienes que usarlos siempre.
    - **A veces, no uses ningún hashtag**, si el post es muy conversacional o una pregunta directa.
    - **Otras veces, integra 1 hashtag** de forma natural DENTRO de una frase (ej: "...mejora tu #productividad...").
    - **Ocasionalmente, puedes poner 1 o 2 hashtags clave** al final si aportan mucho valor de descubrimiento.
    - **Tu decisión debe hacer que el timeline se vea variado y humano, no como un bot de marketing.**
4.  **Finaliza el post según el tipo de CTA:**
    - Si el `tipo_cta` es "interaccion", termina con una pregunta abierta para fomentar la conversación.
    - Si el `tipo_cta` es "promocional", termina con un CTA claro para probar la herramienta, incluyendo el enlace: {app_url}
"""

# ... la función generar_post_estrategico() no cambia ...
def generar_post_estrategico(directriz, url_app, tipo_cta):
    print(f"✍️  Generando post (CTA: {tipo_cta}) basado en la directriz: '{directriz[:50]}...'")
    # ... (código existente es el mismo)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt_final = PROMPT_REDACCION_FINAL.format(directriz_del_dia=directriz, app_url=url_app, tipo_cta=tipo_cta)
        response = model.generate_content(prompt_final)
        print("✅ ¡Post estratégico generado con éxito!")
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error al contactar a Gemini: {e}")
        return None


# --- NUEVA FUNCIÓN PARA GUARDAR EN LA BASE DE DATOS ---
def guardar_tweet_en_db(tweet_id, contenido, pilar, tema):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("⚠️  Advertencia: No se encontró DATABASE_URL. No se guardará en la base de datos.")
        return

    engine = create_engine(db_url)
    try:
        with engine.connect() as connection:
            # Usamos parámetros para evitar inyección SQL
            query = text("""
                INSERT INTO tweets_publicados (tweet_id, contenido_texto, pilar_contenido, tema_contenido)
                VALUES (:id, :contenido, :pilar, :tema)
            """)
            connection.execute(query, {"id": tweet_id, "contenido": contenido, "pilar": pilar, "tema": tema})
            connection.commit()
            print(f"💾 Tweet {tweet_id} guardado en la base de datos.")
    except Exception as e:
        print(f"❌ Error al guardar en la base de datos: {e}")

def publicar_en_x(texto_del_post, twitter_keys, tweet_id_para_url):
    # ... (Función modificada para recibir el ID para la URL)
    print("🐦 Conectando a la API de X para publicar...")
    try:
        client = tweepy.Client(
            consumer_key=twitter_keys["api_key"], consumer_secret=twitter_keys["api_key_secret"],
            access_token=twitter_keys["access_token"], access_token_secret=twitter_keys["access_token_secret"]
        )
        response = client.create_tweet(text=texto_del_post)
        tweet_id = response.data['id']
        tweet_url = f"https://twitter.com/jgr_soluciones/status/{tweet_id}"
        print(f"✅ ¡Publicado en X con éxito! ID del Tweet: {tweet_id}")
        print(f"🔗 URL DEL TWEET GENERADO: {tweet_url}")
        return response.data # Devolvemos los datos del tweet
    except Exception as e:
        import traceback
        print(f"❌ Error al publicar en X: {e}")
        traceback.print_exc()
        return None

# --- Ejecución Principal (MODIFICADA) ---
if __name__ == "__main__":
    try:
        twitter_keys = configurar_api()
        MI_APP_URL_BASE = "https://huggingface.co/spaces/jgr-soluciones-digitales/Generador-Correos-IA"

        plan_semanal = leer_estrategia()

        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        hoy = datetime.now().weekday()
        indice_dia_plan = hoy % 5
        dia_del_plan = dias_semana[indice_dia_plan]
        print(f"🗓️  Hoy es {datetime.now().strftime('%A')}. Usando la estrategia de: {dia_del_plan}")

        directriz_obj = next((item for item in plan_semanal if item["dia"] == dia_del_plan), None)

        if directriz_obj:
            directriz_de_hoy = directriz_obj["directriz"]
            pilar_de_hoy = directriz_obj["pilar"]

            if random.randint(1, 5) == 1:
                tipo_cta_elegido = "promocional"
            else:
                tipo_cta_elegido = "interaccion"

            post_generado = generar_post_estrategico(directriz_de_hoy, MI_APP_URL_BASE, tipo_cta_elegido)

            if post_generado:
                print("\n--- INICIO DEL POST GENERADO ---\n")
                print(post_generado)
                print("\n--- FIN DEL POST GENERADO ---")

                tweet_data = publicar_en_x(post_generado, twitter_keys)

                if tweet_data:
                    # Si se publicó, lo guardamos en la base de datos
                    guardar_tweet_en_db(
                        tweet_id=tweet_data['id'],
                        contenido=post_generado,
                        pilar=pilar_de_hoy,
                        tema=directriz_de_hoy # Usamos la directriz como tema por ahora
                    )
        else:
            print(f"🤷 No se encontró una directriz para el día de hoy ({dia_del_plan}).")

    except (ValueError, FileNotFoundError) as e:
        print(f"❌ ERROR DE CONFIGURACIÓN O ESTRATEGIA: {e}")