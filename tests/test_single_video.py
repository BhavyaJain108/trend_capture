#!/usr/bin/env python3
"""Test processing a single video to debug Config issue."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_single_video_processing():
    """Test processing a single video from the pipeline."""
    
    print("🎬 Debug Single Video Processing")
    print("=" * 50)
    
    try:
        from src.youtube_trends.transcript import YouTubeTranscriptClient
        from src.youtube_trends.transcript_processing import TranscriptProcessor
        
        print("✅ Imported modules")
        
        # Initialize components
        transcript_client = YouTubeTranscriptClient()
        processor = TranscriptProcessor()
        
        print("✅ Initialized components")
        
        # Test with a YouTube URL that should have transcripts
        test_url = "https://www.youtube.com/watch?v=ZwGEQcFo9RE"  # A known video with transcript
        
        print(f"🔍 Testing URL: {test_url}")
        
        # Extract transcript
        print("📝 Extracting transcript...")
        transcript_text = transcript_client.get_transcript(test_url)
        
        if not transcript_text:
            print("❌ No transcript found")
            return False
            
        print(f"✅ Extracted transcript ({len(transcript_text)} characters)")
        
        # Process insights
        print("🧠 Processing insights...")
        video_date = "2024-01-01"
        insights = processor.process_transcript(transcript_text, video_date)
        
        print(f"✅ Processed insights successfully")
        print(f"   Total insights: {insights.processing_metadata['total_insights']}")
        
        # Show breakdown
        categories = [
            ('early_adopter_products', insights.early_adopter_products),
            ('emerging_topics', insights.emerging_topics),
            ('problem_spaces', insights.problem_spaces),
            ('behavioral_patterns', insights.behavioral_patterns),
            ('educational_demand', insights.educational_demand)
        ]
        
        for category, category_insights in categories:
            print(f"   {category}: {len(category_insights)} insights")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_video_processing()
    if success:
        print(f"\n✅ Single video processing test passed!")
    else:
        print(f"\n❌ Single video processing test failed!")