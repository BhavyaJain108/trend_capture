"""DSPy signature definitions for transcript processing with early adopter product focus."""

from typing import List, Tuple
import dspy

from .config import Config

# Type definition for LLM insights
LLMInsight = Tuple[str, float]  # (insight_text, t_t_score Config.TREND_SCORE_MIN to Config.TREND_SCORE_MAX)


class ExtractEarlyAdopterProducts(dspy.Signature):
    """Extract early adopter products mentioned in the transcript - focus heavily on products, trends, platforms, services, and technologies"""
    transcript_chunk: str = dspy.InputField()
    products: List[LLMInsight] = dspy.OutputField(
        desc=Config.SIGNATURE_DESCRIPTIONS["early_adopter_products"]
    )


class ExtractEmergingTopics(dspy.Signature):
    """Extract emerging topics and terminology trends - emphasize topics related to early adopter products and technologies"""
    transcript_chunk: str = dspy.InputField()
    topics: List[LLMInsight] = dspy.OutputField(
        desc=Config.SIGNATURE_DESCRIPTIONS["emerging_topics"]
    )


class ExtractProblemSpaces(dspy.Signature):
    """Extract problem spaces and pain points - focus on problems that early adopter products are solving or creating"""
    transcript_chunk: str = dspy.InputField()
    problems: List[LLMInsight] = dspy.OutputField(
        desc=Config.SIGNATURE_DESCRIPTIONS["problem_spaces"]
    )


class ExtractBehaviorPatterns(dspy.Signature):
    """Extract behavioral patterns and user trends - emphasize adoption behaviors around early adopter products"""
    transcript_chunk: str = dspy.InputField()
    behaviors: List[LLMInsight] = dspy.OutputField(
        desc=Config.SIGNATURE_DESCRIPTIONS["behavioral_patterns"]
    )


class ExtractEducationalDemand(dspy.Signature):
    """Extract educational needs and learning demand signals - focus on learning needs for early adopter products"""
    transcript_chunk: str = dspy.InputField()
    education: List[LLMInsight] = dspy.OutputField(
        desc=Config.SIGNATURE_DESCRIPTIONS["educational_demand"]
    )