#!/usr/bin/env python3
"""
Simple script to run YouTube Trends Analysis with your own prompt.

Usage:
    python run_analysis.py "your query here"
    python run_analysis.py "AI coding tools for developers"
    python run_analysis.py "python data science trends"
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from youtube_trends.pipeline import YouTubeTrendsPipeline

def main():
    """Run the YouTube trends analysis with user input."""
    
    # Check if query was provided
    if len(sys.argv) < 2:
        print("🤖 YouTube Trends Analysis")
        print("=" * 50)
        print("Usage: python run_analysis.py \"your query here\"")
        print()
        print("Examples:")
        print('  python run_analysis.py "AI coding tools"')
        print('  python run_analysis.py "python data science trends"')
        print('  python run_analysis.py "startup funding 2024"')
        print('  python run_analysis.py "remote work productivity tools"')
        sys.exit(1)
    
    # Get user query from command line
    user_query = " ".join(sys.argv[1:])
    
    print("🚀 YouTube Trends Analysis")
    print("=" * 60)
    print(f"Query: '{user_query}'")
    print("=" * 60)
    
    try:
        # Initialize pipeline
        pipeline = YouTubeTrendsPipeline()
        
        # Run analysis with default settings
        result = pipeline.run_analysis(
            user_query=user_query,
            max_videos=5,      # Process up to 5 videos
            show_progress=True # Show progress messages
        )
        
        # Display final summary
        print("\n" + "=" * 60)
        print("📊 ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"📁 Results directory: {result.results_dir}")
        print(f"🎬 Videos processed: {result.videos_processed}")
        print(f"💡 Total insights: {result.total_insights}")
        print(f"⏱️  Processing time: {result.processing_time:.1f}s")
        
        if result.errors:
            print(f"⚠️  Errors encountered: {len(result.errors)}")
        
        # Show file locations
        print(f"\n📋 Generated files:")
        print(f"   • trend_results.csv - {result.total_insights} insights with trend scores")
        print(f"   • query_results.csv - Search query breakdown") 
        print(f"   • youtube_log.csv - {len(result.youtube_log_df)} video details")
        print(f"   • ai_prompt.txt - AI-generated search queries")
        print(f"   • prompt.txt - Your original query")
        
        # Quick preview of top insights
        if not result.insights_df.empty:
            print(f"\n🔍 Top 3 Insights:")
            for i, (_, row) in enumerate(result.insights_df.head(3).iterrows(), 1):
                score_emoji = "📈" if row['score'] > 0.5 else "📉" if row['score'] < -0.5 else "➡️"
                print(f"   {i}. {score_emoji} [{row['score']:+.2f}] {row['category']}: {row['information'][:60]}...")
        
        print(f"\n✅ Open the results directory to explore all insights!")
        print(f"📂 {result.results_dir}")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Make sure your .env file has valid API keys")
        print(f"2. Check your internet connection")
        print(f"3. Try a simpler query like 'programming tutorial'")
        sys.exit(1)

if __name__ == "__main__":
    main()