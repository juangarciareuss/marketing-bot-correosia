# analyst.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import tweepy

def main():
    """
    El proceso principal del analista: leer tweets de la BD,
    obtener sus métricas de la API de X, y actualizar la BD.
    """
    print("🤖 Iniciando el Analista de Rendimiento...")
    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("No se encontró DATABASE_URL en el .env")

    # --- Conexión a la Base de Datos ---
    engine = create_engine(db_url)

    tweet_ids_a_revisar = []
    try:
        with engine.connect() as connection:
            print("📖 Leyendo tweets publicados recientemente desde la base de datos...")
            query = text("SELECT tweet_id FROM tweets_publicados WHERE fecha_publicacion > NOW() - INTERVAL '7 days'")
            result = connection.execute(query)
            tweet_ids_a_revisar = [row[0] for row in result]

            if not tweet_ids_a_revisar:
                print("🤷 No se encontraron tweets recientes para analizar. Saliendo.")
                return

            print(f"📊 Se encontraron {len(tweet_ids_a_revisar)} tweets para analizar.")

    except Exception as e:
        print(f"❌ Error al leer de la base de datos: {e}")
        return

    # --- Conexión a la API de X (Twitter) ---
    twitter_keys = {
        "api_key": os.getenv("API_KEY_X"), "api_key_secret": os.getenv("API_KEY_SECRET_X"),
        "access_token": os.getenv("ACCESS_TOKEN_X"), "access_token_secret": os.getenv("ACCESS_TOKEN_SECRET_X")
    }
    if not all(twitter_keys.values()):
        raise ValueError("Faltan claves de la API de X en el .env")

    try:
        print("🐦 Conectando a la API de X para obtener métricas...")
        client = tweepy.Client(
            consumer_key=twitter_keys["api_key"], consumer_secret=twitter_keys["api_key_secret"],
            access_token=twitter_keys["access_token"], access_token_secret=twitter_keys["access_token_secret"]
        )

        # Pedimos las métricas públicas de los tweets
        response = client.get_tweets(ids=tweet_ids_a_revisar, tweet_fields=["public_metrics"])

        if response.data:
            print(f"📈 Se obtuvieron métricas para {len(response.data)} tweets.")
            # --- Actualizar la Base de Datos con las Métricas ---
            with engine.connect() as connection:
                for tweet in response.data:
                    metrics = tweet.public_metrics
                    update_query = text("""
                        UPDATE tweets_publicados
                        SET likes = :likes, retweets = :retweets, impresiones = :impresiones
                        WHERE tweet_id = :id
                    """)
                    connection.execute(update_query, {
                        "likes": metrics.get('like_count', 0),
                        "retweets": metrics.get('retweet_count', 0),
                        "impresiones": metrics.get('impression_count', 0),
                        "id": tweet.id
                    })
                connection.commit()
                print("💾 Base de datos actualizada con las nuevas métricas de engagement.")

    except Exception as e:
        print(f"❌ Error al obtener o guardar métricas de X: {e}")


if __name__ == "__main__":
    main()