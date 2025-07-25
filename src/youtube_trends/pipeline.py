"""Sophisticated end-to-end YouTube trends analysis pipeline."""

import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import time
import os

from .config import Config
from .youtube_query_generation import YouTubeQueryGenerator, QueryGenerationError
from .youtube_search import YouTubeSearchClient, SearchError
from .transcript import YouTubeTranscriptClient, TranscriptError
from .transcript_processing_claude import ClaudeTranscriptProcessor, TranscriptProcessingError

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Complete pipeline execution result."""
    user_query: str
    optimized_search_query: str
    query_reasoning: str
    videos_processed: int
    total_insights: int
    processing_time: float
    insights_df: pd.DataFrame
    youtube_log_df: pd.DataFrame
    results_dir: str
    errors: List[str]


class YouTubeTrendsPipeline:
    """Sophisticated pipeline for end-to-end YouTube trends analysis."""
    
    def __init__(self, youtube_api_key: str = None, claude_api_key: str = None, results_base_dir: str = "results"):
        """
        Initialize the complete pipeline with all components.
        
        Args:
            youtube_api_key: YouTube Data API key
            claude_api_key: Claude API key
            results_base_dir: Base directory for storing results
        """
        self.start_time = None
        self.errors = []
        self.results_base_dir = results_base_dir
        
        # Initialize all components
        try:
            self.query_generator = YouTubeQueryGenerator(api_key=claude_api_key)
            self.search_client = YouTubeSearchClient(api_key=youtube_api_key)
            self.transcript_client = YouTubeTranscriptClient()
            self.processor = ClaudeTranscriptProcessor(api_key=claude_api_key)
            logger.info("Pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            raise
    
    def run_analysis(
        self, 
        user_query: str, 
        max_videos: int = 5,
        show_progress: bool = True
    ) -> PipelineResult:
        """
        Execute the complete analysis pipeline.
        
        Args:
            user_query: User's research query
            max_videos: Maximum number of videos to analyze
            show_progress: Whether to show progress updates
            
        Returns:
            PipelineResult with insights table
        """
        self.start_time = time.time()
        self.errors = []
        
        if show_progress:
            print(f"🚀 Starting YouTube Trends Analysis")
            print(f"Query: '{user_query}'")
            print("=" * 50)
        
        try:
            # Create results directory
            run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_dir = os.path.join(self.results_base_dir, run_timestamp)
            os.makedirs(results_dir, exist_ok=True)
            
            if show_progress:
                print(f"📁 Results directory: {results_dir}")
            
            # Step 1: Generate optimized search queries
            if show_progress:
                print(f"\n🤖 Generating optimized search queries...")
            
            query_result = self.query_generator.generate_search_query(user_query)
            
            if show_progress:
                print(f"   ✅ Generated {len(query_result.queries)} queries:")
                for i, query in enumerate(query_result.queries, 1):
                    print(f"      {i}. {query}")
                if query_result.date:
                    print(f"   📅 Date filter: {query_result.date}")
            
            # Save prompt files
            with open(os.path.join(results_dir, "prompt.txt"), "w", encoding="utf-8") as f:
                f.write(user_query)
            
            with open(os.path.join(results_dir, "ai_prompt.txt"), "w", encoding="utf-8") as f:
                f.write(f"Original User Query: {user_query}\n\n")
                f.write(f"AI Generated Search Queries:\n")
                for i, query in enumerate(query_result.queries, 1):
                    f.write(f"{i}. {query}\n")
                f.write(f"\nDate Filter: {query_result.date or 'None'}\n\n")
                f.write(f"AI Reasoning:\n{query_result.reasoning}")
            
            # Step 2: Search for videos using multiple queries
            if show_progress:
                print(f"\n🔍 Searching for videos using {len(query_result.queries)} queries...")
            
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
                    'description': video.description[:200] + '...' if len(video.description) > 200 else video.description,
                    'thumbnail': video.thumbnail
                })
            
            youtube_log_df = pd.DataFrame(youtube_log_data)
            
            # Step 3: Extract transcripts and process insights
            if show_progress:
                print(f"\n📝 Processing videos...")
            
            all_insights = []
            
            for i, video in enumerate(videos, 1):
                try:
                    if show_progress:
                        print(f"   🎬 Video {i}/{len(videos)}: {video.title[:50]}...")
                    
                    # Extract transcript
                    transcript_text = self.transcript_client.get_transcript(video.url)
                    
                    if not transcript_text:
                        self.errors.append(f"No transcript for: {video.title}")
                        continue
                    
                    # Process insights
                    video_date = video.publish_time[:10] if video.publish_time else datetime.now().strftime("%Y-%m-%d")
                    insights = self.processor.process_transcript(transcript_text, video_date)
                    
                    # Extract all insights into flat list
                    all_categories = [
                        ('early_adopter_products', insights.early_adopter_products),
                        ('emerging_topics', insights.emerging_topics),
                        ('problem_spaces', insights.problem_spaces),
                        ('behavioral_patterns', insights.behavioral_patterns),
                        ('educational_demand', insights.educational_demand)
                    ]
                    
                    for category, category_insights in all_categories:
                        for insight_text, date, score in category_insights:
                            all_insights.append({
                                'date': date,
                                'category': category,
                                'information': insight_text,
                                'score': score
                            })
                    
                    if show_progress:
                        total = sum(len(insights_list) for _, insights_list in all_categories)
                        print(f"      ✅ Extracted {total} insights")
                        
                except Exception as e:
                    self.errors.append(f"Failed processing '{video.title}': {str(e)}")
                    if show_progress:
                        print(f"      ❌ Failed: {e}")
                    continue
            
            # Create DataFrame
            insights_df = pd.DataFrame(all_insights)
            
            if not insights_df.empty:
                # Sort by absolute score (most significant trends first)
                insights_df = insights_df.sort_values('score', key=abs, ascending=False).reset_index(drop=True)
            
            processing_time = time.time() - self.start_time
            
            # Save all files to results directory
            if show_progress:
                print(f"\n💾 Saving results...")
            
            # Save trend results
            trend_results_file = os.path.join(results_dir, "trend_results.csv")
            insights_df.to_csv(trend_results_file, index=False)
            
            # Save YouTube log
            youtube_log_file = Config.get_file_path(results_dir, "youtube_log")
            youtube_log_df.to_csv(youtube_log_file, index=False)
            
            # Save query results table
            query_results_file = Config.get_file_path(results_dir, "query_results")
            query_results_df.to_csv(query_results_file, index=False)
            
            # Save error log if any errors occurred
            if self.errors:
                error_log_file = os.path.join(results_dir, "errors.txt")
                with open(error_log_file, "w", encoding="utf-8") as f:
                    for error in self.errors:
                        f.write(f"{error}\n")
            
            result = PipelineResult(
                user_query=user_query,
                optimized_search_query=f"{len(query_result.queries)} queries used",
                query_reasoning=query_result.reasoning,
                videos_processed=len(videos) - len([e for e in self.errors if "No transcript" in e or "Failed processing" in e]),
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
                
                print(f"\n✅ Analysis Complete!")
                print(f"   Videos processed: {result.videos_processed}")
                print(f"   Total insights: {result.total_insights}")
                print(f"   Processing time: {result.processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            self.errors.append(f"Pipeline failure: {str(e)}")
            raise
    
    def display_table(self, result: PipelineResult, limit: int = 20):
        """Display the insights table."""
        if result.insights_df.empty:
            print("No insights found.")
            return
        
        print(f"\n📊 INSIGHTS TABLE (Top {min(limit, len(result.insights_df))} entries)")
        print("=" * 100)
        
        # Display with nice formatting
        df_display = result.insights_df.head(limit).copy()
        df_display['information'] = df_display['information'].str[:70] + '...'
        df_display['score'] = df_display['score'].round(2)
        
        print(df_display.to_string(index=True, max_colwidth=70))
        
        if len(result.insights_df) > limit:
            print(f"\n... and {len(result.insights_df) - limit} more entries")
        
        print("=" * 100)
    
    def get_results_summary(self, result: PipelineResult) -> Dict:
        """Get a summary of the results."""
        return {
            'results_directory': result.results_dir,
            'user_query': result.user_query,
            'ai_generated_query': result.optimized_search_query,
            'videos_found': len(result.youtube_log_df),
            'videos_processed': result.videos_processed,
            'total_insights': result.total_insights,
            'processing_time': f"{result.processing_time:.2f}s",
            'error_count': len(result.errors),
            'files_created': [
                'trend_results.csv',
                'youtube_log.csv',
                'query_results.csv',
                'prompt.txt',
                'ai_prompt.txt'
            ] + (['errors.txt'] if result.errors else [])
        }