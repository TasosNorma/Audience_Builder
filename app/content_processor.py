from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.chains.base import Chain
from langchain.schema.runnable import RunnableBranch,RunnablePassthrough
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_openai import ChatOpenAI
from trash.prompt_templates import *
import os
from typing import Dict, Optional
from app.database.database import *
from app.database.models import Prompt,Profile,OnlineArticles
from langchain.prompts import PromptTemplate
from app.crawl4ai import *
import time
from datetime import datetime
import json
from pathlib import Path
import asyncio

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

    # # This method takes a url and returns a beautifully constructed article based on 1 method of extraction that is used in the secondary articles aswell.
    # async def _extract_content_crawl4ai(self, url: str) -> Optional[str]:
    #     try:
    #         self.crawl4ai_article = await extract_article_content(url)
    #     except Exception as e:
    #         print(f"Error extracting article content with crawl4ai: {str(e)}")
    #         self.crawl4ai_article = None
    #     return self.crawl4ai_article

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
            self.article = await extract_article_content(url)
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
            self.secondary_articles = await get_formatted_summaries(url)
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

    async def compare_article_to_profile(self, article_url: str, id: int) -> Dict:
        try:
            # Get profile interests
            profile_interests = self._get_profile_interests(id)
            
            # Extract article content
            article_content = await extract_article_content(article_url)
            
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

# This class is handling all the blogs and the extraction of the articles from them.
class BlogHandler:
    def __init__(self) -> None:
        self.content_processor = ContentProcessor()
        self.profile_comparer = ProfileComparer()

    # Extracts all the articles of a url. 
    async def extract_all_articles(self, url:str) -> Optional[Dict]:
        articles = await extract_all_articles_from_page(url)
        return articles
    
    # Checks if article is in the database, because if it is, it means that we have judged it before.
    def check_if_online_article_in_database(self, url:str, profile_id:int)-> Optional[bool]:
        db = SessionLocal()
        try:
            online_article = db.query(OnlineArticles).filter(OnlineArticles.url == url, OnlineArticles.profile_id == profile_id).first()
            return online_article is not None
        except Exception as e:
            print(f"Error trying to get the online article {str(e)}")
            return None
        finally:
            db.close()

    # Extracts all articles, checks if they are in database and then returns a dictionary of urls and wheather they fit the user profile or not.
    async def process_blog_articles(self,blog_url:str,profile_id:int) -> Optional[Dict]:
        try:
            try:
                print("Extracting all the articles from the blog")
                articles = await extract_all_articles_from_page(blog_url)
                print("Articles extracted")
            except Exception as e:
                print(f"Error extracting articles: {str(e)}")
                return {
                    "status": "error", 
                    "message": f"Failed to extract articles: {str(e)}",
                    "blog_url": blog_url
                }
            results = {}
            try:
                self.profile_comparer.setup_comparison_chain()
            except Exception as e:
                print(f"Error setting up comparison chain: {str(e)}")

            for article_url in articles:
                # Skip if already in database
                if self.check_if_online_article_in_database(article_url, profile_id):
                    results[article_url] = {
                        "status": "skipped",
                        "message": "Article already processed"
                    }
                    continue
                
                # Compare article to profile
                comparison_result = await self.profile_comparer.compare_article_to_profile(
                    article_url=article_url,
                    id=profile_id
                )
                
                results[article_url] = comparison_result
            
            return results
        except Exception as e:
            return{
                "status": "error",
                "message": f"Error processing blog articles: {str(e)}",
                "blog_url": blog_url
            }

    
if __name__ == "__main__":
    # Initialize the BlogHandler
    blog_handler = BlogHandler()
    
    result = asyncio.run(blog_handler.process_blog_articles('https://techcrunch.com/',1))
    print(result)