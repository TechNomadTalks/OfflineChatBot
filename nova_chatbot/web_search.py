"""
Web search functionality using DuckDuckGo.
"""

from ddgs import DDGS


def search_web(query, max_results=5):
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        List of dictionaries containing title, href, and body for each result
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return results
    except Exception as e:
        return [{"title": "Search Error", "href": "", "body": f"Failed to search: {str(e)}"}]
