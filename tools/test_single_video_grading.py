#!/usr/bin/env python3
"""
Test Single Video Trend Discovery and Grading

Processes a single YouTube video, discovers trends, and lets you grade them.
Perfect for testing the trend grading system on a small dataset.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.youtube_search import YouTubeSearchClient
from youtube_trends.transcript_client import TranscriptClient
from youtube_trends.transcript_processing_claude import ClaudeTranscriptProcessor
from youtube_trends.trends_vector_db import TrendsVectorDB
from youtube_trends.config import Config
from datetime import datetime
import json

class SingleVideoTrendTester:
    """Test trend discovery and grading on a single video."""
    
    def __init__(self):
        self.search_client = YouTubeSearchClient(api_key=Config.YOUTUBE_API_KEY)
        self.transcript_client = TranscriptClient()
        self.processor = ClaudeTranscriptProcessor(api_key=Config.CLAUDE_API_KEY)
        self.vector_db = TrendsVectorDB()
        self.test_run_id = f"single_video_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def search_and_select_video(self, query: str) -> dict:
        """Search for videos and let user select one."""
        print(f"🔍 Searching YouTube for: '{query}'")
        
        try:
            videos = self.search_client.search_videos(query, max_results=5)
            
            if not videos:
                print("❌ No videos found")
                return None
            
            print(f"\n📺 Found {len(videos)} videos:")
            for i, video in enumerate(videos, 1):
                duration = video.get('duration', 'unknown')
                views = video.get('view_count', 'unknown')
                print(f"   {i}. {video['title'][:60]}...")
                print(f"      Channel: {video['channel_title']} | Duration: {duration} | Views: {views}")
                print(f"      ID: {video['video_id']}")
            
            # Let user select
            while True:
                try:
                    choice = input(f"\n👉 Select video (1-{len(videos)}): ").strip()
                    idx = int(choice) - 1
                    if 0 <= idx < len(videos):
                        selected_video = videos[idx]
                        print(f"✅ Selected: {selected_video['title']}")
                        return selected_video
                    else:
                        print(f"❌ Please enter a number between 1 and {len(videos)}")
                except ValueError:
                    print("❌ Please enter a valid number")
                except KeyboardInterrupt:
                    return None
                    
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return None
    
    def get_transcript(self, video_id: str) -> str:
        """Get transcript for a video."""
        print(f"📄 Fetching transcript for video {video_id}...")
        
        try:
            transcript = self.transcript_client.get_transcript(video_id)
            
            if not transcript:
                print("❌ No transcript available")
                return None
            
            print(f"✅ Transcript fetched: {len(transcript)} characters")
            return transcript
            
        except Exception as e:
            print(f"❌ Transcript fetch failed: {e}")
            return None
    
    def discover_trends(self, transcript: str, video_info: dict) -> dict:
        """Discover trends from transcript."""
        print(f"🧠 Analyzing transcript with Claude...")
        
        try:
            # Process transcript
            insights = self.processor.process_transcript(
                transcript=transcript,
                transcript_date=datetime.now().strftime('%Y-%m-%d')
            )
            
            print(f"✅ Analysis complete!")
            print(f"   📊 Processing metadata: {json.dumps(insights.processing_metadata, indent=2)}")
            
            # Convert to trends format
            trends = []
            
            # Process each category
            for category_name in ['early_adopter_products', 'emerging_topics', 'problem_spaces', 
                                'behavioral_patterns', 'educational_demand']:
                category_insights = getattr(insights, category_name)
                
                for insight_text, transcript_date, trend_score in category_insights:
                    trend = {
                        'text': insight_text,
                        'category': category_name,
                        'score': trend_score,
                        'date': transcript_date,
                        'video_id': video_info['video_id'],
                        'video_title': video_info['title'],
                        'channel': video_info['channel_title'],
                        'run_id': self.test_run_id,
                        'run_timestamp': datetime.now().isoformat(),
                        'user_query': f"single_video_test"
                    }
                    trends.append(trend)
            
            print(f"📈 Discovered {len(trends)} trends across all categories:")
            
            # Show summary by category
            from collections import Counter
            category_counts = Counter(trend['category'] for trend in trends)
            for category, count in category_counts.items():
                print(f"   • {category}: {count} trends")
            
            return {
                'trends': trends,
                'insights': insights,
                'video_info': video_info
            }
            
        except Exception as e:
            print(f"❌ Trend analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_trends_to_database(self, trends: list) -> bool:
        """Load discovered trends into vector database."""
        print(f"💾 Loading {len(trends)} trends into vector database...")
        
        try:
            # Prepare data for vector database
            documents = []
            metadatas = []
            ids = []
            
            for i, trend in enumerate(trends):
                # Create unique ID
                trend_id = f"{self.test_run_id}_{i:03d}"
                
                # Document text
                documents.append(trend['text'])
                
                # Metadata
                metadata = {
                    'category': trend['category'],
                    'score': float(trend['score']),
                    'date': trend['date'],
                    'video_id': trend['video_id'],
                    'video_title': trend['video_title'],
                    'channel': trend['channel'],
                    'run_id': trend['run_id'],
                    'run_timestamp': trend['run_timestamp'],
                    'user_query': trend['user_query']
                }
                metadatas.append(metadata)
                ids.append(trend_id)
            
            # Add to database
            self.vector_db.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Successfully loaded {len(trends)} trends to database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load trends to database: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_trends_preview(self, trends: list):
        """Show a preview of discovered trends."""
        print(f"\n📋 DISCOVERED TRENDS PREVIEW:")
        print("="*60)
        
        # Group by category
        from collections import defaultdict
        by_category = defaultdict(list)
        for trend in trends:
            by_category[trend['category']].append(trend)
        
        for category, category_trends in by_category.items():
            print(f"\n🏷️  {category.upper().replace('_', ' ')} ({len(category_trends)} trends):")
            
            # Sort by score
            sorted_trends = sorted(category_trends, key=lambda x: x['score'], reverse=True)
            
            for i, trend in enumerate(sorted_trends[:3], 1):  # Show top 3
                score = trend['score']
                text = trend['text'][:70] + "..." if len(trend['text']) > 70 else trend['text']
                print(f"   {i}. [{score:+.2f}] {text}")
            
            if len(category_trends) > 3:
                print(f"   ... and {len(category_trends) - 3} more")
    
    def run_test(self, search_query: str = None):
        """Run the complete single video test."""
        print("🎬 Single Video Trend Discovery & Grading Test")
        print("="*60)
        
        # Step 1: Search and select video
        if not search_query:
            search_query = input("🔍 Enter search query (or press Enter for 'AI tools 2024'): ").strip()
            if not search_query:
                search_query = "AI tools 2024"
        
        video_info = self.search_and_select_video(search_query)
        if not video_info:
            print("❌ No video selected. Exiting.")
            return False
        
        # Step 2: Get transcript
        transcript = self.get_transcript(video_info['video_id'])
        if not transcript:
            print("❌ Could not get transcript. Exiting.")
            return False
        
        # Step 3: Discover trends
        result = self.discover_trends(transcript, video_info)
        if not result:
            print("❌ Trend discovery failed. Exiting.")
            return False
        
        trends = result['trends']
        
        # Step 4: Show preview
        self.show_trends_preview(trends)
        
        # Step 5: Load to database
        success = self.load_trends_to_database(trends)
        if not success:
            print("❌ Failed to load trends. Exiting.")
            return False
        
        # Step 6: Show grading instructions
        print(f"\n" + "="*60)
        print("🎯 READY FOR MANUAL GRADING!")
        print("="*60)
        print(f"✅ Processed video: {video_info['title'][:50]}...")
        print(f"✅ Discovered {len(trends)} trends")
        print(f"✅ Loaded trends to database with run_id: {self.test_run_id}")
        
        print(f"\n🚀 Now you can grade these trends:")
        print(f"   python trend_grader.py grade")
        print(f"   python trend_grader.py stats")
        
        # Ask if user wants to start grading immediately
        start_grading = input(f"\n👉 Start grading session now? (y/n): ").strip().lower()
        if start_grading in ['y', 'yes']:
            print(f"\n🎯 Starting grading session...")
            os.system("python trend_grader.py grade 20")  # Grade up to 20 trends
        
        return True

def main():
    """Main function."""
    try:
        tester = SingleVideoTrendTester()
        
        # Check if API keys are available
        if not Config.YOUTUBE_API_KEY:
            print("❌ YouTube API key not found. Check your environment variables.")
            return 1
        
        if not Config.CLAUDE_API_KEY:
            print("❌ Claude API key not found. Check your environment variables.")
            return 1
        
        # Run test
        search_query = sys.argv[1] if len(sys.argv) > 1 else None
        success = tester.run_test(search_query)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())