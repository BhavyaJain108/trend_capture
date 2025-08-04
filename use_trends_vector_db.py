#!/usr/bin/env python3
"""
How to Use YouTube Trends Vector Database

Simple examples showing how to use the vector database for searching trends.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from youtube_trends.trends_vector_db import TrendsVectorDB

def main():
    print("📚 How to Use YouTube Trends Vector Database")
    print("=" * 50)
    
    # Initialize the database
    print("1. Initialize the database:")
    print("   db = TrendsVectorDB()")
    db = TrendsVectorDB()
    
    # Load your data (only needed once)
    print("\n2. Load your trend data (only needed once):")
    print("   result = db.load_all_available_runs()")
    stats = db.get_stats()
    if stats['total_trends'] == 0:
        print("   Loading data...")
        result = db.load_all_available_runs()
        if result['success']:
            print(f"   ✅ Loaded {result['total_trends_added']} trends")
        else:
            print(f"   ❌ Loading failed: {result['error']}")
            return
    else:
        print(f"   ✅ Already loaded: {stats['total_trends']} trends")
    
    print("\n" + "="*50)
    print("🔍 BASIC SEARCH EXAMPLES")
    print("="*50)
    
    # Example 1: Basic search
    print("\n📝 Example 1: Basic Search")
    print("   Code: db.search('artificial intelligence')")
    results = db.search("artificial intelligence", top_k=3)
    for i, result in enumerate(results, 1):
        score = result['metadata']['score']
        category = result['metadata']['category']
        text = result['text'][:60] + "..."
        print(f"   {i}. [{score:+.1f}] ({category}) {text}")
    
    # Example 2: Category filtering
    print("\n📂 Example 2: Search Within Category")
    print("   Code: db.search('new tools', category='early_adopter_products')")
    results = db.search("new tools", category="early_adopter_products", top_k=3)
    for i, result in enumerate(results, 1):
        score = result['metadata']['score']
        text = result['text'][:60] + "..."
        print(f"   {i}. [{score:+.1f}] {text}")
    
    # Example 3: Score filtering
    print("\n⭐ Example 3: High-Scoring Trends Only")
    print("   Code: db.search('python programming', min_score=0.7)")
    results = db.search("python programming", min_score=0.7, top_k=3)
    for i, result in enumerate(results, 1):
        score = result['metadata']['score']
        similarity = result['similarity']
        text = result['text'][:60] + "..."
        print(f"   {i}. [score:{score:+.1f}, sim:{similarity:.3f}] {text}")
    
    # Example 4: Date filtering
    print("\n📅 Example 4: Recent Trends Only")
    print("   Code: db.search('machine learning', after_date='2024-08-01')")
    results = db.search("machine learning", after_date="2024-08-01", top_k=3)
    for i, result in enumerate(results, 1):
        date = result['metadata']['date']
        score = result['metadata']['score']
        text = result['text'][:60] + "..."
        print(f"   {i}. [{date}] [{score:+.1f}] {text}")
    
    # Example 5: Combined filtering
    print("\n🎯 Example 5: Combined Filtering")
    print("   Code: db.search('AI tools', category='emerging_topics', min_score=0.6, after_date='2024-09-01')")
    results = db.search("AI tools", category="emerging_topics", min_score=0.6, after_date="2024-09-01", top_k=2)
    for i, result in enumerate(results, 1):
        date = result['metadata']['date']
        score = result['metadata']['score']
        text = result['text'][:50] + "..."
        print(f"   {i}. [{date}] [{score:+.1f}] {text}")
    
    print("\n" + "="*50)
    print("📊 ANALYSIS EXAMPLES")
    print("="*50)
    
    # Example 6: Get trending topics
    print("\n🔥 Example 6: Find Trending Topics")
    print("   Code: db.get_trending_topics(min_score=0.8, top_k=3)")
    trending = db.get_trending_topics(min_score=0.8, top_k=3)
    for i, result in enumerate(trending, 1):
        score = result['metadata']['score']
        category = result['metadata']['category']
        text = result['text'][:60] + "..."
        print(f"   {i}. [{score:+.1f}] ({category}) {text}")
    
    # Example 7: Category analysis
    print("\n🔬 Example 7: Analyze Specific Category")
    print("   Code: db.analyze_category('early_adopter_products')")
    analysis = db.analyze_category("early_adopter_products")
    if "error" not in analysis:
        print(f"   • Total trends: {analysis['total_trends']}")
        print(f"   • Average score: {analysis['score_stats']['average']:.2f}")
        print(f"   • Top trend: {analysis['top_trends'][0]['text'][:50]}...")
    
    # Example 8: Database stats
    print("\n📈 Example 8: Database Statistics")
    print("   Code: db.get_stats()")
    stats = db.get_stats()
    print(f"   • Total trends: {stats['total_trends']}")
    print(f"   • Categories: {list(stats['categories'].keys())}")
    print(f"   • Average score: {stats['score_distribution']['average']:.2f}")
    
    print("\n" + "="*50)
    print("💡 QUICK REFERENCE")
    print("="*50)
    
    print("""
🔍 SEARCH METHODS:
   db.search(query, top_k=10, category=None, min_score=None, after_date=None, before_date=None)
   db.get_trending_topics(category=None, top_k=20, min_score=0.5, after_date=None, before_date=None)
   db.analyze_category(category)
   db.get_stats()

📂 CATEGORIES:
   • early_adopter_products  • emerging_topics      • problem_spaces
   • behavioral_patterns     • educational_demand

📅 DATE FORMATS:
   • Use 'YYYY-MM-DD' format (e.g., '2024-08-01')
   • after_date: finds trends after this date
   • before_date: finds trends before this date

⭐ SCORE RANGES:
   • 1.0 = Highly trending/rising
   • 0.5 = Moderate trend
   • 0.0 = Neutral
   • -0.5+ = Declining (filtered out by default)

🎯 COMMON PATTERNS:
   # Find recent AI trends
   db.search("artificial intelligence", after_date="2024-08-01", min_score=0.7)
   
   # Compare periods
   old = db.search("python", before_date="2024-08-01") 
   new = db.search("python", after_date="2024-08-01")
   
   # Category deep dive
   analysis = db.analyze_category("emerging_topics")
   
   # Get what's trending now
   trending = db.get_trending_topics(min_score=0.8)
""")
    
    print("✅ Ready to use! Try these examples in your own code.")
    
    return 0

if __name__ == "__main__":
    exit(main())