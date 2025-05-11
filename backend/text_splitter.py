from typing import List

def split_text_by_paragraphs(text: str, max_chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """
    Separa el texto en chunks agrupando párrafos, sin exceder `max_chunk_size`.
    Puede agregar solapamiento (overlap) entre chunks.
    """
    raw_paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    
    chunks = []
    current_chunk = []

    for paragraph in raw_paragraphs:
        current_text = " ".join(current_chunk)
        if len(current_text) + len(paragraph) + 1 <= max_chunk_size:
            current_chunk.append(paragraph)
        else:
            # guardar chunk actual
            chunks.append(current_text.strip())

            # solapamiento opcional (usa últimas palabras del chunk anterior)
            if overlap > 0 and current_chunk:
                last_text = " ".join(current_chunk)
                last_overlap = last_text[-overlap:]
                current_chunk = [last_overlap.strip(), paragraph]
            else:
                current_chunk = [paragraph]

    # añadir el último chunk si queda algo
    if current_chunk:
        chunks.append(" ".join(current_chunk).strip())

    return chunks
