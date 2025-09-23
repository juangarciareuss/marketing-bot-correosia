# marketer_bot.py (V11.0 - El Agente con Memoria Contextual)
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import tweepy
from datetime import datetime
from sqlalchemy import create_engine, text

# ... (La función configurar_api() y publicar_en_x() no cambian) ...
def configurar_api():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: raise ValueError("GOOGLE_API_KEY no encontrada")
    genai.configure(api_key=api_key)
    twitter_keys = {"api_key": os.getenv("API_KEY_X"), "api_key_secret": os.getenv("API_KEY_SECRET_X"), "access_token": os.getenv("ACCESS_TOKEN_X"), "access_token_secret": os.getenv("ACCESS_TOKEN_SECRET_X")}
    if not all(twitter_keys.values()): raise ValueError("Claves de API de X no encontradas")
    return twitter_keys

def publicar_en_x(texto_del_post, twitter_keys):
    print("🐦 Conectando a la API de X para publicar...")
    try:
        client = tweepy.Client(consumer_key=twitter_keys["api_key"], consumer_secret=twitter_keys["api_key_secret"], access_token=twitter_keys["access_token"], access_token_secret=twitter_keys["access_token_secret"])
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


def leer_estrategia():
    print("📖 Leyendo el plan estratégico desde strategy.json...")
    try:
        with open("strategy.json", "r", encoding="utf-8") as f:
            return json.load(f)["plan_semanal"]
    except Exception as e:
        raise ValueError(f"No se pudo leer o procesar strategy.json: {e}")

# --- NUEVA FUNCIÓN: LEER LA MEMORIA ---
def leer_historial_reciente(num_tweets=3):
    """Lee los tweets más recientes de la base de datos para dar contexto."""
    print(f"🧠 Recordando los últimos {num_tweets} posts...")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("⚠️  Advertencia: No se encontró DATABASE_URL. No se puede leer el historial.")
        return ""
    
    engine = create_engine(db_url)
    try:
        with engine.connect() as connection:
            query = text("SELECT contenido_texto FROM tweets_publicados ORDER BY fecha_publicacion DESC LIMIT :limit")
            result = connection.execute(query, {"limit": num_tweets})
            historial = [row[0] for row in result]
            
            if not historial:
                print("📜 El historial de posts está vacío.")
                return "No hay posts recientes."
            
            # Formateamos el historial para el prompt
            historial_formateado = "\n".join(f"- Post Anterior: '{tweet}'" for tweet in historial)
            print("✅ Historial recordado con éxito.")
            return historial_formateado
    except Exception as e:
        print(f"❌ Error al leer el historial de la base de datos: {e}")
        return "Error al leer el historial."

def guardar_tweet_en_db(tweet_id, contenido, pilar, tema):
    # ... (Esta función no cambia)
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("⚠️  Advertencia: No se encontró DATABASE_URL.")
        return
    engine = create_engine(db_url)
    try:
        with engine.connect() as connection:
            query = text("INSERT INTO tweets_publicados (tweet_id, contenido_texto, pilar_contenido, tema_contenido) VALUES (:id, :contenido, :pilar, :tema)")
            connection.execute(query, {"id": str(tweet_id), "contenido": contenido, "pilar": pilar, "tema": tema})
            connection.commit()
            print(f"💾 Tweet {tweet_id} guardado en la base de datos.")
    except Exception as e:
        print(f"❌ Error al guardar en la base de datos: {e}")


# --- PROMPT V11.0 - CON MEMORIA CONTEXTUAL ---
PROMPT_PERSONA_CON_MEMORIA = """
Actúa como la voz de la marca "Asistente de Correos IA". Eres un experto en comunicación y productividad con una personalidad genuina y útil.

**Tu Misión Hoy:**
Crear un nuevo post para X (Twitter) que sea coherente con la estrategia del día y que continúe la conversación de forma natural, basándote en los posts recientes.

**Historial de Posts Recientes:**
---
{historial_reciente}
---

**Directriz Estratégica para el Post de Hoy:**
---
{directriz_del_dia}
---

**REGLAS DE ORO PARA LA COHERENCIA Y HUMANIZACIÓN:**
1.  **CONSTRUYE SOBRE LO ANTERIOR:** Analiza el historial. Si el último post fue un consejo, quizás el de hoy puede ser un ejemplo práctico de ese consejo, o un error común relacionado. Crea una narrativa. **No te repitas.**
2.  **SIN ESTRUCTURAS FIJAS:** Sé impredecible en tu formato. Varía entre preguntas, reflexiones, datos, etc.
3.  **HASHTAGS ESTRATÉGICOS:** Úsalos con moderación y de forma natural, solo si aportan valor.
4.  **REGLA 80/20 DE VALOR:** La mayoría de tus posts son 100% valor. Ocasionalmente, y solo si se siente natural, incluye un CTA para probar el "Asistente de Correos IA" en: {app_url}.

Tu objetivo es crear un timeline que se sienta como una conversación inteligente y continua, no una serie de anuncios aislados.
"""

def generar_post_contextual(directriz, url_app, historial):
    print(f"✍️  Generando post con Memoria Contextual... Directriz: '{directriz[:50]}...'")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt_final = PROMPT_PERSONA_CON_MEMORIA.format(directriz_del_dia=directriz, app_url=url_app, historial_reciente=historial)
        response = model.generate_content(prompt_final)
        print("✅ ¡Post contextual generado con éxito!")
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error al contactar a Gemini: {e}")
        return None

# --- Ejecución Principal ---
if __name__ == "__main__":
    try:
        twitter_keys = configurar_api()
        MI_APP_URL_BASE = "https://huggingface.co/spaces/jgr-soluciones-digitales/Generador-Correos-IA"
        
        # 1. Recordar los posts recientes
        historial_posts = leer_historial_reciente()
        
        # 2. Leer el plan semanal
        plan_semanal = leer_estrategia()
        
        # 3. Determinar la directriz del día
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        hoy = datetime.now().weekday()
        indice_dia_plan = hoy % 5
        dia_del_plan_str = dias_semana[indice_dia_plan]
        print(f"🗓️  Hoy es {datetime.now().strftime('%A')}. Usando la estrategia de: {dia_del_plan_str}")
        
        directriz_obj = next((item for item in plan_semanal if item["dia"] == dia_del_plan_str), None)
        
        if directriz_obj:
            directriz_de_hoy = directriz_obj["directriz"]
            pilar_de_hoy = directriz_obj.get("pilar", "N/A")

            # 4. Generar el nuevo post con contexto
            post_generado = generar_post_contextual(directriz_de_hoy, MI_APP_URL_BASE, historial_posts)
            
            if post_generado:
                print("\n--- INICIO DEL POST GENERADO ---\n")
                print(post_generado)
                print("\n--- FIN DEL POST GENERADO ---")
                
                # 5. Publicar y guardar en la memoria
                tweet_data = publicar_en_x(post_generado, twitter_keys)
                if tweet_data:
                    guardar_tweet_en_db(
                        tweet_id=tweet_data['id'],
                        contenido=post_generado,
                        pilar=pilar_de_hoy,
                        tema=directriz_de_hoy
                    )
        else:
            print(f"🤷 No se encontró una directriz para el día de hoy.")

    except (ValueError, FileNotFoundError) as e:
        print(f"❌ ERROR DE CONFIGURACIÓN O ESTRATEGIA: {e}")