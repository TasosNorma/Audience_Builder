from newspaper import Article

def get_article_content(url):
    article = Article(url)
    try:
        article.download()
        article.parse()
    except Exception as e:
        print(f"Error downloading or parsing article at {url}: {e}")
        return None
    return {
        'title': article.title,
        'authors': article.authors,
        'publish_date': article.publish_date,
        'text': article.text,
        'top_image': article.top_image
    }

