#!/usr/bin/env python3
"""
Simple YouTube Trends Analysis Runner

Usage: python run_analysis_simple.py "your query"
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_trends.parallel_pipeline import ParallelYouTubeTrendsPipeline

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_analysis_simple.py \"your search query\"")
        print("Example: python run_analysis_simple.py \"day in my life nyc vlog\"")
        return 1
    
    query = sys.argv[1]
    print(f"🚀 Running analysis for: '{query}'")
    
    try:
        # Initialize and run pipeline
        pipeline = ParallelYouTubeTrendsPipeline()
        results = pipeline.run_analysis(query)
        
        if results['success']:
            print(f"✅ Analysis complete!")
            print(f"📊 Results saved to: {results['results_file']}")
            print(f"🎯 Found {results.get('total_insights', 0)} trends")
            
            print(f"\n🎯 Next steps:")
            print(f"   python tools/grade_and_store.py auto")
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            return 1
    
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())