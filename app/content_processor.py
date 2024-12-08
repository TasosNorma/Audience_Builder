from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.chains.base import Chain
from langchain.schema.runnable import RunnableBranch,RunnablePassthrough
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_openai import ChatOpenAI
from trash.prompt_templates import *
import os
from typing import Dict, Optional
from app.database.database import *
from app.database.models import Prompt,Profile
from langchain.prompts import PromptTemplate
from app.crawl4ai import *
import time
from datetime import datetime
import json
from pathlib import Path

# This class can take a url and write a tweet.
class ContentProcessor:
    # Initialize the class with LLM, it takes the API key from an environment variable.
    def __init__(self):
        self.llm = ChatOpenAI(openai_api_key=os.getenv('OPENAI_API_KEY'), model_name='gpt-4o-mini')
        self.traces_dir = Path("traces")
        self.traces_dir.mkdir(exist_ok=True)

    # This method takes a dictionary and saves the trace in the traces folder
    def _save_trace(self,trace_data:dict):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_file = self.traces_dir / f"trace_{timestamp}.json"
        
        if not isinstance(trace_data, dict):
            raise ValueError(f"trace_data must be a dictionary, got {type(trace_data)}")

        with open(trace_file, 'w') as f:
            json.dump(trace_data,f,indent=2)
            
    # This method fetches the prompt template of a prompt in the database and takes its ID as an arguement.
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

    # This method takes a url and returns a beautifully constructed article based on 1 method of extraction that is used in the secondary articles aswell.
    def _extract_content_crawl4ai(self,url:str) -> Optional[str]:
        try:
            self.crawl4ai_article = asyncio.run(extract_article_content(url))
        except Exception as e:
            print(f"Error extracting article content with crawl4ai: {str(e)}")
            self.crawl4ai_article = None
        return self.crawl4ai_article

    # This method creates a chain with the proper chain template so that we can insert the primary and secondary articles.
    def setup_chain(self):
        self.prompt = self.get_prompt(1)
        self.prompt_template = PromptTemplate(template=self.prompt,input_variables=["primary","secondary"])
        self.post_chain = self.prompt_template | self.llm

    # This method takes the string of the final post and breaks it down to sub-tweets.
    @staticmethod
    def _parse_tweets(social_post: str) -> list:
        content = social_post.content if hasattr(social_post, 'content') else social_post
        return [tweet.strip() for tweet in content.split('\n\n') 
                if tweet.strip() and not tweet.isspace()]
    
    # This method takes one URL and returns a dictionary that inside has the list of tweets.
    def process_url(self, url:str) -> Optional[Dict]:
        trace = {
            "url": url,
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "content": {}
        }

        try:
            # Extract the article
            step_start = time.time()
            self.article = self._extract_content_crawl4ai(url)
            trace["steps"].append({
                "name": "extract_article",
                "duration": time.time() - step_start,
                "success": True
            })
            trace["content"]["article_preview"] = self.article
            
            # Setup the chain
            try:
                print('Setting up the chains')
                self.setup_chain()
            except Exception as e:
                print(f'Error setting up the chains : {str(e)}')

            # Get all the secondary articles in a long string
            step_start = time.time()
            self.secondary_articles = asyncio.run(get_formatted_summaries(url))
            trace["steps"].append({
                "name": "get_secondary_articles",
                "duration": time.time() - step_start,
                "success": True
            })
            trace["content"]["secondary_articles"] = self.secondary_articles

            
            # Run the chain
            step_start = time.time()
            trace["content"]["prompt_template"] = self.prompt  # Store the template
            trace["content"]["final_prompt"] = self.prompt_template.format(  # Store the formatted prompt
                primary=self.article,
                secondary=self.secondary_articles
            )
            self.result = self.post_chain.invoke({
                "primary": self.article,
                "secondary": self.secondary_articles
            })
            trace["steps"].append({
                "name": "run_chain",
                "duration": time.time() - step_start,
                "success": True
            })
            
            #break down the result in tweets
            step_start = time.time()
            self.tweets = self._parse_tweets(self.result)
            trace["steps"].append({
                "name": "parse_tweets",
                "duration": time.time() - step_start,
                "success": True
            })
            trace["content"]["tweets"] = self.tweets
            
            result = {
                "status": "success",
                "tweets": self.tweets,
                "tweet_count": len(self.tweets),
                "url": url
            }
            trace["status"] = "success"
            self._save_trace(trace)
            return result
        
        except Exception as e:
            trace["status"] = "error"
            trace["error"] = str(e)
            self._save_trace(trace)
            return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "url": url
            }
    
        # Setup a chain that will take only the primary article as input varibles and will create a chain, the purpose is for tests
    
# This class is handling the comparison of the article to the profile of the user
class ProfileComparer:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(openai_api_key=os.getenv('OPENAI_API_KEY'), model_name='gpt-4o', temperature=0)
        self.crawler = ContentProcessor()
    
    # This method returns the interests of a profile, gets an ID of the profile
    def _get_profile_interests(self, id:int):
        db= SessionLocal()
        try:
            profile = db.query(Profile).filter(Profile.id == id).first()
            return profile.interests_description
        except Exception as e:
            print(f"Error trying to get the profile {str(e)}")
        finally:
            db.close()
    
    # This method sets up the chain
    def setup_comparison_chain(self):
        self.prompt = self.crawler.get_prompt(2)
        self.comparison_prompt_template = PromptTemplate(template=self.prompt,input_variables=["profile","article"])
        self.comparison_chain = self.comparison_prompt_template | self.llm

    def compare_article_to_profile(self, article_url: str, id: int) -> Dict:
        try:
            # Get profile interests
            profile_interests = self._get_profile_interests(id)
            
            # Extract article content
            article_content = self.crawler._extract_content_crawl4ai(article_url)
            
            # Run the comparison chain
            result = self.comparison_chain.invoke({
                "profile": profile_interests,
                "article": article_content
            })
            
            # Return structured result
            return {
                "status": "success",
                "url": article_url,
                "profile_id": id,
                "llm_response": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}",
                "url": article_url,
                "profile_id": id
            }

if __name__ == "__main__":
    # Initialize the ProfileComparer
    comparer = ProfileComparer()
    
    # Setup the comparison chain
    comparer.setup_comparison_chain()
    
    # Test URL and profile ID (adjust these values based on your database)
    test_url = "https://www.databricks.com/blog/equiniti-from-zero-ai"
    profile_id = 1  # Make sure this ID exists in your database
    
    # Run the comparison
    result = comparer.compare_article_to_profile(test_url, profile_id)
    
    # Print results
    print("\nProfile Comparison Test Results:")
    print("-" * 50)
    print(f"Article URL: {result['url']}")
    print(f"Profile ID: {result['profile_id']}")
    print(f"Full Response: {result['llm_response']}")