# marketer_bot.py (V4.2 - Estratega de Contenido 80/20)
import os
import json
import random
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
    # ... (Esta función no cambia)
    print("📖 Leyendo el plan estratégico desde strategy.json...")
    try:
        with open("strategy.json", "r", encoding="utf-8") as f:
            estrategia = json.load(f)
        return estrategia["plan_semanal"]
    except Exception as e:
        raise ValueError(f"No se pudo leer o procesar strategy.json: {e}")


# --- PROMPT ACTUALIZADO CON LÓGICA 80/20 ---
PROMPT_REDACCION_FINAL = """
Actúa como un Social Media Manager de clase mundial.
Tu única tarea es tomar la siguiente directriz estratégica y convertirla en un post de alta calidad para X (Twitter).

**Directriz Estratégica para Hoy:**
---
{directriz_del_dia}
---

**Tipo de Llamado a la Acción (CTA) para hoy:** {tipo_cta}

**Reglas:**
1.  Elabora la idea de la directriz. No la repitas literalmente.
2.  El límite de X es de 280 caracteres. Sé breve.
3.  Incluye 3-4 hashtags relevantes en español.
4.  **Finaliza el post según el tipo de CTA:**
    - Si el `tipo_cta` es **"interaccion"**, termina con una pregunta abierta relacionada con el tema para fomentar la conversación (ej: "¿Qué opinas?", "¿Cuál es tu mayor desafío con esto?").
    - Si el `tipo_cta` es **"promocional"**, termina con un llamado a la acción claro para probar la herramienta, incluyendo el enlace: {app_url}
"""

def generar_post_estrategico(directriz, url_app, tipo_cta):
    print(f"✍️  Generando post (CTA: {tipo_cta}) basado en la directriz: '{directriz[:50]}...'")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt_final = PROMPT_REDACCION_FINAL.format(directriz_del_dia=directriz, app_url=url_app, tipo_cta=tipo_cta)
        response = model.generate_content(prompt_final)
        print("✅ ¡Post estratégico generado con éxito!")
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error al contactar a Gemini: {e}")
        return None

def publicar_en_x(texto_del_post, twitter_keys):
    # ... (Esta función no cambia)
    # ...
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
        return response
    except Exception as e:
        import traceback
        print(f"❌ Error al publicar en X: {e}")
        traceback.print_exc()
        return None

# --- Ejecución Principal con LÓGICA 80/20 ---
if __name__ == "__main__":
    try:
        twitter_keys = configurar_api()
        MI_APP_URL = "https://huggingface.co/spaces/jgr-soluciones-digitales/Generador-Correos-IA"
        
        plan_semanal = leer_estrategia()
        
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        hoy = datetime.now().weekday()
        indice_dia_plan = hoy % 5 
        dia_del_plan = dias_semana[indice_dia_plan]
        print(f"🗓️  Hoy es {datetime.now().strftime('%A')}. Usando la estrategia de: {dia_del_plan}")
        
        directriz_de_hoy = next((item["directriz"] for item in plan_semanal if item["dia"] == dia_del_plan), None)
        
        if directriz_de_hoy:
            # --- LÓGICA 80/20 ---
            # Se elige un número al azar. Si es 1 (20% de probabilidad), el CTA es promocional.
            if random.randint(1, 5) == 1:
                tipo_cta_elegido = "promocional"
            else:
                tipo_cta_elegido = "interaccion"
            # --- FIN DE LA LÓGICA ---

            post_generado = generar_post_estrategico(directriz_de_hoy, MI_APP_URL, tipo_cta_elegido)
            
            if post_generado:
                print("\n--- INICIO DEL POST GENERADO ---\n")
                print(post_generado)
                print("\n--- FIN DEL POST GENERADO ---")
                publicar_en_x(post_generado, twitter_keys)
        else:
            print(f"🤷 No se encontró una directriz para el día de hoy ({dia_del_plan}).")

    except (ValueError, FileNotFoundError) as e:
        print(f"❌ ERROR DE CONFIGURACIÓN O ESTRATEGIA: {e}")