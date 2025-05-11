import os
import json

REGISTRY_PATH = "uploaded_urls.json"

def load_uploaded_urls() -> set:
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_uploaded_urls(urls: set):
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(list(urls), f, indent=2)

def is_url_already_uploaded(url: str) -> bool:
    return url in load_uploaded_urls()

def mark_url_as_uploaded(url: str):
    urls = load_uploaded_urls()
    urls.add(url)
    save_uploaded_urls(urls)
