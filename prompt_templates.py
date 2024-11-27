from langchain.prompts import PromptTemplate

criteria = """
The content should be relevant to professionals in the analytics and data sector, including:

- Analysts in big companies who use tools like Power BI for data visualization.
- Data scientists interacting with customers and selling data products.
- Consultants and business analysts using data for better decision-making.
- Data engineers managing and structuring large datasets.
- Business executives and management consultants interested in leveraging data.

**The content should:**

- **Have interesing & new information about things that could interest analytics and data sector professionals.
- **Include unique insights or surprising facts** that provoke thought and interest.
- **Evoke emotions** such as curiosity, excitement, or inspiration to encourage sharing.
- **Be timely and relevant**, referencing recent developments, trends, or news in the field.
- **Include actionable takeaways or tips** that the audience can apply in their work.
- **Align with your personal brand** as a well-rounded generalist specializing in analytics.

"""

# Template for determining relevance
relevance_prompt = PromptTemplate(
    input_variables=["content"],
    template=f"""
        Given the following content:

        {{content}}

        Determine if this content is relevant to the following criteria:

        {criteria}

        Respond with 'Yes' if it is relevant or 'No' if it is not
    """
)

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
