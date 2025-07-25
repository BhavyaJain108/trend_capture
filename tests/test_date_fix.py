#!/usr/bin/env python3
"""Test different date fixing approaches."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.youtube_search import YouTubeSearchClient

def test_date_formats():
    """Test different date formats to see what works."""
    
    print("🗓️ Testing Date Formats")
    print("=" * 50)
    
    search_client = YouTubeSearchClient()
    test_query = "python tutorial"
    
    # Test different date formats
    date_formats = [
        None,                    # No date filter
        "2024",                  # Year only
        "2024-01",               # Year-month
        "2024-01-01",            # Full date
        "2023-01-01",            # Earlier date
        "2022-01-01",            # Even earlier
    ]
    
    for date_filter in date_formats:
        try:
            print(f"\n📅 Testing date: {date_filter or 'None'}")
            
            videos = search_client.search_videos(
                query=test_query,
                limit=3,
                published_after=date_filter
            )
            
            print(f"   ✅ {len(videos)} videos found")
            if videos:
                print(f"   📹 Sample: {videos[0].title[:50]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}...")

if __name__ == "__main__":
    test_date_formats()