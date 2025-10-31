from duckduckgo_search import DDGS

def search_web(query):
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=5)]
        return results
