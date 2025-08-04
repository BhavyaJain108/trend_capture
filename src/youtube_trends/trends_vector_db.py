"""
YouTube Trends Vector Database - Simple & Clean

Handles vector storage and search for YouTube trend analysis results.
Uses ChromaDB with built-in embeddings (no API keys required).
"""

import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from .config import Config

logger = logging.getLogger(__name__)

class TrendsVectorDB:
    """Simple vector database for YouTube trends analysis results."""
    
    def __init__(self, db_path: str = None):
        """Initialize the vector database."""
        try:
            import chromadb
            from chromadb.config import Settings
            self._chromadb = chromadb
        except ImportError:
            raise Exception("ChromaDB required: pip install chromadb")
        
        # Setup database path
        self.db_path = Path(db_path or Config.VECTOR_DB_PATH)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection_name = "youtube_trends"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Connected to existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "YouTube trends with automatic embeddings"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def load_trends_from_run(self, run_id: str) -> Dict[str, Any]:
        """Load trends from a single analysis run."""
        results_dir = Path(Config.RESULTS_BASE_DIR)
        run_dir = results_dir / run_id
        trends_file = run_dir / "trend_results.csv"
        
        if not trends_file.exists():
            return {"success": False, "error": f"No trend_results.csv found in {run_dir}"}
        
        try:
            # Read the CSV file
            df = pd.read_csv(trends_file)
            
            # Check if file is empty
            if df.empty:
                return {"success": False, "error": "Empty CSV file"}
            
            # Validate expected columns
            required_cols = ['date', 'category', 'information', 'score']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {"success": False, "error": f"Missing columns: {missing_cols}"}
            
            # Filter out low-scoring trends if needed
            df = df[df['score'] >= Config.TREND_MIN_SCORE_THRESHOLD]
            
            if df.empty:
                return {"success": False, "error": "No trends above score threshold"}
            
            # Prepare data for ChromaDB
            ids = [f"{run_id}_{i}" for i in range(len(df))]
            documents = df['information'].astype(str).tolist()
            metadatas = []
            
            for _, row in df.iterrows():
                metadata = {
                    "date": str(row['date']),
                    "category": str(row['category']),
                    "score": float(row['score']),
                    "run_id": run_id
                }
                metadatas.append(metadata)
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            return {
                "success": True,
                "trends_added": len(df),
                "run_id": run_id
            }
            
        except pd.errors.EmptyDataError:
            return {"success": False, "error": "Empty CSV file"}
        except Exception as e:
            return {"success": False, "error": f"Failed to load run {run_id}: {str(e)}"}
    
    def load_all_available_runs(self) -> Dict[str, Any]:
        """Load trends from all available analysis runs."""
        results_dir = Path(Config.RESULTS_BASE_DIR)
        
        if not results_dir.exists():
            return {"success": False, "error": f"Results directory not found: {results_dir}"}
        
        # Find all run directories with trend_results.csv
        run_dirs = []
        for item in results_dir.iterdir():
            if item.is_dir() and (item / "trend_results.csv").exists():
                run_dirs.append(item.name)
        
        if not run_dirs:
            return {"success": False, "error": "No run directories with trend_results.csv found"}
        
        # Load each run
        total_added = 0
        successful_runs = 0
        failed_runs = []
        
        for run_id in run_dirs:
            result = self.load_trends_from_run(run_id)
            if result["success"]:
                total_added += result["trends_added"]
                successful_runs += 1
                logger.info(f"Loaded {result['trends_added']} trends from {run_id}")
            else:
                failed_runs.append(run_id)
                logger.warning(f"Failed to load {run_id}: {result['error']}")
        
        return {
            "success": successful_runs > 0,
            "total_trends_added": total_added,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "total_runs_found": len(run_dirs)
        }
    
    def search(self, 
               query: str, 
               top_k: int = 10, 
               category: str = None,
               min_score: float = None,
               after_date: str = None,
               before_date: str = None) -> List[Dict[str, Any]]:
        """Search for similar trends.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            category: Filter by category (e.g., 'early_adopter_products')
            min_score: Minimum trend score (e.g., 0.5)
            after_date: Only include trends after this date (YYYY-MM-DD format)
            before_date: Only include trends before this date (YYYY-MM-DD format)
        """
        # ChromaDB has limitations with complex where clauses, so we'll use simple filtering
        # and do more complex filtering post-search
        where_clause = None
        if category:
            where_clause = {"category": category}
        elif min_score is not None:
            where_clause = {"score": {"$gte": min_score}}
        
        # Get more results if we need to filter (since we'll filter post-search)
        search_limit = top_k * 3 if (after_date or before_date or min_score) else top_k
        
        # Perform search
        results = self.collection.query(
            query_texts=[query],
            n_results=search_limit,
            where=where_clause,
            include=["metadatas", "documents", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "similarity": 1.0 - results["distances"][0][i]  # Convert to similarity
                }
                formatted_results.append(result)
        
        # Apply post-search filtering
        if after_date or before_date:
            formatted_results = self._filter_by_date(formatted_results, after_date, before_date)
        
        # Apply score filtering if not already done in ChromaDB query
        if min_score is not None and not where_clause:
            formatted_results = [r for r in formatted_results if r["metadata"].get("score", 0) >= min_score]
        
        # Apply category filtering if we used score filtering in ChromaDB query
        if category and min_score is not None:
            formatted_results = [r for r in formatted_results if r["metadata"].get("category") == category]
        
        # Return only requested number of results
        return formatted_results[:top_k]
    
    def _filter_by_date(self, results: List[Dict[str, Any]], after_date: str = None, before_date: str = None) -> List[Dict[str, Any]]:
        """Filter results by date range, handling various date formats."""
        from datetime import datetime
        
        def parse_date(date_str: str) -> datetime:
            """Parse various date formats to datetime."""
            date_formats = [
                "%Y-%m-%d",      # 2024-08-01
                "%m/%d/%y",      # 10/18/23
                "%m/%d/%Y",      # 10/18/2023
                "%Y-%m-%d",      # 2024-08-01
                "%d/%m/%Y",      # 18/10/2023
                "%d-%m-%Y",      # 18-10-2023
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If no format works, try to handle partial dates
            try:
                # Handle formats like "2019-09-29"
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                # Return a very old date if parsing fails
                return datetime(1900, 1, 1)
        
        filtered_results = []
        
        # Parse filter dates
        after_dt = parse_date(after_date) if after_date else None
        before_dt = parse_date(before_date) if before_date else None
        
        for result in results:
            result_date_str = result["metadata"].get("date", "")
            if not result_date_str:
                continue
                
            result_dt = parse_date(result_date_str)
            
            # Apply date filters
            if after_dt and result_dt < after_dt:
                continue
            if before_dt and result_dt > before_dt:
                continue
                
            filtered_results.append(result)
        
        return filtered_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        count = self.collection.count()
        
        if count == 0:
            return {
                "total_trends": 0,
                "categories": {},
                "score_distribution": {},
                "runs": {}
            }
        
        # Get sample for analysis
        sample_size = min(1000, count)
        sample = self.collection.get(
            limit=sample_size,
            include=["metadatas"]
        )
        
        # Analyze metadata
        categories = {}
        runs = {}
        scores = []
        
        if sample["metadatas"]:
            for metadata in sample["metadatas"]:
                # Count categories
                category = metadata.get("category", "unknown")
                categories[category] = categories.get(category, 0) + 1
                
                # Count runs
                run_id = metadata.get("run_id", "unknown")
                runs[run_id] = runs.get(run_id, 0) + 1
                
                # Collect scores
                score = metadata.get("score", 0)
                scores.append(score)
        
        # Score distribution
        score_dist = {
            "high (>0.7)": len([s for s in scores if s > 0.7]),
            "medium (0.3-0.7)": len([s for s in scores if 0.3 <= s <= 0.7]),
            "low (<0.3)": len([s for s in scores if s < 0.3]),
            "average": sum(scores) / len(scores) if scores else 0
        }
        
        return {
            "total_trends": count,
            "categories": categories,
            "score_distribution": score_dist,
            "runs": runs,
            "sample_size": sample_size
        }
    
    def get_trending_topics(self, 
                          category: str = None, 
                          top_k: int = 20,
                          min_score: float = 0.5,
                          after_date: str = None,
                          before_date: str = None) -> List[Dict[str, Any]]:
        """Get trending topics (high-scoring trends)."""
        # Search for generally trending terms
        results = self.search(
            query="trending popular emerging viral new",
            top_k=top_k * 2,  # Get more to filter
            category=category,
            min_score=min_score,
            after_date=after_date,
            before_date=before_date
        )
        
        # Sort by trend score and return top results
        sorted_results = sorted(
            results, 
            key=lambda x: x["metadata"]["score"], 
            reverse=True
        )
        
        return sorted_results[:top_k]
    
    def analyze_category(self, category: str) -> Dict[str, Any]:
        """Analyze all trends in a specific category."""
        # Get all trends in category (use empty query with category filter)
        results = self.search(
            query="",  # Empty query to get broad results
            top_k=1000,  # Large number to get all
            category=category
        )
        
        if not results:
            return {"error": f"No trends found for category: {category}"}
        
        # Analyze the results
        scores = [r["metadata"]["score"] for r in results]
        runs = set(r["metadata"]["run_id"] for r in results)
        
        return {
            "category": category,
            "total_trends": len(results),
            "score_stats": {
                "average": sum(scores) / len(scores),
                "max": max(scores),
                "min": min(scores),
                "high_score_count": len([s for s in scores if s > 0.7])
            },
            "runs_represented": len(runs),
            "top_trends": sorted(results, key=lambda x: x["metadata"]["score"], reverse=True)[:10]
        }
    
    def clear_database(self) -> bool:
        """Clear all data from the database."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "YouTube trends with automatic embeddings"}
            )
            logger.info("Database cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            return False