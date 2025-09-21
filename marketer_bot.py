import os
import google.generativeai as genai
from dotenv import load_dotenv
import tweepy

def configurar_api():
    """Carga todas las API Keys del archivo .env."""
    load_dotenv()
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key:
        raise ValueError("No se encontró la GOOGLE_API_KEY en el archivo .env")
    genai.configure(api_key=gemini_api_key)

    twitter_keys = {
        "api_key": os.getenv("API_KEY_X"),
        "api_key_secret": os.getenv("API_KEY_SECRET_X"),
        "access_token": os.getenv("ACCESS_TOKEN_X"),
        "access_token_secret": os.getenv("ACCESS_TOKEN_SECRET_X")
    }
    if not all(twitter_keys.values()):
        raise ValueError("Faltan una o más claves de la API de X en el archivo .env")

    return twitter_keys

PROMPT_MAESTRO_MARKETING = """
Actúa como un Social Media Manager experto para una startup de tecnología.
El producto es "Asistente de Correos IA", que ayuda a escribir correos de alta calidad.
Tu tarea es generar el texto para un post para X (Twitter).

**Reglas:**
1.  **Elige aleatoriamente uno de los siguientes 4 formatos de contenido:** "Consejo Rápido", "Caso de Uso", "Transformación (Antes/Después)", o "Agitación del Problema".
2.  **Sé conciso y directo.** El límite de X es de 280 caracteres, ¡respétalo!
3.  **Incluye 3-4 hashtags relevantes** en español.
4.  **No expliques el formato que elegiste.** Simplemente escribe el post.
5.  **Termina SIEMPRE con un CTA** que invite a probar la herramienta y el enlace: {app_url}
"""

def generar_post_marketing(url_app):
    """Genera un nuevo post de marketing usando la IA."""
    print("🤖 Contactando a Gemini para generar un nuevo post...")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt_final = PROMPT_MAESTRO_MARKETING.format(app_url=url_app)
        response = model.generate_content(prompt_final)
        print("✅ ¡Post generado con éxito!")
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error al contactar a Gemini: {e}")
        return None

def publicar_en_x(texto_del_post, twitter_keys):
    """Se conecta a la API de X y publica el tuit."""
    print("🐦 Conectando a la API de X para publicar...")
    try:
        client = tweepy.Client(
            consumer_key=twitter_keys["api_key"],
            consumer_secret=twitter_keys["api_key_secret"],
            access_token=twitter_keys["access_token"],
            access_token_secret=twitter_keys["access_token_secret"]
        )
        response = client.create_tweet(text=texto_del_post)

        tweet_id = response.data['id']
        # Reemplaza 'tu_handle_de_twitter' con tu @ real para que el enlace funcione
        tweet_url = f"https://twitter.com/jgr_soluciones/status/{tweet_id}"

        print(f"✅ ¡Publicado en X con éxito! ID del Tweet: {tweet_id}")
        print(f"🔗 URL DEL TWEET GENERADO: {tweet_url}")

        return response
    except Exception as e:
        print(f"❌ Error al publicar en X: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Ejecución Principal del Script ---
if __name__ == "__main__":
    try:
        twitter_keys = configurar_api()

        MI_APP_URL = "https://huggingface.co/spaces/jgr-soluciones-digitales/Generador-Correos-IA"
        # Asegúrate de que esta URL sea la de tu organización

        post_generado = generar_post_marketing(MI_APP_URL)

        if post_generado:
            print("\n--- INICIO DEL POST GENERADO ---\n")
            print(post_generado)
            print("\n--- FIN DEL POST GENERADO ---\n")

            publicar_en_x(post_generado, twitter_keys)

    except ValueError as e:
        print(f"❌ ERROR DE CONFIGURACIÓN: {e}")