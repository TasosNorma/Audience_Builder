from typing import List, Optional
from ..database.database import SessionLocal
from ..database.models import Prompt, User
from datetime import datetime

def set_default_prompt(user_id:int) -> Optional[str]:
    default_prompt_2 = Prompt(
        type=2,
        name="Profile Comparison Prompt",
        description = 'Compares an article with the profile and returns Yes or No based on Fit.',
        user_id=user_id,
        template="""
    You will receive two inputs: a profile description and an article. Your task is to determine if the person described in the profile would find the article relevant, interesting, and suitable for sharing on their social media.
    You must be very strict: only answer "Yes" if the article strongly aligns with their interests, professional focus, or sharing habits as described in the profile. Otherwise, answer "No".

    Instructions:
    1. Read the profile carefully to understand the individual's professional background, interests, and the types of content they are likely to share.
    2. Read the article and assess its topic, tone, and relevance to the profile's interests.
    3. If the article's content clearly matches the individual's interests or sharing criteria described in the profile, respond with "Yes".
    4. If it does not, respond with "No".
    5. Provide no additional commentary—only "Yes" or "No".

    Profile:
    "{profile}"

    Article:
    "{article}"
    """,
        input_variables='["profile", "article"]',
        is_active=True
    )
    default_prompt_1 = Prompt(
        name = 'Tweet Thread Generator',
        type=1,
        description = 'Generates viral tweet threads from article content',
        user_id = user_id,
        template = """
You are a professional Twitter writer who focuses on business, data analytics, AI, and related news. Your goal is to craft engaging Twitter threads that attract and inform your audience, ultimately building a following for future entrepreneurial ventures.

**Thread Structure & Guidelines:**

1. **Hook (First Tweet):**
    - **Purpose:** Grab attention and entice readers. Make them understand it's about news and not personal opinions.
    - **Content:** Start with a bold statement or a compelling question related to the main topic. Be objective and highlight the key value proposition or benefit.
    - **Length:** Keep under 280 characters.
    - **Style:** Use concise and impactful language.
2. **Body (Middle Tweets):**
    - **Purpose:** Deliver key information and insights.
    - **Content:** Break down the main points from the articles into digestible pieces. Incorporate relevant data, quotes, or statistics to add value.
    - **Flow:** Ensure a natural progression between tweets for readability.
    - **Length:** Each tweet should be under 280 characters.
    - **Style:** Maintain clear and readable sentences.
3. **Call-to-Action (Final Tweet):**
    - **Purpose:** Drive engagement.
    - **Content:** Include a clear directive that encourages interaction, such as asking for thoughts or suggesting to follow for more insights.
    - **Alignment:** Make sure it aligns with the thread's content.
    - **Length:** Under 280 characters.

**Additional Guidelines:**

- **Tone:** Maintain a professional and informative voice while staying approachable. Focus on factual news reporting rather than sensationalism, particularly in the opening tweet.
- **Audience Focus:** Tailor content to professionals interested in business, data analytics, and AI.
- **Language:** Avoid jargon; keep it accessible to a broad audience.
- **Originality:** While summarizing the articles, ensure the content is original and offers a unique perspective. 
- **Facts-Based:** Don't comment with opinions, focus mainly on the facts that you can find in the articles. 
 ### Suffix_     

You will be provided with one main article and additional secondary articles. The secondary articles are links referenced in the primary article.
Your task is to write a compelling Twitter thread about the main article, enriching it with insights and context from the secondary articles. The thread should be informative, engaging, and encourage audience interaction.

** Primary Article **
This is the primary article:
{primary}


** Secondary Articles **
These are the secondary articles.
{secondary}

""",
    input_variables='["primary", "secondary"]',
    is_active=True
    )
    try:
        db = SessionLocal()
        db.add(default_prompt_2)
        db.add(default_prompt_1)
        db.commit()
        return print('Successfully added the default prompt to the user')
    except Exception as e:
        db.rollback()
        return print(f"The Setting of the default type 2 prompt failed : {str(e)}")
    finally:
        db.close()

def create_new_user(email:str,password:str)-> Optional[str]:
    db = SessionLocal()
    try:
        user = User(email=email, is_active = True,is_onboarded=False)
        user.set_password(password)
        db.add(user)
        db.commit()

        set_default_prompt(user_id=user.id)
        return print('Successfully added the user')
    except Exception as e:
        db.rollback()
        return print(f'Error trying to add the new user {str(e)}')
    finally:
        db.close()

        
    