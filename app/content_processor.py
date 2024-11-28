from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.chains.base import Chain
from langchain.schema.runnable import RunnableBranch,RunnablePassthrough
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_openai import ChatOpenAI
from app.prompt_templates import *
import os
from typing import Dict, Optional
from app.extractor import extract_content_all_methods


class ContentProcessor:
    # Initialize the class with LLM, it takes the API key from an environment variable.
    def __init__(self, model_name='gpt-4-mini'):
        self.llm = ChatOpenAI(openai_api_key=os.getenv('OPENAI_API_KEY'), model_name='gpt-4o-mini')

    # This takes a url and returns a beautifully constructed article based on 4 methods of extraction. 
    def _extract_content(self, url: str) -> Optional[str]:
        """Extract content from URL"""
        extracted_content = extract_content_all_methods(url)
        if not extracted_content or 'llm_analysis' not in extracted_content:
            return {
                "status": "error",
                "message": "Failed to extract content from URL",
                "url": url
            }
        article_text = extracted_content['llm_analysis']
        return article_text
    

    def setup_chains(self, article):
        """Initialize the processing chains"""
        self.post_chain = post_prompt | self.llm


    def process_url(self, url: str) -> Optional[Dict]:
        """Process a single URL and generate social media posts if relevant"""
        try:
            print('Extracting Content from URL')
            self.article = self._extract_content(url)
            print(f'Article extraction result: {self.article}')
            
            if not self.article:
                return self._create_response("error", "Failed to extract content from URL", url)
            else:
                print('Contents from URL extracted')
            
            print('Setting up Chains')
            self.setup_chains(self.article)
            
            print('Running chain...')
            try:
                result = self.post_chain.invoke({"content": self.article})
                print(f'Chain result: {result.content[:100]}...')
            except Exception as chain_error:
                print(f'Chain error: {str(chain_error)}')
                raise

            if not result:
                return self._create_response("error", "Failed to generate social post", url)
            else: 
                print('Social Post generated')

            print('Parsing tweets')
            tweets = self._parse_tweets(result)

            return {
                "status": "success",
                "tweets": tweets,
                "tweet_count": len(tweets),
                "url": url
            }

        except Exception as e:
            print(f'Detailed error: {type(e).__name__}: {str(e)}')
            return self._create_response("error", f"An error occurred: {str(e)}", url)
        
    @staticmethod
    def _parse_tweets(social_post: str) -> list:
        """Split and clean tweets from social post"""
        content = social_post.content if hasattr(social_post, 'content') else social_post
        return [tweet.strip() for tweet in content.split('\n\n') 
                if tweet.strip() and not tweet.isspace()]
    
    @staticmethod
    def _create_response(status: str, message: str, url: str) -> Dict:
        """Create a standardized response dictionary"""
        return {
            "status": status,
            "message": message,
            "url": url
        }
        


if __name__ == "__main__":
    processor = ContentProcessor()
    test_url = "https://www.cnbc.com/2024/06/12/databricks-says-annualized-revenue-to-reach-2point4-billion-in-first-half.html"
    result = processor.process_url(test_url)
    print("\nTest Result:")
    print(result)