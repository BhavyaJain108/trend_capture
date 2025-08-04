#!/usr/bin/env python3
"""
Grade and Store Pipeline

Workflow: CSV Results → Manual Grading → Vector Database
Loads trends from pipeline CSV results, lets you grade them, then stores graded trends in vector DB.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from youtube_trends.trends_vector_db import TrendsVectorDB
from youtube_trends.config import Config

class CSVTrendGrader:
    """Grade trends from CSV files before storing in vector database."""
    
    def __init__(self):
        self.vector_db = TrendsVectorDB()
        self.current_trends = []
        self.graded_trends = []
        self.current_index = 0
    
    def load_trends_from_csv(self, csv_path: str) -> List[Dict]:
        """Load trends from CSV file."""
        print(f"📄 Loading trends from: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            if df.empty:
                print("❌ CSV file is empty")
                return []
            
            # Convert to trend dictionaries
            trends = []
            for _, row in df.iterrows():
                trend = {
                    'text': row.get('information', ''),
                    'category': row.get('category', 'unknown'),
                    'score': float(row.get('score', 0.0)),
                    'date': row.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'csv_source': csv_path,
                    'row_index': len(trends)
                }
                
                # Add video metadata if available
                for col in ['video_id', 'video_title', 'channel', 'run_id', 'user_query']:
                    if col in df.columns:
                        trend[col] = row.get(col, '')
                
                trends.append(trend)
            
            print(f"✅ Loaded {len(trends)} trends from CSV")
            return trends
            
        except Exception as e:
            print(f"❌ Failed to load CSV: {e}")
            return []
    
    def find_latest_results(self) -> str:
        """Find the most recent results CSV file."""
        results_dir = Path("results")
        
        if not results_dir.exists():
            return None
        
        # Find most recent directory
        result_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
        if not result_dirs:
            return None
        
        latest_dir = max(result_dirs, key=lambda x: x.name)
        
        # Look for trend_results.csv (the actual trends, not queries)
        csv_file = latest_dir / "trend_results.csv"
        if csv_file.exists():
            return str(csv_file)
        
        # Fallback to query_results.csv if trend_results doesn't exist
        csv_file = latest_dir / "query_results.csv"
        if csv_file.exists():
            return str(csv_file)
        
        return None
    
    def display_trend_for_grading(self, trend: Dict, index: int, total: int):
        """Display a trend for manual grading."""
        print("\n" + "="*80)
        print(f"TREND {index + 1} of {total}")
        print("="*80)
        
        # Main trend content
        print(f"📝 TREND:")
        print(f"   {trend['text']}")
        
        # Metadata
        print(f"\n📊 DETAILS:")
        print(f"   • Category: {trend['category']}")
        print(f"   • Score: {trend['score']:+.2f}")
        print(f"   • Date: {trend['date']}")
        
        # Additional context if available
        if trend.get('video_title'):
            title = trend['video_title'][:60] + "..." if len(trend['video_title']) > 60 else trend['video_title']
            print(f"   • Video: {title}")
        
        if trend.get('channel'):
            print(f"   • Channel: {trend['channel']}")
        
        print(f"   • Source: {Path(trend['csv_source']).name}")
    
    def get_grade_from_user(self) -> tuple:
        """Get user's grade for current trend."""
        while True:
            print(f"\n💭 Grade this trend:")
            print("   [y] Interesting - Include in vector database")
            print("   [n] Not Interesting - Skip this trend")
            print("   [s] Skip - Don't grade, but include anyway")
            print("   [q] Quit - Save progress and exit")
            print("   [info] Show grading guidelines")
            
            choice = input("\n👉 Your choice: ").strip().lower()
            
            if choice in ['y', 'yes']:
                notes = input("📝 Optional notes (press Enter to skip): ").strip()
                return True, notes if notes else None
            
            elif choice in ['n', 'no']:
                notes = input("📝 Optional notes (press Enter to skip): ").strip()
                return False, notes if notes else None
            
            elif choice in ['s', 'skip']:
                return None, None  # Include without grade
            
            elif choice in ['q', 'quit']:
                return 'quit', None
            
            elif choice in ['info', 'help']:
                self.show_grading_guidelines()
                continue
            
            else:
                print("❌ Invalid choice. Please enter y, n, s, q, or info.")
    
    def show_grading_guidelines(self):
        """Show grading guidelines."""
        print("\n" + "="*60)
        print("📋 GRADING GUIDELINES")
        print("="*60)
        print("""
🟢 Mark as INTERESTING (y) if:
   • Genuinely new or emerging trend/technology
   • Significant behavioral shift or adoption pattern  
   • Could impact your business/interests
   • Reveals unexpected insights
   • Actionable information you'd investigate further

🔴 Mark as NOT INTERESTING (n) if:
   • Already well-known or obvious
   • Too generic/vague to be useful
   • Doesn't apply to your domain
   • Poor quality extraction
   • Declining/outdated information

⏭️ SKIP (s) if:
   • Unsure but want to include it anyway
   • Need more context to decide
   • Want to grade later

💡 TIPS:
   • Focus on personal/business value
   • Consider actionability and novelty
   • Trust your instincts
   • Use notes to capture reasoning
""")
        print("="*60)
    
    def grade_trends_interactive(self, trends: List[Dict]) -> List[Dict]:
        """Interactively grade a list of trends."""
        print(f"\n🎯 Interactive Trend Grading Session")
        print(f"📊 {len(trends)} trends to review")
        
        graded_trends = []
        skipped_count = 0
        interesting_count = 0
        not_interesting_count = 0
        
        for i, trend in enumerate(trends):
            self.display_trend_for_grading(trend, i, len(trends))
            
            grade, notes = self.get_grade_from_user()
            
            if grade == 'quit':
                print(f"\n👋 Ending session. Processed {i} trends.")
                break
            
            # Create graded trend
            graded_trend = trend.copy()
            graded_trend['grading_timestamp'] = datetime.now().isoformat()
            
            if grade is not None:  # y or n
                graded_trend['manual_grade'] = grade
                graded_trend['manual_grade_notes'] = notes or ""
                graded_trend['include_in_vector_db'] = grade  # Only include if interesting
                
                if grade:
                    interesting_count += 1
                    print("✅ Marked as INTERESTING - will include in vector DB")
                else:
                    not_interesting_count += 1
                    print("❌ Marked as NOT INTERESTING - will skip")
            else:  # skip
                graded_trend['manual_grade'] = None
                graded_trend['manual_grade_notes'] = "Skipped during grading"
                graded_trend['include_in_vector_db'] = True  # Include ungraded
                skipped_count += 1
                print("⏭️ Skipped - will include in vector DB without grade")
            
            if notes:
                print(f"📝 Notes: {notes}")
            
            graded_trends.append(graded_trend)
        
        # Summary
        print(f"\n🎉 Grading session complete!")
        print(f"   • Trends processed: {len(graded_trends)}")
        print(f"   • Interesting: {interesting_count}")
        print(f"   • Not interesting: {not_interesting_count}")
        print(f"   • Skipped (ungraded): {skipped_count}")
        print(f"   • Will include in vector DB: {len([t for t in graded_trends if t['include_in_vector_db']])}")
        
        return graded_trends
    
    def store_graded_trends(self, graded_trends: List[Dict]) -> bool:
        """Store graded trends in vector database."""
        # Filter to only trends marked for inclusion
        trends_to_store = [t for t in graded_trends if t['include_in_vector_db']]
        
        if not trends_to_store:
            print("❌ No trends marked for storage")
            return False
        
        print(f"💾 Storing {len(trends_to_store)} graded trends in vector database...")
        
        try:
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            run_id = f"graded_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            for i, trend in enumerate(trends_to_store):
                # Create unique ID
                trend_id = f"{run_id}_{i:04d}"
                
                # Document text
                documents.append(trend['text'])
                
                # Metadata - include grading information
                metadata = {
                    'category': trend['category'],
                    'score': float(trend['score']),
                    'date': trend['date'],
                    'run_id': run_id,
                    'run_timestamp': datetime.now().isoformat(),
                    'csv_source': Path(trend['csv_source']).name,
                    'was_graded': trend['manual_grade'] is not None,
                }
                
                # Add grading info if available
                if trend['manual_grade'] is not None:
                    metadata['manual_grade'] = trend['manual_grade']
                    metadata['manual_grade_timestamp'] = trend['grading_timestamp']
                    metadata['manual_grade_notes'] = trend['manual_grade_notes']
                
                # Add video metadata if available
                for field in ['video_id', 'video_title', 'channel', 'user_query']:
                    if field in trend and trend[field]:
                        metadata[field] = str(trend[field])
                
                metadatas.append(metadata)
                ids.append(trend_id)
            
            # Add to ChromaDB
            self.vector_db.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Successfully stored {len(trends_to_store)} trends with run_id: {run_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store trends: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_grading_workflow(self, csv_path: str = None):
        """Run the complete grading workflow."""
        print("🔄 Grade and Store Workflow")
        print("="*50)
        print("CSV Results → Manual Grading → Vector Database")
        
        # Step 1: Find or load CSV
        if not csv_path:
            csv_path = self.find_latest_results()
            if not csv_path:
                print("❌ No results CSV found. Run the pipeline first:")
                print("   python -m youtube_trends.parallel_pipeline 'your query'")
                return False
            print(f"📄 Using latest results: {csv_path}")
        
        # Step 2: Load trends
        trends = self.load_trends_from_csv(csv_path)
        if not trends:
            return False
        
        # Step 3: Show preview
        print(f"\n📋 TRENDS PREVIEW:")
        from collections import Counter
        category_counts = Counter(t['category'] for t in trends)
        for category, count in category_counts.items():
            print(f"   • {category}: {count} trends")
        
        # Step 4: Grade trends
        print(f"\n🎯 Ready to grade {len(trends)} trends")
        proceed = input("👉 Start grading session? (y/n): ").strip().lower()
        
        if proceed not in ['y', 'yes']:
            print("👋 Grading cancelled")
            return False
        
        graded_trends = self.grade_trends_interactive(trends)
        
        # Step 5: Store in vector database
        if graded_trends:
            store_success = self.store_graded_trends(graded_trends)
            if store_success:
                print(f"\n✅ Workflow complete! Graded trends are now in vector database.")
                print(f"🔍 You can search them with: python interactive_search.py")
                return True
        
        return False

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("🔄 Grade and Store Pipeline")
        print("="*40)
        print("Usage:")
        print("  python grade_and_store.py auto          - Use latest results CSV")
        print("  python grade_and_store.py <csv_path>    - Use specific CSV file")
        print("\nExamples:")
        print("  python grade_and_store.py auto")
        print("  python grade_and_store.py results/20241201_143022/query_results.csv")
        print("\nWorkflow: CSV Results → Manual Grading → Vector Database")
        return 1
    
    grader = CSVTrendGrader()
    
    command = sys.argv[1]
    
    if command == 'auto':
        success = grader.run_grading_workflow()
    else:
        # Treat as CSV path
        csv_path = command
        if not Path(csv_path).exists():
            print(f"❌ CSV file not found: {csv_path}")
            return 1
        success = grader.run_grading_workflow(csv_path)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Grading cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)