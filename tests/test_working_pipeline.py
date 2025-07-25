#!/usr/bin/env python3
"""Test pipeline with a query that should find videos with transcripts."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.pipeline import YouTubeTrendsPipeline

def test_working_pipeline():
    """Test pipeline with a query likely to have transcripts."""
    
    pipeline = YouTubeTrendsPipeline()
    
    print("🚀 Working Pipeline Test")
    print("=" * 50)
    
    try:
        result = pipeline.run_analysis(
            user_query="python data science",
            max_videos=2,  # 2 videos for better chance of transcripts
            show_progress=True
        )
        
        print(f"\n📊 Results Summary:")
        print(f"   Videos processed: {result.videos_processed}")
        print(f"   Total insights: {result.total_insights}")
        print(f"   Results directory: {result.results_dir}")
        print(f"   Processing time: {result.processing_time:.2f}s")
        
        # Show insights by category
        if not result.insights_df.empty:
            print(f"\n🔍 Insights by Category:")
            for category in result.insights_df['category'].unique():
                count = len(result.insights_df[result.insights_df['category'] == category])
                print(f"   {category}: {count} insights")
            
            print(f"\n📈 Top Insights:")
            for _, row in result.insights_df.head(5).iterrows():
                print(f"   [{row['score']:+.2f}] {row['category']}: {row['information'][:60]}...")
        
        # Show errors if any
        if result.errors:
            print(f"\n⚠️  Errors ({len(result.errors)}):")
            for error in result.errors[:3]:
                print(f"   • {error}")
        
        return result
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return None

if __name__ == "__main__":
    result = test_working_pipeline()
    if result:
        print(f"\n✅ Success! Check results at: {result.results_dir}")
    else:
        print(f"\n❌ Failed!")