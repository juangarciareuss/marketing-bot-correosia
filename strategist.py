
# strategist.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from researcher import buscar_tendencias

def configurar_api():
    """Configura la API de Gemini."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No se encontró la GOOGLE_API_KEY en el archivo .env")
    genai.configure(api_key=api_key)

PROMPT_ESTRATEGA = """
Actúa como un Director de Estrategia de Contenidos (Head of Content Strategy) de clase mundial.
Tu tarea es tomar la siguiente investigación de mercado sobre un tema y convertirla en un plan de contenido concreto para una semana en X (Twitter).

**INVESTIGACIÓN DE MERCADO:**
---
{investigacion_de_mercado}
---

**REGLAS:**
1.  **Analiza la investigación:** Identifica los 3-4 conceptos más importantes, novedosos o impactantes.
2.  **Crea un Plan Semanal:** Diseña un plan de contenido para 5 días (Lunes a Viernes).
3.  **Asigna un Pilar de Contenido a cada día:** Usa los pilares: "Consejo Experto", "Estadística Impactante", "Error Común", "Plantilla Rápida", "Caso de Uso".
4.  **Conecta los Pilares a la Investigación:** Cada post diario debe basarse en uno de los conceptos que identificaste en la investigación.
5.  **RESPONDE SIEMPRE EN FORMATO JSON VÁLIDO.** Tu salida debe ser un objeto JSON que contenga una clave "plan_semanal". Esta clave contendrá una lista de 5 objetos, uno para cada día.

**FORMATO DE SALIDA JSON (EJEMPLO ESTRICTO):**
```json
{{
  "plan_semanal": [
    {{
      "dia": "Lunes",
      "pilar": "Consejo Experto",
      "directriz": "Crear un post que dé un consejo práctico sobre la hiper-personalización en el email, mencionando el uso de IA."
    }},
    {{
      "dia": "Martes",
      "pilar": "Error Común",
      "directriz": "Crear un post que hable del error de no tener los emails autenticados (SPF, DKIM) y cómo afecta la entregabilidad."
    }}
  ]
}}
Ahora, crea el plan de contenido para la próxima semana basado en la investigación proporcionada.
"""

def crear_estrategia(investigacion: str):
    """Usa la IA para convertir la investigación en un plan estratégico."""
    print("🧠 Creando estrategia de contenido semanal con el modelo Pro...")
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
    
# --- Ejecución Principal ---
if __name__ == "__main__":
    try:
        configurar_api()

        tema = "tendencias de email marketing para el público de startups"
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