"""
Parallel YouTube Trends Analysis Pipeline

This pipeline is identical to the regular pipeline but uses parallel processing
for transcript extraction and processing to handle larger video volumes efficiently.
"""

import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .config import Config
from .youtube_query_generation import YouTubeQueryGenerator, QueryGenerationError
from .youtube_search import YouTubeSearchClient, SearchError
from .transcript import YouTubeTranscriptClient, TranscriptError
from .transcript_processing_claude import ClaudeTranscriptProcessor, TranscriptProcessingError
from .pipeline import PipelineResult  # Reuse the same result structure

logger = logging.getLogger(__name__)

class ParallelYouTubeTrendsPipeline:
    """Parallel version of the YouTube trends analysis pipeline with concurrent video processing."""
    
    def __init__(self, results_base_dir: str = "results"):
        """
        Initialize the parallel pipeline with all components.
        
        Args:
            youtube_api_key: YouTube Data API key
            claude_api_key: Claude API key
            results_base_dir: Base directory for storing results
        """
        self.start_time = None
        self.errors = []
        self.results_base_dir = results_base_dir
        self.lock = threading.Lock()  # For thread-safe error collection
        
        # Initialize all components
        try:
            self.query_generator = YouTubeQueryGenerator(api_key=Config.CLAUDE_API_KEY)
            self.search_client = YouTubeSearchClient(api_key=Config.YOUTUBE_API_KEY)
            # Note: transcript_client and processor will be created per thread
            logger.info("Parallel pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Parallel pipeline initialization failed: {e}")
            raise
    
    def _extract_transcript(self, video, video_index: int, total_videos: int, show_progress: bool = True) -> Dict:
        """
        Extract transcript from a single video (runs in parallel).
        
        Args:
            video: VideoResult object
            video_index: Index of this video (1-based)
            total_videos: Total number of videos being processed
            show_progress: Whether to show progress messages
            
        Returns:
            Dict with transcript data or error information
        """
        thread_id = threading.current_thread().ident
        
        try:
            # Create thread-local transcript client
            transcript_client = YouTubeTranscriptClient()
            
            if show_progress:
                print(f"   📝 Video {video_index}/{total_videos} [Thread-{thread_id}]: {video.title[:50]}...")
            
            # Extract transcript
            transcript_text = transcript_client.get_transcript(video.url)
            
            if not transcript_text:
                with self.lock:
                    self.errors.append(f"No transcript for: {video.title}")
                return {"error": "no_transcript", "video": video}
            
            # Prepare video date
            video_date = video.publish_time[:10] if video.publish_time else datetime.now().strftime(Config.DATE_FORMAT)
            
            if show_progress:
                print(f"      ✅ [Thread-{thread_id}] Transcript extracted ({len(transcript_text)} chars)")
            
            return {
                "success": True,
                "video": video,
                "transcript": transcript_text,
                "video_date": video_date
            }
            
        except Exception as e:
            error_msg = f"Failed extracting transcript from '{video.title}': {str(e)}"
            with self.lock:
                self.errors.append(error_msg)
            
            if show_progress:
                print(f"      ❌ [Thread-{thread_id}] Failed: {e}")
            
            return {"error": "extraction_failed", "video": video, "message": str(e)}

    def _process_single_video(self, video, video_index: int, total_videos: int, show_progress: bool = True) -> Dict:
        """
        Process a single video (transcript extraction + insight processing).
        This function runs in a separate thread.
        
        Args:
            video: VideoResult object
            video_index: Index of this video (1-based)
            total_videos: Total number of videos being processed
            show_progress: Whether to show progress messages
            
        Returns:
            Dict with insights data or error information
        """
        thread_id = threading.current_thread().ident
        
        try:
            # Create thread-local instances (API clients are not thread-safe)
            transcript_client = YouTubeTranscriptClient()
            # Create thread-local processor instance for parallel processing
            processor = ClaudeTranscriptProcessor()
            
            if show_progress:
                print(f"   🎬 Video {video_index}/{total_videos} [Thread-{thread_id}]: {video.title[:50]}...")
            
            # Extract transcript
            transcript_text = transcript_client.get_transcript(video.url)
            
            if not transcript_text:
                with self.lock:
                    self.errors.append(f"No transcript for: {video.title}")
                return {"error": "no_transcript", "video": video}
            
            # Process insights
            video_date = video.publish_time[:10] if video.publish_time else datetime.now().strftime(Config.DATE_FORMAT)
            insights = processor.process_transcript(transcript_text, video_date)
            
            # Extract all insights into flat list
            all_categories = [
                ('early_adopter_products', insights.early_adopter_products),
                ('emerging_topics', insights.emerging_topics),
                ('problem_spaces', insights.problem_spaces),
                ('behavioral_patterns', insights.behavioral_patterns),
                ('educational_demand', insights.educational_demand)
            ]
            
            video_insights = []
            for category, category_insights in all_categories:
                for insight_text, date, score in category_insights:
                    video_insights.append({
                        'date': date,
                        'category': category,
                        'information': insight_text,
                        'score': score
                    })
            
            if show_progress:
                total = sum(len(insights_list) for _, insights_list in all_categories)
                print(f"      ✅ [Thread-{thread_id}] Extracted {total} insights")
            
            return {
                "success": True,
                "video": video,
                "insights": video_insights,
                "insights_count": len(video_insights)
            }
            
        except Exception as e:
            error_msg = f"Failed processing '{video.title}': {str(e)}"
            with self.lock:
                self.errors.append(error_msg)
            
            if show_progress:
                print(f"      ❌ [Thread-{thread_id}] Failed: {e}")
            
            return {"error": "processing_failed", "video": video, "message": str(e)}
    
    def run_analysis(
        self, 
        user_query: str, 
        max_videos: int = Config.DEFAULT_MAX_VIDEOS,
        show_progress: bool = True,
        max_workers: int = Config.MAX_PARALLEL_VIDEOS
    ) -> PipelineResult:
        """
        Execute the complete analysis pipeline with parallel video processing.
        
        Args:
            user_query: User's research query
            max_videos: Maximum number of videos to analyze
            show_progress: Whether to show progress updates
            max_workers: Maximum number of parallel threads for video processing
            
        Returns:
            PipelineResult with insights table
        """
        self.start_time = time.time()
        self.errors = []
        
        if show_progress:
            print(f"🚀 Starting Parallel YouTube Trends Analysis")
            print(f"Query: '{user_query}'")
            print(f"Parallel workers: {max_workers}")
            print("=" * 50)
        
        try:
            # Create results directory
            run_timestamp = datetime.now().strftime(Config.TIMESTAMP_FORMAT)
            results_dir = os.path.join(self.results_base_dir, run_timestamp)
            os.makedirs(results_dir, exist_ok=True)
            
            if show_progress:
                print(f"📁 Results directory: {results_dir}")
            
            # Step 1: Generate optimized search queries (same as regular pipeline)
            if show_progress:
                print(f"\\n🤖 Generating optimized search queries...")
            
            query_result = self.query_generator.generate_search_query(user_query)
            
            if show_progress:
                print(f"   ✅ Generated {len(query_result.queries)} queries:")
                for i, query in enumerate(query_result.queries, 1):
                    print(f"      {i}. {query}")
                if query_result.date:
                    print(f"   📅 Date filter: {query_result.date}")
            
            # Save prompt files
            with open(Config.get_file_path(results_dir, "prompt"), "w", encoding="utf-8") as f:
                f.write(user_query)
            
            with open(Config.get_file_path(results_dir, "ai_prompt"), "w", encoding="utf-8") as f:
                f.write(f"Original User Query: {user_query}\\n\\n")
                f.write(f"AI Generated Search Queries:\\n")
                for i, query in enumerate(query_result.queries, 1):
                    f.write(f"{i}. {query}\\n")
                f.write(f"\\nDate Filter: {query_result.date or 'None'}\\n\\n")
                f.write(f"AI Reasoning:\\n{query_result.reasoning}")
            
            # Step 2: Search for videos using multiple queries (same as regular pipeline)
            if show_progress:
                print(f"\\n🔍 Searching for videos using {len(query_result.queries)} queries...")
            
            all_videos = []
            query_results_data = []
            
            for i, query in enumerate(query_result.queries, 1):
                try:
                    if show_progress:
                        print(f"   Query {i}: {query[:50]}...")
                    
                    query_videos = self.search_client.search_videos(
                        query,
                        limit=Config.VIDEOS_PER_QUERY,
                        published_after=query_result.date
                    )
                    
                    query_results_data.append({
                        'query_number': i,
                        'query_text': query,
                        'videos_found': len(query_videos),
                        'date_filter': query_result.date,
                        'status': 'success'
                    })
                    
                    all_videos.extend(query_videos)
                    
                    if show_progress:
                        print(f"      ✅ {len(query_videos)} videos found")
                    
                except Exception as e:
                    self.errors.append(f"Query {i} failed: {str(e)}")
                    query_results_data.append({
                        'query_number': i,
                        'query_text': query,
                        'videos_found': 0,
                        'date_filter': query_result.date,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
                    if show_progress:
                        print(f"      ❌ Failed: {e}")
            
            # Deduplicate videos by URL before limiting
            unique_videos = []
            seen_urls = set()
            
            for video in all_videos:
                if video.url not in seen_urls:
                    unique_videos.append(video)
                    seen_urls.add(video.url)
            
            videos = unique_videos[:max_videos]
            
            if show_progress:
                total_found = sum(r['videos_found'] for r in query_results_data)
                duplicates_removed = len(all_videos) - len(unique_videos)
                print(f"   ✅ Total: {total_found} videos found, {duplicates_removed} duplicates removed")
                print(f"   📹 Processing {len(videos)} unique videos (limited to {max_videos})")
            
            # Create query results DataFrame
            query_results_df = pd.DataFrame(query_results_data)
            
            # Step 3: Extract transcripts in parallel, process insights sequentially (DSPy limitation)
            if show_progress:
                print(f"\\n📝 Processing {len(videos)} videos (parallel transcript extraction)...")
            
            all_insights = []
            successful_videos = 0
            
            # Parallel processing enabled with DSPy-free Claude processor
            all_insights = []
            successful_videos = 0
            
            # Step 3: Process videos in parallel (transcript extraction AND insight processing)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_video = {
                    executor.submit(self._process_single_video, video, i, len(videos), show_progress): video 
                    for i, video in enumerate(videos, 1)
                }
                
                for future in as_completed(future_to_video, timeout=Config.PARALLEL_TIMEOUT):
                    result = future.result()
                    if result.get("success"):
                        all_insights.extend(result["insights"])
                        successful_videos += 1
            
            # Create YouTube log DataFrame  
            youtube_log_data = []
            for video in videos:
                youtube_log_data.append({
                    'title': video.title,
                    'url': video.url,
                    'channel': video.channel,
                    'duration': video.duration,
                    'views': video.views,
                    'publish_time': video.publish_time,
                    'description': Config.truncate_text(video.description, Config.DESCRIPTION_TRUNCATION_LENGTH),
                    'thumbnail': video.thumbnail
                })
            
            youtube_log_df = pd.DataFrame(youtube_log_data)
            
            # Create DataFrame
            insights_df = pd.DataFrame(all_insights)
            
            if not insights_df.empty:
                # Sort by absolute score (most significant trends first)
                insights_df = insights_df.sort_values('score', key=abs, ascending=False).reset_index(drop=True)
            
            processing_time = time.time() - self.start_time
            
            # Save all files to results directory
            if show_progress:
                print(f"\\n💾 Saving results...")
            
            # Save trend results
            trend_results_file = Config.get_file_path(results_dir, "trend_results")
            insights_df.to_csv(trend_results_file, index=False)
            
            # Save YouTube log
            youtube_log_file = Config.get_file_path(results_dir, "youtube_log")
            youtube_log_df.to_csv(youtube_log_file, index=False)
            
            # Save query results table
            query_results_file = Config.get_file_path(results_dir, "query_results")
            query_results_df.to_csv(query_results_file, index=False)
            
            # Save error log if any errors occurred
            if self.errors:
                error_log_file = Config.get_file_path(results_dir, "errors")
                with open(error_log_file, "w", encoding="utf-8") as f:
                    for error in self.errors:
                        f.write(f"{error}\\n")
            
            result = PipelineResult(
                user_query=user_query,
                optimized_search_query=f"{len(query_result.queries)} queries used (parallel)",
                query_reasoning=query_result.reasoning,
                videos_processed=successful_videos,
                total_insights=len(insights_df),
                processing_time=processing_time,
                insights_df=insights_df,
                youtube_log_df=youtube_log_df,
                results_dir=results_dir,
                errors=self.errors.copy()
            )
            
            if show_progress:
                print(f"   ✅ Saved to: {results_dir}/")
                print(f"      - trend_results.csv ({len(insights_df)} insights)")
                print(f"      - youtube_log.csv ({len(youtube_log_df)} videos)")
                print(f"      - query_results.csv ({len(query_results_df)} queries)")
                print(f"      - prompt.txt")
                print(f"      - ai_prompt.txt")
                if self.errors:
                    print(f"      - errors.txt ({len(self.errors)} errors)")
                
                print(f"\\n✅ Parallel Analysis Complete!")
                print(f"   Videos processed: {result.videos_processed} (using {max_workers} parallel threads)")
                print(f"   Total insights: {result.total_insights}")
                print(f"   Processing time: {result.processing_time:.2f}s")
                
                # Show performance comparison hint
                sequential_estimate = result.processing_time * max_workers
                print(f"   📊 Estimated sequential time: ~{sequential_estimate:.1f}s (speedup: {sequential_estimate/result.processing_time:.1f}x)")
            
            return result
            
        except Exception as e:
            logger.error(f"Parallel pipeline execution failed: {e}")
            self.errors.append(f"Pipeline failure: {str(e)}")
            raise