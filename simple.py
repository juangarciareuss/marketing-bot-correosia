# simple.py (Test de Longitud)
import os
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session

print("--- Iniciando prueba de TUIT LARGO ---")

load_dotenv()
twitter_keys = {
    "api_key": os.getenv("API_KEY_X"),
    "api_key_secret": os.getenv("API_KEY_SECRET_X"),
    "access_token": os.getenv("ACCESS_TOKEN_X"),
    "access_token_secret": os.getenv("ACCESS_TOKEN_SECRET_X")
}

if not all(twitter_keys.values()):
    print("❌ ERROR: Faltan claves de la API de X en el archivo .env.")
else:
    # Texto largo y con hashtags, pero escrito por un humano
    texto_del_tweet = (
        "Esta es una prueba de un tuit largo desde el script simple. "
        "El objetivo es verificar si la API de X bloquea los posts basados en la longitud "
        "del contenido en el plan gratuito. Si este post se publica, el problema es otro. "
        "#PruebaAPI #Debug"
    )

    url = "https://api.twitter.com/2/tweets"
    payload = {"text": texto_del_tweet}

    print(f"📝 Intentando publicar un tuit largo ({len(texto_del_tweet)} caracteres)...")

    try:
        oauth = OAuth1Session(
            client_key=twitter_keys["api_key"], client_secret=twitter_keys["api_key_secret"],
            resource_owner_key=twitter_keys["access_token"], resource_owner_secret=twitter_keys["access_token_secret"]
        )
        response = oauth.post(url, json=payload)

        if response.status_code != 201:
            raise Exception(f"Error: {response.status_code} {response.text}")

        response_data = response.json()
        tweet_id = response_data["data"]["id"]
        print(f"✅ ¡ÉXITO! El tuit largo fue publicado. ID: {tweet_id}")

    except Exception as e:
        print("❌ FALLO: La publicación del tuit largo fue bloqueada.")
        print(f"Error específico: {e}")

print("\n--- Prueba finalizada ---")