#!/usr/bin/env python3
"""Simple test script to verify YouTube transcript functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.transcript import YouTubeTranscriptClient

def test_simple_transcript():
    """Test getting a transcript from a YouTube URL."""
    client = YouTubeTranscriptClient()
    
    # Use a well-known YouTube video that likely has transcripts
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        print(f"Testing with URL: {test_url}")
        transcript = client.get_transcript(test_url)
        
        if transcript:
            print("✅ SUCCESS: Got transcript!")
            print(f"\n📝 FULL SCRIPT:\n{transcript}")
        else:
            print("❌ FAILED: No transcript returned")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_simple_transcript()