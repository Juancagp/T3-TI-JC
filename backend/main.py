from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scrapper import get_wikipedia_article_text
from text_splitter import split_text_by_paragraphs
from embeddings import embed_texts
from vector_store import load_vector_store, add_documents, search_similar
from upload_registry import is_url_already_uploaded, mark_url_as_uploaded
from llm_client import ask_llm_with_context


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


    
# Inicializar app FastAPI
app = FastAPI()

# Habilitar CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar FAISS + metadatos al iniciar
load_vector_store()

# Entrada para /scrape
class ScrapeRequest(BaseModel):
    url: str


@app.get("/")
def home():
    return {"message": "Backend activo"}

@app.post("/scrape")
async def scrape_article(body: ScrapeRequest):
    try:
        # Verifica si ya fue subido
        if is_url_already_uploaded(body.url):
            return {
                "message": "Este artículo ya fue subido anteriormente. Puedes hacer preguntas.",
                "already_uploaded": True
            }

        # 1. Scraping
        text = get_wikipedia_article_text(body.url)

        # 2. Chunking
        chunks = split_text_by_paragraphs(text)
        if not chunks:
            raise Exception("No se pudieron generar fragmentos del artículo.")

        # 3. Embeddings
        embeddings = embed_texts(chunks)

        # 4. Guardar en FAISS
        add_documents(chunks, embeddings)

        # 5. Registrar el link
        mark_url_as_uploaded(body.url)

        return {
            "message": "Artículo procesado y almacenado exitosamente.",
            "num_chunks": len(chunks),
            "already_uploaded": False,
            "preview": text[:1000]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ask")
async def ask_question(body: AskRequest):
    try:
        question_embedding = embed_texts([body.question])[0]
        results = search_similar(question_embedding, k=body.top_k)

        return {
            "question": body.question,
            "matches": [
                {"chunk": chunk, "distance": round(dist, 4)}
                for chunk, dist in results
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/askllm")
async def ask_question(body: AskRequest):
    try:
        question_embedding = embed_texts([body.question])[0]
        raw_results = search_similar(question_embedding, k=body.top_k * 2)

        seen = set()
        filtered = []
        for chunk, dist in raw_results:
            if chunk not in seen:
                filtered.append(chunk)
                seen.add(chunk)
            if len(filtered) == body.top_k:
                break

        llm_response = ask_llm_with_context(body.question, filtered)

        return {
            "question": body.question,
            "answer": llm_response,
            "context_used": filtered
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

