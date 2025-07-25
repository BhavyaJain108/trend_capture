#!/usr/bin/env python3
"""Test script for the complete YouTube trends analysis pipeline."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.pipeline import YouTubeTrendsPipeline

def test_full_pipeline():
    """Test the complete pipeline end-to-end."""
    
    # Initialize pipeline
    pipeline = YouTubeTrendsPipeline()
    
    # Run analysis
    user_query = "AI coding tools for developers 2024"
    
    print("🎯 Testing Full YouTube Trends Pipeline")
    print("=" * 60)
    
    try:
        # Execute pipeline
        result = pipeline.run_analysis(
            user_query=user_query,
            max_videos=3,  # Keep small for testing
            show_progress=True
        )
        
        # Display results table
        pipeline.display_table(result, limit=15)
        
        # Show simple stats
        if not result.insights_df.empty:
            print(f"\n📈 QUICK STATS:")
            print(f"   Categories: {result.insights_df['category'].nunique()}")
            print(f"   Avg Score: {result.insights_df['score'].mean():.2f}")
            print(f"   Score Range: {result.insights_df['score'].min():.2f} to {result.insights_df['score'].max():.2f}")
        
        # Save to CSV
        filename = pipeline.save_to_csv(result)
        print(f"\n💾 Saved to: {filename}")
        
        print(f"\n🎉 Pipeline test completed successfully!")
        return result
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return None

if __name__ == "__main__":
    test_full_pipeline()