import faiss
import os
import json
from typing import List, Tuple
import numpy as np


VECTOR_DIM = 768
INDEX_PATH = "faiss_index.index"
METADATA_PATH = "faiss_metadata.json"

# globales en memoria (cargan al importar)
index = None
metadata: List[str] = []

def load_vector_store():
    global index, metadata
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
    else:
        index = faiss.IndexFlatL2(VECTOR_DIM)

    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata.extend(json.load(f))

def save_vector_store():
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def add_documents(chunks: List[str], embeddings: List[List[float]]):
    """
    Agrega nuevos vectores y chunks al índice y metadatos.
    """
    global index, metadata
    if len(chunks) != len(embeddings):
        raise ValueError("chunks y embeddings deben tener la misma longitud.")

    index.add(np.array(embeddings).astype("float32"))
    metadata.extend(chunks)
    save_vector_store()

def search_similar(query_vector: List[float], k: int = 5) -> List[Tuple[str, float]]:
    """
    Devuelve los k fragmentos más similares junto a su distancia.
    """
    query = np.array([query_vector]).astype("float32")
    distances, indices = index.search(query, k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx < len(metadata):
            results.append((metadata[idx], float(dist)))

    return results
