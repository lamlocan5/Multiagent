from typing import List, Dict, Any, Optional, Union
import aiohttp
import asyncio
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

async def web_search(
    query: str,
    num_results: int = 5,
    language: str = "en",
    region: Optional[str] = None,
    safe_search: bool = True
) -> List[Dict[str, Any]]:
    """
    Perform a web search using SerpAPI.
    
    Args:
        query: Search query
        num_results: Number of results to return
        language: Language code (e.g., 'en', 'vi')
        region: Region code (e.g., 'us', 'vn')
        safe_search: Whether to enable safe search
        
    Returns:
        List of search results
    """
    api_key = settings.SERPAPI_API_KEY
    if not api_key:
        logger.warning("No SerpAPI key available, returning mock search results")
        return _mock_search_results(query, num_results)
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": num_results,
        "hl": language
    }
    
    # Add optional parameters
    if region:
        params["gl"] = region
    
    if safe_search:
        params["safe"] = "active"
    
    try:
        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.get("https://serpapi.com/search", params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"SerpAPI error: {response.status} - {error_text}")
                    return _mock_search_results(query, num_results)
                
                data = await response.json()
                
                # Extract organic results
                results = []
                if "organic_results" in data:
                    for result in data["organic_results"][:num_results]:
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "position": result.get("position", 0)
                        })
                
                return results
    except Exception as e:
        logger.error(f"Web search error: {str(e)}")
        return _mock_search_results(query, num_results)

def _mock_search_results(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """Generate mock search results for testing."""
    logger.warning(f"Generating mock search results for query: {query}")
    
    results = []
    for i in range(min(num_results, 3)):
        results.append({
            "title": f"Mock Result {i+1} for '{query}'",
            "url": f"https://example.com/result/{i+1}",
            "snippet": f"This is a mock search result for '{query}'. " 
                      f"This would contain actual content in a real search.",
            "position": i+1
        })
    
    return results

async def fetch_webpage_content(url: str) -> Dict[str, Any]:
    """
    Fetch and extract content from a webpage.
    
    Args:
        url: URL to fetch
        
    Returns:
        Dictionary with extracted content and metadata
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    return {
                        "url": url,
                        "success": False,
                        "error": f"HTTP Error: {response.status}"
                    }
                
                content_type = response.headers.get("Content-Type", "")
                
                # Handle only HTML content
                if "text/html" not in content_type:
                    return {
                        "url": url,
                        "success": False,
                        "error": f"Not HTML content: {content_type}"
                    }
                
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.extract()
                
                # Extract title
                title = soup.title.string if soup.title else ""
                
                # Extract main content
                main_content = ""
                
                # Try to find main content
                main_elements = soup.find_all(["article", "main", "div"], class_=re.compile("content|article|post"))
                if main_elements:
                    for element in main_elements:
                        main_content += element.get_text(separator=" ", strip=True) + "\n\n"
                else:
                    # Fallback to body
                    main_content = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
                
                # Extract metadata
                meta_description = ""
                meta_tag = soup.find("meta", attrs={"name": "description"})
                if meta_tag:
                    meta_description = meta_tag.get("content", "")
                
                return {
                    "url": url,
                    "success": True,
                    "title": title,
                    "content": main_content,
                    "description": meta_description,
                    "word_count": len(main_content.split())
                }
    
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return {
            "url": url,
            "success": False,
            "error": str(e)
        }

async def enrich_search_results(results: List[Dict[str, Any]], fetch_content: bool = True) -> List[Dict[str, Any]]:
    """
    Enrich search results with additional content.
    
    Args:
        results: Search results to enrich
        fetch_content: Whether to fetch full content for each result
        
    Returns:
        Enriched search results
    """
    if not fetch_content:
        return results
    
    enriched_results = []
    
    # Fetch content for all results concurrently
    tasks = [fetch_webpage_content(result["url"]) for result in results]
    content_results = await asyncio.gather(*tasks)
    
    # Combine original results with fetched content
    for i, result in enumerate(results):
        content_result = content_results[i]
        
        if content_result["success"]:
            enriched_results.append({
                **result,
                "full_content": content_result["content"],
                "full_title": content_result.get("title", result["title"]),
                "word_count": content_result.get("word_count", 0)
            })
        else:
            # Keep original result if fetching failed
            enriched_results.append({
                **result,
                "full_content": None,
                "fetch_error": content_result.get("error")
            })
    
    return enriched_results
