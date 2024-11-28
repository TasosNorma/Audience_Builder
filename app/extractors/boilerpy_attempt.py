from boilerpy3 import extractors
import requests

def extract_text(url):
    extractor = extractors.ArticleExtractor()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        # First get the page content with headers
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        # Then pass the text content to boilerpy
        content = extractor.get_content(response.text)
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None
    return content
