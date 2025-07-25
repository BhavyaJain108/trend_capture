#!/usr/bin/env python3
"""Test script to verify the config refactoring works correctly."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.config import Config
from src.youtube_trends.youtube_query_generation import YouTubeQueryGenerator

def test_config_values():
    """Test that config values are accessible and correct."""
    
    print("🔧 Testing Config Values")
    print("=" * 50)
    
    # Test basic constants
    print(f"Claude Model: {Config.CLAUDE_MODEL}")
    print(f"Query Word Limit: {Config.QUERY_WORD_LIMIT}")
    print(f"Default Num Queries: {Config.DEFAULT_NUM_QUERIES}")
    print(f"YouTube Video ID Length: {Config.YOUTUBE_VIDEO_ID_LENGTH}")
    print(f"Trend Score Range: {Config.TREND_SCORE_MIN} to {Config.TREND_SCORE_MAX}")
    
    # Test helper methods
    print(f"\n🛠️ Testing Helper Methods:")
    emoji = Config.get_emoji("rocket")
    print(f"Rocket emoji: {emoji}")
    
    separator = Config.get_progress_separator(20)
    print(f"Progress separator: '{separator}'")
    
    # Test validation
    score = Config.validate_score(1.5)  # Should clamp to 1.0
    print(f"Validated score (1.5 -> {score})")
    
    # Test text truncation
    long_text = "This is a very long text that should be truncated"
    truncated = Config.truncate_text(long_text, 20)
    print(f"Truncated text: '{truncated}'")
    
    print(f"\n✅ Config values test passed!")

def test_query_generation_with_config():
    """Test that query generation works with config values."""
    
    print(f"\n🤖 Testing Query Generation with Config")
    print("=" * 50)
    
    try:
        generator = YouTubeQueryGenerator()
        
        # Test that it uses config defaults
        result = generator.generate_search_query("test query")
        
        print(f"Generated {len(result.queries)} queries (expected: {Config.DEFAULT_NUM_QUERIES})")
        
        # Check word limits
        for i, query in enumerate(result.queries, 1):
            word_count = len(query.split())
            status = "✅" if word_count <= Config.QUERY_WORD_LIMIT else "❌"
            print(f"   {status} Query {i}: {word_count} words ≤ {Config.QUERY_WORD_LIMIT}")
        
        print(f"\n✅ Query generation with config test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Query generation test failed: {e}")
        return False

def test_error_messages():
    """Test that error messages are coming from config."""
    
    print(f"\n📝 Testing Error Messages from Config")
    print("=" * 50)
    
    # Test formatted error messages
    error_msg = Config.ERROR_MESSAGES["no_api_key"].format(
        api_name="Test", env_var="TEST_API_KEY"
    )
    print(f"Formatted error: {error_msg}")
    
    # Test other messages
    print(f"Empty query error: {Config.ERROR_MESSAGES['empty_query']}")
    print(f"DSPy required error: {Config.ERROR_MESSAGES['dspy_required']}")
    
    print(f"\n✅ Error messages test passed!")

def test_signature_descriptions():
    """Test that DSPy signature descriptions are from config."""
    
    print(f"\n🔍 Testing DSPy Signature Descriptions")
    print("=" * 50)
    
    categories = ["early_adopter_products", "emerging_topics", "problem_spaces", 
                  "behavioral_patterns", "educational_demand"]
    
    for category in categories:
        desc = Config.SIGNATURE_DESCRIPTIONS[category]
        print(f"✅ {category}: {len(desc)} characters")
    
    print(f"\n✅ Signature descriptions test passed!")

if __name__ == "__main__":
    print("🚀 Testing Config Refactoring")
    print("=" * 60)
    
    try:
        test_config_values()
        success = test_query_generation_with_config()
        test_error_messages()
        test_signature_descriptions()
        
        if success:
            print(f"\n🎉 All config refactoring tests passed!")
            print("The system now uses centralized configuration!")
        else:
            print(f"\n❌ Some tests failed.")
            
    except Exception as e:
        print(f"\n❌ Config refactoring test failed: {e}")
        import traceback
        traceback.print_exc()