"""
YouTube Trends Analysis System Configuration

This file contains all configurable constants, prompts, and settings
for the YouTube trends analysis pipeline.
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv



load_dotenv() 

class Config:
    """Centralized configuration for YouTube trends analysis."""
    
    # =============================================================================
    # API CONFIGURATION
    # =============================================================================
    
    # Claude API Settings
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    CLAUDE_MAX_TOKENS = 1000
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY_ENV")
    
    # YouTube API Settings  
    YOUTUBE_API_SERVICE = "youtube"
    YOUTUBE_API_VERSION = "v3"
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    
    # OpenAI API Settings (for embeddings)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSIONS = 1536
    
    # =============================================================================
    # PROCESSING LIMITS & THRESHOLDS
    # =============================================================================
    
    # Transcript Processing
    TRANSCRIPT_MAX_CHUNK_SIZE = 4000  # characters
    TRANSCRIPT_OVERLAP_SIZE = 200     # characters
    TRANSCRIPT_MIN_SENTENCE_LENGTH = 10  # characters for sentence splitting
    
    # Query Generation
    QUERY_WORD_LIMIT = 8           # maximum words per query
    DEFAULT_NUM_QUERIES = 5         # number of queries to generate
    
    # Video Processing
    DEFAULT_MAX_VIDEOS = 25         # default number of videos to process
    DEFAULT_VIDEO_SEARCH_LIMIT = 10 # default YouTube search limit
    VIDEOS_PER_QUERY = 5           # videos to search per query
    USE_MULTIPLE_QUERIES = True    # whether to use multiple queries or just first one
    
    # Parallel Processing
    MAX_PARALLEL_VIDEOS = 8        # maximum videos to process concurrently
    ENABLE_PARALLEL_PROCESSING = True  # whether to use parallel processing
    PARALLEL_TIMEOUT = 500         # timeout per video processing in seconds
    
    # Scoring System
    TREND_SCORE_MIN = -1.0         # minimum trend score (declining)
    TREND_SCORE_MAX = 1.0          # maximum trend score (rising)
    
        
    # =============================================================================
    # FILE PATHS & DIRECTORIES
    # =============================================================================
    
    # Directory Structure
    RESULTS_BASE_DIR = "results"
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
    DATE_FORMAT = "%Y-%m-%d"
    YOUTUBE_DATE_SUFFIX = "T00:00:00Z"
    
    # File Names
    FILES = {
        "prompt": "prompt.txt",
        "ai_prompt": "ai_prompt.txt", 
        "trend_results": "trend_results.csv",
        "youtube_log": "youtube_log.csv",
        "query_results": "query_results.csv",
        "errors": "errors.txt"
    }
    
    # File Extensions
    EXTENSIONS = {
        "text": ".txt",
        "csv": ".csv"
    }
    
    # =============================================================================
    # DISPLAY & FORMATTING
    # =============================================================================
    
    # Table Display Settings
    TABLE_MAX_WIDTH = 70           # characters for table display
    TABLE_DISPLAY_LIMIT = 20       # default number of entries to show
    INFO_TRUNCATION_LENGTH = 70    # characters for info field truncation
    DESCRIPTION_PREVIEW_LENGTH = 100  # characters for description preview
    DESCRIPTION_TRUNCATION_LENGTH = 200  # characters for CSV description field
    
    # Progress Display
    PROGRESS_SEPARATOR_LENGTH = 50
    PROGRESS_SEPARATOR_CHAR = "="
    TABLE_SEPARATOR_LENGTH = 100
    
    # Display Emojis
    EMOJIS = {
        "rocket": "🚀",
        "folder": "📁", 
        "robot": "🤖",
        "check": "✅",
        "calendar": "📅",
        "search": "🔍",
        "memo": "📝",
        "film": "🎬",
        "cross": "❌",
        "disk": "💾",
        "chart": "📊",
        "fire": "🔥",
        "snow": "❄️",
        "repeat": "🔄",
        "warning": "⚠️",
        "books": "📚",
        "up": "⬆️",
        "down": "⬇️",
        "right": "➡️"
    }
    
    # =============================================================================
    # URL PATTERNS & VALIDATION
    # =============================================================================
    
    # YouTube URL Patterns
    YOUTUBE_DOMAINS = ["www.youtube.com", "youtube.com"]
    YOUTUBE_SHORT_DOMAINS = ["youtu.be"]
    YOUTUBE_WATCH_PATH = "/watch"
    YOUTUBE_EMBED_PATH = "/embed/"
    YOUTUBE_URL_TEMPLATE = "https://www.youtube.com/watch?v={video_id}"
    YOUTUBE_VIDEO_ID_LENGTH = 11
    
    # Sentence Delimiters
    SENTENCE_DELIMITERS = ".!?"
    
    # =============================================================================
    # PROMPT TEMPLATES
    # =============================================================================
    
    # Query Generation Prompt
    QUERY_GENERATION_PROMPT = """
You are an expert at crafting optimized YouTube search queries tailored for market research and trendy content discovery. Your goal is to generate {num_queries} unique queries.

User Query: "{user_query}"

Strategy categories (each should produce at least one query):

1. **Expert & Analyst Reviews** - authoritative channels, expert names, “review”, “analysis”, “opinion”
2. **Educational & Tutorial Content** - how-to, step-by-step, guide, explanation
3. **Trending Influencer Content** - influencers, trending topics, commentary, “viral discussion”

CRITICAL REQUIREMENTS:
- Each query must be **{word_limit} words or fewer. Keep them simple and general
- Take advantage of youtube's inherent search capabilities and do not complicate the queries
- Return **exactly one JSON object, with no extra output

JSON format:
{{
  "queries": [
    "query 1 (≤{word_limit} words)",
    "... up to {num_queries} items"
  ],
  "date": "YYYY-MM-DD or null",
  "reasoning": "brief explanation of how these queries map to expert, tutorial, influencer or review content"
}}
"""

    # Insight Extraction Prompts
    INSIGHT_EXTRACTION_PROMPTS = {
        "early_adopter_products": (
            "List of (product_description, t_t_score) where t_t_score is -1.0 to 1.0: "
            "1.0 = highest level of highly trending/rising, 0.0 = neutral/stable, -1.0 = lowest level of declining/losing momentum. "
            "PRIORITIZE: specific product names, tools, platforms, hardware, services, apps, technologies. "
            "Include both direct mentions and implied products/tools being discussed."
        ),
        
        "emerging_topics": (
            "List of (topic_description, t_t_score) where t_t_score is -1.0 to 1.0: "
            "1.0 = highest level of rapidly emerging/growing, 0.0 = steady state, -1.0 = lowest level of fading/losing relevance. "
            "EMPHASIZE: trends, product categories, innovation areas that drive early adoption. "
            "Connect topics to specific products/tools when mentioned."
        ),
        
        "problem_spaces": (
            "List of (problem_description, t_t_score) where t_t_score is -1.0 to 1.0: "
            "1.0 = highest level of intensifying/urgent problems, 0.0 = persistent issues, -1.0 = lowest level of diminishing/solved problems. "
            "FOCUS ON: problems that early adopter products are addressing, limitations of current tools, "
            "adoption barriers for new trends, and product-specific pain points."
        ),
        
        "behavioral_patterns": (
            "List of (behavior_description, t_t_score) where t_t_score is -1.0 to 1.0: "
            "1.0 = highest level of accelerating behaviors, 0.0 = stable patterns, -1.0 = lowest level of declining/abandoning behaviors. "
            "PRIORITIZE: how people are adopting/using/abandoning specific products and technologies, "
            "workflow changes driven by new trends, user resistance or enthusiasm for new products."
        ),
        
        "educational_demand": (
            "List of (education_demand_description, t_t_score) where t_t_score is -1.0 to 1.0: "
            "1.0 = highest level of high/growing demand, 0.0 = steady demand, -1.0 = lowest level of decreasing/obsolete demand. "
            "EMPHASIZE: learning needs for specific products/tools, skill gaps for new technologies, "
            "training demand for emerging platforms, certification needs for innovative products."
        )
    }
    
    # Progress Messages
    MESSAGES = {
        "pipeline_start": "Starting YouTube Trends Analysis",
        "query_generation": "Generating optimized search queries...",
        "video_search": "Searching for videos using primary query...",
        "video_processing": "Processing videos...",
        "saving_results": "Saving results...",
        "analysis_complete": "Analysis Complete!",
        "pipeline_test": "Testing Full YouTube Trends Pipeline"
    }
    
    # Error Messages
    ERROR_MESSAGES = {
        "empty_query": "User query cannot be empty",
        "no_api_key": "{api_name} API key is required. Set {env_var} environment variable or pass api_key parameter.",
        "no_transcript": "No transcript for: {title}",
        "processing_failed": "Failed processing '{title}': {error}",
        "empty_transcript": "Transcript cannot be empty", 
        "no_results": "No results found for query: {query}",
        "invalid_video_id": "Invalid YouTube video ID: {video_id}",
        "anthropic_required": "anthropic is required for query generation. Install it with: pip install anthropic"
    }
    
    # =============================================================================
    # SEARCH CONFIGURATION
    # =============================================================================
    
    # YouTube Search Parameters
    YOUTUBE_SEARCH_PARAMS = {
        "type": "video",
        "order": "viewCount",  # Options: date, rating, relevance, title, videoCount, viewCount
        "regionCode": None,    # Optional: country code
        "relevanceLanguage": None  # Optional: language code
    }
    
    # Web Frontend Configuration
    WEB_HOST = "127.0.0.1"
    WEB_PORT = 5000
    WEB_DEBUG = True
    FLASK_SECRET_KEY = "youtube-trends-analysis-key"
    
    # =============================================================================
    # VECTOR DATABASE CONFIGURATION
    # =============================================================================
    
    # Vector Database Settings
    VECTOR_DB_TYPE = "chroma"  # Options: chroma, faiss, pinecone
    VECTOR_DB_PATH = "vector_db"  # Local path for Chroma DB
    VECTOR_DB_COLLECTION = "youtube_trends"
    
    # Embedding Configuration
    EMBEDDING_BATCH_SIZE = 100
    EMBEDDING_MAX_RETRIES = 3
    EMBEDDING_RETRY_DELAY = 1.0  # seconds
    
    # Trend Aggregation Settings
    TREND_SIMILARITY_THRESHOLD = 0.85  # For deduplication
    TREND_MIN_SCORE_THRESHOLD = -0.5   # Filter out very negative trends
    TREND_TEXT_MAX_LENGTH = 1000       # Truncate long trend descriptions
    
    # Search and Retrieval
    VECTOR_SEARCH_TOP_K = 20          # Default number of results to return
    VECTOR_SEARCH_SCORE_THRESHOLD = 0.7  # Minimum similarity score for relevance
    
    # Metadata Fields for Trends
    TREND_METADATA_FIELDS = [
        "category",           # early_adopter_products, emerging_topics, etc.
        "trend_score",        # -1.0 to 1.0
        "transcript_date",    # When the trend was discussed
        "video_title",        # Source video title
        "video_id",           # YouTube video ID
        "channel",            # YouTube channel name
        "run_id",             # Analysis run identifier
        "run_timestamp",      # When analysis was performed
        "user_query"          # Original search query
    ]
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    @classmethod
    def get_api_key(cls, api_name: str) -> str:
        """Get API key from config attributes."""
        return getattr(cls, f"{api_name.upper()}_API_KEY")
    
    @classmethod
    def get_formatted_prompt(cls, template_name: str, **kwargs) -> str:
        """Get a formatted prompt template."""
        template = getattr(cls, template_name.upper())
        return template.format(**kwargs)
    
    @classmethod
    def get_file_path(cls, base_dir: str, file_key: str) -> str:
        """Get full file path for a given file key."""
        filename = cls.FILES[file_key]
        return os.path.join(base_dir, filename)
    
    @classmethod
    def get_progress_separator(cls, length: int = None) -> str:
        """Get a progress separator line."""
        length = length or cls.PROGRESS_SEPARATOR_LENGTH
        return cls.PROGRESS_SEPARATOR_CHAR * length
    
    @classmethod
    def get_emoji(cls, key: str) -> str:
        """Get an emoji by key, with fallback to empty string."""
        return cls.EMOJIS.get(key, "")
    
    @classmethod 
    def validate_score(cls, score: float) -> float:
        """Validate and clamp score to valid range."""
        return max(cls.TREND_SCORE_MIN, min(cls.TREND_SCORE_MAX, score))
    
    @classmethod
    def truncate_text(cls, text: str, length: int, suffix: str = "...") -> str:
        """Truncate text to specified length with suffix."""
        if len(text) <= length:
            return text
        return text[:length - len(suffix)] + suffix