from content_processor import ContentProcessor
import openai

def test_openai_api():
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Write a haiku about recursion in programming."
                }
                ]
            )
        print("API Test Result:", response.choices[0].message)
        print("✅ OpenAI API connection successful!")
        return True
    except Exception as e:
        print("❌ OpenAI API Error:", str(e))
        return False

if __name__ == "__main__":
    # Test OpenAI API first
    if test_openai_api():
        # Only proceed with the main processing if API test passes
        processor = ContentProcessor()
        test_url = "https://www.cnbc.com/2024/06/12/databricks-says-annualized-revenue-to-reach-2point4-billion-in-first-half.html"
        result = processor.process_url(test_url)
        print("\nTest Result:")
        print(result)


