from mcp.server.fastmcp import FastMCP
from pathlib import Path
import json
from utils.openlibrary import search_books_api, fetch_work_details
from prompts import BOOK_REVIEW_PROMPT

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FAV_FILE = DATA_DIR / "favorites.json"

mcp = FastMCP("Book Explorer")

# ---------- Helpers ----------
def _ensure_data_file():
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    if not FAV_FILE.exists():
        FAV_FILE.write_text("[]", encoding="utf-8")

# ---------- Tools ----------
def search_books(query: str, limit: int = 5) -> list[dict]:
    """
    Search books on Open Library by text query.
    Args:
        query (str): Search query (title/author/topic).
        limit (int): Max results (default 5).
    Returns:
        list[dict]: Simplified results with title, author, year, work_key.
    """
    return search_books_api(query, limit)

def get_book_details(work_key: str) -> dict:
    """
    Fetch detailed info for an Open Library work.
    Args:
        work_key (str): e.g., '/works/OL45804W'
    Returns:
        dict: Basic fields: title, description, subjects, first_publish_year.
    """
    return fetch_work_details(work_key)

def add_favorite(work_key: str) -> str:
    """
    Add a work to local favorites list.
    Args:
        work_key (str): '/works/OLxxxxW'
    Returns:
        str: Confirmation message.
    """
    _ensure_data_file()
    favs = json.loads(FAV_FILE.read_text(encoding="utf-8"))
    if work_key not in favs:
        favs.append(work_key)
        FAV_FILE.write_text(json.dumps(favs, ensure_ascii=False, indent=2), encoding="utf-8")
        return f"Added {work_key} to favorites."
    return f"{work_key} is already in favorites."

# ---------- Resources ----------
def list_favorites() -> str:
    """
    Read-only resource with the list of favorite work keys.
    Returns:
        str: JSON string list of favorites.
    """
    _ensure_data_file()
    return FAV_FILE.read_text(encoding="utf-8")

# ---------- Prompts ----------
def book_review_prompt(topic_or_title: str) -> list[dict]:
    """
    Return a structured prompt to ask the LLM for a review/summary.
    Args:
        topic_or_title (str): Book title or topic.
    Returns:
        list[dict]: chat-style messages (system + user).
    """
    return [
        {"role": "system", "content": BOOK_REVIEW_PROMPT},
        {"role": "user", "content": f"Please review/summarize: {topic_or_title}"},
    ]

# Register as MCP capabilities
mcp.tool()(search_books)
mcp.tool()(get_book_details)
mcp.tool()(add_favorite)

mcp.resource(
    "favorites://list",
    name="Favorite Works",
    description="JSON list of saved Open Library work keys",
    mime_type="application/json",
)(list_favorites)

mcp.prompt()(book_review_prompt)

if __name__ == "__main__":
    mcp.run()
