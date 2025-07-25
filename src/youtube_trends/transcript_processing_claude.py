"""
Transcript processing module using direct Claude API calls for structured insight extraction.
This replaces the DSPy version to enable true parallel processing.
"""

import logging
import os
import json
from typing import List, Tuple, Dict
from dataclasses import dataclass
from datetime import datetime

from .config import Config

logger = logging.getLogger(__name__)

# Type definitions
LLMInsight = Tuple[str, float]  # (insight_text, trend_score -1.0 to 1.0)
InsightTuple = Tuple[str, str, float]  # (insight_text, transcript_date, trend_score)

@dataclass
class TranscriptInsights:
    """Container for all extracted insights from a transcript."""
    early_adopter_products: List[InsightTuple]
    emerging_topics: List[InsightTuple]
    problem_spaces: List[InsightTuple]
    behavioral_patterns: List[InsightTuple]
    educational_demand: List[InsightTuple]
    transcript_date: str
    processing_metadata: Dict

class TranscriptProcessingError(Exception):
    """Base exception for transcript processing errors."""
    pass

class TranscriptChunker:
    """Smart transcript chunking system that preserves context."""
    
    def __init__(self, max_chunk_size: int = Config.TRANSCRIPT_MAX_CHUNK_SIZE, overlap_size: int = Config.TRANSCRIPT_OVERLAP_SIZE):
        """
        Initialize chunker with size parameters.
        
        Args:
            max_chunk_size: Maximum characters per chunk
            overlap_size: Characters to overlap between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
    
    def chunk_transcript(self, transcript: str) -> List[str]:
        """
        Split transcript into overlapping chunks at sentence boundaries.
        
        Args:
            transcript: Full transcript text
            
        Returns:
            List of transcript chunks with preserved context
        """
        if len(transcript) <= self.max_chunk_size:
            return [transcript]
        
        # Split into sentences while preserving punctuation
        sentences = self._split_sentences(transcript)
        chunks = []
        current_chunk = ""
        overlap_buffer = ""
        
        for sentence in sentences:
            # Check if adding this sentence would exceed limit
            if len(current_chunk + sentence) > self.max_chunk_size and current_chunk:
                # Add current chunk
                chunks.append(overlap_buffer + current_chunk)
                
                # Prepare overlap for next chunk
                overlap_buffer = self._create_overlap(current_chunk)
                current_chunk = sentence
            else:
                current_chunk += sentence
        
        # Add final chunk
        if current_chunk:
            chunks.append(overlap_buffer + current_chunk)
        
        logger.info(f"Split transcript into {len(chunks)} chunks")
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences while preserving context."""
        sentences = []
        current = ""
        
        for char in text:
            current += char
            if char in Config.SENTENCE_DELIMITERS and len(current.strip()) > Config.TRANSCRIPT_MIN_SENTENCE_LENGTH:
                sentences.append(current.strip() + " ")
                current = ""
        
        # Add remaining text
        if current.strip():
            sentences.append(current.strip())
        
        return sentences
    
    def _create_overlap(self, chunk: str) -> str:
        """Create overlap buffer from end of chunk."""
        if len(chunk) <= self.overlap_size:
            return chunk
        
        # Take last overlap_size characters, but start at word boundary
        overlap = chunk[-self.overlap_size:]
        space_idx = overlap.find(' ')
        if space_idx > 0:
            overlap = overlap[space_idx:]
        
        return overlap.strip() + " "

class ClaudeTranscriptProcessor:
    """Main processor for extracting insights from transcripts using direct Claude API calls."""
    
    def __init__(self, api_key: str = None):
        """Initialize processor with Claude API key."""
        try:
            import anthropic
            self._anthropic = anthropic
        except ImportError:
            raise TranscriptProcessingError(Config.ERROR_MESSAGES["anthropic_required"])
        
        self.api_key = api_key or Config.get_api_key('claude')
        if not self.api_key:
            raise TranscriptProcessingError(
                Config.ERROR_MESSAGES["no_api_key"].format(
                    api_name="Claude", env_var=Config.CLAUDE_API_KEY_ENV
                )
            )
        
        self.client = self._anthropic.Anthropic(api_key=self.api_key)
        self.chunker = TranscriptChunker()
        
        logger.info("Successfully initialized Claude transcript processor")
    
    def process_transcript(self, transcript: str, transcript_date: str = None) -> TranscriptInsights:
        """
        Process a full transcript and extract structured insights.
        
        Args:
            transcript: Full transcript text
            transcript_date: Date of the transcript (ISO format YYYY-MM-DD)
            
        Returns:
            TranscriptInsights with all extracted information
            
        Raises:
            TranscriptProcessingError: If processing fails
        """
        if not transcript.strip():
            raise TranscriptProcessingError(Config.ERROR_MESSAGES["empty_transcript"])
        
        # Use current date if not provided
        if not transcript_date:
            transcript_date = datetime.now().strftime(Config.DATE_FORMAT)
        
        logger.info(f"Processing transcript from {transcript_date}, length: {len(transcript)}")
        
        try:
            # Step 1: Chunk transcript
            chunks = self.chunker.chunk_transcript(transcript)
            
            # Step 2: Extract insights from each chunk for all categories
            all_insights = {
                'early_adopter_products': [],
                'emerging_topics': [],
                'problem_spaces': [],
                'behavioral_patterns': [],
                'educational_demand': []
            }
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                # Extract from each category
                for category in all_insights.keys():
                    insights = self._extract_insights_for_category(chunk, category)
                    all_insights[category].extend(insights)
            
            # Step 3: Aggregate and finalize insights
            final_insights = {}
            for category, insights in all_insights.items():
                final_insights[category] = self._aggregate_insights(insights, transcript_date)
            
            # Step 4: Create final result
            insights = TranscriptInsights(
                early_adopter_products=final_insights['early_adopter_products'],
                emerging_topics=final_insights['emerging_topics'],
                problem_spaces=final_insights['problem_spaces'],
                behavioral_patterns=final_insights['behavioral_patterns'],
                educational_demand=final_insights['educational_demand'],
                transcript_date=transcript_date,
                processing_metadata={
                    "chunks_processed": len(chunks),
                    "total_insights": sum(len(insights) for insights in final_insights.values()),
                    "transcript_length": len(transcript),
                    "processing_date": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Processing complete. Extracted {insights.processing_metadata['total_insights']} insights")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to process transcript: {e}")
            raise TranscriptProcessingError(f"Transcript processing failed: {str(e)}")
    
    def _extract_insights_for_category(self, chunk: str, category: str) -> List[LLMInsight]:
        """Extract insights for a specific category using Claude API."""
        
        try:
            # Build prompt for this category
            prompt = self._build_category_prompt(chunk, category)
            
            # Call Claude API
            response = self.client.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=Config.CLAUDE_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            insights = self._parse_insights_response(response.content[0].text)
            
            # Validate and clean insights
            cleaned_insights = []
            for insight in insights:
                if isinstance(insight, (list, tuple)) and len(insight) >= 2:
                    text, score = str(insight[0]).strip(), float(insight[1])
                    # Clamp score to valid range
                    score = Config.validate_score(score)
                    if text:  # Only keep non-empty insights
                        cleaned_insights.append((text, score))
            
            return cleaned_insights
            
        except Exception as e:
            logger.warning(f"Failed to extract {category} from chunk: {e}")
            return []
    
    def _build_category_prompt(self, chunk: str, category: str) -> str:
        """Build prompt for extracting insights from a specific category."""
        
        category_descriptions = {
            "early_adopter_products": "Extract specific product names, tools, platforms, hardware, services, apps, and technologies mentioned or discussed. Focus on concrete products and technologies.",
            
            "emerging_topics": "Extract trending topics, innovation areas, and emerging themes that are gaining traction. Focus on concepts and trends rather than specific products.",
            
            "problem_spaces": "Extract problems, pain points, limitations, and challenges being discussed. Focus on issues that need solutions or are causing difficulties.",
            
            "behavioral_patterns": "Extract behavioral changes, usage patterns, workflow modifications, and adoption/abandonment behaviors being described.",
            
            "educational_demand": "Extract learning needs, skill gaps, training demands, certification requirements, and educational opportunities being discussed."
        }
        
        description = category_descriptions[category]
        
        return f"""Analyze this transcript excerpt and extract insights related to: {description}

Transcript excerpt:
{chunk}

Extract insights and score each from -1.0 to +1.0 where:
- +1.0 = highly trending/rising/growing/urgent
- 0.0 = neutral/stable/unclear
- -1.0 = declining/losing momentum/solved/obsolete

Return ONLY a JSON array in this exact format:
[
    ["insight description", score],
    ["another insight", score]
]

Focus on specific, actionable insights. If no relevant insights are found, return an empty array: []"""

    def _parse_insights_response(self, response_text: str) -> List[List]:
        """Parse Claude's response containing insights array."""
        try:
            # Extract JSON array from response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                return []  # No array found, return empty
            
            json_str = response_text[start_idx:end_idx]
            insights_array = json.loads(json_str)
            
            return insights_array if isinstance(insights_array, list) else []
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse insights response: {e}")
            return []
    
    def _aggregate_insights(self, insights: List[LLMInsight], transcript_date: str) -> List[InsightTuple]:
        """Attach transcript date and sort insights by significance."""
        if not insights:
            return []

        # Attach date to each insight
        final_insights = [
            (text, transcript_date, score)
            for text, score in insights
        ]

        # Sort by absolute score (most significant trends first)
        final_insights.sort(key=lambda x: abs(x[2]), reverse=True)

        return final_insights