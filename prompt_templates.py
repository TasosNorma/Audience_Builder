from langchain.prompts import PromptTemplate


post_prompt = PromptTemplate(
    input_variables=["content"],
    template= """
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
)
