# researcher.py
import os
import google.generativeai as genai

def buscar_tendencias(tema: str, max_resultados=5):
    """
    Usa la Búsqueda de Google a través de la API de Gemini para encontrar
    tendencias recientes sobre un tema específico.
    Devuelve un string formateado con los resultados.
    """
    print(f"🔬 Investigando tendencias sobre: '{tema}'...")
    try:
        # Usamos el modelo con la herramienta de búsqueda integrada
# CÓDIGO CORREGIDO
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',
            tools=[genai.protos.Tool(
                google_search_retrieval=genai.protos.GoogleSearchRetrieval() # Parámetro eliminado
            )]
        )
        
        # El prompt le pide al modelo que use la herramienta de búsqueda
        prompt = f"Busca en Google y resume en puntos clave las tendencias más recientes y novedosas sobre '{tema}'. Dame una lista de {max_resultados} puntos."
        
        response = model.generate_content(prompt)
        
        print("✅ Investigación completada.")
        return response.text
    except Exception as e:
        print(f"❌ Error durante la investigación: {e}")
        return None

if __name__ == '__main__':
    # Esto es para probar el investigador por sí solo
    # Debes tener tu GOOGLE_API_KEY en el .env
    from dotenv import load_dotenv
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    tema_de_investigacion = "tendencias de email marketing para startups en 2025"
    resultados = buscar_tendencias(tema_de_investigacion)
    
    if resultados:
        print("\n--- RESULTADOS DE LA INVESTIGACIÓN ---\n")
        print(resultados)
        print("\n--- FIN DE LA INVESTIGACIÓN ---")