#!/usr/bin/env python3
"""
Interactive Trend Grader

Simple interface for manually grading discovered trends as interesting or not.
Allows you to quickly go through all trends and build a labeled dataset.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.trends_vector_db import TrendsVectorDB
import json

class TrendGrader:
    """Interactive trend grading interface."""
    
    def __init__(self):
        self.db = TrendsVectorDB()
    
    def display_trend(self, trend: dict, index: int, total: int) -> None:
        """Display a trend for grading."""
        print("\n" + "="*80)
        print(f"TREND {index + 1} of {total}")
        print("="*80)
        
        # Trend content
        print(f"📝 TREND TEXT:")
        print(f"   {trend['text']}")
        
        # Metadata
        metadata = trend['metadata']
        print(f"\n📊 METADATA:")
        print(f"   • Category: {metadata.get('category', 'unknown')}")
        print(f"   • Score: {metadata.get('score', 0):+.2f}")
        print(f"   • Date: {metadata.get('date', 'unknown')}")
        print(f"   • Run ID: {metadata.get('run_id', 'unknown')}")
        
        # Additional context if available
        if 'video_title' in metadata:
            title = metadata['video_title'][:60] + "..." if len(metadata['video_title']) > 60 else metadata['video_title']
            print(f"   • Video: {title}")
        
        if 'channel' in metadata:
            print(f"   • Channel: {metadata['channel']}")
    
    def get_user_grade(self) -> tuple:
        """Get user's grade for the current trend."""
        while True:
            print(f"\n💭 Grade this trend:")
            print("   [y] Interesting - I find this trend valuable/noteworthy")
            print("   [n] Not Interesting - This trend isn't useful to me")
            print("   [s] Skip - Don't grade this one")
            print("   [q] Quit grading session")
            print("   [info] Show grading guidelines")
            
            choice = input("\n👉 Your choice: ").strip().lower()
            
            if choice in ['y', 'yes']:
                notes = input("📝 Optional notes (press Enter to skip): ").strip()
                return True, notes if notes else None
            
            elif choice in ['n', 'no']:
                notes = input("📝 Optional notes (press Enter to skip): ").strip()
                return False, notes if notes else None
            
            elif choice in ['s', 'skip']:
                return None, None
            
            elif choice in ['q', 'quit']:
                return 'quit', None
            
            elif choice in ['info', 'help']:
                self.show_grading_guidelines()
                continue
            
            else:
                print("❌ Invalid choice. Please enter y, n, s, q, or info.")
    
    def show_grading_guidelines(self):
        """Show guidelines for grading trends."""
        print("\n" + "="*60)
        print("📋 GRADING GUIDELINES")
        print("="*60)
        print("""
🟢 Mark as INTERESTING (y) if the trend:
   • Represents a genuinely new or emerging technology/topic
   • Shows a significant shift in behavior or adoption
   • Could impact your business, interests, or industry
   • Reveals an unexpected pattern or insight
   • Is something you'd want to investigate further

🔴 Mark as NOT INTERESTING (n) if the trend:
   • Is obvious or already well-known
   • Doesn't apply to your interests/industry
   • Is too generic or vague to be actionable
   • Represents declining or outdated information
   • Is poorly extracted from the source content

💡 TIPS:
   • Consider the trend's potential value, not just novelty
   • Think about whether this would help inform decisions
   • Trust your instincts - you know what's valuable to you
   • It's okay to be selective - quality over quantity
   • Use notes to capture WHY you made the decision
""")
        print("="*60)
    
    def show_stats(self):
        """Show current grading statistics."""
        stats = self.db.get_grading_stats()
        
        if "error" in stats:
            print(f"❌ Error getting stats: {stats['error']}")
            return
        
        print(f"\n📊 GRADING PROGRESS:")
        print(f"   • Total trends: {stats['total_trends']}")
        print(f"   • Graded: {stats['graded']} ({stats['graded_percentage']:.1f}%)")
        print(f"   • Remaining: {stats['ungraded']}")
        
        if stats['graded'] > 0:
            print(f"\n✅ GRADING RESULTS:")
            print(f"   • Interesting: {stats['interesting']} ({stats['interesting_percentage']:.1f}%)")
            print(f"   • Not interesting: {stats['not_interesting']}")
    
    def start_grading_session(self, category: str = None, limit: int = 50):
        """Start an interactive grading session."""
        print("🎯 Interactive Trend Grader")
        print("="*50)
        print("Grade trends as interesting or not to build your labeled dataset")
        
        # Show current stats
        self.show_stats()
        
        # Get ungraded trends
        print(f"\n🔍 Loading ungraded trends...")
        trends = self.db.get_ungraded_trends(limit=limit, category=category)
        
        if not trends:
            print("✅ No ungraded trends found!")
            if category:
                print(f"   All trends in '{category}' have been graded.")
            else:
                print("   All trends have been graded.")
            return
        
        total_trends = len(trends)
        print(f"📋 Found {total_trends} ungraded trends")
        
        if category:
            print(f"📂 Filtering by category: {category}")
        
        # Start grading
        graded_count = 0
        interesting_count = 0
        
        print(f"\n🚀 Starting grading session...")
        print("💡 Type 'info' anytime for grading guidelines")
        
        for i, trend in enumerate(trends):
            # Display trend
            self.display_trend(trend, i, total_trends)
            
            # Get user's grade
            grade, notes = self.get_user_grade()
            
            if grade == 'quit':
                print(f"\n👋 Ending session. Graded {graded_count} trends.")
                break
            
            if grade is None:  # Skip
                print("⏭️  Skipped")
                continue
            
            # Save grade
            success = self.db.add_manual_grade(trend['id'], grade, notes)
            
            if success:
                graded_count += 1
                if grade:
                    interesting_count += 1
                    print("✅ Marked as INTERESTING")
                else:
                    print("❌ Marked as NOT INTERESTING")
                
                if notes:
                    print(f"📝 Notes: {notes}")
            else:
                print("⚠️  Failed to save grade")
        
        # Final stats
        print(f"\n🎉 Grading session complete!")
        print(f"   • Trends graded: {graded_count}")
        print(f"   • Interesting: {interesting_count}")
        print(f"   • Not interesting: {graded_count - interesting_count}")
        
        # Show updated stats
        self.show_stats()
    
    def review_graded_trends(self, interesting_only: bool = None, limit: int = 20):
        """Review previously graded trends."""
        print("📋 Reviewing Graded Trends")
        print("="*40)
        
        trends = self.db.get_graded_trends(interesting_only=interesting_only, limit=limit)
        
        if not trends:
            filter_text = ""
            if interesting_only is True:
                filter_text = " interesting"
            elif interesting_only is False:
                filter_text = " uninteresting"
            print(f"No{filter_text} graded trends found.")
            return
        
        for i, trend in enumerate(trends, 1):
            metadata = trend['metadata']
            grade = "✅ INTERESTING" if metadata['manual_grade'] else "❌ NOT INTERESTING"
            timestamp = metadata.get('manual_grade_timestamp', 'unknown')[:19]  # Remove microseconds
            
            print(f"\n{i}. {grade} - {timestamp}")
            print(f"   📝 {trend['text'][:80]}...")
            print(f"   📊 Category: {metadata.get('category')}, Score: {metadata.get('score', 0):+.1f}")
            
            if metadata.get('manual_grade_notes'):
                print(f"   💭 Notes: {metadata['manual_grade_notes']}")

def main():
    """Main CLI interface."""
    grader = TrendGrader()
    
    if len(sys.argv) < 2:
        print("🎯 YouTube Trends Grader")
        print("="*30)
        print("Usage:")
        print("  python trend_grader.py grade [category] [limit]     - Start grading session")
        print("  python trend_grader.py review [interesting|all]     - Review graded trends")
        print("  python trend_grader.py stats                        - Show grading statistics")
        print("\nExamples:")
        print("  python trend_grader.py grade                        - Grade any 50 trends")
        print("  python trend_grader.py grade emerging_topics        - Grade emerging_topics only")
        print("  python trend_grader.py grade early_adopter_products 100  - Grade 100 product trends")
        print("  python trend_grader.py review interesting           - Review interesting trends")
        print("  python trend_grader.py stats                        - Show progress")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'grade':
        category = sys.argv[2] if len(sys.argv) > 2 else None
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        
        # Validate category
        if category and category not in ['early_adopter_products', 'emerging_topics', 'problem_spaces', 'behavioral_patterns', 'educational_demand']:
            print(f"❌ Invalid category: {category}")
            print("Valid categories: early_adopter_products, emerging_topics, problem_spaces, behavioral_patterns, educational_demand")
            return
        
        grader.start_grading_session(category=category, limit=limit)
    
    elif command == 'review':
        filter_type = sys.argv[2] if len(sys.argv) > 2 else 'all'
        
        if filter_type == 'interesting':
            interesting_only = True
        elif filter_type == 'uninteresting':
            interesting_only = False
        else:
            interesting_only = None
        
        grader.review_graded_trends(interesting_only=interesting_only)
    
    elif command == 'stats':
        grader.show_stats()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: grade, review, stats")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()