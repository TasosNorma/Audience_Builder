from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.chains.base import Chain
from langchain.schema.runnable import RunnableBranch,RunnablePassthrough
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_openai import ChatOpenAI
from trash.prompt_templates import *
import os
from typing import Dict, Optional
from app.database.database import *
from app.database.models import Prompt,Profile,OnlineArticles,User
from langchain.prompts import PromptTemplate
from app.crawl4ai import *
import time
from datetime import datetime
import json
from pathlib import Path
import asyncio
import logging
import urllib3
import warnings
from app.api.prompt_operations import get_prompt
from cryptography.fernet import Fernet

logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('LiteLLM').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger('crawl4ai').setLevel(logging.ERROR)
logging.getLogger('crawl4ai.extraction_strategy').setLevel(logging.ERROR)
logging.getLogger('crawl4ai.crawler').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=urllib3.exceptions.NotOpenSSLWarning)

# This class can take a url and write a tweet.
class ContentProcessor:
    # Initialize the class with LLM, it takes the API key from an environment variable.
    def __init__(self,user):
        self.user = user
        fernet = Fernet(os.environ['ENCRYPTION_KEY'].encode())
        self.decripted_api_key = fernet.decrypt(self.user.openai_api_key).decode()
        self.llm = ChatOpenAI(openai_api_key=self.decripted_api_key, model_name='gpt-4o-mini')
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
    # def get_prompt(self, id: int) -> Optional[str]:
    #     db = SessionLocal()
    #     try:
    #         prompt = db.query(Prompt).filter(Prompt.id == id).first()
    #         print(f"Fetched the template from the database and the template is :{prompt.template[:50]}")
    #         return prompt.template if prompt else None
    #     except Exception as e:
    #         print(f"Error fetching prompt from database {str(e)}")
    #         return None
    #     finally:
    #         db.close()

    # This method creates a chain with the proper chain template so that we can insert the primary and secondary articles.
    def setup_chain(self):
        self.prompt = get_prompt(1,self.user.id)
        self.prompt_template = PromptTemplate(template=self.prompt,input_variables=["primary","secondary"])
        self.post_chain = self.prompt_template | self.llm

    # This method takes the string of the final post and breaks it down to sub-tweets.
    @staticmethod
    def _parse_tweets(social_post: str) -> list:
        content = social_post.content if hasattr(social_post, 'content') else social_post
        return [tweet.strip() for tweet in content.split('\n\n') 
                if tweet.strip() and not tweet.isspace()]
    
    # This method takes one URL and returns a dictionary that inside has the list of tweets.
    async def process_url(self, url:str) -> Optional[Dict]:
        trace = {
            "url": url,
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "content": {}
        }

        try:
            # Extract the article
            step_start = time.time()
            self.article = await extract_article_content(url,self.decripted_api_key)
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
            self.secondary_articles = await get_formatted_summaries(url,self.decripted_api_key)
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
    def __init__(self,user) -> None:
        self.user = user
        fernet = Fernet(os.environ['ENCRYPTION_KEY'].encode())
        self.decripted_api_key = fernet.decrypt(self.user.openai_api_key).decode()
        self.llm = ChatOpenAI(openai_api_key=self.decripted_api_key, model_name='gpt-4o-mini',temperature=0)
        self.user_id = user.id
        self.setup_comparison_chain()
    
    # This method returns the interests of a profile, gets an ID of the profile
    def _get_profile_interests(self, user_id: int):
        db = SessionLocal()
        try:
            profile = db.query(Profile).filter(Profile.user_id == user_id).first()
            if not profile:
                raise ValueError(f"No profile found for user_id: {user_id}")
            print(f"Got the profile interests")
            return profile.interests_description
        except Exception as e:
            print(f"Error trying to get the profile {str(e)}")
        finally:
            db.close()
    
    # This method sets up the chain
    def setup_comparison_chain(self):
        self.prompt = get_prompt(prompt_type=2, user_id=self.user_id)
        self.comparison_prompt_template = PromptTemplate(template=self.prompt,input_variables=["profile","article"])
        self.comparison_chain = self.comparison_prompt_template | self.llm

    async def compare_article_to_profile(self, article_url: str, user_id: int) -> Dict:
        try:
            profile_interests = self._get_profile_interests(user_id)
            article_content = await extract_article_content(article_url,self.decripted_api_key)
            print(f"Profile interests: {profile_interests[:50]}")
            print(f"Article content preview: {article_content[:50]}...")
            result = self.comparison_chain.invoke({
                "profile": profile_interests,
                "article": article_content
            })
            llm_response = result.content if hasattr(result, 'content') else str(result)
            print(f"LLM Response: {llm_response}")  # Debug print
            return {
                "status": "success",
                "url": article_url,
                "user_id": user_id,
                "llm_response": llm_response
            }
            
        except Exception as e:
            print(f"Comparison error: {str(e)}")
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}",
                "url": article_url,
                "profile_id": id
            }

# This class is handling all the blogs and the extraction of the articles from them.
class BlogHandler:
    def __init__(self,user) -> None:
        self.user = user
        fernet = Fernet(os.environ['ENCRYPTION_KEY'].encode())
        self.decripted_api_key = fernet.decrypt(self.user.openai_api_key).decode()
        self.content_processor = ContentProcessor(self.user)
        self.profile_comparer = ProfileComparer(self.user)
    
    # This method takes a url (a blog url) and a profile, it returns a list of dictionaries with all the relevant articles of the blog and wheather they fit the profile or not. 
    # It also stores the results in the database
    async def process_and_store_articles(self, blog_url: str, user_id: int) -> list[Dict]:
        db = SessionLocal()
        try:
            # Get all articles from the blog
            print('Extracting all the articles from the page')
            articles_dict = await extract_all_articles_from_page(blog_url,self.decripted_api_key)
            # Get the user's profile
            print('Done extracting, now creating a batch of tasks and running them simultanously')
            profile = db.query(Profile).filter(Profile.user_id == user_id).first()
            if not profile:
                raise ValueError(f"No profile found for user_id: {user_id}")
            
            # Create tasks for all article comparisons
            comparison_tasks = [
                self.profile_comparer.compare_article_to_profile(url, self.user.id)
                for url in articles_dict.keys()
            ]

            # Run all comparisons concurrently
            comparison_results = await asyncio.gather(*comparison_tasks)
            print('Done running the tasks, now shaping everything nicely')

            # Process Results and Store in Database
            results = []
            for (url, title), result in zip(articles_dict.items(), comparison_results):
                fits_profile = False
                if result["status"] == "success":
                    llm_response = str(result["llm_response"]).lower()
                    print(f"\nAnalyzing article: {title}")
                    print(f"LLM Response: {llm_response}")
                    
                    # More comprehensive check for positive responses
                    positive_indicators = ["yes", "true", "relevant", "matches", "fits"]
                    fits_profile = any(indicator in llm_response for indicator in positive_indicators)
                    print(f"Fits profile: {fits_profile}")
                
                # Create new OnlineArticles entry
                new_article = OnlineArticles(
                    user_id=self.user.id,
                    url=url,
                    title=title,
                    source_blog=blog_url,
                    profile_fit=fits_profile
                )
                db.add(new_article)
                
                article_result = {
                    "url": url,
                    "title": title,
                    "fits_profile": fits_profile
                }
                results.append(article_result)
            print('finished shaping, now commiting')
            
            # Commit all database changes
            db.commit()
            return results
            
        except Exception as e:
            db.rollback()
            print(f"Error processing and storing articles: {str(e)}")
            return []
        finally:
            db.close()
    
if __name__ == "__main__":
    # Initialize the BlogHandler
    blog_handler = BlogHandler()
    results = asyncio.run(blog_handler.process_articles_for_profile('https://www.qlik.com/blog?page=1&limit=9',1))
    print(results)