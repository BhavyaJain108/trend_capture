#!/usr/bin/env python3
"""Test script for YouTube search with date filtering."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.youtube_search import YouTubeSearchClient, SearchError

def test_date_filtering():
    """Test searching with date filters and popularity ranking."""
    try:
        client = YouTubeSearchClient()
        
        query = "ChatGPT tutorial"
        limit = 3
        
        print("🔍 TESTING DATE FILTERING & POPULARITY RANKING")
        print("=" * 60)
        
        # Test 1: All videos (no date filter)
        print(f"\n1️⃣ ALL VIDEOS for '{query}' (sorted by popularity)")
        print("-" * 40)
        videos_all = client.search_videos(query, limit)
        
        for i, video in enumerate(videos_all, 1):
            print(f"{i}. {video.title}")
            print(f"   📅 Published: {video.publish_time}")
            print(f"   👀 Views: {video.views}")
            print(f"   🔗 {video.url}")
            print()
        
        # Test 2: Recent videos only (last 6 months)
        print(f"\n2️⃣ RECENT VIDEOS for '{query}' (published after 2024-06-01)")
        print("-" * 40)
        videos_recent = client.search_videos(query, limit, published_after="2024-06-01")
        
        for i, video in enumerate(videos_recent, 1):
            print(f"{i}. {video.title}")
            print(f"   📅 Published: {video.publish_time}")
            print(f"   👀 Views: {video.views}")
            print(f"   🔗 {video.url}")
            print()
            
        # Test 3: Very recent videos (last month)
        print(f"\n3️⃣ VERY RECENT VIDEOS for '{query}' (published after 2024-12-01)")
        print("-" * 40)
        try:
            videos_very_recent = client.search_videos(query, limit, published_after="2024-12-01")
            
            for i, video in enumerate(videos_very_recent, 1):
                print(f"{i}. {video.title}")
                print(f"   📅 Published: {video.publish_time}")
                print(f"   👀 Views: {video.views}")
                print(f"   🔗 {video.url}")
                print()
        except SearchError as e:
            print(f"   No videos found: {e}")
            
        print("\n✅ Date filtering test completed!")
        
    except SearchError as e:
        print(f"❌ Search Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_date_filtering()