#!/usr/bin/env python3
"""
YouTube Trends Vector Database Demo

Simple demo using your actual trend_results.csv files.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.trends_vector_db import TrendsVectorDB

def main():
    print("🚀 YouTube Trends Vector Database Demo")
    print("=" * 45)
    
    try:
        # Initialize vector database
        print("1. Initializing vector database...")
        db = TrendsVectorDB(db_path="trends_vector_db")
        
        # Check current state
        stats = db.get_stats()
        print(f"   📊 Current database: {stats['total_trends']} trends")
        
        if stats['total_trends'] == 0:
            print("\n2. Loading trends from analysis runs...")
            result = db.load_all_available_runs()
            
            if result['success']:
                print(f"   ✅ Successfully loaded {result['total_trends_added']} trends")
                print(f"   📁 From {result['successful_runs']} runs")
                if result['failed_runs']:
                    print(f"   ⚠️  Failed runs: {result['failed_runs']}")
            else:
                print(f"   ❌ Loading failed: {result['error']}")
                return 1
        else:
            print("   ✅ Database already contains trends")
        
        # Show database stats
        print("\n3. 📊 Database Statistics:")
        final_stats = db.get_stats()
        print(f"   • Total trends: {final_stats['total_trends']}")
        print(f"   • Categories: {list(final_stats['categories'].keys())}")
        print(f"   • Runs: {len(final_stats['runs'])}")
        print(f"   • Average score: {final_stats['score_distribution']['average']:.2f}")
        
        # Category breakdown
        print(f"\n   📂 Category breakdown:")
        for category, count in final_stats['categories'].items():
            print(f"      • {category}: {count} trends")
        
        # Demo search functionality
        print("\n4. 🔍 Search Examples:")
        
        # Search for AI/ML content
        print("\n   🤖 Search: 'artificial intelligence machine learning'")
        ai_results = db.search("artificial intelligence machine learning", top_k=3)
        for i, result in enumerate(ai_results, 1):
            similarity = result['similarity']
            score = result['metadata']['score']
            category = result['metadata']['category']
            text = result['text'][:70] + "..." if len(result['text']) > 70 else result['text']
            print(f"      {i}. [sim:{similarity:.3f}, score:{score:+.1f}] ({category}) {text}")
        
        # Search for Python content
        print("\n   🐍 Search: 'Python programming development'")
        python_results = db.search("Python programming development", top_k=3)
        for i, result in enumerate(python_results, 1):
            similarity = result['similarity']
            score = result['metadata']['score']
            date = result['metadata']['date']
            text = result['text'][:60] + "..." if len(result['text']) > 60 else result['text']
            print(f"      {i}. [sim:{similarity:.3f}, {date}] {text}")
        
        # Category-specific search
        print("\n   📊 Category search: 'early_adopter_products' + 'new tools'")
        product_results = db.search("new tools software", category="early_adopter_products", top_k=3)
        for i, result in enumerate(product_results, 1):
            similarity = result['similarity']
            score = result['metadata']['score']
            text = result['text'][:60] + "..." if len(result['text']) > 60 else result['text']
            print(f"      {i}. [sim:{similarity:.3f}, score:{score:+.1f}] {text}")
        
        # High-scoring trends
        print("\n5. 📈 Trending Topics (High Scores):")
        trending = db.get_trending_topics(top_k=5, min_score=0.7)
        for i, result in enumerate(trending, 1):
            score = result['metadata']['score']
            category = result['metadata']['category']
            text = result['text'][:70] + "..." if len(result['text']) > 70 else result['text']
            print(f"   {i}. [{score:+.1f}] ({category}) {text}")
        
        # Category analysis
        print("\n6. 🔬 Deep Dive: 'emerging_topics' Category")
        category_analysis = db.analyze_category("emerging_topics")
        if "error" not in category_analysis:
            print(f"   • Total trends: {category_analysis['total_trends']}")
            print(f"   • Average score: {category_analysis['score_stats']['average']:.2f}")
            print(f"   • High-scoring trends: {category_analysis['score_stats']['high_score_count']}")
            print(f"   • Top 3 emerging topics:")
            for i, trend in enumerate(category_analysis['top_trends'][:3], 1):
                score = trend['metadata']['score']
                text = trend['text'][:60] + "..." if len(trend['text']) > 60 else trend['text']
                print(f"      {i}. [{score:+.1f}] {text}")
        
        print("\n✅ Demo completed successfully!")
        print("\n🎯 What This Demonstrates:")
        print("   • Automatic loading of your trend_results.csv files")
        print("   • Semantic search across all your trends")
        print("   • Category filtering and analysis")
        print("   • Score-based trend ranking")
        print("   • No API keys required!")
        
        print("\n💡 Next Steps:")
        print("   • Use db.search('your query') for custom searches")
        print("   • Filter by category: db.search('query', category='early_adopter_products')")
        print("   • Analyze specific categories: db.analyze_category('category_name')")
        print("   • Find trending topics: db.get_trending_topics()")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())