#!/usr/bin/env python3
"""Test script for YouTube query generation using Claude API."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.youtube_query_generation import YouTubeQueryGenerator, QueryGenerationError

def test_single_query_generation():
    """Test generating a single optimized search query."""
    try:
        generator = YouTubeQueryGenerator()
        
        # Test queries for different types of products/markets
        test_queries = [
            "Tesla Model 3 reliability issues",
            "iPhone 15 vs Samsung Galaxy S24",
            "best project management software for startups",
            "artificial intelligence impact on healthcare"
        ]
        
        print("🤖 TESTING SINGLE QUERY GENERATION")
        print("=" * 60)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. USER QUERY: '{query}'")
            print("-" * 40)
            
            result = generator.generate_search_query(query)
            
            print(f"🔍 OPTIMIZED SEARCH: '{result.search_query}'")
            print(f"📅 DATE FILTER: {result.published_after or 'None'}")
            print(f"💭 REASONING: {result.reasoning}")
            print()
            
    except QueryGenerationError as e:
        print(f"❌ Query Generation Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_multiple_query_variations():
    """Test generating multiple query variations."""
    try:
        generator = YouTubeQueryGenerator()
        
        user_query = "best gaming laptops 2024"
        
        print("\n🔄 TESTING MULTIPLE QUERY VARIATIONS")
        print("=" * 60)
        print(f"USER QUERY: '{user_query}'")
        print("-" * 40)
        
        results = generator.generate_multiple_queries(user_query, num_variations=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. VARIATION {i}:")
            print(f"   🔍 SEARCH: '{result.search_query}'")
            print(f"   📅 DATE: {result.published_after or 'None'}")
            print(f"   💭 STRATEGY: {result.reasoning}")
            
    except QueryGenerationError as e:
        print(f"❌ Query Generation Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_edge_cases():
    """Test edge cases and error handling."""
    try:
        generator = YouTubeQueryGenerator()
        
        print("\n🚨 TESTING EDGE CASES")
        print("=" * 60)
        
        # Test empty query
        try:
            result = generator.generate_search_query("")
            print("❌ Empty query should have failed")
        except QueryGenerationError:
            print("✅ Empty query properly rejected")
        
        # Test very specific query
        result = generator.generate_search_query("MacBook Pro M3 chip thermal throttling performance")
        print(f"\n✅ SPECIFIC QUERY HANDLED:")
        print(f"   🔍 '{result.search_query}'")
        print(f"   📅 {result.published_after or 'No date filter'}")
        
    except Exception as e:
        print(f"❌ Edge case error: {e}")

if __name__ == "__main__":
    test_single_query_generation()
    test_multiple_query_variations() 
    test_edge_cases()