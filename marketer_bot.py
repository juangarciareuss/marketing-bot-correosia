# marketer_bot.py (V4.0 - El Ejecutor Estratégico)
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import tweepy
from datetime import datetime

def configurar_api():
    # ... (Esta función no cambia)
    load_dotenv()
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

def leer_estrategia():
    """Lee el plan de contenido del archivo strategy.json."""
    print("📖 Leyendo el plan estratégico desde strategy.json...")
    try:
        with open("strategy.json", "r", encoding="utf-8") as f:
            estrategia = json.load(f)
        return estrategia["plan_semanal"]
    except FileNotFoundError:
        raise FileNotFoundError("El archivo strategy.json no fue encontrado. Ejecuta strategist.py primero.")
    except (json.JSONDecodeError, KeyError):
        raise ValueError("El archivo strategy.json está corrupto o no tiene el formato esperado.")

# --- NUEVO PROMPT: Más simple, solo ejecuta la directriz ---
PROMPT_REDACCION_FINAL = """
Actúa como un Social Media Manager de clase mundial.
Tu única tarea es tomar la siguiente directriz estratégica y convertirla en un post de alta calidad, conciso y atractivo para X (Twitter).

**Directriz Estratégica para Hoy:**
---
{directriz_del_dia}
---

**Reglas:**
1.  Elabora la idea de la directriz. No la repitas literalmente.
2.  El límite de X es de 280 caracteres. Sé breve.
3.  Incluye 3-4 hashtags relevantes en español.
4.  Añade siempre un CTA para probar la herramienta con este enlace: {app_url}
"""

def generar_post_estrategico(directriz, url_app):
    """Genera un post basado en la directriz estratégica del día."""
    print(f"✍️  Generando post basado en la directriz: '{directriz[:50]}...'")
    try:
        # Usamos Flash para la redacción final, es rápido y eficiente
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt_final = PROMPT_REDACCION_FINAL.format(directriz_del_dia=directriz, app_url=url_app)
        response = model.generate_content(prompt_final)
        print("✅ ¡Post estratégico generado con éxito!")
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error al contactar a Gemini: {e}")
        return None

def publicar_en_x(texto_del_post, twitter_keys):
    # ... (Esta función no cambia)
    print("🐦 Conectando a la API de X para publicar...")
    # ... (el resto del código es igual)
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
        return response
    except Exception as e:
        import traceback
        print(f"❌ Error al publicar en X: {e}")
        traceback.print_exc()
        return None

# --- Ejecución Principal ---
if __name__ == "__main__":
    try:
        twitter_keys = configurar_api()
        MI_APP_URL = "https://huggingface.co/spaces/jgr-soluciones-digitales/Generador-Correos-IA"
        
        # 1. Leer el plan semanal
        plan_semanal = leer_estrategia()
        
        # 2. Determinar el día de hoy y obtener la directriz correcta
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        hoy = datetime.now().weekday() # Lunes=0, Martes=1...
        
        if hoy < 5: # Solo publica de Lunes a Viernes
            dia_actual_str = dias_semana[hoy]
            directriz_de_hoy = next((item["directriz"] for item in plan_semanal if item["dia"] == dia_actual_str), None)
            
            if directriz_de_hoy:
                # 3. Generar el post basado en la estrategia
                post_generado = generar_post_estrategico(directriz_de_hoy, MI_APP_URL)
                
                if post_generado:
                    print("\n--- INICIO DEL POST GENERADO ---\n")
                    print(post_generado)
                    print("\n--- FIN DEL POST GENERADO ---")
                    # 4. Publicar el post
                    publicar_en_x(post_generado, twitter_keys)
            else:
                print(f"🤷 No se encontró una directriz para el día de hoy ({dia_actual_str}).")
        else:
            print("🗓️  Es fin de semana. No se publicará contenido hoy.")

    except (ValueError, FileNotFoundError) as e:
        print(f"❌ ERROR DE CONFIGURACIÓN O ESTRATEGIA: {e}")