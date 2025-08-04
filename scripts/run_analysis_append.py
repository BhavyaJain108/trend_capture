#!/usr/bin/env python3
"""
Run Analysis with Append Option

Simple runner that can either create new analysis or append to existing ones.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pathlib import Path
import subprocess

def show_help():
    print("""
🔄 YouTube Trends Analysis Runner

USAGE:
  python run_analysis_append.py "query"                    # Create new analysis
  python run_analysis_append.py --append "query"           # Append to existing
  python run_analysis_append.py -a "query"                 # Append to existing (short)

EXAMPLES:
  # New analysis (creates results/YYYYMMDD_HHMMSS/)
  python run_analysis_append.py "day in my life nyc vlog"
  
  # Append to existing analysis
  python run_analysis_append.py --append "nyc morning routine vlog"
  python run_analysis_append.py -a "productivity tools nyc"

WORKFLOW:
  New Analysis:     Query → New Results Folder → CSV → Vector DB
  Append Analysis:  Query → Select Existing Folder → Append CSV → Update Vector DB
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return 1
    
    # Parse arguments
    if sys.argv[1] in ['--append', '-a']:
        if len(sys.argv) < 3:
            print("❌ Please provide a query for append mode")
            print("Usage: python run_analysis_append.py --append \"your query\"")
            return 1
        
        query = sys.argv[2]
        print(f"🔄 Append Mode: \"{query}\"")
        
        # Use the append tool
        result = subprocess.run([
            sys.executable, 
            "tools/append_analysis.py", 
            query
        ], cwd=os.path.dirname(__file__))
        
        return result.returncode
    
    elif sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
        return 0
    
    else:
        # Regular new analysis
        query = sys.argv[1]
        print(f"🚀 New Analysis: \"{query}\"")
        
        # Use the regular pipeline
        result = subprocess.run([
            sys.executable, 
            "scripts/run_parallel_analysis.py", 
            query
        ], cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print(f"\n✅ Analysis complete!")
            print(f"🎯 Next steps:")
            print(f"   python tools/load_to_vector_db.py auto    # Load to vector DB")
            print(f"   python tools/search_results.py            # Search results")
        
        return result.returncode

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Analysis cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        exit(1)