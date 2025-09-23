# marketer_bot.py (V12.2 - Golden Master)
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
import tweepy
from datetime import datetime
from sqlalchemy import create_engine, text

def configurar_api():
    load_dotenv()
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key: raise ValueError("GOOGLE_API_KEY no encontrada")
    genai.configure(api_key=gemini_api_key)
    twitter_keys = {"api_key": os.getenv("API_KEY_X"), "api_key_secret": os.getenv("API_KEY_SECRET_X"), "access_token": os.getenv("ACCESS_TOKEN_X"), "access_token_secret": os.getenv("ACCESS_TOKEN_SECRET_X")}
    if not all(twitter_keys.values()): raise ValueError("Claves de API de X no encontradas")
    return twitter_keys

def leer_estrategia():
    print("📖 Leyendo el plan estratégico desde strategy.json...")
    try:
        with open("strategy.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("plan_semanal") or data.get("plan_contenido_semanal")
    except Exception as e:
        raise ValueError(f"No se pudo leer o procesar strategy.json: {e}")

def analizar_texto(texto: str):
    total_chars = len(texto)
    print(f"--- ANÁLISIS FORENSE: {total_chars} caracteres ---")

# --- PROMPT V12.2 - CON LÍMITE DE 250 CARACTERES ---
PROMPT_PERSONA = """
Actúa como la voz de la marca "Asistente de Correos IA". Eres un experto en comunicación y productividad.

**Tu Personalidad en X (Twitter):**
- **Profesor Apasionado:** Enseñas trucos para escribir mejor.
- **Útil y Práctico:** Compartes consejos aplicables inmediatamente.
- **Empático:** Entiendes la frustración de la "página en blanco".
- **Genuino:** Tu tono es humano y cercano.

**Tu Misión Hoy:**
Basado en la directriz estratégica del día, crea un post para X (Twitter).

**Directriz Estratégica del Día:**
---
{directriz_del_dia}
---

**REGLAS DE ORO PARA LA HUMANIZACIÓN (INQUEBRANTABLES):**
1.  **LÍMITE ESTRICTO DE CARACTERES:** Tu respuesta final debe ser idealmente de unos **250 caracteres**. NUNCA debe superar los 280.
2.  **NO USES EMOJIS.** El texto debe ser limpio y directo.
3.  **SIN ESTRUCTURAS FIJAS:** Sé impredecible en tu formato.
4.  **HASHTAGS MÍNIMOS:** Usa un máximo de 1 o 2 hashtags, solo si es natural.
5.  **REGLA 80/20 DE VALOR:** La mayoría de tus posts son 100% valor. Ocasionalmente, si se alinea, haz un CTA natural para probar la app en: {app_url}.
"""

def generar_post_persona(directriz, url_app):
    print(f"✍️  Generando post... Directriz: '{directriz[:50]}...'")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt_final = PROMPT_PERSONA.format(directriz_del_dia=directriz, app_url=url_app)
        response = model.generate_content(prompt_final)
        print("✅ ¡Post de Persona generado con éxito!")
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error al contactar a Gemini: {e}")
        return None

# --- FUNCIÓN DE PUBLICACIÓN RESTAURADA A TWEEPY (LIMPIA Y PROFESIONAL) ---
def publicar_en_x(texto_del_post, twitter_keys):
    print("🐦 Conectando a la API de X con Tweepy (v2)...")
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
        return response.data
    except Exception as e:
        import traceback
        print(f"❌ Error al publicar en X: {e}")
        traceback.print_exc()
        return None

# --- FUNCIÓN DE GUARDADO EN BASE DE DATOS (CORREGIDA) ---
def guardar_tweet_en_db(tweet_id, contenido, pilar, tema):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("⚠️  Advertencia: No se encontró DATABASE_URL.")
        return
    engine = create_engine(db_url)
    try:
        with engine.connect() as connection: # <-- ESTA LÍNEA FALTABA
            tema_truncado = (tema[:250] + '...') if len(tema) > 255 else tema
            query = text("INSERT INTO tweets_publicados (tweet_id, contenido_texto, pilar_contenido, tema_contenido) VALUES (:id, :contenido, :pilar, :tema)")
            connection.execute(query, {"id": str(tweet_id), "contenido": contenido, "pilar": pilar, "tema": tema_truncado})
            connection.commit()
            print(f"💾 Tweet {tweet_id} guardado en la base de datos.")
    except Exception as e:
        print(f"❌ Error al guardar en la base de datos: {e}")

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    try:
        twitter_keys = configurar_api()
        MI_APP_URL_BASE = "https://huggingface.co/spaces/jgr-soluciones-digitales/Generador-Correos-IA"
        
        plan_semanal = leer_estrategia()
        
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        hoy = datetime.now().weekday()
        indice_dia_plan = hoy % 5
        dia_del_plan_str = dias_semana[indice_dia_plan]
        directriz_obj = next((item for item in plan_semanal if item["dia"] == dia_del_plan_str), None)

        if directriz_obj:
            directriz_de_hoy = directriz_obj["directriz"]
            pilar_de_hoy = directriz_obj.get("pilar_contenido") or directriz_obj.get("pilar", "N/A")

            post_generado = generar_post_persona(directriz_de_hoy, MI_APP_URL_BASE)
            
            if post_generado:
                print("\n--- TEXTO GENERADO POR LA IA ---")
                print(post_generado)
                analizar_texto(post_generado)
                
                tweet_data = publicar_en_x(post_generado, twitter_keys)
                
                if tweet_data:
                    guardar_tweet_en_db(
                        tweet_id=tweet_data['id'],
                        contenido=post_generado,
                        pilar=pilar_de_hoy,
                        tema=directriz_de_hoy
                    )
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ ERROR DE CONFIGURACIÓN O ESTRATEGIA: {e}")