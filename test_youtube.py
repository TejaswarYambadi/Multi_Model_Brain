from processors.youtube_processor import YouTubeProcessor

processor = YouTubeProcessor()
url = "https://www.youtube.com/watch?v=V1DS-fEoZFM"

try:
    result = processor.process(url)
    print("YouTube Processing Result:")
    print("=" * 50)
    print(result)
except Exception as e:
    print(f"Error: {e}")