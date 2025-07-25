#!/usr/bin/env python3
"""Integration test script to demonstrate real YouTube transcript fetching."""

import sys
from src.youtube_trends.transcript import YouTubeTranscriptClient, TranscriptError

def test_transcript_fetching():
    """Test fetching transcripts from real YouTube videos."""
    client = YouTubeTranscriptClient()
    
    # Test videos with known transcripts (educational/public domain content)
    test_videos = [
        {
            "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "description": "Python tutorial video (short)"
        },
        {
            "url": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
            "description": "Programming tutorial"
        }
    ]
    
    for video in test_videos:
        print(f"\n{'='*60}")
        print(f"Testing: {video['description']}")
        print(f"URL: {video['url']}")
        print(f"{'='*60}")
        
        try:
            # Extract video ID
            video_id = client.extract_video_id(video['url'])
            print(f"Extracted Video ID: {video_id}")
            
            # Get available languages
            print("\nChecking available languages...")
            try:
                languages = client.get_available_languages(video['url'])
                print(f"Available languages: {languages}")
            except TranscriptError as e:
                print(f"Could not get languages: {e}")
                continue
            
            # Get transcript
            print("\nFetching transcript...")
            transcript = client.get_transcript(video['url'])
            
            print(f"Transcript entries: {len(transcript)}")
            print("\nFirst 3 entries:")
            for i, entry in enumerate(transcript[:3]):
                print(f"  {i+1}. [{entry['start']:.1f}s] {entry['text']}")
            
            if len(transcript) > 3:
                print(f"  ... and {len(transcript) - 3} more entries")
                
        except TranscriptError as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def test_url_parsing():
    """Test URL parsing with various formats."""
    client = YouTubeTranscriptClient()
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "dQw4w9WgXcQ",
        "invalid_url",
        ""
    ]
    
    print(f"\n{'='*60}")
    print("Testing URL parsing")
    print(f"{'='*60}")
    
    for url in test_urls:
        video_id = client.extract_video_id(url)
        status = "✅" if video_id else "❌"
        print(f"{status} {url:<40} -> {video_id}")

def interactive_test():
    """Allow user to test with their own YouTube URL."""
    client = YouTubeTranscriptClient()
    
    print(f"\n{'='*60}")
    print("Interactive Test")
    print(f"{'='*60}")
    
    while True:
        url = input("\nEnter a YouTube URL (or 'quit' to exit): ").strip()
        
        if url.lower() in ['quit', 'exit', 'q']:
            break
            
        if not url:
            continue
            
        try:
            print(f"\nTesting URL: {url}")
            
            # Extract video ID
            video_id = client.extract_video_id(url)
            if not video_id:
                print("❌ Invalid YouTube URL")
                continue
                
            print(f"✅ Video ID: {video_id}")
            
            # Get available languages
            try:
                languages = client.get_available_languages(url)
                print(f"Available languages: {languages}")
            except TranscriptError as e:
                print(f"❌ Cannot get transcript: {e}")
                continue
            
            # Ask for language preference
            if len(languages) > 1:
                print(f"Available: {', '.join(languages)}")
                lang_input = input("Enter preferred language codes (comma-separated, or press Enter for default): ").strip()
                preferred_langs = [l.strip() for l in lang_input.split(',')] if lang_input else None
            else:
                preferred_langs = None
            
            # Get transcript
            transcript = client.get_transcript(url, languages=preferred_langs)
            
            print(f"\n✅ Retrieved {len(transcript)} transcript entries")
            
            # Show sample entries
            show_count = min(5, len(transcript))
            print(f"\nFirst {show_count} entries:")
            for i, entry in enumerate(transcript[:show_count]):
                print(f"  {i+1}. [{entry['start']:.1f}s] {entry['text']}")
                
        except TranscriptError as e:
            print(f"❌ Transcript error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("YouTube Transcript Integration Test")
    print("==================================")
    
    # Run automated tests
    test_url_parsing()
    test_transcript_fetching()
    
    # Ask if user wants interactive test
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        print(f"\n{'='*60}")
        print("Run with --interactive flag to test your own URLs")
        print("Example: python integration_test.py --interactive")
        print(f"{'='*60}")