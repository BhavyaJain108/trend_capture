#!/usr/bin/env python3
"""
Demo: Date Filtering in YouTube Trends Vector Database
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.trends_vector_db import TrendsVectorDB

def main():
    print("📅 Date Filtering Demo - YouTube Trends Vector Database")
    print("=" * 55)
    
    try:
        # Initialize vector database
        print("1. Initializing vector database...")
        db = TrendsVectorDB(db_path="trends_vector_db")
        
        # Get date range from the data
        print("\n2. 📊 Analyzing date range in database...")
        stats = db.get_stats()
        print(f"   • Total trends: {stats['total_trends']}")
        
        # Get sample to see date range
        sample_results = db.search("", top_k=100)  # Get sample
        if sample_results:
            dates = [r['metadata']['date'] for r in sample_results]
            unique_dates = sorted(set(dates))
            print(f"   • Date range: {unique_dates[0]} to {unique_dates[-1]}")
            print(f"   • Available dates: {unique_dates}")
        
        # Demo 1: Search for recent trends only
        print(f"\n3. 🔍 Search Examples with Date Filtering:")
        
        print(f"\n   📅 Recent trends only (after 2024-08-01):")
        recent_results = db.search(
            query="artificial intelligence programming", 
            top_k=5, 
            after_date="2024-08-01"
        )
        for i, result in enumerate(recent_results, 1):
            date = result['metadata']['date']
            score = result['metadata']['score']
            category = result['metadata']['category']
            text = result['text'][:60] + "..." if len(result['text']) > 60 else result['text']
            print(f"      {i}. [{date}] [score:{score:+.1f}] ({category}) {text}")
        
        # Demo 2: Compare old vs new trends
        print(f"\n   📊 Comparison: Before vs After 2024-10-01")
        
        print(f"   🔙 Before 2024-10-01:")
        old_results = db.search(
            query="python programming", 
            top_k=3, 
            before_date="2024-10-01"
        )
        for i, result in enumerate(old_results, 1):
            date = result['metadata']['date']
            similarity = result['similarity']
            text = result['text'][:50] + "..." if len(result['text']) > 50 else result['text']
            print(f"      {i}. [{date}] [sim:{similarity:.3f}] {text}")
        
        print(f"   🔜 After 2024-10-01:")
        new_results = db.search(
            query="python programming", 
            top_k=3, 
            after_date="2024-10-01"
        )
        for i, result in enumerate(new_results, 1):
            date = result['metadata']['date']
            similarity = result['similarity']
            text = result['text'][:50] + "..." if len(result['text']) > 50 else result['text']
            print(f"      {i}. [{date}] [sim:{similarity:.3f}] {text}")
        
        # Demo 3: Date range filtering
        print(f"\n   📊 Date Range: 2024-08-01 to 2024-10-15")
        range_results = db.search(
            query="machine learning AI", 
            top_k=4,
            after_date="2024-08-01",
            before_date="2024-10-15"
        )
        for i, result in enumerate(range_results, 1):
            date = result['metadata']['date']
            score = result['metadata']['score']
            text = result['text'][:55] + "..." if len(result['text']) > 55 else result['text']
            print(f"      {i}. [{date}] [score:{score:+.1f}] {text}")
        
        # Demo 4: Recent trending topics
        print(f"\n4. 📈 Recent Trending Topics (after 2024-10-01, high scores):")
        recent_trending = db.get_trending_topics(
            top_k=5, 
            min_score=0.7,
            after_date="2024-10-01"
        )
        for i, result in enumerate(recent_trending, 1):
            date = result['metadata']['date']
            score = result['metadata']['score']
            category = result['metadata']['category']
            text = result['text'][:60] + "..." if len(result['text']) > 60 else result['text']
            print(f"   {i}. [{date}] [{score:+.1f}] ({category}) {text}")
        
        # Demo 5: Category + Date filtering
        print(f"\n5. 🎯 Advanced Filtering: 'early_adopter_products' after 2024-09-01")
        advanced_results = db.search(
            query="new tools software development",
            category="early_adopter_products",
            after_date="2024-09-01",
            min_score=0.6,
            top_k=3
        )
        for i, result in enumerate(advanced_results, 1):
            date = result['metadata']['date']
            score = result['metadata']['score']
            similarity = result['similarity']
            text = result['text'][:55] + "..." if len(result['text']) > 55 else result['text']
            print(f"   {i}. [{date}] [score:{score:+.1f}, sim:{similarity:.3f}] {text}")
        
        print(f"\n✅ Date filtering demo completed!")
        print(f"\n💡 Date Filtering Usage:")
        print(f"   • After date: db.search('query', after_date='2024-08-01')")
        print(f"   • Before date: db.search('query', before_date='2024-10-01')")
        print(f"   • Date range: db.search('query', after_date='2024-08-01', before_date='2024-10-15')")
        print(f"   • Combined filters: category + date + min_score")
        print(f"   • Date format: 'YYYY-MM-DD' (e.g., '2024-08-01')")
        
        print(f"\n🚀 Use Cases:")
        print(f"   • Track trend evolution over time")
        print(f"   • Compare before/after periods")
        print(f"   • Focus on recent developments only")
        print(f"   • Analyze seasonal patterns")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())