
import asyncio
import os
from drama.helpers._thumbnails import Thumbnail
from drama.helpers import Track

# Mock Track object
class MockTrack:
    def __init__(self):
        self.id = "test_track"
        self.title = "Cintaku Gagal Membuatmu Hangat (Sulih Suara) - EP 4 - Some Extra Text"
        self.thumbnail = "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg" # Dummy image
        self.tags = "Drama, Romance"
        self.book_id = "12345"

async def main():
    if not os.path.exists("cache"):
        os.makedirs("cache")
    
    thumb = Thumbnail()
    track = MockTrack()
    
    print("Generating thumbnail...")
    try:
        output = await thumb.generate(track)
        print(f"Thumbnail generated at: {output}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
