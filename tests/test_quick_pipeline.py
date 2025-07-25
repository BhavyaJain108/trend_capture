#!/usr/bin/env python3
"""Quick pipeline test with minimal videos."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.pipeline import YouTubeTrendsPipeline

def test_quick_pipeline():
    """Test pipeline with just 1 video for quick results."""
    
    pipeline = YouTubeTrendsPipeline()
    
    print("🚀 Quick Pipeline Test")
    print("=" * 50)
    
    try:
        result = pipeline.run_analysis(
            user_query="programming tutorial",
            max_videos=1,  # Just 1 video for speed
            show_progress=True
        )
        
        print(f"\n📊 Results Summary:")
        print(f"   Videos processed: {result.videos_processed}")
        print(f"   Total insights: {result.total_insights}")
        print(f"   Results directory: {result.results_dir}")
        
        # Show a few insights
        if not result.insights_df.empty:
            print(f"\n🔍 Sample Insights:")
            for _, row in result.insights_df.head(3).iterrows():
                print(f"   [{row['score']:+.2f}] {row['category']}: {row['information'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return False

if __name__ == "__main__":
    success = test_quick_pipeline()
    print(f"\n{'✅ Success!' if success else '❌ Failed!'}")