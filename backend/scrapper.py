import wikipediaapi

def extract_title_from_url(url: str) -> str:
    if "en.wikipedia.org/wiki/" not in url:
        raise ValueError("❌ El link debe ser un artículo de Wikipedia en inglés")
    return url.split("/wiki/")[1].split("#")[0]

def get_wikipedia_article_text(url: str, lang: str = "en") -> str:
    title = extract_title_from_url(url)
    
    wiki = wikipediaapi.Wikipedia(
        language=lang,
        user_agent="TareaRAG-bot/1.0 (juan@ejemplo.cl)"
    )

    page = wiki.page(title)

    if not page.exists():
        raise ValueError(f"❌ El artículo '{title}' no existe.")

    return page.text
