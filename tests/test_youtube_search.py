#!/usr/bin/env python3
"""Simple test script to verify YouTube search functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.youtube_search import YouTubeSearchClient, SearchError

def test_simple_search():
    """Test searching for videos with a natural language query."""
    try:
        # You need to set YOUTUBE_API_KEY environment variable or pass api_key
        client = YouTubeSearchClient()
        
        # Test query
        query = "python programming tutorial"
        limit = 5
        
        print(f"Testing search with query: '{query}' (limit: {limit})")
        
        # Test search_videos method
        videos = client.search_videos(query, limit)
        
        if videos:
            print(f"✅ SUCCESS: Found {len(videos)} videos!")
            
            # Display first video details
            first_video = videos[0]
            print(f"\n📺 First video:")
            print(f"   Title: {first_video.title}")
            print(f"   Channel: {first_video.channel}")
            print(f"   URL: {first_video.url}")
            print(f"   Duration: {first_video.duration}")
            print(f"   Views: {first_video.views}")
            
            # Test get_video_urls method
            urls = client.get_video_urls(query, 3)
            print(f"\n🔗 Top 3 URLs:")
            for i, url in enumerate(urls, 1):
                print(f"   {i}. {url}")
                
        else:
            print("❌ FAILED: No videos returned")
            
    except SearchError as e:
        print(f"❌ SEARCH ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

def test_display_search():
    """Test the search_and_display method."""
    try:
        client = YouTubeSearchClient()
        query = "machine learning explained"
        
        print(f"\n" + "="*80)
        print("TESTING SEARCH AND DISPLAY FUNCTIONALITY")
        print("="*80)
        
        client.search_and_display(query, limit=3)
        
    except Exception as e:
        print(f"❌ ERROR in display test: {e}")

if __name__ == "__main__":
    test_simple_search()
    test_display_search()