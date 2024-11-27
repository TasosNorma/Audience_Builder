from content_processor import ContentProcessor

if __name__ == "__main__":
    processor = ContentProcessor()
    test_url = "https://www.cnbc.com/2024/06/12/databricks-says-annualized-revenue-to-reach-2point4-billion-in-first-half.html"
    result = processor.process_url(test_url)
    print("\nTest Result:")
    print(result)