# strategist.py (V11.0 - El Director)
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from researcher import buscar_tendencias

def configurar_api():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: raise ValueError("No se encontró la GOOGLE_API_KEY")
    genai.configure(api_key=api_key)

PROMPT_ESTRATEGA = """
Actúa como un Director de Estrategia de Contenidos de clase mundial.
Tu tarea es tomar la siguiente investigación de mercado y convertirla en un plan de temas de conversación para una semana.

**INVESTIGACIÓN DE MERCADO:**
---
{investigacion_de_mercado}
---

**REGLAS:**
1.  Analiza la investigación e identifica 3-4 conceptos clave.
2.  Crea un Plan Semanal de 5 días.
3.  Asigna un Pilar de Contenido a cada día: "Consejo de Productividad", "Tip de Redacción", "Error a Evitar", "Frase Ganadora", "Caso de Uso".
4.  Para cada día, escribe una **"directriz"**: un tema de conversación o un ángulo de alto nivel. NO escribas el tuit final.
   - Ejemplo de directriz BUENA: "Hablar sobre la importancia de la hiper-personalización en el email, más allá de solo usar el nombre del cliente."
   - Ejemplo de directriz MALA: "Escribir un tuit sobre la hiper-personalización."
5.  RESPONDE SIEMPRE EN FORMATO JSON VÁLIDO.

Crea el plan de contenido.
"""

def crear_estrategia(investigacion: str):
    print("🧠 Creando estrategia de contenido con el modelo Pro...")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt_final = PROMPT_ESTRATEGA.format(investigacion_de_mercado=investigacion)
        response = model.generate_content(prompt_final)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        estrategia_json = json.loads(cleaned_response)
        print("✅ ¡Estrategia creada con éxito!")
        return estrategia_json
    except Exception as e:
        print(f"❌ Error al crear la estrategia: {e}")
        return None

if __name__ == "__main__":
    try:
        configurar_api()
        tema = "consejos de escritura de correos electrónicos persuasivos y profesionales 2025"
        investigacion = buscar_tendencias(tema)
        if investigacion:
            estrategia = crear_estrategia(investigacion)
            if estrategia:
                with open("strategy.json", "w", encoding="utf-8") as f:
                    json.dump(estrategia, f, ensure_ascii=False, indent=2)
                print("💾 Estrategia guardada con éxito en 'strategy.json'")
                print("\nContenido del plan:")
                print(json.dumps(estrategia, indent=2, ensure_ascii=False))
    except ValueError as e:
        print(f"ERROR DE CONFIGURACIÓN: {e}")