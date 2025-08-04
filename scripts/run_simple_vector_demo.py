#!/usr/bin/env python3
"""
Simple Vector Database Demo - No OpenAI Required!

Uses ChromaDB's built-in embeddings for small datasets.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.simple_vector_store import SimpleTrendSearch

def main():
    print("🚀 Simple YouTube Trends Vector Search (No API Keys Required!)")
    print("=" * 65)
    
    try:
        # Initialize simple search system
        print("1. Initializing vector search system...")
        search = SimpleTrendSearch()
        
        # Check current stats
        stats = search.get_database_stats()
        print(f"   📊 Current database: {stats['total_trends']} trends indexed")
        
        if stats['total_trends'] == 0:
            print("\n2. Indexing YouTube analysis runs...")
            result = search.index_all_runs()
            
            if result['success']:
                print(f"   ✅ Successfully indexed {result['trends_added']} trends")
                print(f"   📁 Processed {result['runs_processed']} analysis runs")
            else:
                print(f"   ❌ Indexing failed: {result['error']}")
                print("   💡 Make sure you have YouTube analysis results in the 'results/' directory")
                return 1
        else:
            print("   ✅ Database already contains trends")
        
        # Demo search capabilities
        print("\n3. 🔍 Semantic Search Examples:")
        
        # Search for AI content
        print("\n   🤖 Searching for 'artificial intelligence machine learning':")
        ai_results = search.search_trends("artificial intelligence machine learning", top_k=3)
        for i, result in enumerate(ai_results[:3], 1):
            similarity = result['similarity']
            score = result['metadata']['trend_score']
            category = result['metadata']['category']
            text = result['text'][:70] + "..." if len(result['text']) > 70 else result['text']
            print(f"      {i}. [sim:{similarity:.2f}, score:{score:+.1f}] ({category}) {text}")
        
        # Search for programming content
        print("\n   💻 Searching for 'Python programming development':")
        python_results = search.search_trends("Python programming development", top_k=3)
        for i, result in enumerate(python_results[:3], 1):
            similarity = result['similarity']
            channel = result['metadata']['channel']
            text = result['text'][:70] + "..." if len(result['text']) > 70 else result['text']
            print(f"      {i}. [sim:{similarity:.2f}] by {channel}: {text}")
        
        # Category-specific search
        print("\n   📊 Searching within 'early_adopter_products' category:")
        product_results = search.search_trends("new tools software", category="early_adopter_products", top_k=3)
        for i, result in enumerate(product_results[:3], 1):
            similarity = result['similarity']
            score = result['metadata']['trend_score']
            text = result['text'][:60] + "..." if len(result['text']) > 60 else result['text']
            print(f"      {i}. [sim:{similarity:.2f}, trend:{score:+.1f}] {text}")
        
        print("\n4. 📈 Trending Topics Analysis:")
        
        # Get trending topics
        trending = search.get_trending_topics()[:5]
        print(f"   🔥 Top {len(trending)} trending topics:")
        for i, result in enumerate(trending, 1):
            score = result['metadata']['trend_score']
            category = result['metadata']['category']
            text = result['text'][:60] + "..." if len(result['text']) > 60 else result['text']
            print(f"      {i}. [{score:+.1f}] ({category}) {text}")
        
        # Category analysis
        print("\n   📂 Category breakdown:")
        final_stats = search.get_database_stats()
        for category, count in final_stats['categories'].items():
            print(f"      • {category}: {count} trends")
        
        print(f"\n5. 📊 Final Statistics:")
        print(f"   • Total trends: {final_stats['total_trends']}")
        print(f"   • Unique channels: {final_stats['unique_channels']}")
        print(f"   • Analysis runs: {final_stats['unique_runs']}")
        
        print("\n✅ Simple vector search demo completed!")
        print("\n🎯 Key Advantages:")
        print("   • No API keys required")
        print("   • Works offline")
        print("   • Fast semantic search")
        print("   • Perfect for small datasets")
        print("   • Built-in ChromaDB embeddings")
        
        print("\n💡 Usage Tips:")
        print("   • Use natural language queries")
        print("   • Filter by category for focused results")
        print("   • Higher similarity scores = better matches")
        print("   • Trend scores show rising/declining topics")
        
        return 0
    
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())