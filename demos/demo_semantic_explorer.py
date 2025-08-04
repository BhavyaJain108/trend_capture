#!/usr/bin/env python3
"""
Semantic Dense Region Explorer Demo

Discovers dense semantic regions using proper density-based clustering algorithms.
No arbitrary thresholds - uses DBSCAN, OPTICS, and adaptive methods.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_trends.trends_vector_db import TrendsVectorDB
from youtube_trends.semantic_explorer import SemanticRegionExplorer

def print_region_summary(region, index):
    """Print a formatted summary of a dense region."""
    print(f"\n🔍 Region {index + 1} (Cluster {region['cluster_id']}):")
    print(f"   📊 Size: {region['size']} trends")
    print(f"   🎯 Density Score: {region['density_score']:.3f}")
    print(f"   🏷️  Key Themes: {', '.join(region['themes'][:3])}")
    
    # Category breakdown
    categories = region['category_distribution']
    top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:2]
    cat_summary = ', '.join([f"{cat}({count})" for cat, count in top_categories])
    print(f"   📂 Top Categories: {cat_summary}")
    
    # Score stats
    score_stats = region['score_stats']
    print(f"   ⭐ Avg Score: {score_stats['mean']:.2f} (range: {score_stats['min']:.1f}-{score_stats['max']:.1f})")
    
    # Date range
    date_range = region['date_range']
    print(f"   📅 Date Range: {date_range['earliest']} to {date_range['latest']}")
    
    # Sample trends
    print(f"   📝 Sample Trends:")
    for i, sample in enumerate(region['sample_trends'][:2], 1):
        text = sample['text'][:60] + "..." if len(sample['text']) > 60 else sample['text']
        print(f"      {i}. [{sample['score']:+.1f}] {text}")

def main():
    print("🗺️  Semantic Dense Region Explorer")
    print("=" * 50)
    print("Using proper density-based clustering algorithms (DBSCAN, OPTICS)")
    print("No arbitrary thresholds - discovers natural dense regions in vector space")
    
    try:
        # Initialize
        print("\n1. Initializing vector database and semantic explorer...")
        db = TrendsVectorDB()
        explorer = SemanticRegionExplorer(db)
        
        # Check database
        stats = db.get_stats()
        print(f"   📊 Database contains {stats['total_trends']} trends")
        
        if stats['total_trends'] == 0:
            print("   ❌ No trends found. Run the vector database demo first.")
            return 1
        
        print(f"   📂 Categories: {list(stats['categories'].keys())}")
        
        # Method 1: DBSCAN
        print(f"\n2. 🔬 Method 1: DBSCAN Clustering")
        print("   DBSCAN finds dense regions and identifies outliers automatically...")
        
        dbscan_result = explorer.discover_dense_regions_dbscan()
        
        print(f"   ✅ Found {dbscan_result['n_clusters']} dense regions")
        print(f"   📊 {dbscan_result['noise_points']} noise points ({dbscan_result['noise_ratio']:.1%})")
        print(f"   🧠 Using {dbscan_result['embedding_dimension']}-dimensional embeddings")
        
        # Show top regions
        print(f"\n   🏆 Top 3 Densest Regions (DBSCAN):")
        for i, region in enumerate(dbscan_result['dense_regions'][:3]):
            print_region_summary(region, i)
        
        # Method 2: OPTICS  
        print(f"\n" + "="*50)
        print(f"3. 🔬 Method 2: OPTICS Clustering")
        print("   OPTICS handles varying densities better than DBSCAN...")
        
        optics_result = explorer.discover_dense_regions_optics()
        
        print(f"   ✅ Found {optics_result['n_clusters']} dense regions")
        print(f"   📊 {optics_result['noise_points']} noise points ({optics_result['noise_ratio']:.1%})")
        
        # Compare with DBSCAN
        print(f"\n   📊 Comparison with DBSCAN:")
        print(f"      DBSCAN: {dbscan_result['n_clusters']} clusters, {dbscan_result['noise_ratio']:.1%} noise")
        print(f"      OPTICS: {optics_result['n_clusters']} clusters, {optics_result['noise_ratio']:.1%} noise")
        
        # Show top OPTICS regions
        print(f"\n   🏆 Top 3 Densest Regions (OPTICS):")
        for i, region in enumerate(optics_result['dense_regions'][:3]):
            print_region_summary(region, i)
        
        # Method 3: Adaptive
        print(f"\n" + "="*50)
        print(f"4. 🧠 Method 3: Adaptive Algorithm Selection")
        print("   Tries multiple algorithms and picks the best based on silhouette score...")
        
        adaptive_result = explorer.discover_dense_regions_adaptive()
        
        print(f"   ✅ Best algorithm: {adaptive_result.get('algorithm_comparison', {}).get('best_algorithm', 'Unknown')}")
        
        if 'algorithm_comparison' in adaptive_result:
            comp = adaptive_result['algorithm_comparison']
            print(f"   📊 Silhouette Score: {comp['best_silhouette_score']:.3f}")
            print(f"   ⚙️  Best Parameters: {comp['best_parameters']}")
            print(f"   🔍 Algorithms Tried: {comp['algorithms_tried']}")
        
        print(f"\n   ✅ Final Result: {adaptive_result['n_clusters']} dense regions")
        print(f"   📊 {adaptive_result['noise_points']} noise points ({adaptive_result['noise_ratio']:.1%})")
        
        # Detailed analysis of top regions
        print(f"\n" + "="*50)
        print(f"5. 📋 Detailed Analysis of Top Dense Regions:")
        
        for i, region in enumerate(adaptive_result['dense_regions'][:5], 1):
            print(f"\n{'='*60}")
            print(f"🎯 DENSE REGION #{i}")
            print(f"{'='*60}")
            
            print(f"📊 Cluster ID: {region['cluster_id']}")
            print(f"📏 Size: {region['size']} trends ({region['size']/stats['total_trends']:.1%} of total)")
            print(f"🎯 Density Score: {region['density_score']:.4f}")
            
            print(f"\n🏷️  Semantic Themes:")
            for j, theme in enumerate(region['themes'][:5], 1):
                print(f"   {j}. {theme}")
            
            print(f"\n📂 Category Distribution:")
            for category, count in region['category_distribution'].items():
                percentage = count / region['size'] * 100
                print(f"   • {category}: {count} trends ({percentage:.1f}%)")
            
            print(f"\n⭐ Score Statistics:")
            stats_info = region['score_stats']
            print(f"   • Average: {stats_info['mean']:.3f}")
            print(f"   • Range: {stats_info['min']:.2f} to {stats_info['max']:.2f}")
            print(f"   • Std Dev: {stats_info['std']:.3f}")
            
            print(f"\n📅 Temporal Distribution:")
            date_info = region['date_range']
            print(f"   • Date Range: {date_info['earliest']} → {date_info['latest']}")
            print(f"   • Unique Dates: {date_info['unique_dates']}")
            
            print(f"\n📝 Representative Trends:")
            for j, trend in enumerate(region['sample_trends'], 1):
                print(f"   {j}. [{trend['score']:+.2f}] ({trend['category']})")
                print(f"      {trend['text']}")
        
        # Summary insights
        print(f"\n" + "="*50)
        print(f"🎯 KEY INSIGHTS:")
        print(f"=" * 50)
        
        top_region = adaptive_result['dense_regions'][0]
        print(f"🥇 Densest Region: '{', '.join(top_region['themes'][:2])}' ({top_region['size']} trends)")
        
        # Find most common themes across all regions
        all_themes = []
        for region in adaptive_result['dense_regions']:
            all_themes.extend(region['themes'])
        
        from collections import Counter
        theme_counts = Counter(all_themes)
        print(f"🔥 Most Common Themes Across All Regions:")
        for theme, count in theme_counts.most_common(5):
            print(f"   • {theme}: appears in {count} regions")
        
        # Category analysis
        region_categories = {}
        for region in adaptive_result['dense_regions']:
            for category, count in region['category_distribution'].items():
                if category not in region_categories:
                    region_categories[category] = []
                region_categories[category].append(count)
        
        print(f"\n📂 Category Concentration:")
        for category, counts in region_categories.items():
            avg_size = sum(counts) / len(counts)
            print(f"   • {category}: avg {avg_size:.1f} trends per region")
        
        print(f"\n✅ Dense region discovery completed!")
        print(f"💡 Use these regions to:")
        print(f"   • Discover unexpected semantic clusters")
        print(f"   • Find related trends you didn't know existed")  
        print(f"   • Understand the main themes in your data")
        print(f"   • Guide targeted searches in specific regions")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Exploration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())