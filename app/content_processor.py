from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.chains.base import Chain
from langchain.schema.runnable import RunnableBranch,RunnablePassthrough
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_openai import ChatOpenAI
from trash.prompt_templates import *
import os
from typing import Dict, Optional
from app.database.database import *
from app.database.models import Prompt
from langchain.prompts import PromptTemplate
from app.crawl4ai import *

class ContentProcessor:
    # Initialize the class with LLM, it takes the API key from an environment variable.
    def __init__(self):
        self.llm = ChatOpenAI(openai_api_key=os.getenv('OPENAI_API_KEY'), model_name='gpt-4o-mini')
    
    # Here we give the name of the Prompt i.e. the value inside the column "Name"
    def get_prompt(self, id: int) -> Optional[str]:
        db = SessionLocal()
        try:
            prompt = db.query(Prompt).filter(Prompt.id == id).first()
            print(f"Fetched the template from the database and the template is :{prompt.template}")
            return prompt.template if prompt else None
        except Exception as e:
            print(f"Error fetching prompt from database {str(e)}")
            return None
        finally:
            db.close()

    # This takes a url and returns a beautifully constructed article based on 1 method of extraction that is used in the secondary articles aswell.
    def _extract_content_crawl4ai(self,url:str) -> Optional[str]:
        try:
            self.crawl4ai_article = asyncio.run(extract_article_content(url))
        except Exception as e:
            print(f"Error extracting article content with crawl4ai: {str(e)}")
            self.crawl4ai_article = None
        return self.crawl4ai_article

    # Although not really necessary, we create a chain for our OpenAI interaction
    def setup_chain(self):
        self.prompt = self.get_prompt(1)
        self.prompt_template = PromptTemplate(template=self.prompt,input_variables=["primary","secondary"])
        self.post_chain = self.prompt_template | self.llm

    # This is a method that takes the string of the final post and breaks it down to sub-tweets.
    @staticmethod
    def _parse_tweets(social_post: str) -> list:
        content = social_post.content if hasattr(social_post, 'content') else social_post
        return [tweet.strip() for tweet in content.split('\n\n') 
                if tweet.strip() and not tweet.isspace()]
    
    # This is the main method of this class that takes one URL and returns a dictionary that inside has the list of tweets.
    def process_url(self, url:str) -> Optional[Dict]:
        try:
            # Extract the article
            try:
                print('Extracting the article from the URL')
                self.article = self._extract_content_crawl4ai(url)
                print(f'The article extracted is {self.article[:200]}...')
            except Exception as e:
                print(f'Error extracting the article: {str(e)}')
            
            # Setup the chain
            try:
                print('Setting up the chains')
                self.setup_chain()
            except Exception as e:
                print(f'Error setting up the chains : {str(e)}')

            # Get all the secondary articles in a long string
            try: 
                self.secondary_articles = asyncio.run(get_formatted_summaries(url))
                print('We got all the secondary articles successfully!')
            except Exception as e:
                print(f'Error getting the secondary articles: {str(e)}')

            
            # Run the chain
            try:
                print("Running the chain")
                self.result = self.post_chain.invoke({
                    "primary": self.article,
                    "secondary": self.secondary_articles
                    })
                print("Successfully completed the run of the chain")
            except Exception as e:
                print(f"Error trying to run the chain : {str(e)}")
            
            #break down the result in tweets
            try:
                print("breaking down the results in different tweets")
                self.tweets =  self._parse_tweets(self.result)
            except Exception as e:
                print(f"Error parsing the tweets : {str(e)}")
            
            return {
                "status": "success",
                "tweets": self.tweets,
                "tweet_count": len(self.tweets),
                "url": url
            }
        
        except Exception as e:
            print(f'Detailed error trying to run the process_url function: {type(e).__name__}: {str(e)}')
            return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "url": url
            }
    
        # Setup a chain that will take only the primary article as input varibles and will create a chain, the purpose is for tests
    

if __name__ == "__main__":
    processor = ContentProcessor()
    test_url = "https://techcrunch.com/2024/12/06/2927301/"
    
    print("\n=== Multiple Articles Method Results ===")
    multi_result = processor.process_url(test_url)
    print(f"Status: {multi_result['status']}")
    print(f"URL: {multi_result['url']}")
    print(f"Total Tweets: {multi_result['tweet_count']}\n")
    print("Tweets:")
    for tweet in multi_result['tweets']:
        print(f"\n{tweet}")
        print("-" * 80) 