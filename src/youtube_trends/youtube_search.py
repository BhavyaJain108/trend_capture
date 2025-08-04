"""YouTube search module for retrieving videos based on natural language queries."""

import logging
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class VideoResult:
    """Data class for YouTube video search results."""
    title: str
    video_id: str
    url: str
    channel: str
    duration: str
    views: str
    publish_time: str
    description: str
    thumbnail: str


class SearchError(Exception):
    """Base exception for search-related errors."""
    pass


class YouTubeSearchClient:
    """Client for searching YouTube videos using natural language queries."""
    
    def __init__(self, api_key: str = None):
        """Initialize the search client with YouTube Data API v3."""
        try:
            from googleapiclient.discovery import build
            self._build = build
        except ImportError:
            raise SearchError(
                "google-api-python-client is required for YouTube API access. "
                "Install it with: pip install google-api-python-client"
            )
        
        self.api_key = api_key or Config.get_api_key('youtube')
        if not self.api_key:
            raise SearchError(
                Config.ERROR_MESSAGES["no_api_key"].format(
                    api_name="YouTube", env_var="YOUTUBE_API_KEY"
                )
            )
    
    def search_videos(self, query: str, limit: int = Config.DEFAULT_VIDEO_SEARCH_LIMIT, published_after: str = None) -> List[VideoResult]:
        """
        Search for YouTube videos using natural language query.
        
        Args:
            query: Natural language search query
            limit: Maximum number of videos to return (default: 10)
            published_after: Filter videos published after this date (ISO 8601 format: 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ')
            
        Returns:
            List of VideoResult objects containing video information (sorted by popularity)
            
        Raises:
            SearchError: If search fails or returns no results
        """
        if not query.strip():
            raise SearchError("Search query cannot be empty")
            
        if limit <= 0:
            raise SearchError("Limit must be greater than 0")
            
        logger.info(f"Searching for videos with query: '{query}' (limit: {limit})")
        
        try:
            # Build YouTube API client
            youtube = self._build(
                Config.YOUTUBE_API_SERVICE, 
                Config.YOUTUBE_API_VERSION, 
                developerKey=self.api_key
            )
            
            # Build search parameters
            search_params = {
                'q': query,
                'part': 'id,snippet',
                'maxResults': limit,
                'type': Config.YOUTUBE_SEARCH_PARAMS['type'],
                'order': Config.YOUTUBE_SEARCH_PARAMS['order']  # Sort by popularity (view count)
            }
            
            # Add date filter if provided
            if published_after:
                # Convert various date formats to ISO 8601
                if len(published_after) == 4:  # YYYY format
                    published_after += '-01-01T00:00:00Z'
                elif len(published_after) == 7:  # YYYY-MM format  
                    published_after += '-01T00:00:00Z'
                elif len(published_after) == 10:  # YYYY-MM-DD format
                    published_after += Config.YOUTUBE_DATE_SUFFIX
                elif not published_after.endswith('Z'):  # Already has time but no Z
                    published_after += 'Z'
                search_params['publishedAfter'] = published_after
            
            # Search for videos
            search_response = youtube.search().list(**search_params).execute()
            
            if not search_response.get('items'):
                raise SearchError(f"No results found for query: {query}")
            
            # Get video IDs for additional details
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get video statistics and details
            videos_response = youtube.videos().list(
                part='statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            # Combine search results with video details
            video_results = []
            for i, item in enumerate(search_response['items']):
                try:
                    video_stats = videos_response['items'][i] if i < len(videos_response['items']) else {}
                    video_result = self._parse_api_data(item, video_stats)
                    video_results.append(video_result)
                except Exception as e:
                    logger.warning(f"Failed to parse video data: {e}")
                    continue
                    
            if not video_results:
                raise SearchError(f"No valid video results found for query: {query}")
                
            logger.info(f"Found {len(video_results)} videos for query: '{query}'")
            return video_results
            
        except Exception as e:
            if isinstance(e, SearchError):
                raise
            logger.error(f"Unexpected error during search: {e}")
            raise SearchError(f"Failed to search videos: {str(e)}")
    
    def _parse_api_data(self, search_item: Dict, video_stats: Dict) -> VideoResult:
        """
        Parse raw video data from YouTube API into VideoResult object.
        
        Args:
            search_item: Search result item from YouTube API
            video_stats: Video statistics from YouTube API
            
        Returns:
            VideoResult object with parsed video information
        """
        try:
            snippet = search_item.get('snippet', {})
            video_id = search_item.get('id', {}).get('videoId', '')
            
            # Parse duration from ISO 8601 format
            duration = video_stats.get('contentDetails', {}).get('duration', 'Unknown')
            if duration != 'Unknown':
                duration = self._parse_duration(duration)
            
            # Format view count
            view_count = video_stats.get('statistics', {}).get('viewCount', '0')
            views = f"{int(view_count):,} views" if view_count.isdigit() else "Unknown views"
            
            return VideoResult(
                title=snippet.get('title', 'Unknown Title'),
                video_id=video_id,
                url=f"https://www.youtube.com/watch?v={video_id}",
                channel=snippet.get('channelTitle', 'Unknown Channel'),
                duration=duration,
                views=views,
                publish_time=snippet.get('publishedAt', 'Unknown time'),
                description=snippet.get('description', ''),
                thumbnail=snippet.get('thumbnails', {}).get('high', {}).get('url', '')
            )
        except Exception as e:
            logger.error(f"Error parsing video data: {e}")
            raise SearchError(f"Failed to parse video data: {str(e)}")
    
    def _parse_duration(self, duration: str) -> str:
        """
        Parse ISO 8601 duration format (PT4M13S) to readable format.
        
        Args:
            duration: ISO 8601 duration string
            
        Returns:
            Human readable duration string
        """
        import re
        
        # Parse PT4M13S format
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return duration
            
        hours, minutes, seconds = match.groups()
        
        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds:
            parts.append(f"{seconds}s")
            
        return " ".join(parts) if parts else "0s"
    
    def get_video_urls(self, query: str, limit: int = 10, published_after: str = None) -> List[str]:
        """
        Get just the URLs of top videos for a query.
        
        Args:
            query: Natural language search query
            limit: Maximum number of URLs to return
            published_after: Filter videos published after this date
            
        Returns:
            List of YouTube video URLs (sorted by popularity)
        """
        videos = self.search_videos(query, limit, published_after)
        return [video.url for video in videos]
    
    def search_and_display(self, query: str, limit: int = 10, published_after: str = None) -> None:
        """
        Search for videos and display results in a formatted way.
        
        Args:
            query: Natural language search query
            limit: Maximum number of videos to display
            published_after: Filter videos published after this date
        """
        try:
            videos = self.search_videos(query, limit, published_after)
            
            print(f"\n🔍 Search Results for: '{query}' (Top {len(videos)} videos)\n")
            print("=" * 80)
            
            for i, video in enumerate(videos, 1):
                print(f"\n{i}. {video.title}")
                print(f"   Channel: {video.channel}")
                print(f"   Duration: {video.duration}")
                print(f"   Views: {video.views}")
                print(f"   Published: {video.publish_time}")
                print(f"   URL: {video.url}")
                if video.description:
                    desc_preview = video.description[:100] + "..." if len(video.description) > 100 else video.description
                    print(f"   Description: {desc_preview}")
                print("-" * 80)
                
        except SearchError as e:
            print(f"❌ Search failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")