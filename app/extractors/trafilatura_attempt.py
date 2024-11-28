import trafilatura
import requests

def extract_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        # First get the page content with requests
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Then use trafilatura to extract the content
        content = trafilatura.extract(response.text)
        
        return content
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None
