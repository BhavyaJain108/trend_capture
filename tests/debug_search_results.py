#!/usr/bin/env python3
"""Debug why we're getting so few search results."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.youtube_query_generation import YouTubeQueryGenerator
from src.youtube_trends.youtube_search import YouTubeSearchClient

def debug_search_results():
    """Debug search results for each generated query."""
    
    print("🔍 DEBUG: Search Results Analysis")
    print("=" * 60)
    
    try:
        # Generate queries
        generator = YouTubeQueryGenerator()
        search_client = YouTubeSearchClient()
        
        user_query = "python programming tutorial"
        print(f"User Query: '{user_query}'")
        print("-" * 60)
        
        # Generate multiple queries
        query_result = generator.generate_search_query(user_query)
        
        print(f"\n🤖 Generated {len(query_result.queries)} queries:")
        print(f"Date Filter: {query_result.date}")
        print()
        
        query_results = []
        
        # Test each query individually
        for i, query in enumerate(query_result.queries, 1):
            print(f"📊 Query {i}: '{query}'")
            
            try:
                # Search with different limits to see what happens
                for limit in [5, 10, 20]:
                    videos = search_client.search_videos(
                        query=query,
                        limit=limit,
                        published_after=query_result.date
                    )
                    print(f"   Limit {limit:2d}: {len(videos)} videos found")
                
                # Store result for table
                final_videos = search_client.search_videos(
                    query=query,
                    limit=10,
                    published_after=query_result.date
                )
                
                query_results.append({
                    'query_number': i,
                    'query_text': query,
                    'videos_found': len(final_videos),
                    'date_filter': query_result.date
                })
                
                # Show first few video titles
                if final_videos:
                    print(f"   📹 Sample videos:")
                    for j, video in enumerate(final_videos[:3], 1):
                        print(f"      {j}. {video.title[:60]}...")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                query_results.append({
                    'query_number': i,
                    'query_text': query,
                    'videos_found': 0,
                    'date_filter': query_result.date,
                    'error': str(e)
                })
            
            print()
        
        # Create summary table
        print("📋 QUERY RESULTS SUMMARY")
        print("=" * 80)
        print(f"{'#':<2} {'Videos':<7} {'Query':<50} {'Date Filter':<12}")
        print("-" * 80)
        
        total_videos = 0
        for result in query_results:
            error_marker = " ❌" if 'error' in result else ""
            print(f"{result['query_number']:<2} {result['videos_found']:<7} {result['query_text'][:48]:<50} {result['date_filter'] or 'None':<12}{error_marker}")
            total_videos += result['videos_found']
        
        print("-" * 80)
        print(f"Total unique videos across all queries: ~{total_videos}")
        
        # Try without date filter
        print(f"\n🔄 Testing without date filter...")
        test_query = query_result.queries[0]
        videos_no_date = search_client.search_videos(query=test_query, limit=10, published_after=None)
        print(f"First query without date filter: {len(videos_no_date)} videos")
        
        return query_results
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_search_results()