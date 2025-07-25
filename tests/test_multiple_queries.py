#!/usr/bin/env python3
"""Test the multiple queries functionality with a simpler topic."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.pipeline import YouTubeTrendsPipeline

def test_multiple_queries():
    """Test pipeline with multiple queries on a topic likely to have many videos."""
    
    print("🔍 Testing Multiple Query Pipeline")
    print("=" * 60)
    
    try:
        pipeline = YouTubeTrendsPipeline()
        
        # Use a broader topic that should have lots of videos
        result = pipeline.run_analysis(
            user_query="programming tutorial",
            max_videos=5,  # Limit for faster testing
            show_progress=True
        )
        
        print(f"\n📊 Final Results Summary:")
        print(f"   Videos processed: {result.videos_processed}")
        print(f"   Total insights: {result.total_insights}")
        print(f"   Results directory: {result.results_dir}")
        
        # Show query results breakdown
        query_results_file = os.path.join(result.results_dir, "query_results.csv")
        if os.path.exists(query_results_file):
            print(f"\n📋 Query Results Breakdown:")
            with open(query_results_file, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if i == 0:  # Header
                        print(f"   {line.strip()}")
                        print(f"   {'-' * 50}")
                    else:
                        parts = line.strip().split(',')
                        if len(parts) >= 4:
                            query_num = parts[0]
                            videos_found = parts[2]
                            status = parts[4]
                            query_text = parts[1][:40] + "..." if len(parts[1]) > 40 else parts[1]
                            print(f"   {query_num}: {videos_found} videos - {status} - {query_text}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_multiple_queries()
    if result:
        print(f"\n✅ Multiple queries test completed!")
        print(f"Check detailed results at: {result.results_dir}")
    else:
        print(f"\n❌ Test failed!")