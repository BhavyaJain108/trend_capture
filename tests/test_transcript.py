"""Tests for the transcript module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound

from src.youtube_trends.transcript import (
    YouTubeTranscriptClient,
    TranscriptError,
    VideoNotFoundError,
    TranscriptNotAvailableError
)


class TestYouTubeTranscriptClient:
    """Test cases for YouTubeTranscriptClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = YouTubeTranscriptClient()
    
    def test_init(self):
        """Test client initialization."""
        client = YouTubeTranscriptClient()
        assert client is not None
    
    def test_extract_video_id_from_watch_url(self):
        """Test extracting video ID from standard YouTube watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.client.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_embed_url(self):
        """Test extracting video ID from YouTube embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        result = self.client.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_embed_url_with_params(self):
        """Test extracting video ID from YouTube embed URL with parameters."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ?start=10"
        result = self.client.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_short_url(self):
        """Test extracting video ID from shortened youtu.be URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = self.client.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_raw_id(self):
        """Test extracting video ID when input is already a video ID."""
        video_id = "dQw4w9WgXcQ"
        result = self.client.extract_video_id(video_id)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_empty_string(self):
        """Test extracting video ID from empty string."""
        result = self.client.extract_video_id("")
        assert result is None
    
    def test_extract_video_id_none(self):
        """Test extracting video ID from None."""
        result = self.client.extract_video_id(None)
        assert result is None
    
    def test_extract_video_id_invalid_url(self):
        """Test extracting video ID from invalid URL."""
        url = "https://example.com/invalid"
        result = self.client.extract_video_id(url)
        assert result is None
    
    def test_extract_video_id_malformed_youtube_url(self):
        """Test extracting video ID from malformed YouTube URL."""
        url = "https://www.youtube.com/invalid"
        result = self.client.extract_video_id(url)
        assert result is None
    
    def test_extract_video_id_invalid_id_length(self):
        """Test extracting video ID with invalid length."""
        invalid_id = "shortid"
        result = self.client.extract_video_id(invalid_id)
        assert result is None
    
    @patch('src.youtube_trends.transcript.YouTubeTranscriptApi.get_transcript')
    def test_get_transcript_success(self, mock_get_transcript):
        """Test successful transcript retrieval."""
        mock_transcript = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.5},
            {'text': 'This is a test', 'start': 2.5, 'duration': 3.0}
        ]
        mock_get_transcript.return_value = mock_transcript
        
        result = self.client.get_transcript("dQw4w9WgXcQ")
        
        assert result == mock_transcript
        mock_get_transcript.assert_called_once_with("dQw4w9WgXcQ")
    
    @patch('src.youtube_trends.transcript.YouTubeTranscriptApi.get_transcript')
    def test_get_transcript_with_languages(self, mock_get_transcript):
        """Test transcript retrieval with specific languages."""
        mock_transcript = [{'text': 'Hola mundo', 'start': 0.0, 'duration': 2.5}]
        mock_get_transcript.return_value = mock_transcript
        
        result = self.client.get_transcript("dQw4w9WgXcQ", languages=['es', 'en'])
        
        assert result == mock_transcript
        mock_get_transcript.assert_called_once_with("dQw4w9WgXcQ", languages=['es', 'en'])
    
    def test_get_transcript_invalid_url(self):
        """Test transcript retrieval with invalid URL."""
        with pytest.raises(VideoNotFoundError, match="Invalid YouTube URL or video ID"):
            self.client.get_transcript("invalid_url")
    
    @patch('src.youtube_trends.transcript.YouTubeTranscriptApi.get_transcript')
    def test_get_transcript_disabled(self, mock_get_transcript):
        """Test transcript retrieval when transcripts are disabled."""
        mock_get_transcript.side_effect = TranscriptsDisabled("video_id")
        
        with pytest.raises(TranscriptNotAvailableError, match="Transcripts are disabled"):
            self.client.get_transcript("dQw4w9WgXcQ")
    
    @patch('src.youtube_trends.transcript.YouTubeTranscriptApi.get_transcript')
    @patch.object(YouTubeTranscriptClient, '_get_available_languages_safe')
    def test_get_transcript_not_found_with_available_languages(self, mock_get_languages, mock_get_transcript):
        """Test transcript retrieval when not found but other languages available."""
        mock_get_transcript.side_effect = NoTranscriptFound("video_id", ["en"], [])
        mock_get_languages.return_value = ['es', 'fr']
        
        with pytest.raises(TranscriptNotAvailableError, match="Available languages: es, fr"):
            self.client.get_transcript("dQw4w9WgXcQ")
    
    @patch('src.youtube_trends.transcript.YouTubeTranscriptApi.get_transcript')
    @patch.object(YouTubeTranscriptClient, '_get_available_languages_safe')
    def test_get_transcript_not_found_no_available_languages(self, mock_get_languages, mock_get_transcript):
        """Test transcript retrieval when not found and no languages available."""
        mock_get_transcript.side_effect = NoTranscriptFound("video_id", ["en"], [])
        mock_get_languages.return_value = []
        
        with pytest.raises(TranscriptNotAvailableError, match="No transcripts available"):
            self.client.get_transcript("dQw4w9WgXcQ")
    
    @patch('src.youtube_trends.transcript.YouTubeTranscriptApi.get_transcript')
    def test_get_transcript_unexpected_error(self, mock_get_transcript):
        """Test transcript retrieval with unexpected error."""
        mock_get_transcript.side_effect = Exception("Unexpected error")
        
        with pytest.raises(TranscriptError, match="Failed to retrieve transcript"):
            self.client.get_transcript("dQw4w9WgXcQ")
    
    @patch('src.youtube_trends.transcript.YouTubeTranscriptApi.list_transcripts')
    def test_get_available_languages_success(self, mock_list_transcripts):
        """Test successful retrieval of available languages."""
        mock_transcript1 = Mock()
        mock_transcript1.language_code = 'en'
        mock_transcript2 = Mock()
        mock_transcript2.language_code = 'es'
        
        mock_list_transcripts.return_value = [mock_transcript1, mock_transcript2]
        
        result = self.client.get_available_languages("dQw4w9WgXcQ")
        
        assert result == ['en', 'es']
        mock_list_transcripts.assert_called_once_with("dQw4w9WgXcQ")
    
    def test_get_available_languages_invalid_url(self):
        """Test getting available languages with invalid URL."""
        with pytest.raises(VideoNotFoundError, match="Invalid YouTube URL or video ID"):
            self.client.get_available_languages("invalid_url")
    
    @patch('src.youtube_trends.transcript.YouTubeTranscriptApi.list_transcripts')
    def test_get_available_languages_disabled(self, mock_list_transcripts):
        """Test getting available languages when transcripts are disabled."""
        mock_list_transcripts.side_effect = TranscriptsDisabled("video_id")
        
        with pytest.raises(TranscriptNotAvailableError, match="Transcripts are disabled"):
            self.client.get_available_languages("dQw4w9WgXcQ")
    
    @patch('src.youtube_trends.transcript.YouTubeTranscriptApi.list_transcripts')
    def test_get_available_languages_not_found(self, mock_list_transcripts):
        """Test getting available languages when no transcripts found."""
        mock_list_transcripts.side_effect = NoTranscriptFound("video_id", [], [])
        
        with pytest.raises(TranscriptNotAvailableError, match="No transcripts available"):
            self.client.get_available_languages("dQw4w9WgXcQ")
    
    @patch('src.youtube_trends.transcript.YouTubeTranscriptApi.list_transcripts')
    def test_get_available_languages_unexpected_error(self, mock_list_transcripts):
        """Test getting available languages with unexpected error."""
        mock_list_transcripts.side_effect = Exception("Unexpected error")
        
        with pytest.raises(TranscriptError, match="Failed to get available languages"):
            self.client.get_available_languages("dQw4w9WgXcQ")
    
    @patch.object(YouTubeTranscriptClient, 'get_available_languages')
    def test_get_available_languages_safe_success(self, mock_get_languages):
        """Test safe language retrieval with success."""
        mock_get_languages.return_value = ['en', 'es']
        
        result = self.client._get_available_languages_safe("dQw4w9WgXcQ")
        
        assert result == ['en', 'es']
    
    @patch.object(YouTubeTranscriptClient, 'get_available_languages')
    def test_get_available_languages_safe_exception(self, mock_get_languages):
        """Test safe language retrieval with exception."""
        mock_get_languages.side_effect = Exception("Any error")
        
        result = self.client._get_available_languages_safe("dQw4w9WgXcQ")
        
        assert result == []


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_transcript_error(self):
        """Test TranscriptError exception."""
        error = TranscriptError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_video_not_found_error(self):
        """Test VideoNotFoundError exception."""
        error = VideoNotFoundError("Video not found")
        assert str(error) == "Video not found"
        assert isinstance(error, TranscriptError)
        assert isinstance(error, Exception)
    
    def test_transcript_not_available_error(self):
        """Test TranscriptNotAvailableError exception."""
        error = TranscriptNotAvailableError("Transcript not available")
        assert str(error) == "Transcript not available"
        assert isinstance(error, TranscriptError)
        assert isinstance(error, Exception)