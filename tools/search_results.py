#!/usr/bin/env python3
"""
Search Results - Interactive Vector Database Search

Finds and searches vector databases in results folders.
Automatically detects the most recent results or lets you choose.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.trends_vector_db import TrendsVectorDB

def find_vector_databases():
    """Find all vector databases in results folders."""
    results_dir = Path("results")
    
    if not results_dir.exists():
        return []
    
    vector_dbs = []
    for result_dir in results_dir.iterdir():
        if result_dir.is_dir():
            vector_db_path = result_dir / "vector_db"
            if vector_db_path.exists():
                # Check if it has data
                try:
                    test_db = TrendsVectorDB(db_path=str(vector_db_path))
                    stats = test_db.get_stats()
                    if stats['total_trends'] > 0:
                        vector_dbs.append({
                            'path': str(vector_db_path),
                            'results_dir': str(result_dir),
                            'name': result_dir.name,
                            'trends_count': stats['total_trends'],
                            'categories': list(stats['categories'].keys())
                        })
                except:
                    continue
    
    # Sort by most recent
    vector_dbs.sort(key=lambda x: x['name'], reverse=True)
    return vector_dbs

def select_vector_database(vector_dbs):
    """Let user select which vector database to search."""
    if not vector_dbs:
        print("❌ No vector databases found in results folders.")
        print("💡 Run: python tools/load_to_vector_db.py auto")
        return None
    
    if len(vector_dbs) == 1:
        db = vector_dbs[0]
        print(f"📊 Using vector database: {db['name']} ({db['trends_count']} trends)")
        return db
    
    print(f"📂 Found {len(vector_dbs)} vector databases:")
    for i, db in enumerate(vector_dbs, 1):
        print(f"   {i}. {db['name']} - {db['trends_count']} trends")
        print(f"      Categories: {', '.join(db['categories'][:3])}{'...' if len(db['categories']) > 3 else ''}")
    
    while True:
        try:
            choice = input(f"\n👉 Select database (1-{len(vector_dbs)}, or Enter for most recent): ").strip()
            
            if not choice:  # Default to most recent
                return vector_dbs[0]
            
            idx = int(choice) - 1
            if 0 <= idx < len(vector_dbs):
                return vector_dbs[idx]
            else:
                print(f"❌ Please enter a number between 1 and {len(vector_dbs)}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            return None

def print_results(results, title="Results"):
    """Print search results in a nice format."""
    if not results:
        print("   No results found.")
        return
    
    print(f"\n   {title} ({len(results)} found):")
    for i, result in enumerate(results, 1):
        score = result['metadata']['score']
        date = result['metadata']['date']
        category = result['metadata']['category']
        similarity = result.get('similarity', 0)
        text = result['text'][:70] + "..." if len(result['text']) > 70 else result['text']
        print(f"   {i}. [{date}] [score:{score:+.1f}, sim:{similarity:.2f}] ({category})")
        print(f"      {text}")

def main():
    print("🔍 Search Results - Interactive Vector Database Search")
    print("="*60)
    
    # Find available vector databases
    print("🔍 Looking for vector databases in results folders...")
    vector_dbs = find_vector_databases()
    
    # Select database
    selected_db = select_vector_database(vector_dbs)
    if not selected_db:
        return 1
    
    # Initialize database
    print(f"\n📊 Loading database: {selected_db['name']}")
    db = TrendsVectorDB(db_path=selected_db['path'])
    
    # Show stats
    stats = db.get_stats()
    print(f"   • Total trends: {stats['total_trends']}")
    print(f"   • Categories: {list(stats['categories'].keys())}")
    print(f"   • Location: {selected_db['path']}")
    
    print(f"\n" + "="*60)
    print("💡 Commands:")
    print("  search <query>                    - Basic search")
    print("  search <query> in <category>      - Search in category")  
    print("  search <query> after <date>       - Search after date")
    print("  trending                          - Show trending topics")
    print("  trending in <category>            - Trending in category")
    print("  analyze <category>                - Analyze category")
    print("  stats                             - Database stats")
    print("  help                              - Show commands")
    print("  quit                              - Exit")
    print("="*60)
    
    while True:
        try:
            command = input(f"\n🔍 Enter command: ").strip()
            
            if not command or command.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if command.lower() == 'help':
                print("\n💡 Available commands:")
                print("  search AI tools")
                print("  search python in early_adopter_products")
                print("  search machine learning after 2024-08-01")
                print("  trending")
                print("  trending in emerging_topics")
                print("  analyze behavioral_patterns")
                print("  stats")
                continue
            
            if command.lower() == 'stats':
                stats = db.get_stats()
                print(f"\n📊 Database Statistics:")
                print(f"   Total trends: {stats['total_trends']}")
                print(f"   Average score: {stats['score_distribution']['average']:.2f}")
                print(f"   Categories: {stats['categories']}")
                continue
            
            if command.lower().startswith('trending'):
                parts = command.split()
                category = None
                if 'in' in parts and len(parts) > 2:
                    category = parts[parts.index('in') + 1]
                
                trending = db.get_trending_topics(category=category, top_k=5, min_score=0.6)
                title = f"Trending Topics" + (f" in {category}" if category else "")
                print_results(trending, title)
                continue
            
            if command.lower().startswith('analyze'):
                parts = command.split()
                if len(parts) < 2:
                    print("Usage: analyze <category>")
                    continue
                
                category = parts[1]
                analysis = db.analyze_category(category)
                if "error" in analysis:
                    print(f"   {analysis['error']}")
                else:
                    print(f"\n🔬 Analysis of '{category}':")
                    print(f"   Total trends: {analysis['total_trends']}")
                    print(f"   Average score: {analysis['score_stats']['average']:.2f}")
                    print(f"   High-scoring trends: {analysis['score_stats']['high_score_count']}")
                    print_results(analysis['top_trends'][:3], "Top trends")
                continue
            
            if command.lower().startswith('search'):
                # Parse search command
                parts = command.split()
                if len(parts) < 2:
                    print("Usage: search <query> [in <category>] [after <date>]")
                    continue
                
                # Extract query
                query_parts = []
                category = None
                after_date = None
                
                i = 1
                while i < len(parts):
                    if parts[i].lower() == 'in' and i + 1 < len(parts):
                        category = parts[i + 1]
                        i += 2
                    elif parts[i].lower() == 'after' and i + 1 < len(parts):
                        after_date = parts[i + 1]
                        i += 2
                    else:
                        query_parts.append(parts[i])
                        i += 1
                
                query = ' '.join(query_parts)
                
                if not query:
                    print("Please provide a search query")
                    continue
                
                # Perform search
                results = db.search(
                    query=query,
                    category=category,
                    after_date=after_date,
                    top_k=5
                )
                
                title = f"Search: '{query}'"
                if category:
                    title += f" in {category}"
                if after_date:
                    title += f" after {after_date}"
                
                print_results(results, title)
                continue
            
            print("Unknown command. Type 'help' for available commands.")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        exit(0)