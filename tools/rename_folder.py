#!/usr/bin/env python3
"""
Rename Results Folder

Simple tool to rename results folders from timestamp to meaningful names.
"""

import sys
import os
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        print("📝 Rename Results Folder")
        print("="*30)
        print("Usage: python rename_folder.py <old_name> <new_name>")
        print("\nExamples:")
        print("  python rename_folder.py 20250803_230008 nyc_vlogs")
        print("  python rename_folder.py 20250804_120000 ai_productivity_tools")
        return 1
    
    old_name = sys.argv[1]
    new_name = sys.argv[2]
    
    results_dir = Path("results")
    old_path = results_dir / old_name
    new_path = results_dir / new_name
    
    # Check if old folder exists
    if not old_path.exists():
        print(f"❌ Folder not found: results/{old_name}")
        return 1
    
    # Check if new name already exists
    if new_path.exists():
        print(f"❌ Folder already exists: results/{new_name}")
        return 1
    
    # Rename the folder
    try:
        old_path.rename(new_path)
        print(f"✅ Renamed: results/{old_name} → results/{new_name}")
        return 0
    except Exception as e:
        print(f"❌ Failed to rename: {e}")
        return 1

if __name__ == "__main__":
    exit(main())