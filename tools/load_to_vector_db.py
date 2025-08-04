#!/usr/bin/env python3
"""
Direct CSV to Vector Database Loader

Loads all trends from CSV results directly into vector database (no manual grading).
Use this when you have too many trends to manually grade.
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

class DirectVectorLoader:
    """Load trends directly from CSV to vector database."""
    
    def __init__(self, db_path: str = None):
        self.vector_db = TrendsVectorDB(db_path=db_path)
        self.db_path = db_path
    
    def find_latest_results(self) -> tuple:
        """Find the most recent results CSV file and return (csv_path, results_dir)."""
        results_dir = Path("results")
        
        if not results_dir.exists():
            return None, None
        
        # Find most recent directory
        result_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
        if not result_dirs:
            return None, None
        
        latest_dir = max(result_dirs, key=lambda x: x.name)
        
        # Look for trend_results.csv (the actual trends)
        csv_file = latest_dir / "trend_results.csv"
        if csv_file.exists():
            return str(csv_file), str(latest_dir)
        
        return None, None
    
    def load_trends_from_csv(self, csv_path: str) -> List[Dict]:
        """Load all trends from CSV file."""
        print(f"📄 Loading trends from: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            if df.empty:
                print("❌ CSV file is empty")
                return []
            
            print(f"📊 CSV contains {len(df)} trends")
            
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
                
                # Add any additional columns as metadata
                for col in df.columns:
                    if col not in ['information', 'category', 'score', 'date']:
                        trend[col] = str(row.get(col, ''))
                
                # Skip empty trends
                if trend['text'].strip():
                    trends.append(trend)
            
            print(f"✅ Loaded {len(trends)} valid trends from CSV")
            return trends
            
        except Exception as e:
            print(f"❌ Failed to load CSV: {e}")
            return []
    
    def show_trends_summary(self, trends: List[Dict]):
        """Show summary of trends to be loaded."""
        if not trends:
            return
        
        print(f"\n📋 TRENDS SUMMARY:")
        print("="*50)
        
        # Category breakdown
        from collections import Counter
        category_counts = Counter(t['category'] for t in trends)
        
        print(f"📊 By Category:")
        for category, count in category_counts.most_common():
            print(f"   • {category}: {count} trends")
        
        # Score distribution
        scores = [t['score'] for t in trends]
        high_score = len([s for s in scores if s > 0.7])
        medium_score = len([s for s in scores if 0.3 <= s <= 0.7])
        low_score = len([s for s in scores if s < 0.3])
        
        print(f"\n⭐ By Score:")
        print(f"   • High (>0.7): {high_score} trends")
        print(f"   • Medium (0.3-0.7): {medium_score} trends")
        print(f"   • Low (<0.3): {low_score} trends")
        print(f"   • Average: {sum(scores)/len(scores):.2f}")
        
        # Show top trends
        print(f"\n🏆 Top 5 Trends:")
        sorted_trends = sorted(trends, key=lambda x: x['score'], reverse=True)
        for i, trend in enumerate(sorted_trends[:5], 1):
            text = trend['text'][:60] + "..." if len(trend['text']) > 60 else trend['text']
            print(f"   {i}. [{trend['score']:+.1f}] ({trend['category']}) {text}")
    
    def load_to_vector_database(self, trends: List[Dict]) -> bool:
        """Load all trends directly into vector database."""
        if not trends:
            print("❌ No trends to load")
            return False
        
        print(f"💾 Loading {len(trends)} trends into vector database...")
        
        try:
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            run_id = f"direct_load_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            for i, trend in enumerate(trends):
                # Create unique ID
                trend_id = f"{run_id}_{i:04d}"
                
                # Document text
                documents.append(trend['text'])
                
                # Metadata
                metadata = {
                    'category': trend['category'],
                    'score': float(trend['score']),
                    'date': trend['date'],
                    'run_id': run_id,
                    'run_timestamp': datetime.now().isoformat(),
                    'csv_source': Path(trend['csv_source']).name,
                    'load_method': 'direct_load',  # Mark as directly loaded (not graded)
                }
                
                # Add any additional metadata
                for key, value in trend.items():
                    if key not in ['text', 'category', 'score', 'date', 'csv_source', 'row_index']:
                        if value and str(value).strip():
                            metadata[key] = str(value)
                
                metadatas.append(metadata)
                ids.append(trend_id)
            
            # Add to ChromaDB
            self.vector_db.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Successfully loaded {len(trends)} trends with run_id: {run_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load trends to vector database: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_direct_load(self, csv_path: str = None):
        """Run the direct loading workflow."""
        print("⚡ Direct CSV to Vector Database Loader")
        print("="*50)
        print("Loads ALL trends without manual grading - fast and simple!")
        
        # Step 1: Find or load CSV and determine vector DB location
        if not csv_path:
            csv_path, results_dir = self.find_latest_results()
            if not csv_path:
                print("❌ No results CSV found. Run the pipeline first:")
                print("   python scripts/run_parallel_analysis.py 'your query'")
                return False
            print(f"📄 Using latest results: {csv_path}")
            
            # Create vector DB in the same results directory
            vector_db_path = Path(results_dir) / "vector_db"
            print(f"💾 Vector DB will be created at: {vector_db_path}")
            
            # Re-initialize with the specific path
            self.vector_db = TrendsVectorDB(db_path=str(vector_db_path))
            self.db_path = str(vector_db_path)
        else:
            # If specific CSV path provided, put vector DB in same directory
            csv_dir = Path(csv_path).parent
            vector_db_path = csv_dir / "vector_db"
            print(f"📄 Using CSV: {csv_path}")
            print(f"💾 Vector DB will be created at: {vector_db_path}")
            
            # Re-initialize with the specific path
            self.vector_db = TrendsVectorDB(db_path=str(vector_db_path))
            self.db_path = str(vector_db_path)
        
        # Step 2: Load trends
        trends = self.load_trends_from_csv(csv_path)
        if not trends:
            return False
        
        # Step 3: Show summary
        self.show_trends_summary(trends)
        
        # Step 4: Confirm loading
        print(f"\n🚀 Ready to load {len(trends)} trends to vector database")
        proceed = input("👉 Proceed with loading? (y/n): ").strip().lower()
        
        if proceed not in ['y', 'yes']:
            print("👋 Loading cancelled")
            return False
        
        # Step 5: Load to vector database
        success = self.load_to_vector_database(trends)
        
        if success:
            print(f"\n✅ Direct loading complete!")
            print(f"💾 Vector database created at: {self.db_path}")
            print(f"🔍 You can now search trends with: python tools/interactive_search.py")
            
            # Show vector DB stats
            stats = self.vector_db.get_stats()
            print(f"\n📊 Vector Database Stats:")
            print(f"   • Total trends: {stats['total_trends']}")
            print(f"   • Database location: {self.db_path}")
            print(f"   • Categories: {list(stats['categories'].keys())}")
            return True
        
        return False

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("⚡ Direct CSV to Vector Database Loader")
        print("="*50)
        print("Usage:")
        print("  python load_to_vector_db.py auto          - Use latest results CSV")
        print("  python load_to_vector_db.py <csv_path>    - Use specific CSV file")
        print("\nExamples:")
        print("  python load_to_vector_db.py auto")
        print("  python load_to_vector_db.py results/20241201_143022/trend_results.csv")
        print("\n⚡ This bypasses manual grading and loads ALL trends directly!")
        return 1
    
    loader = DirectVectorLoader()
    
    command = sys.argv[1]
    
    if command == 'auto':
        success = loader.run_direct_load()
    else:
        # Treat as CSV path
        csv_path = command
        if not Path(csv_path).exists():
            print(f"❌ CSV file not found: {csv_path}")
            return 1
        success = loader.run_direct_load(csv_path)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Loading cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)