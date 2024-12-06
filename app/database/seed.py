from .database import SessionLocal, init_db, get_db , engine
from .models import Prompt, Base
import json


def seed_initial_prompt():

    template = """
    Using the following content:

    {content}

    The post should follow the following guidelines on structure:

    STRUCTURE GUIDELINES:

    THREAD STRUCTURE:

    1. Hook (First Tweet)
    - Purpose: Grab attention and entice readers
    - Format: Bold statement or compelling question
    - Focus: Value proposition or key benefit
    - Length: Keep under 280 chars
    - Style: Concise, impactful language

    2. Body (Middle Tweets) 
    - Purpose: Deliver key information
    - Format: Break into digestible points
    - Style: Clear, readable sentences
    - Flow: Natural progression between tweets
    - Length: Each tweet under 280 chars

    3. Call-to-Action (Final Tweet)
    - Purpose: Drive engagement
    - Format: Clear directive
    - Examples: "Share thoughts" or "Follow for more"
    - Alignment: Match thread content
    - Length: Under 280 chars

    REQUIREMENTS:
    - Create multi-tweet thread
    - Each tweet max 280 characters
    - Return plain text tweets in sequence
    - No formatting or metadata
    - No explanations/commentary
    - Verify character count per tweet
        """
    init_db()
    db = SessionLocal()

    try:
        existing_prompt = db.query(Prompt).first()
        if not existing_prompt:
            prompt = Prompt(
                name="Tweet Thread Generator",
                description="Generates viral tweet threads from article content",
                template=template,
                input_variables=json.dumps(["content"]),
                is_active=True               
            )
            db.add(prompt)
            db.commit()
            print("initial prompt seeded successfully!")
        else:
            print("Prompt already exists in database!")
    finally:
        db.close() 



template_6_12_2024 = """
First template: You are a professional Twitter writer who focuses on business, data analytics, AI, and related news. Your goal is to craft engaging Twitter threads that attract and inform your audience, ultimately building a following for future entrepreneurial ventures.

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
- **Engagement:** Encourage sharing and discussions to build community.
- **Originality:** While summarizing the articles, ensure the content is original and offers a unique perspective. 
 ### Suffix_  

You will be provided with one main article and additional secondary articles. The secondary articles are links referenced in the primary article.
Your task is to write a compelling Twitter thread about the main article, enriching it with insights and context from the secondary articles. The thread should be informative, engaging, and encourage audience interaction.

** Primary Article **
This is the primary article:
{primary}


** Secondary Articles **
These are the secondary articles.
{secondary}
"""
    
# A function that takes a prompt id and a template and replaces the template of that prompt with the new template
def update_prompt_template(prompt_id:int,new_template:str):
    db = SessionLocal()
    try:
        prompt = db.query(Prompt).filter(Prompt.id==prompt_id).first()
        if prompt:
            prompt.template = new_template
            db.commit()
            print(f"Successfully changed the template of prompt with ID {prompt.id}")
        else:
            print(f"No prompt found with ID {prompt.id}")
    finally:
        db.close()


if __name__ == "__main__":
    update_prompt_template(1,template_6_12_2024)