#!/usr/bin/env python3
"""Debug YouTube API search vs regular YouTube search behavior."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.youtube_search import YouTubeSearchClient

def debug_youtube_search():
    """Test the exact query that failed and variations."""
    
    print("🔍 DEBUG: YouTube API vs Regular YouTube Search")
    print("=" * 70)
    
    search_client = YouTubeSearchClient()
    
    # Test the exact failing query and variations
    test_queries = [
        # The exact failing query
        "EV expert review Tesla Rivian Ford comparison in-depth analysis 2024 models",
        
        # Simpler variations
        "Tesla Rivian Ford comparison",
        "EV comparison Tesla Ford",
        "Tesla review 2024",
        "electric car comparison", 
        "Tesla vs Ford",
        "EV review",
        "Tesla",
        
        # Test with different date filters
        ("Tesla review", None),
        ("Tesla review", "2024"),
        ("Tesla review", "2023"),
        ("Tesla review", "2022"),
    ]
    
    for i, query_data in enumerate(test_queries, 1):
        if isinstance(query_data, tuple):
            query, date_filter = query_data
            print(f"\n{i:2d}. Query: '{query}' (Date: {date_filter or 'None'})")
        else:
            query = query_data
            date_filter = "2024"
            print(f"\n{i:2d}. Query: '{query}' (Date: {date_filter})")
        
        try:
            videos = search_client.search_videos(
                query=query,
                limit=5,
                published_after=date_filter
            )
            
            print(f"    ✅ {len(videos)} videos found")
            
            if videos:
                print(f"    📹 Sample results:")
                for j, video in enumerate(videos[:2], 1):
                    print(f"       {j}. {video.title[:60]}...")
                    print(f"          👀 {video.views} views | 📅 {video.publish_time}")
            else:
                print(f"    ❌ No videos found - this shouldn't happen for basic queries!")
                
        except Exception as e:
            print(f"    ❌ API Error: {str(e)}")
    
    # Test API limits and quotas
    print(f"\n" + "=" * 70)
    print(f"🔧 DEBUGGING API BEHAVIOR:")
    
    # Test with maximum simple query
    try:
        simple_videos = search_client.search_videos("Tesla", limit=50, published_after=None)
        print(f"✅ Simple 'Tesla' query: {len(simple_videos)} videos (no date filter)")
        
        if simple_videos:
            # Show publication dates
            dates = [v.publish_time[:4] for v in simple_videos[:5] if v.publish_time]
            print(f"   Recent video years: {dates}")
            
    except Exception as e:
        print(f"❌ Even simple 'Tesla' query failed: {e}")
    
    print(f"\n💡 ANALYSIS:")
    print(f"   • YouTube Data API v3 is more restrictive than web search")
    print(f"   • Long queries with many keywords often return 0 results")  
    print(f"   • Date filters can be very restrictive")
    print(f"   • API quotas may affect results")
    print(f"   • Consider shorter, more focused queries")

if __name__ == "__main__":
    debug_youtube_search()