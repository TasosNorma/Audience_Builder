from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.chains.base import Chain
from langchain.schema.runnable import RunnableBranch,RunnablePassthrough
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_openai import ChatOpenAI
from prompt_templates import *
import os
from typing import Dict, Optional
from extractor import extract_content_all_methods
from fetch_hacker import *


class ContentProcessor:
    # Initialize the class with LLM, it takes the API key from an environment variable.
    def __init__(self, model_name='gpt-4-mini'):
        self.llm = ChatOpenAI(openai_api_key=os.getenv('OPENAI_API_KEY'), model_name='gpt-4o-mini')

    # This takes a url and returns a beautifully constructed article based on 4 methods of extraction. 
    # The URL can be anything from a github repo to a cnbc article.
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
    
    # Here we setup the chains that are going to be used for our logic, basically we want to check if the article is
    # relevant to our profile and then create a twitter post from it
    def setup_chains(self,article):
        """Initialize the processing chains"""
        self.relevance_chain = relevance_prompt | self.llm | (lambda x: {
            "content": article,
            "relevance_result": x.content
        })

        self.post_chain = post_prompt | self.llm | (lambda x: {
            "social_post": x.content
        })

        self.branch = RunnableBranch(
            (lambda x: x["relevance_result"].lower() == "yes", self.post_chain),
            (lambda x: None)
        )

        self.chain = self.relevance_chain | self.branch    

    # Here we create a twitter post from the article. 
    # We take the article, we setup the chains and then we invoke them.
    # The post is in a form of a list of tweets created by the 
    def process_url(self, url: str) -> Optional[Dict]:
        """Process a single URL and generate social media posts if relevant"""
        try:
            self.article = self._extract_content(url)
            if not self.article:
                return self._create_response("error", "Failed to extract content from URL", url)

            self.setup_chains(self.article)
            result = self.chain.invoke({
                "content": self.article,
            })

            if result is None:
                return self._create_response("not_relevant", 
                    "Content not relevant to data/analytics sector", url)

            social_post = result.get('social_post', '')
            if not social_post:
                return self._create_response("error", 
                    "Failed to generate social post", url)

            tweets = self._parse_tweets(social_post)
            return {
                "status": "success",
                "tweets": tweets,
                "tweet_count": len(tweets),
                "url": url
            }

        except Exception as e:
            return self._create_response("error", f"An error occurred: {str(e)}", url)
        
    @staticmethod
    def _parse_tweets(social_post: str) -> list:
        """Split and clean tweets from social post"""
        return [tweet.strip() for tweet in social_post.split('\n\n') 
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