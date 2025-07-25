#!/usr/bin/env python3
"""Test to compare regular pipeline vs parallel pipeline results."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.pipeline import YouTubeTrendsPipeline
from src.youtube_trends.parallel_pipeline import ParallelYouTubeTrendsPipeline
import time

def test_pipeline_comparison():
    """Compare regular vs parallel pipeline with the same query."""
    
    test_query = "javascript tutorial"
    max_videos = 3  # Keep small for faster testing
    
    print("🔄 Pipeline Comparison Test")
    print("=" * 60)
    print(f"Query: '{test_query}'")
    print(f"Max videos: {max_videos}")
    print("=" * 60)
    
    results = {}
    
    # Test Regular Pipeline
    print("\n🐌 Testing Regular Pipeline:")
    print("-" * 40)
    
    try:
        regular_pipeline = YouTubeTrendsPipeline()
        
        start_time = time.time()
        regular_result = regular_pipeline.run_analysis(
            user_query=test_query,
            max_videos=max_videos,
            show_progress=True
        )
        regular_time = time.time() - start_time
        
        results['regular'] = {
            'result': regular_result,
            'time': regular_time,
            'success': True
        }
        
        print(f"\n✅ Regular Pipeline Complete:")
        print(f"   Videos processed: {regular_result.videos_processed}")
        print(f"   Total insights: {regular_result.total_insights}")
        print(f"   Processing time: {regular_time:.2f}s")
        print(f"   Results dir: {regular_result.results_dir}")
        
    except Exception as e:
        print(f"❌ Regular pipeline failed: {e}")
        results['regular'] = {'success': False, 'error': str(e)}
    
    # Test Parallel Pipeline
    print(f"\n" + "=" * 60)
    print("⚡ Testing Parallel Pipeline:")
    print("-" * 40)
    
    try:
        parallel_pipeline = ParallelYouTubeTrendsPipeline()
        
        start_time = time.time()
        parallel_result = parallel_pipeline.run_analysis(
            user_query=test_query,
            max_videos=max_videos,
            show_progress=True,
            max_workers=2  # Use 2 workers for testing
        )
        parallel_time = time.time() - start_time
        
        results['parallel'] = {
            'result': parallel_result,
            'time': parallel_time,
            'success': True
        }
        
        print(f"\n✅ Parallel Pipeline Complete:")
        print(f"   Videos processed: {parallel_result.videos_processed}")
        print(f"   Total insights: {parallel_result.total_insights}")
        print(f"   Processing time: {parallel_time:.2f}s")
        print(f"   Results dir: {parallel_result.results_dir}")
        
    except Exception as e:
        print(f"❌ Parallel pipeline failed: {e}")
        results['parallel'] = {'success': False, 'error': str(e)}
    
    # Compare Results
    print(f"\n" + "=" * 60)
    print("📊 COMPARISON RESULTS:")
    print("=" * 60)
    
    if results['regular']['success'] and results['parallel']['success']:
        reg_result = results['regular']['result']
        par_result = results['parallel']['result']
        reg_time = results['regular']['time']
        par_time = results['parallel']['time']
        
        print(f"📈 Performance Comparison:")
        print(f"   Regular time:  {reg_time:.2f}s")
        print(f"   Parallel time: {par_time:.2f}s")
        
        if par_time > 0:
            speedup = reg_time / par_time
            print(f"   Speedup:       {speedup:.2f}x {'🚀' if speedup > 1 else '🐌'}")
        
        print(f"\n📊 Output Comparison:")
        print(f"   Regular videos processed:  {reg_result.videos_processed}")
        print(f"   Parallel videos processed: {par_result.videos_processed}")
        print(f"   Regular insights:          {reg_result.total_insights}")
        print(f"   Parallel insights:         {par_result.total_insights}")
        
        # Check if results are similar
        video_diff = abs(reg_result.videos_processed - par_result.videos_processed)
        insight_diff = abs(reg_result.total_insights - par_result.total_insights)
        
        print(f"\n🔍 Result Consistency:")
        print(f"   Video count difference:   {video_diff} {'✅' if video_diff <= 1 else '⚠️'}")
        print(f"   Insight count difference: {insight_diff} {'✅' if insight_diff <= 10 else '⚠️'}")
        
        # Check error counts
        reg_errors = len(reg_result.errors)
        par_errors = len(par_result.errors)
        print(f"   Regular errors:  {reg_errors}")
        print(f"   Parallel errors: {par_errors}")
        
        # Show sample insights comparison
        if not reg_result.insights_df.empty and not par_result.insights_df.empty:
            print(f"\n🎯 Sample Insights Comparison:")
            print(f"   Regular top insight:  [{reg_result.insights_df.iloc[0]['score']:+.2f}] {reg_result.insights_df.iloc[0]['information'][:50]}...")
            print(f"   Parallel top insight: [{par_result.insights_df.iloc[0]['score']:+.2f}] {par_result.insights_df.iloc[0]['information'][:50]}...")
        
        # Overall assessment
        if video_diff <= 1 and insight_diff <= 10:
            print(f"\n✅ PIPELINES PRODUCE CONSISTENT RESULTS!")
        else:
            print(f"\n⚠️  PIPELINES HAVE SIGNIFICANT DIFFERENCES")
            
    else:
        print("❌ Cannot compare - one or both pipelines failed")
        if not results['regular']['success']:
            print(f"   Regular error: {results['regular']['error']}")
        if not results['parallel']['success']:
            print(f"   Parallel error: {results['parallel']['error']}")
    
    return results

if __name__ == "__main__":
    test_pipeline_comparison()