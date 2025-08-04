#!/usr/bin/env python3
"""
Basic Vector Database Demo (No OpenAI Required)

Demonstrates the vector database functionality using ChromaDB's built-in embeddings.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.vector_store import ChromaTrendStore
from youtube_trends.trend_aggregator import TrendEntry

def main():
    print("🗄️  Basic Vector Database Demo (No OpenAI Required)")
    print("=" * 60)
    
    try:
        # Initialize vector store with test collection
        print("1. Initializing ChromaDB vector store...")
        store = ChromaTrendStore(db_path="demo_vector_db", collection_name="demo_trends")
        
        # Create sample trend entries (without embeddings - ChromaDB will generate them)
        print("\n2. Creating sample trend data...")
        sample_trends = [
            TrendEntry(
                text="Artificial intelligence is revolutionizing software development with AI-powered coding assistants",
                category="early_adopter_products",
                trend_score=0.9,
                transcript_date="2024-01-15",
                video_title="AI Coding Revolution",
                video_id="demo123",
                channel="Tech Insights",
                run_id="demo_run_1",
                run_timestamp="2024-01-15T10:00:00",
                user_query="AI coding tools",
                embedding=None  # ChromaDB will generate embeddings
            ),
            TrendEntry(
                text="Python remains the most popular programming language for data science and machine learning projects",
                category="emerging_topics",
                trend_score=0.7,
                transcript_date="2024-01-16",
                video_title="Python Data Science Trends",
                video_id="demo456",
                channel="Data Science Hub",
                run_id="demo_run_1",
                run_timestamp="2024-01-16T11:00:00",
                user_query="python programming",
                embedding=None
            ),
            TrendEntry(
                text="Cloud computing adoption is accelerating with containers and serverless architectures",
                category="behavioral_patterns",
                trend_score=0.8,
                transcript_date="2024-01-17",
                video_title="Cloud Architecture Evolution",
                video_id="demo789",
                channel="Cloud Expert",
                run_id="demo_run_2",
                run_timestamp="2024-01-17T12:00:00",
                user_query="cloud computing",
                embedding=None
            ),
            TrendEntry(
                text="React and Next.js are dominating frontend development with improved developer experience",
                category="early_adopter_products",
                trend_score=0.6,
                transcript_date="2024-01-18",
                video_title="Modern Frontend Frameworks",
                video_id="demo101",
                channel="Frontend Masters",
                run_id="demo_run_2",
                run_timestamp="2024-01-18T13:00:00",
                user_query="react development",
                embedding=None
            )
        ]
        
        print(f"   Created {len(sample_trends)} sample trends")
        
        # Since we don't have embeddings, we'll need to use ChromaDB's text search
        print("\n3. Adding trends to vector store...")
        
        # For demo purposes, let's manually add the trends using ChromaDB's add method
        ids = []
        documents = []
        metadatas = []
        
        for i, trend in enumerate(sample_trends):
            ids.append(f"trend_{i}")
            documents.append(trend.text)
            metadatas.append({
                "category": trend.category,
                "trend_score": trend.trend_score,
                "transcript_date": trend.transcript_date,
                "video_title": trend.video_title,
                "video_id": trend.video_id,
                "channel": trend.channel,
                "run_id": trend.run_id,
                "run_timestamp": trend.run_timestamp,
                "user_query": trend.user_query
            })
        
        # Add to ChromaDB (it will generate embeddings automatically)
        store.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"   ✅ Added {len(sample_trends)} trends to vector store")
        
        # Test search functionality
        print("\n4. Demonstrating search capabilities...")
        
        # Search for AI-related content
        print("\n   🔍 Searching for 'artificial intelligence programming':")
        ai_results = store.search_similar(
            query_text="artificial intelligence programming",
            top_k=3
        )
        
        for i, result in enumerate(ai_results, 1):
            score = result.get('similarity_score', result.get('distance', 0))
            category = result['metadata']['category']
            text = result['text'][:80] + "..." if len(result['text']) > 80 else result['text']
            print(f"      {i}. [score: {score:.3f}] ({category}) {text}")
        
        # Search for Python content
        print("\n   🐍 Searching for 'Python programming data science':")
        python_results = store.search_similar(
            query_text="Python programming data science",
            top_k=2
        )
        
        for i, result in enumerate(python_results, 1):
            score = result.get('similarity_score', result.get('distance', 0))
            channel = result['metadata']['channel']
            text = result['text'][:80] + "..." if len(result['text']) > 80 else result['text']
            print(f"      {i}. [score: {score:.3f}] by {channel}: {text}")
        
        # Search with filters
        print("\n   🎯 Searching within 'early_adopter_products' category:")
        filtered_results = store.search_similar(
            query_text="software development tools",
            top_k=3,
            filters={"category": "early_adopter_products"}
        )
        
        for i, result in enumerate(filtered_results, 1):
            score = result.get('similarity_score', result.get('distance', 0))
            trend_score = result['metadata']['trend_score']
            text = result['text'][:60] + "..." if len(result['text']) > 60 else result['text']
            print(f"      {i}. [search: {score:.3f}, trend: {trend_score:+.1f}] {text}")
        
        # Show collection statistics
        print("\n5. Vector Store Statistics:")
        stats = store.get_collection_stats()
        print(f"   📊 Total trends: {stats['total_trends']}")
        print(f"   📂 Categories: {list(stats['categories'].keys())}")
        print(f"   🏃 Unique runs: {stats['unique_runs']}")
        print(f"   📺 Unique channels: {stats['unique_channels']}")
        
        # Cleanup
        print("\n6. Cleaning up demo data...")
        store.clear_collection()
        print("   🧹 Demo data cleared")
        
        print("\n✅ Basic vector database demo completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("   • Vector storage with ChromaDB")
        print("   • Semantic search using built-in embeddings")
        print("   • Metadata filtering")
        print("   • Collection statistics")
        print("\n🚀 Next Steps:")
        print("   • Add OPENAI_API_KEY for better embeddings")
        print("   • Use real trend data from your YouTube analysis runs")
        print("   • Scale up with the full TrendVectorDatabase class")
        
        return 0
    
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())