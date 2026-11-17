import requests
import html
import re

HEADERS = {
    "User-Agent": "AntigravityAgent/2.0 (Windows NT 10.0; Win64; x64)"
}

def search_web(query: str, max_results: int = 4) -> str:
    """
    Search online technical resources (StackOverflow & Knowledge Base) for:
    - Code errors and tracebacks
    - Library documentation
    - Implementation examples
    Requires zero login and zero API keys!
    """
    results = []
    
    # 1. Search StackOverflow for error messages and programming questions
    try:
        so_url = "https://api.stackexchange.com/2.3/search/advanced"
        params = {
            "order": "desc",
            "sort": "relevance",
            "q": query,
            "site": "stackoverflow",
            "pagesize": max_results
        }
        resp = requests.get(so_url, params=params, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            for idx, item in enumerate(items, 1):
                title = html.unescape(item.get("title", ""))
                link = item.get("link", "")
                is_answered = item.get("is_answered", False)
                score = item.get("score", 0)
                tags = ", ".join(item.get("tags", []))
                status = "Answered" if is_answered else "Open"
                results.append(
                    f"[{idx}] {title}\n"
                    f"    Status: {status} (Score: {score}) | Tags: [{tags}]\n"
                    f"    URL: {link}"
                )
    except Exception as e:
        results.append(f"[StackOverflow Search Notice]: {str(e)}")

    # 2. Search Wikipedia/Technical Encyclopedia if general concept or tech overview
    try:
        wiki_url = "https://en.wikipedia.org/w/api.php"
        wiki_params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 2
        }
        w_resp = requests.get(wiki_url, params=wiki_params, headers=HEADERS, timeout=6)
        if w_resp.status_code == 200:
            w_data = w_resp.json()
            search_items = w_data.get("query", {}).get("search", [])
            for w in search_items:
                w_title = w.get("title", "")
                w_snippet = re.sub(r'<[^>]+>', '', html.unescape(w.get("snippet", "")))
                results.append(f"[Wiki Reference] {w_title}:\n    {w_snippet}")
    except Exception:
        pass

    if not results:
        return f"No online technical discussions found for query: '{query}'."

    return "\n\n".join(results)
