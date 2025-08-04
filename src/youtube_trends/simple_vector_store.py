"""
Simple Vector Store using ChromaDB's built-in embeddings (no OpenAI required)
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import logging

from .config import Config
from .trend_aggregator import TrendEntry, TrendResultsParser

logger = logging.getLogger(__name__)

class SimpleVectorStore:
    """Simple vector store using ChromaDB's built-in embeddings."""
    
    def __init__(self, db_path: str = None, collection_name: str = None):
        """Initialize with ChromaDB's default embedding function."""
        try:
            import chromadb
            from chromadb.config import Settings
            self._chromadb = chromadb
        except ImportError:
            raise Exception("chromadb package required: pip install chromadb")
        
        self.db_path = Path(db_path or "simple_vector_db")
        self.collection_name = collection_name or "trends"
        
        # Create directory
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection (ChromaDB will use default embeddings)
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Connected to existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "YouTube trends with automatic embeddings"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def add_trends_from_runs(self, run_ids: List[str] = None) -> Dict[str, Any]:
        """Add trends from YouTube analysis runs."""
        parser = TrendResultsParser()
        results_dir = Path(Config.RESULTS_BASE_DIR)
        
        if run_ids is None:
            # Discover all runs
            run_ids = []
            if results_dir.exists():
                for item in results_dir.iterdir():
                    if item.is_dir() and (item / "trend_results.csv").exists():
                        run_ids.append(item.name)
        
        if not run_ids:
            return {"success": False, "error": "No runs found"}
        
        all_trends = []
        for run_id in run_ids:
            try:
                run_dir = results_dir / run_id
                trends = parser.parse_run_directory(run_dir)
                all_trends.extend(trends)
            except Exception as e:
                logger.warning(f"Failed to parse run {run_id}: {e}")
        
        if not all_trends:
            return {"success": False, "error": "No trends found"}
        
        # Add to ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for i, trend in enumerate(all_trends):
            ids.append(f"trend_{i}")
            documents.append(trend.text)
            metadatas.append({
                "category": trend.category,
                "trend_score": trend.trend_score,
                "video_title": trend.video_title,
                "channel": trend.channel,
                "run_id": trend.run_id,
                "user_query": trend.user_query
            })
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        return {
            "success": True,
            "trends_added": len(all_trends),
            "runs_processed": len(run_ids)
        }
    
    def search(self, query: str, top_k: int = 10, category: str = None) -> List[Dict[str, Any]]:
        """Search for similar trends."""
        where_clause = None
        if category:
            where_clause = {"category": category}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_clause,
            include=["metadatas", "documents", "distances"]
        )
        
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "similarity": 1.0 - results["distances"][0][i]  # Convert distance to similarity
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        count = self.collection.count()
        
        if count > 0:
            sample = self.collection.get(limit=min(100, count), include=["metadatas"])
            categories = {}
            channels = set()
            runs = set()
            
            if sample["metadatas"]:
                for metadata in sample["metadatas"]:
                    cat = metadata.get("category", "unknown")
                    categories[cat] = categories.get(cat, 0) + 1
                    channels.add(metadata.get("channel", "unknown"))
                    runs.add(metadata.get("run_id", "unknown"))
            
            return {
                "total_trends": count,
                "categories": categories,
                "unique_channels": len(channels),
                "unique_runs": len(runs)
            }
        
        return {"total_trends": 0, "categories": {}, "unique_channels": 0, "unique_runs": 0}
    
    def clear(self) -> bool:
        """Clear all data."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "YouTube trends with automatic embeddings"}
            )
            return True
        except:
            return False

class SimpleTrendSearch:
    """Simple interface for trend searching."""
    
    def __init__(self, vector_store: SimpleVectorStore = None):
        self.store = vector_store or SimpleVectorStore()
    
    def index_all_runs(self):
        """Index all available YouTube analysis runs."""
        return self.store.add_trends_from_runs()
    
    def search_trends(self, query: str, category: str = None, top_k: int = 10):
        """Search for trends matching the query."""
        return self.store.search(query, top_k=top_k, category=category)
    
    def get_trending_topics(self, category: str = None):
        """Get high-scoring trends."""
        results = self.store.search("trending popular emerging viral", top_k=20, category=category)
        # Sort by trend score
        return sorted(results, key=lambda x: x["metadata"].get("trend_score", 0), reverse=True)
    
    def analyze_category(self, category: str):
        """Get all trends in a category."""
        return self.store.search("", top_k=100, category=category)
    
    def get_database_stats(self):
        """Get database statistics."""
        return self.store.get_stats()