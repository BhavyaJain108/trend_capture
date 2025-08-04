"""YouTube query generation module using Claude API for intelligent search query optimization."""

import logging
import os
from typing import Dict, Optional
from dataclasses import dataclass
import json

from .config import Config

# Import all required configuration values at the top for clarity
DEFAULT_NUM_QUERIES = Config.DEFAULT_NUM_QUERIES
QUERY_WORD_LIMIT = Config.QUERY_WORD_LIMIT
CLAUDE_MODEL = Config.CLAUDE_MODEL
CLAUDE_MAX_TOKENS = Config.CLAUDE_MAX_TOKENS
CLAUDE_API_KEY = Config.CLAUDE_API_KEY

# Error messages
ERROR_ANTHROPIC_REQUIRED = Config.ERROR_MESSAGES["anthropic_required"]
ERROR_NO_API_KEY = Config.ERROR_MESSAGES["no_api_key"]
ERROR_EMPTY_QUERY = Config.ERROR_MESSAGES["empty_query"]

# Prompt template
QUERY_GENERATION_PROMPT = Config.get_formatted_prompt

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Data class for generated YouTube search query results."""
    queries: list[str]  # List of search queries (max QUERY_WORD_LIMIT words each)
    date: Optional[str]  # Date filter or None
    reasoning: str


class QueryGenerationError(Exception):
    """Base exception for query generation errors."""
    pass


class YouTubeQueryGenerator:
    """Generator for optimized YouTube search queries using Claude API."""
    
    def __init__(self, api_key: str = None):
        """Initialize the query generator with Claude API."""
        try:
            import anthropic
            self._anthropic = anthropic
        except ImportError:
            raise QueryGenerationError(ERROR_ANTHROPIC_REQUIRED)
        
        self.api_key = api_key or Config.get_api_key('claude')
        if not self.api_key:
            raise QueryGenerationError(
                ERROR_NO_API_KEY.format(
                    api_name="Claude", 
                    env_var="CLAUDE_API_KEY"
                )
            )
        
        self.client = self._anthropic.Anthropic(api_key=self.api_key)
    
    def generate_search_query(self, user_query: str, num_queries: int = DEFAULT_NUM_QUERIES) -> QueryResult:
        """
        Generate multiple optimized YouTube search queries for product/market research.
        
        Args:
            user_query: User's query about a product, market, or topic
            num_queries: Number of different search queries to generate
            
        Returns:
            QueryResult with multiple optimized search queries, date filter, and reasoning
            
        Raises:
            QueryGenerationError: If query generation fails
        """
        if not user_query.strip():
            raise QueryGenerationError(ERROR_EMPTY_QUERY)
            
        logger.info(f"Generating {num_queries} search queries for: '{user_query}'")
        
        try:
            prompt = self._build_prompt(user_query, num_queries)
            
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response
            result = self._parse_response(response.content[0].text)
            
            logger.info(f"Successfully generated {len(result.queries)} search queries")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate query for '{user_query}': {e}")
            raise QueryGenerationError(f"Query generation failed: {str(e)}")
    
    def _build_prompt(self, user_query: str, num_queries: int) -> str:
        """
        Build the prompt for Claude to generate optimized YouTube search queries.
        
        Args:
            user_query: User's input query
            num_queries: Number of queries to generate
            
        Returns:
            Formatted prompt for Claude API
        """
        return QUERY_GENERATION_PROMPT(
            "query_generation_prompt",
            user_query=user_query,
            num_queries=num_queries,
            word_limit=QUERY_WORD_LIMIT
        )
    
    def _parse_response(self, response_text: str) -> QueryResult:
        """
        Parse Claude's response into a QueryResult object.
        
        Args:
            response_text: Raw response from Claude API
            
        Returns:
            Parsed QueryResult object
            
        Raises:
            QueryGenerationError: If parsing fails
        """
        try:
            # Extract JSON from response
            json_data = self._extract_json_from_response(response_text)
            
            # Validate and clean queries
            queries = self._validate_and_clean_queries(json_data.get('queries', []))
            
            if not queries:
                raise ValueError("No valid queries found in response")
            
            return QueryResult(
                queries=queries,
                date=json_data.get('date') if json_data.get('date') != 'null' else None,
                reasoning=json_data.get('reasoning', '').strip()
            )
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse response: {e}")
            logger.error(f"Response text: {response_text}")
            raise QueryGenerationError(f"Failed to parse Claude's response: {str(e)}")
    
    def _extract_json_from_response(self, response_text: str) -> dict:
        """Extract and parse JSON from Claude's response text."""
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response_text[start_idx:end_idx]
        return json.loads(json_str)
    
    def _validate_and_clean_queries(self, queries: list) -> list[str]:
        """Validate and clean the generated queries."""
        validated_queries = []
        
        for query in queries:
            query = query.strip()
            if not query:
                continue
                
            # Enforce word limit
            words = query.split()
            if len(words) > QUERY_WORD_LIMIT:
                query = ' '.join(words[:QUERY_WORD_LIMIT])
                logger.warning(f"Query truncated to {QUERY_WORD_LIMIT} words: {query}")
            
            validated_queries.append(query)
        
        return validated_queries