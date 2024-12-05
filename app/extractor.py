from typing import Dict, Optional
import openai
import os

# Import your existing functions
from app.extractors.newspaper3k_attempt import get_article_content as newspaper3k_extract
from app.extractors.trafilatura_attempt import extract_text as trafilatura_extract
from app.extractors.boilerpy_attempt import extract_text as boilerpy_extract
from app.extractors.readability_attempt import get_main_content as readability_extract


"""Creates a prompt for the LLM using the extracted contents."""
def create_llm_prompt(extracted_contents: Dict[str, Optional[str]]) -> str:
    prompt = """I have extracted the contents of a webpage using 4 different methods. 
    Using these extracted versions, please reconstruct the content into a well-structured article format. 
    The article should maintain the original information and flow, but be cleanly formatted with proper 
    headings, paragraphs, and sections. Ignore any parsing artifacts or incomplete extractions.

    Here are the different versions:
    """
    for method, content in extracted_contents.items():
        prompt += f"\n\n{method.upper()} VERSION:\n{content if content else 'No content extracted'}"

    prompt += "\n\nPlease reconstruct this content into a well-structured article that maintains the original information and context."
    return prompt



"""Sends the extracted contents to OpenAI and gets back an analysis."""
def get_llm_analysis(extracted_contents: Dict[str, Optional[str]]) -> str:
    prompt = create_llm_prompt(extracted_contents)
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at reconstructing webpage contents into well-structured articles. Format the content with appropriate headings, sections, and paragraphs while maintaining the original information and context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM analysis failed: {e}"

# Gets a url, extracts all the relevant data 4 times and then passes it into the llm 
# which writes a clean article from scratch without all the clutter of the internet
def extract_content_all_methods(url: str) -> Dict[str, Optional[str]]:
    """
    Extracts content from a URL using multiple extraction methods.
    Returns a dictionary with results from each method.
    """
    results = {
        'newspaper3k': None,
        'trafilatura': None,
        'boilerpy': None,
        'readability': None
    }

    try:
        results['newspaper3k'] = newspaper3k_extract(url)
    except Exception as e:
        print(f"Newspaper3k extraction failed: {e}")

    try:
        results['trafilatura'] = trafilatura_extract(url)
    except Exception as e:
        print(f"Trafilatura extraction failed: {e}")

    try:
        results['boilerpy'] = boilerpy_extract(url)
    except Exception as e:
        print(f"Boilerpy extraction failed: {e}")

    try:
        readability_result = readability_extract(url)
        results['readability'] = readability_result.get('text') if readability_result else None
    except Exception as e:
        print(f"Readability extraction failed: {e}")

    results['llm_analysis'] = get_llm_analysis(results)

    return results


if __name__ == "__main__":
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    
    url = "https://www.worldlabs.ai/blog"
    results = extract_content_all_methods(url)
    
    # Print LLM analysis
    print("\nLLM ANALYSIS:")
    print(results['llm_analysis'])
    print("-" * 50)
        