#!/usr/bin/env python3
"""Debug transcript processing to find Config issue."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_transcript_processing():
    """Test transcript processing step by step."""
    
    print("🔍 Debug Transcript Processing")
    print("=" * 50)
    
    try:
        from src.youtube_trends.transcript_processing import TranscriptProcessor
        print("✅ Imported TranscriptProcessor")
        
        processor = TranscriptProcessor()
        print("✅ Initialized TranscriptProcessor")
        
        # Test with a simple transcript
        sample_transcript = "This is a test transcript about Python programming. It's very useful for learning."
        
        print("🧪 Testing process_transcript...")
        insights = processor.process_transcript(sample_transcript, "2024-01-01")
        print(f"✅ Processed transcript successfully")
        print(f"   Total insights: {insights.processing_metadata['total_insights']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_transcript_processing()