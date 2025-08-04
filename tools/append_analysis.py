#!/usr/bin/env python3
"""
Append Analysis Tool

Run additional analysis and append results to an existing results folder.
Allows you to expand existing analyses with new queries.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.parallel_pipeline import ParallelYouTubeTrendsPipeline
from youtube_trends.trends_vector_db import TrendsVectorDB
import json
from datetime import datetime

def find_results_folders():
    """Find all existing results folders."""
    results_dir = Path("results")
    
    if not results_dir.exists():
        return []
    
    folders = []
    for result_dir in results_dir.iterdir():
        if result_dir.is_dir():
            # Check if it has the expected files
            trend_file = result_dir / "trend_results.csv"
            if trend_file.exists():
                # Try to get some info about this analysis
                info = {
                    'path': str(result_dir),
                    'name': result_dir.name,
                    'trend_file': str(trend_file)
                }
                
                # Try to read the original query
                prompt_file = result_dir / "prompt.txt"
                if prompt_file.exists():
                    try:
                        info['original_query'] = prompt_file.read_text().strip()
                    except:
                        info['original_query'] = "Unknown"
                else:
                    info['original_query'] = "Unknown"
                
                # Count existing trends
                try:
                    import pandas as pd
                    df = pd.read_csv(trend_file)
                    info['trend_count'] = len(df)
                except:
                    info['trend_count'] = 0
                
                folders.append(info)
    
    # Sort by most recent
    folders.sort(key=lambda x: x['name'], reverse=True)
    return folders

def select_results_folder(folders):
    """Let user select which results folder to append to."""
    if not folders:
        print("❌ No existing results folders found.")
        print("💡 Run a regular analysis first: python scripts/run_parallel_analysis.py 'query'")
        return None
    
    print(f"📂 Found {len(folders)} existing results folders:")
    for i, folder in enumerate(folders, 1):
        print(f"   {i}. {folder['name']} - {folder['trend_count']} trends")
        print(f"      Original query: \"{folder['original_query'][:60]}{'...' if len(folder['original_query']) > 60 else ''}\"")
    
    while True:
        try:
            choice = input(f"\n👉 Select folder to append to (1-{len(folders)}): ").strip()
            
            if not choice:
                print("❌ Please select a folder")
                continue
            
            idx = int(choice) - 1
            if 0 <= idx < len(folders):
                return folders[idx]
            else:
                print(f"❌ Please enter a number between 1 and {len(folders)}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            return None

def run_append_analysis(results_folder, new_query):
    """Run analysis and append to existing results folder."""
    print(f"🔄 Appending analysis to: {results_folder['name']}")
    print(f"📂 Target folder: {results_folder['path']}")
    print(f"🔍 New query: \"{new_query}\"")
    
    try:
        # Initialize pipeline with parent directory (results/)
        # The pipeline will create a new timestamped folder, so we need to work around this
        pipeline = ParallelYouTubeTrendsPipeline(results_base_dir="results")
        
        # Run the analysis to get new trends
        print(f"\n🚀 Running analysis...")
        results = pipeline.run_analysis(new_query)
        
        if not results['success']:
            return False
        
        # Now we need to move the new results into the existing folder
        print(f"🔄 Moving results to existing folder...")
        
        # Get the new results files
        new_results_dir = Path(results['results_dir'])
        new_trend_file = new_results_dir / "trend_results.csv"
        new_youtube_log = new_results_dir / "youtube_log.csv"
        
        # Append to existing files
        existing_trend_file = Path(results_folder['path']) / "trend_results.csv"
        existing_youtube_log = Path(results_folder['path']) / "youtube_log.csv"
        
        # Append trend results (skip header from new file)
        if new_trend_file.exists():
            import pandas as pd
            new_df = pd.read_csv(new_trend_file)
            new_df.to_csv(existing_trend_file, mode='a', header=False, index=False)
            print(f"✅ Appended {len(new_df)} new trends")
        
        # Append youtube log (skip header from new file)
        if new_youtube_log.exists():
            import pandas as pd
            new_df = pd.read_csv(new_youtube_log)
            if existing_youtube_log.exists():
                new_df.to_csv(existing_youtube_log, mode='a', header=False, index=False)
            else:
                new_df.to_csv(existing_youtube_log, index=False)
        
        # Clean up the temporary results directory
        import shutil
        shutil.rmtree(new_results_dir)
        
        # Update results info
        results['results_file'] = str(existing_trend_file)
        results['results_dir'] = results_folder['path']
        
        if results['success']:
            print(f"✅ Analysis complete!")
            print(f"📊 Found {results.get('total_insights', 0)} new trends")
            print(f"📁 Appended to: {results['results_file']}")
            
            # Update the query log
            query_log_file = Path(results_folder['path']) / "queries_log.txt"
            with open(query_log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{datetime.now().isoformat()}: {new_query}")
            
            return True
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"💥 Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_vector_database(results_folder):
    """Update the vector database with new trends."""
    vector_db_path = Path(results_folder['path']) / "vector_db"
    
    if not vector_db_path.exists():
        print("📊 No existing vector database found - will create new one")
        return load_all_to_vector_db(results_folder)
    
    print(f"🔄 Updating existing vector database...")
    
    # For now, we'll reload everything to keep it simple
    # In the future, this could be optimized to only add new trends
    return load_all_to_vector_db(results_folder)

def load_all_to_vector_db(results_folder):
    """Load/reload all trends to vector database."""
    from load_to_vector_db import DirectVectorLoader
    
    vector_db_path = Path(results_folder['path']) / "vector_db"
    trend_file = Path(results_folder['path']) / "trend_results.csv"
    
    print(f"💾 Loading all trends to vector database...")
    
    try:
        # Use the direct loader with specific paths
        loader = DirectVectorLoader(db_path=str(vector_db_path))
        
        # Load trends from the CSV
        trends = loader.load_trends_from_csv(str(trend_file))
        if not trends:
            print("❌ No trends to load")
            return False
        
        # Clear existing database and reload everything
        loader.vector_db.clear_database()
        success = loader.load_to_vector_database(trends)
        
        if success:
            print(f"✅ Vector database updated with {len(trends)} total trends")
            return True
        else:
            print("❌ Failed to update vector database")
            return False
    
    except Exception as e:
        print(f"💥 Error updating vector database: {e}")
        return False

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("🔄 Append Analysis Tool")
        print("="*40)
        print("Add new trends to existing results folders")
        print("\nUsage:")
        print("  python append_analysis.py \"new search query\"")
        print("\nExamples:")
        print("  python append_analysis.py \"productivity apps 2024\"")
        print("  python append_analysis.py \"morning routine tools\"")
        print("\nThis will:")
        print("  1. Show existing results folders")
        print("  2. Let you choose which one to append to")
        print("  3. Run analysis with new query")
        print("  4. Append results to chosen folder")
        print("  5. Update vector database")
        return 1
    
    new_query = sys.argv[1]
    print(f"🔄 Append Analysis: \"{new_query}\"")
    print("="*50)
    
    # Step 1: Find existing results folders
    print("🔍 Looking for existing results folders...")
    folders = find_results_folders()
    
    # Step 2: Select folder
    selected_folder = select_results_folder(folders)
    if not selected_folder:
        return 1
    
    print(f"\n✅ Selected: {selected_folder['name']}")
    print(f"📊 Current trends: {selected_folder['trend_count']}")
    print(f"📝 Original query: \"{selected_folder['original_query']}\"")
    
    # Step 3: Confirm append
    confirm = input(f"\n👉 Append new analysis to this folder? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("👋 Append cancelled")
        return 0
    
    # Step 4: Run append analysis
    success = run_append_analysis(selected_folder, new_query)
    if not success:
        print("❌ Append analysis failed")
        return 1
    
    # Step 5: Update vector database
    print(f"\n🔄 Updating vector database...")
    db_success = update_vector_database(selected_folder)
    
    if db_success:
        print(f"\n🎉 Append complete!")
        print(f"📂 Results folder: {selected_folder['path']}")
        print(f"🔍 Search with: python tools/search_results.py")
    else:
        print(f"\n⚠️  Analysis appended but vector database update failed")
        print(f"💡 Try: python tools/load_to_vector_db.py {selected_folder['path']}/trend_results.csv")
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Append cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)