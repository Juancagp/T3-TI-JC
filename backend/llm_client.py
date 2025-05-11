import os
from dotenv import load_dotenv
from google import genai

load_dotenv()  # esto carga las variables desde .env

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def ask_llm_with_context(question: str, context_chunks: list[str]) -> str:
    """
    Arma el prompt a partir del contexto + pregunta y llama a Gemini.
    """
    context = "\n\n".join(context_chunks)

    prompt = f"""Responde la siguiente pregunta en base al contexto entregado.

    Contexto:
    {context}

    Pregunta:
    {question}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",  # o "gemini-2.0-flash" si prefieres velocidad
        contents=prompt
    )

    return response.text
