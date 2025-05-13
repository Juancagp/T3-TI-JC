import httpx
import os

LLM_API_URL = "http://asteroide.ing.uc.cl/api/generate"

def ask_llm_with_context(question: str, context: list[str]) -> str:
    prompt = (
        "Responde en base al siguiente contexto extraído de Wikipedia.\n\n"
        f"Contexto:\n{''.join(context)}\n\n"
        f"Pregunta: {question}\n"
    )

    try:
        response = httpx.post(
            LLM_API_URL,
            json={
                "model": "integracion",
                "prompt": prompt,
                "stream": False
            },
            timeout=180  # por si tarda mucho
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "(sin respuesta)")
    except Exception as e:
        return f"❌ Error al consultar el modelo: {str(e)}"
