import requests

# This is not used yet


def fetch_top_story():
    # Get the list of top stories
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    stories = requests.get(top_stories_url).json()
    first_story_id = stories[0]
    first_story_details_url = f"https://hacker-news.firebaseio.com/v0/item/{first_story_id}.json"
    first_story_details = requests.get(first_story_details_url).json()
    return first_story_details['url']

def fetch_all_stories():
    # Get the list of top stories
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    stories = requests.get(top_stories_url).json()
    story_urls = []

    for story_id in stories:
        story_details_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story_details = requests.get(story_details_url).json()
        if 'url' in story_details:
            story_urls.append(story_details['url'])

    return story_urls


