import requests
from readability import Document

def get_main_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',  # Do Not Track
        'Upgrade-Insecure-Requests': '1'
    }
    response = requests.get(url, headers=headers)
    doc = Document(response.text)
    title = doc.short_title()
    content_html = doc.summary()
    
    # Convert HTML content to plain text
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content_html, 'html.parser')
    text = soup.get_text(separator='\n')
    
    return {
        'title': title,
        'text': text
    }
