#!/usr/bin/env python3
"""
Demo with Sample Data - Simple Vector Search
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.simple_vector_store import SimpleVectorStore

def main():
    print("🚀 Simple Vector Search Demo with Sample Data")
    print("=" * 50)
    
    try:
        # Initialize vector store
        print("1. Initializing vector store...")
        store = SimpleVectorStore(db_path="demo_db", collection_name="sample_trends")
        
        # Add sample trend data
        print("\n2. Adding sample trend data...")
        sample_data = [
            {
                "text": "Artificial intelligence coding assistants like GitHub Copilot are revolutionizing software development",
                "category": "early_adopter_products",
                "trend_score": 0.9,
                "channel": "Tech Insights",
                "user_query": "AI coding tools"
            },
            {
                "text": "Python continues to dominate data science with libraries like pandas, numpy, and scikit-learn",
                "category": "emerging_topics", 
                "trend_score": 0.8,
                "channel": "Data Science Hub",
                "user_query": "python data science"
            },
            {
                "text": "React and Next.js frameworks are becoming the standard for modern web development",
                "category": "early_adopter_products",
                "trend_score": 0.7,
                "channel": "Frontend Masters", 
                "user_query": "react development"
            },
            {
                "text": "Cloud computing adoption is accelerating with containerization and serverless architectures",
                "category": "behavioral_patterns",
                "trend_score": 0.8,
                "channel": "Cloud Expert",
                "user_query": "cloud computing"
            },
            {
                "text": "Machine learning operations (MLOps) tools are gaining traction for model deployment",
                "category": "emerging_topics",
                "trend_score": 0.6,
                "channel": "ML Engineering",
                "user_query": "mlops tools"
            }
        ]
        
        # Add to ChromaDB
        ids = [f"sample_{i}" for i in range(len(sample_data))]
        documents = [item["text"] for item in sample_data]
        metadatas = [{k: v for k, v in item.items() if k != "text"} for item in sample_data]
        
        store.collection.add(ids=ids, documents=documents, metadatas=metadatas)
        print(f"   ✅ Added {len(sample_data)} sample trends")
        
        # Test search functionality
        print("\n3. 🔍 Testing Search Capabilities:")
        
        # Search for AI content
        print("\n   🤖 Search: 'artificial intelligence programming'")
        ai_results = store.search("artificial intelligence programming", top_k=3)
        for i, result in enumerate(ai_results, 1):
            similarity = result['similarity']
            score = result['metadata']['trend_score']
            text = result['text'][:70] + "..."
            print(f"      {i}. [sim:{similarity:.3f}, score:{score:+.1f}] {text}")
        
        # Search for Python
        print("\n   🐍 Search: 'Python data science libraries'")
        python_results = store.search("Python data science libraries", top_k=2)
        for i, result in enumerate(python_results, 1):
            similarity = result['similarity']
            channel = result['metadata']['channel']
            text = result['text'][:60] + "..."
            print(f"      {i}. [sim:{similarity:.3f}] by {channel}: {text}")
        
        # Category search
        print("\n   📊 Category filter: 'early_adopter_products'")
        category_results = store.search("new software tools", category="early_adopter_products", top_k=3)
        for i, result in enumerate(category_results, 1):
            similarity = result['similarity']
            score = result['metadata']['trend_score']
            text = result['text'][:60] + "..."
            print(f"      {i}. [sim:{similarity:.3f}, trend:{score:+.1f}] {text}")
        
        # Broad search
        print("\n   🌐 Broad search: 'development trends technology'")
        broad_results = store.search("development trends technology", top_k=5)
        print(f"      Found {len(broad_results)} results:")
        for i, result in enumerate(broad_results[:3], 1):
            similarity = result['similarity']
            category = result['metadata']['category']
            text = result['text'][:50] + "..."
            print(f"      {i}. [sim:{similarity:.3f}] ({category}) {text}")
        
        # Stats
        print("\n4. 📊 Database Statistics:")
        stats = store.get_stats()
        print(f"   • Total trends: {stats['total_trends']}")
        print(f"   • Categories: {list(stats['categories'].keys())}")
        print(f"   • Category breakdown: {stats['categories']}")
        
        # Cleanup
        print("\n5. 🧹 Cleaning up demo data...")
        store.clear()
        print("   ✅ Demo data cleared")
        
        print("\n🎉 Simple Vector Search Demo Complete!")
        print("\n✨ What This Demonstrates:")
        print("   • Automatic embeddings (no API keys needed)")
        print("   • Semantic similarity search")
        print("   • Metadata filtering by category")
        print("   • Perfect for small YouTube trend datasets")
        print("   • Fast and efficient with ChromaDB")
        
        print("\n💡 Ready for Your Data:")
        print("   • Replace sample data with your YouTube trends")
        print("   • Use natural language search queries")
        print("   • Filter by categories, channels, etc.")
        print("   • Scale up as your dataset grows")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())