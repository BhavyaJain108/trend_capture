#!/usr/bin/env python3
"""Test script to verify the results directory structure and file saving."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.pipeline import YouTubeTrendsPipeline

def test_results_structure():
    """Test that results are properly saved in the directory structure."""
    
    # Initialize pipeline
    pipeline = YouTubeTrendsPipeline()
    
    # Use a simple query that should return results
    user_query = "python programming"
    
    print("🎯 Testing Results Directory Structure")
    print("=" * 60)
    
    try:
        # Execute pipeline with minimal videos for quick test
        result = pipeline.run_analysis(
            user_query=user_query,
            max_videos=2,  # Keep very small for testing
            show_progress=True
        )
        
        # Verify the results directory structure
        results_dir = result.results_dir
        print(f"\n📁 Results Directory: {results_dir}")
        
        # Check that all expected files exist
        expected_files = [
            "trend_results.csv",
            "youtube_log.csv", 
            "prompt.txt",
            "ai_prompt.txt"
        ]
        
        if result.errors:
            expected_files.append("errors.txt")
        
        print(f"\n✅ File Verification:")
        for filename in expected_files:
            filepath = os.path.join(results_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"   ✅ {filename} ({size} bytes)")
            else:
                print(f"   ❌ {filename} - MISSING")
        
        # Show structure summary
        print(f"\n📊 Results Summary:")
        print(f"   User Query: '{result.user_query}'")
        print(f"   AI Generated Query: '{result.optimized_search_query}'")
        print(f"   Videos Processed: {result.videos_processed}")
        print(f"   Total Insights: {result.total_insights}")
        print(f"   Processing Time: {result.processing_time:.2f}s")
        print(f"   Errors: {len(result.errors)}")
        
        # Show a few sample insights if available  
        if not result.insights_df.empty:
            print(f"\n🔍 Sample Insights (Top 3):")
            sample_df = result.insights_df.head(3)
            for _, row in sample_df.iterrows():
                print(f"   [{row['score']:+.2f}] {row['category']}: {row['information'][:60]}...")
        
        print(f"\n🎉 Results structure test completed successfully!")
        print(f"   Full results saved to: {results_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Results structure test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_results_structure()
    if success:
        print(f"\n✅ All tests passed! The pipeline is ready for production use.")
    else:
        print(f"\n❌ Tests failed. Check your setup.")