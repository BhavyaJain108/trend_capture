#!/usr/bin/env python3
"""
Demo: Trend Grading System

Shows how to use the manual trend grading functionality.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.trends_vector_db import TrendsVectorDB

def main():
    print("🎯 Trend Grading System Demo")
    print("="*50)
    
    # Initialize database
    print("1. Initializing vector database...")
    db = TrendsVectorDB()
    
    # Check if we have data
    stats = db.get_stats()
    if stats['total_trends'] == 0:
        print("   ❌ No trends found. Run vector database demo first to load data.")
        print("   Try: python use_trends_vector_db.py")
        return 1
    
    print(f"   ✅ Database loaded with {stats['total_trends']} trends")
    
    # Show current grading stats
    print("\n2. Current grading status:")
    grading_stats = db.get_grading_stats()
    
    if "error" not in grading_stats:
        print(f"   • Total trends: {grading_stats['total_trends']}")
        print(f"   • Already graded: {grading_stats['graded']} ({grading_stats['graded_percentage']:.1f}%)")
        print(f"   • Ungraded: {grading_stats['ungraded']}")
        
        if grading_stats['graded'] > 0:
            print(f"   • Interesting: {grading_stats['interesting']} ({grading_stats['interesting_percentage']:.1f}%)")
            print(f"   • Not interesting: {grading_stats['not_interesting']}")
    
    # Show ungraded trends sample
    print("\n3. Sample ungraded trends:")
    ungraded = db.get_ungraded_trends(limit=3)
    
    if ungraded:
        for i, trend in enumerate(ungraded, 1):
            metadata = trend['metadata']
            text = trend['text'][:60] + "..." if len(trend['text']) > 60 else trend['text']
            print(f"   {i}. [{metadata.get('score', 0):+.1f}] ({metadata.get('category', 'unknown')})")
            print(f"      {text}")
    else:
        print("   ✅ All trends have been graded!")
    
    # Show graded trends sample if any exist
    print("\n4. Sample graded trends:")
    graded = db.get_graded_trends(limit=3)
    
    if graded:
        for i, trend in enumerate(graded, 1):
            metadata = trend['metadata']
            grade = "✅ Interesting" if metadata['manual_grade'] else "❌ Not interesting"
            text = trend['text'][:50] + "..." if len(trend['text']) > 50 else trend['text']
            print(f"   {i}. {grade} - [{metadata.get('score', 0):+.1f}]")
            print(f"      {text}")
            if metadata.get('manual_grade_notes'):
                print(f"      💭 Notes: {metadata['manual_grade_notes']}")
    else:
        print("   No graded trends yet.")
    
    # Demo programmatic grading
    if ungraded:
        print("\n5. Demo: Programmatic grading (for testing)")
        sample_trend = ungraded[0]
        
        print(f"   Grading trend: {sample_trend['text'][:50]}...")
        success = db.add_manual_grade(
            trend_id=sample_trend['id'],
            is_interesting=True,
            notes="Demo grade - marked as interesting for testing"
        )
        
        if success:
            print("   ✅ Successfully added demo grade")
        else:
            print("   ❌ Failed to add demo grade")
    
    print("\n" + "="*50)
    print("🚀 HOW TO USE THE GRADING SYSTEM:")
    print("="*50)
    print("""
📋 INTERACTIVE GRADING:
   python trend_grader.py grade                    # Grade any 50 trends
   python trend_grader.py grade emerging_topics    # Grade specific category
   python trend_grader.py grade early_adopter_products 100  # Grade 100 product trends

📊 REVIEW GRADED TRENDS:
   python trend_grader.py review                   # Review all graded trends
   python trend_grader.py review interesting       # Review only interesting ones
   python trend_grader.py review uninteresting     # Review only uninteresting ones

📈 CHECK PROGRESS:
   python trend_grader.py stats                    # Show grading statistics

💡 PROGRAMMATIC ACCESS:
   # Get ungraded trends
   ungraded = db.get_ungraded_trends(limit=50, category='emerging_topics')
   
   # Add manual grade
   db.add_manual_grade(trend_id, is_interesting=True, notes="Really valuable insight")
   
   # Get graded trends
   interesting = db.get_graded_trends(interesting_only=True)
   
   # Check progress
   stats = db.get_grading_stats()

🎯 CATEGORIES AVAILABLE:
   • early_adopter_products  • emerging_topics      • problem_spaces  
   • behavioral_patterns     • educational_demand

💭 GRADING TIPS:
   • Grade based on personal/business value to you
   • Use notes to capture why you made the decision  
   • Be selective - quality over quantity
   • Consider actionability and novelty
   • Trust your instincts about what's valuable
""")
    
    if ungraded:
        print(f"\n🎯 Ready to start grading! You have {len(ungraded)} ungraded trends waiting.")
        print("   Run: python trend_grader.py grade")
    else:
        print("\n✅ All trends graded! Use 'review' to see your results.")
    
    return 0

if __name__ == "__main__":
    exit(main())