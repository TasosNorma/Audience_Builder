import asyncio
import os
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from urllib.parse import urlparse

# This is to help the URL extraction function
class UrlSchema(BaseModel):
    title: str = Field(..., description='The title of the link, indicative')
    url: str = Field(..., description='The actual url')

# Takes a url and tries to re-create the article of the URL as realistically as possible.
async def extract_article_content(url):
    async with AsyncWebCrawler(verbose = True) as crawler:
        result = await crawler.arun(
            url=url,
            word_count_threshold=5,
            extraction_strategy=LLMExtractionStrategy(
                provider='openai/gpt-4o-mini',
                api_token=os.getenv('OPENAI_API_KEY'),
                instruction=""" 
You are an expert at reading raw webpage markup and reconstructing the original article text. You will be given the complete HTML markup of a webpage that contains an article. Your task is to produce the clean article text in a well-structured, hierarchical format, reflecting the original headings and subheadings as closely as possible.
# Instructions:
* Article Content Only: Reproduce only the main article text. Omit any content not integral to the article (e.g., ads, navigation menus, related posts, social media links, comments).
* No Additional Commentary: Do not include your own explanations or remarks. Present only what the original author wrote.
* Don't Repeat Yourself: Do not repeat yourself, if you've said something once, do not say it again at the end of the article
* Clean and Hierarchical Structure:
* Use a clear hierarchy for titles and headings (e.g., # for the main title, ## for subheadings, etc.)
* Maintain paragraph structure and any lists the author included.
* Do not restate content unnecessarily. If something appears once, do not repeat it unless it was repeated in the original text.
* No Non-textual Elements: Exclude images, URLs, and references that are not essential for understanding the article's core message.
Your final output should be a neatly organized version of the article's textual content, suitable for further processing or summarization.
                """
            ),
            bypass_cache=True
        )
    content_blocks = json.loads(result.extracted_content)
    formatted_article = []
    for block in content_blocks:
        if 'content' in block:
            formatted_article.extend(block['content'])
    
    article = "\n\n".join(formatted_article)
    return article

# Takes a url and returns all the relevant urls referenced in the article of this URL
async def extract_relevant_urls(url):
    domain = urlparse(url).netloc 
    base_url = f"https://{domain}"
    formatted_urls = []
    async with AsyncWebCrawler(verbose = True) as crawler:
        result = await crawler.arun(
            url=url,
            extraction_strategy=LLMExtractionStrategy(
                provider='openai/gpt-4o-mini',
                api_token=os.getenv('OPENAI_API_KEY'),
                schema= UrlSchema.model_json_schema(),
                extraction_type='schema',
                instruction="""You are given an HTML document representing an article. 
                INSTRUCTIONS:
                1. Identify all relevant articles that the current article links to. These will be <a> tags located in the main content area of the article.
                2. Exclude any links that are not relevant to the main content (ignore nav menus, ads, headers, footers).
                3. Extract only the top 5 most relevants, don't return more than 5 articles
                3. Output the final result as a JSON array, where each element is an object with "title" and "url" fields.
                Example:
                [{
                    "title": "Article Title",
                    "url": "https://example.com/article-url"
                }]
                """
            ),
            bypass_cache = True
        )
        urls = json.loads(result.extracted_content)
        for article in urls:
            article_url = article['url']
            if article_url.startswith('/'):
                article_url = f"{base_url}{article_url}"
                # print(article_url)
            formatted_urls.append(article_url)
        print(formatted_urls)
        return formatted_urls

# Takes a url and returns a small summary
async def write_small_summary(url):
    async with AsyncWebCrawler(verbose = True) as crawler:
        result = await crawler.arun(
            url=url,
            word_count_threshold=5,
            extraction_strategy=LLMExtractionStrategy(
                provider='openai/gpt-4o-mini',
                api_token=os.getenv('OPENAI_API_KEY'),
                instruction="""You are tasked with creating a concise summary of the provided webpage content.

INSTRUCTIONS:
1. Create a summary of approximately 3-4 sentences (100-150 words)
2. Focus on answering:
   - What is the main topic/announcement?
   - What are the key benefits or implications?
   - What are the most important technical details or facts?

GUIDELINES:
- Be factual and objective
- Use clear, direct language
- Avoid marketing language or subjective claims
- Include specific numbers or metrics when present
- Exclude quotes unless absolutely crucial
- Do not include background information about the company
- Do not mention the article's author or publication date

FORMAT:
Return only the summary text, with no additional headers or metadata."""
            ),
            bypass_cache = True
        )
        
        content_blocks = json.loads(result.extracted_content)
        formatted_article = []
        for block in content_blocks:
            if 'content' in block:
                formatted_article.extend(block['content'])
    
        summary = "\n\n".join(formatted_article)
        return summary.strip()

# This is the main function, It takes the url and returns a dictionary of all relevant URLs and their Summary. 
async def get_summaries_of_urls(url:str) -> dict:
    urls = await extract_relevant_urls(url)
    summaries = {}
    for article_url in urls:
        try:
            summary = await write_small_summary(article_url)
            summaries[article_url]= summary
        except Exception as e:
            print(f"Error processing {article_url}: {str(e)}")
            summaries[article_url] = "Error: Could not generate summary"
    return summaries

# This takes a dictionary from get_summaries_of_urls and returns a string in nice format to passed into another prompt
def format_summaries(summaries:dict) -> str:
    formatted_output = []
    for index,(url,summary) in enumerate(summaries.items(),1):
        article_block = f"""
Article: {index}
URL: {url}
Content: {summary}
"""
        formatted_output.append(article_block)
    return "\n".join(formatted_output)

# This takes a dictionary from get_summaries_of_urls and returns a string in nice format to passed into another prompt
async def get_formatted_summaries(url: str) -> str:
    summaries = await get_summaries_of_urls(url)
    formatted_output = []
    for index, (url, summary) in enumerate(summaries.items(), 1):
        article_block = f"""**Article: {index}**
URL: {url}
Content: {summary}

---
"""
        formatted_output.append(article_block)
    
    return "\n".join(formatted_output)

# Example usage:
if __name__ == "__main__":
    formatted_result = asyncio.run(get_formatted_summaries('https://www.databricks.com/blog/introducing-structured-outputs-batch-and-agent-workflows'))
    print(formatted_result)