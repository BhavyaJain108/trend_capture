"""Transcript processing module using DSPy for structured insight extraction."""

import logging
import os
from typing import List, Tuple, Dict
from dataclasses import dataclass
from datetime import datetime

from .config import Config

logger = logging.getLogger(__name__)

# Type definitions
LLMInsight = Tuple[str, float]  # (insight_text, t_t_score -1.0 to 1.0)
InsightTuple = Tuple[str, str, float]  # (insight_text, transcript_date, t_t_score)

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
        # Simple sentence splitting - could be enhanced with NLTK
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


class TranscriptProcessor:
    """Main processor for extracting insights from transcripts using DSPy."""
    
    def __init__(self, api_key: str = None):
        """Initialize processor with Claude API key."""
        try:
            import dspy
        except ImportError:
            raise TranscriptProcessingError(Config.ERROR_MESSAGES["dspy_required"])
        
        self.api_key = api_key or Config.get_api_key('claude')
        if not self.api_key:
            raise TranscriptProcessingError(
                Config.ERROR_MESSAGES["no_api_key"].format(
                    api_name="Claude", env_var=Config.CLAUDE_API_KEY_ENV
                )
            )
        
        # Initialize DSPy with Claude
        try:
            lm = dspy.LM(model=Config.CLAUDE_MODEL, api_key=self.api_key)
            dspy.settings.configure(lm=lm)
            logger.info("Successfully initialized DSPy with Claude")
        except Exception as e:
            logger.error(f"Failed to initialize DSPy with Claude: {e}")
            raise TranscriptProcessingError(f"DSPy initialization failed: {str(e)}")
        
        # Initialize components
        self.chunker = TranscriptChunker()
        self._setup_extractors()
    
    def _setup_extractors(self):
        """Setup DSPy signature extractors."""
        import dspy
        from .transcript_signatures import (
            ExtractEarlyAdopterProducts,
            ExtractEmergingTopics,
            ExtractProblemSpaces,
            ExtractBehaviorPatterns,
            ExtractEducationalDemand
        )
        
        # Create predictor instances
        self.extract_products = dspy.Predict(ExtractEarlyAdopterProducts)
        self.extract_topics = dspy.Predict(ExtractEmergingTopics)
        self.extract_problems = dspy.Predict(ExtractProblemSpaces)
        self.extract_behaviors = dspy.Predict(ExtractBehaviorPatterns)
        self.extract_education = dspy.Predict(ExtractEducationalDemand)
    
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
            
            # Step 2: Extract insights from each chunk
            all_products = []
            all_topics = []
            all_problems = []
            all_behaviors = []
            all_education = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                # Extract from each category
                products = self._safe_extract(self.extract_products, chunk, "products")
                topics = self._safe_extract(self.extract_topics, chunk, "topics")
                problems = self._safe_extract(self.extract_problems, chunk, "problems")
                behaviors = self._safe_extract(self.extract_behaviors, chunk, "behaviors")
                education = self._safe_extract(self.extract_education, chunk, "education")
                
                all_products.extend(products)
                all_topics.extend(topics)
                all_problems.extend(problems)
                all_behaviors.extend(behaviors)
                all_education.extend(education)
            
            # Step 3: Aggregate and deduplicate
            final_products = self._aggregate_insights(all_products, transcript_date)
            final_topics = self._aggregate_insights(all_topics, transcript_date)
            final_problems = self._aggregate_insights(all_problems, transcript_date)
            final_behaviors = self._aggregate_insights(all_behaviors, transcript_date)
            final_education = self._aggregate_insights(all_education, transcript_date)
            
            # Step 4: Create final result
            insights = TranscriptInsights(
                early_adopter_products=final_products,
                emerging_topics=final_topics,
                problem_spaces=final_problems,
                behavioral_patterns=final_behaviors,
                educational_demand=final_education,
                transcript_date=transcript_date,
                processing_metadata={
                    "chunks_processed": len(chunks),
                    "total_insights": len(final_products) + len(final_topics) + len(final_problems) + len(final_behaviors) + len(final_education),
                    "transcript_length": len(transcript),
                    "processing_date": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Processing complete. Extracted {insights.processing_metadata['total_insights']} insights")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to process transcript: {e}")
            raise TranscriptProcessingError(f"Transcript processing failed: {str(e)}")
    
    def _safe_extract(self, extractor, chunk: str, category: str) -> List[LLMInsight]:
        """Safely extract insights with error handling."""
        try:
            result = extractor(transcript_chunk=chunk)
            insights = getattr(result, category, [])
            
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