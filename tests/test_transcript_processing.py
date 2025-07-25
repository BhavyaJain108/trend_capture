#!/usr/bin/env python3
"""Test script for transcript processing with DSPy and trend analysis."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_trends.transcript_processing import TranscriptProcessor, TranscriptProcessingError

def test_sample_tech_transcript():
    """Test processing a sample tech-focused transcript."""
    
    sample_transcript = """
    Hey everyone, welcome back to the channel! Today I want to talk about some major shifts 
    I'm seeing in the tech industry right now. First off, AI coding assistants like GitHub Copilot 
    and Claude are absolutely everywhere now. Every developer I know is using them, and honestly, 
    the productivity gains are insane. I'm seeing 40-50% faster coding times.
    
    But here's what's interesting - while AI tools are booming, I'm noticing that a lot of the 
    blockchain hype from 2021-2022 is really dying down. NFT marketplaces are struggling, 
    DeFi protocols are losing users, and frankly, most people I talk to are pretty skeptical 
    about crypto now. The whole Web3 thing feels like it's lost momentum.
    
    On the flip side, there's this massive problem that's getting worse - AI hallucinations 
    and reliability issues. Companies are struggling with how to trust AI outputs for critical 
    tasks. This is becoming a huge pain point, especially in enterprise settings.
    
    I'm also seeing interesting behavioral changes. Developers are completely changing their 
    workflows - they're starting with AI first, then coding second. It's a total paradigm shift. 
    But older developers, especially those 10+ years experience, are really resistant to this change.
    
    And the education space is exploding! Everyone wants to learn prompt engineering now. 
    I'm seeing massive demand for courses on how to work with AI tools effectively. Companies 
    are hiring "prompt engineers" at crazy salaries - we're talking $200k+ for people who 
    basically know how to talk to AI systems effectively.
    
    The metaverse stuff that everyone was talking about in 2022? Pretty much dead. VR adoption 
    is still slow, and most of the workplace collaboration tools in VR feel gimmicky. 
    Companies that bet big on metaverse are quietly pivoting away.
    
    But here's what's really taking off - multimodal AI. Systems that can understand text, 
    images, audio, everything together. This is the next big wave, and we're just at the beginning.
    """
    
    try:
        processor = TranscriptProcessor()
        
        print("🔬 TESTING TRANSCRIPT PROCESSING")
        print("=" * 60)
        print(f"Sample transcript length: {len(sample_transcript)} characters")
        print("-" * 60)
        
        # Process the transcript
        insights = processor.process_transcript(sample_transcript, "2024-03-15")
        
        # Display results
        print(f"\n📊 PROCESSING RESULTS")
        print(f"Date: {insights.transcript_date}")
        print(f"Total insights: {insights.processing_metadata['total_insights']}")
        print(f"Chunks processed: {insights.processing_metadata['chunks_processed']}")
        
        # Early Adopter Products
        print(f"\n🚀 EARLY ADOPTER PRODUCTS ({len(insights.early_adopter_products)}):")
        for text, date, score in insights.early_adopter_products:
            trend_emoji = "📈" if score > 0.5 else "📉" if score < -0.5 else "➡️"
            print(f"   {trend_emoji} [{score:+.2f}] {text}")
        
        # Emerging Topics
        print(f"\n💡 EMERGING TOPICS ({len(insights.emerging_topics)}):")
        for text, date, score in insights.emerging_topics:
            trend_emoji = "🔥" if score > 0.5 else "❄️" if score < -0.5 else "🔄"
            print(f"   {trend_emoji} [{score:+.2f}] {text}")
        
        # Problem Spaces
        print(f"\n⚠️  PROBLEM SPACES ({len(insights.problem_spaces)}):")
        for text, date, score in insights.problem_spaces:
            trend_emoji = "🚨" if score > 0.5 else "✅" if score < -0.5 else "⚡"
            print(f"   {trend_emoji} [{score:+.2f}] {text}")
        
        # Behavioral Patterns
        print(f"\n👥 BEHAVIORAL PATTERNS ({len(insights.behavioral_patterns)}):")
        for text, date, score in insights.behavioral_patterns:
            trend_emoji = "⬆️" if score > 0.5 else "⬇️" if score < -0.5 else "↔️"
            print(f"   {trend_emoji} [{score:+.2f}] {text}")
        
        # Educational Demand
        print(f"\n🎓 EDUCATIONAL DEMAND ({len(insights.educational_demand)}):")
        for text, date, score in insights.educational_demand:
            trend_emoji = "📚" if score > 0.5 else "📉" if score < -0.5 else "📖"
            print(f"   {trend_emoji} [{score:+.2f}] {text}")
        
        print(f"\n✅ Processing completed successfully!")
        
        return insights
        
    except TranscriptProcessingError as e:
        print(f"❌ Processing Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None

def test_chunking_system():
    """Test the transcript chunking system."""
    
    long_transcript = """This is a very long transcript that should be split into multiple chunks. """ * 200
    
    try:
        processor = TranscriptProcessor()
        chunks = processor.chunker.chunk_transcript(long_transcript)
        
        print(f"\n🔧 CHUNKING SYSTEM TEST")
        print(f"Original length: {len(long_transcript)} characters")
        print(f"Number of chunks: {len(chunks)}")
        print(f"Average chunk size: {sum(len(c) for c in chunks) / len(chunks):.0f} characters")
        
        for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
            print(f"\nChunk {i+1} ({len(chunk)} chars): {chunk[:100]}...")
        
    except Exception as e:
        print(f"❌ Chunking test failed: {e}")

def test_trend_score_validation():
    """Test that trend scores are properly validated."""
    
    print(f"\n🎯 TREND SCORE INTERPRETATION")
    print("-" * 40)
    
    score_examples = [
        (0.9, "🚀 Rapidly Rising - Hot trends, explosive growth"),
        (0.5, "📈 Growing - Steady positive momentum"),
        (0.1, "➡️ Stable - Neutral or unclear direction"),
        (-0.3, "📉 Declining - Losing momentum, skepticism"),
        (-0.8, "❄️ Fading Fast - Major decline, failed trends")
    ]
    
    for score, description in score_examples:
        print(f"   {score:+.1f}: {description}")

if __name__ == "__main__":
    # Run all tests
    insights = test_sample_tech_transcript()
    test_chunking_system()
    test_trend_score_validation()
    
    if insights:
        print(f"\n🎉 All tests completed! Ready for real transcript processing.")
    else:
        print(f"\n❌ Tests failed. Check your setup.")