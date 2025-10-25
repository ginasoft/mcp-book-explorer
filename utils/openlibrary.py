import httpx

BASE = "https://openlibrary.org"

def search_books_api(query: str, limit: int = 5) -> list[dict]:
    r = httpx.get(f"{BASE}/search.json", params={"q": query, "limit": limit}, timeout=30)
    r.raise_for_status()
    data = r.json()
    out = []
    for doc in data.get("docs", []):
        work_key = doc.get("key")  # e.g., "/works/OL45804W"
        if work_key and work_key.startswith("/works/"):
            out.append({
                "title": doc.get("title"),
                "author": (doc.get("author_name") or [None])[0],
                "first_publish_year": doc.get("first_publish_year"),
                "work_key": work_key
            })
    return out

def fetch_work_details(work_key: str) -> dict:
    # work_key example: "/works/OL45804W"
    if not work_key.startswith("/works/"):
        raise ValueError("work_key must look like '/works/OLxxxxW'")
    r = httpx.get(f"{BASE}{work_key}.json", timeout=30)
    r.raise_for_status()
    j = r.json()
    desc = j.get("description")
    if isinstance(desc, dict):
        desc = desc.get("value")
    return {
        "title": j.get("title"),
        "description": desc,
        "subjects": j.get("subjects"),
        "first_publish_date": j.get("first_publish_date"),
        "key": j.get("key"),
    }
