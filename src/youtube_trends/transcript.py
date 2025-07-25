"""YouTube transcript retrieval module."""

import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

from .config import Config

logger = logging.getLogger(__name__)


class TranscriptError(Exception):
    """Base exception for transcript-related errors."""
    pass


class VideoNotFoundError(TranscriptError):
    """Raised when a YouTube video cannot be found."""
    pass


class TranscriptNotAvailableError(TranscriptError):
    """Raised when transcript is not available for a video."""
    pass


class YouTubeTranscriptClient:
    """Client for retrieving YouTube video transcripts."""
    
    def __init__(self):
        """Initialize the transcript client."""
        pass
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.
        
        Args:
            url: YouTube URL or video ID
            
        Returns:
            Video ID if valid, None otherwise
        """
        if not url:
            return None
            
        # If it's already a video ID (Config.YOUTUBE_VIDEO_ID_LENGTH characters, alphanumeric)
        if len(url) == Config.YOUTUBE_VIDEO_ID_LENGTH and url.isalnum():
            return url
            
        try:
            parsed_url = urlparse(url)
            
            # Standard YouTube URLs
            if parsed_url.hostname in Config.YOUTUBE_DOMAINS:
                if parsed_url.path == Config.YOUTUBE_WATCH_PATH:
                    return parse_qs(parsed_url.query).get('v', [None])[0]
                elif parsed_url.path.startswith(Config.YOUTUBE_EMBED_PATH):
                    return parsed_url.path.split(Config.YOUTUBE_EMBED_PATH)[1].split('?')[0]
                    
            # Shortened YouTube URLs
            elif parsed_url.hostname in Config.YOUTUBE_SHORT_DOMAINS:
                return parsed_url.path.lstrip('/')
                
        except Exception as e:
            logger.warning(f"Failed to parse URL {url}: {e}")
            
        return None
    
    def get_transcript(self, video_url: str, languages: Optional[List[str]] = None) -> str:
        """
        Retrieve transcript for a YouTube video.
        
        Args:
            video_url: YouTube video URL or ID
            languages: List of preferred language codes (e.g., ['en', 'es'])
            
        Returns:
            Combined transcript text as a single string
            
        Raises:
            VideoNotFoundError: If video cannot be found
            TranscriptNotAvailableError: If transcript is not available
            TranscriptError: For other transcript-related errors
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise VideoNotFoundError(f"Invalid YouTube URL or video ID: {video_url}")
            
        logger.info(f"Retrieving transcript for video ID: {video_id}")
        
        try:
            api = YouTubeTranscriptApi()
            if languages:
                transcript = api.fetch(video_id, languages=languages)
            else:
                transcript = api.fetch(video_id)
            transcript_list = [snippet.text for snippet in transcript]
            combined_transcript = " ".join(transcript_list)
                
            logger.info(f"Successfully retrieved transcript with {len(transcript_list)} entries")
            return combined_transcript
            
        except TranscriptsDisabled:
            raise TranscriptNotAvailableError(f"Transcripts are disabled for video: {video_id}")
        except NoTranscriptFound:
            available_langs = self._get_available_languages_safe(video_id)
            if available_langs:
                raise TranscriptNotAvailableError(
                    f"No transcript found for video: {video_id} in requested languages. "
                    f"Available languages: {', '.join(available_langs)}"
                )
            else:
                raise TranscriptNotAvailableError(f"No transcripts available for video: {video_id}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving transcript for {video_id}: {e}")
            raise TranscriptError(f"Failed to retrieve transcript: {str(e)}")
    
    def get_available_languages(self, video_url: str) -> List[str]:
        """
        Get list of available transcript languages for a video.
        
        Args:
            video_url: YouTube video URL or ID
            
        Returns:
            List of available language codes
            
        Raises:
            VideoNotFoundError: If video cannot be found
            TranscriptError: For other transcript-related errors
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise VideoNotFoundError(f"Invalid YouTube URL or video ID: {video_url}")
            
        logger.info(f"Getting available languages for video ID: {video_id}")
        
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            languages = []
            
            for transcript in transcript_list:
                languages.append(transcript.language_code)
                
            logger.info(f"Found {len(languages)} available languages: {languages}")
            return languages
            
        except TranscriptsDisabled:
            raise TranscriptNotAvailableError(f"Transcripts are disabled for video: {video_id}")
        except NoTranscriptFound:
            raise TranscriptNotAvailableError(f"No transcripts available for video: {video_id}")
        except Exception as e:
            logger.error(f"Unexpected error getting languages for {video_id}: {e}")
            raise TranscriptError(f"Failed to get available languages: {str(e)}")
    
    def _get_available_languages_safe(self, video_id: str) -> List[str]:
        """
        Safely get available languages without raising exceptions.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of available language codes, empty if none found
        """
        try:
            return self.get_available_languages(video_id)
        except Exception:
            return []