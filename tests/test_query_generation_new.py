#!/usr/bin/env python3
"""Test script for the updated YouTube query generation with multiple queries."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.youtube_query_generation import YouTubeQueryGenerator, QueryGenerationError

def test_multiple_query_generation():
    """Test the new multiple query generation structure."""
    
    try:
        generator = YouTubeQueryGenerator()
        
        print("🎯 TESTING NEW QUERY GENERATION STRUCTURE")
        print("=" * 60)
        
        # Test with a simple query
        user_query = "AI coding tools for developers"
        
        print(f"User Query: '{user_query}'")
        print("-" * 60)
        
        # Generate queries
        result = generator.generate_search_query(user_query)
        
        print(f"\n📊 GENERATION RESULTS:")
        print(f"Number of queries: {len(result.queries)}")
        print(f"Date filter: {result.date}")
        print(f"Reasoning: {result.reasoning}")
        
        print(f"\n🔍 GENERATED QUERIES:")
        for i, query in enumerate(result.queries, 1):
            word_count = len(query.split())
            status = "✅" if word_count <= 15 else "❌"
            print(f"   {status} Query {i} ({word_count} words): {query}")
        
        # Validate word count constraint
        all_valid = all(len(q.split()) <= 15 for q in result.queries)
        print(f"\n📏 WORD COUNT VALIDATION:")
        print(f"   All queries ≤ 15 words: {'✅ PASS' if all_valid else '❌ FAIL'}")
        
        # Test data structure
        print(f"\n🔧 DATA STRUCTURE TEST:")
        print(f"   result.queries type: {type(result.queries)}")
        print(f"   result.date type: {type(result.date)}")
        print(f"   result.reasoning type: {type(result.reasoning)}")
        
        print(f"\n✅ New query generation structure test completed!")
        return result
        
    except QueryGenerationError as e:
        print(f"❌ Query Generation Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None

def test_word_count_enforcement():
    """Test that the 15-word limit is properly enforced."""
    
    print(f"\n🎯 TESTING WORD COUNT ENFORCEMENT")
    print("=" * 60)
    
    # This tests the parsing logic with a mock response that has long queries
    generator = YouTubeQueryGenerator()
    
    # Test response parsing directly
    mock_response = '''
    {
        "queries": [
            "This is a very long query that definitely exceeds the fifteen word limit and should be truncated properly",
            "Short query",
            "Another extremely long query with many words that should be cut off at exactly fifteen words maximum"
        ],
        "date": "2024-01-01",
        "reasoning": "Test reasoning"
    }
    '''
    
    try:
        result = generator._parse_response(mock_response)
        
        print(f"📊 WORD COUNT TEST RESULTS:")
        for i, query in enumerate(result.queries, 1):
            word_count = len(query.split())
            status = "✅" if word_count <= 15 else "❌"
            print(f"   {status} Query {i} ({word_count} words): {query}")
        
        max_words = max(len(q.split()) for q in result.queries)
        print(f"\n📏 Maximum word count: {max_words}")
        print(f"   Enforcement working: {'✅ YES' if max_words <= 15 else '❌ NO'}")
        
    except Exception as e:
        print(f"❌ Word count test failed: {e}")

if __name__ == "__main__":
    # Run tests
    result = test_multiple_query_generation()
    test_word_count_enforcement()
    
    if result:
        print(f"\n🎉 All tests completed! New query generation structure is working.")
    else:
        print(f"\n❌ Tests failed. Check your setup.")