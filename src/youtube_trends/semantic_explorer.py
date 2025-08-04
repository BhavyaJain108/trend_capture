"""
Semantic Dense Region Explorer

Uses proper density-based algorithms to discover dense semantic regions
in the vector space without arbitrary thresholds.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sklearn.cluster import DBSCAN, OPTICS
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score
from collections import Counter
import logging

from .trends_vector_db import TrendsVectorDB

logger = logging.getLogger(__name__)


class SemanticRegionExplorer:
    """Discovers dense semantic regions using density-based clustering algorithms."""
    
    def __init__(self, vector_db: TrendsVectorDB):
        self.db = vector_db
        self.trends_cache = None
        self.embeddings_cache = None
    
    def _get_all_trends_with_embeddings(self) -> Tuple[List[Dict], np.ndarray]:
        """Get all trends and extract their embeddings from ChromaDB."""
        if self.trends_cache is not None and self.embeddings_cache is not None:
            return self.trends_cache, self.embeddings_cache
        
        # Get all trends from ChromaDB
        all_results = self.db.collection.get(
            include=["documents", "metadatas", "embeddings"]
        )
        
        if not all_results["ids"]:
            raise ValueError("No trends found in database")
        
        # Format trends
        trends = []
        embeddings = []
        
        for i in range(len(all_results["ids"])):
            trend = {
                "id": all_results["ids"][i],
                "text": all_results["documents"][i],
                "metadata": all_results["metadatas"][i]
            }
            trends.append(trend)
            embeddings.append(all_results["embeddings"][i])
        
        self.trends_cache = trends
        self.embeddings_cache = np.array(embeddings)
        
        logger.info(f"Loaded {len(trends)} trends with {self.embeddings_cache.shape[1]}-dim embeddings")
        return trends, self.embeddings_cache
    
    def discover_dense_regions_dbscan(self, 
                                    min_samples: int = None,
                                    eps: float = None) -> Dict[str, Any]:
        """
        Use DBSCAN to find dense regions in semantic space.
        
        DBSCAN finds clusters of varying density and identifies outliers.
        It doesn't require pre-specifying number of clusters.
        """
        trends, embeddings = self._get_all_trends_with_embeddings()
        
        # Auto-determine parameters if not provided
        if min_samples is None:
            # Rule of thumb: min_samples = 2 * dimensions, but capped
            min_samples = min(max(5, 2 * embeddings.shape[1] // 100), 20)
        
        if eps is None:
            # Use k-distance graph method to find optimal eps
            eps = self._estimate_eps(embeddings, min_samples)
        
        logger.info(f"Running DBSCAN with eps={eps:.4f}, min_samples={min_samples}")
        
        # Apply DBSCAN
        clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        cluster_labels = clustering.fit_predict(embeddings)
        
        return self._analyze_clusters(trends, embeddings, cluster_labels, "DBSCAN")
    
    def discover_dense_regions_optics(self, 
                                    min_samples: int = None,
                                    xi: float = 0.05) -> Dict[str, Any]:
        """
        Use OPTICS to find dense regions with hierarchical density-based clustering.
        
        OPTICS is better than DBSCAN for data with varying densities.
        """
        trends, embeddings = self._get_all_trends_with_embeddings()
        
        if min_samples is None:
            min_samples = min(max(5, len(trends) // 100), 20)
        
        logger.info(f"Running OPTICS with min_samples={min_samples}, xi={xi}")
        
        # Apply OPTICS
        clustering = OPTICS(min_samples=min_samples, xi=xi, metric='cosine')
        cluster_labels = clustering.fit_predict(embeddings)
        
        return self._analyze_clusters(trends, embeddings, cluster_labels, "OPTICS")
    
    def discover_dense_regions_adaptive(self) -> Dict[str, Any]:
        """
        Adaptive approach that tries multiple algorithms and picks the best.
        
        Uses silhouette score to evaluate clustering quality.
        """
        trends, embeddings = self._get_all_trends_with_embeddings()
        
        algorithms = []
        
        # Try DBSCAN with wider range of parameters to find more granular clusters
        for min_samples in [3, 5, 8, 12, 20]:
            eps = self._estimate_eps(embeddings, min_samples)
            # Also try more aggressive eps values
            for eps_factor in [0.5, 0.75, 1.0, 1.25]:
                adjusted_eps = eps * eps_factor
                dbscan = DBSCAN(eps=adjusted_eps, min_samples=min_samples, metric='cosine')
                labels = dbscan.fit_predict(embeddings)
                
                unique_labels = set(labels)
                n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
                
                # Accept clustering with 2+ clusters and reasonable noise ratio
                if n_clusters >= 2 and n_clusters <= len(trends) // 3:
                    noise_ratio = np.sum(labels == -1) / len(labels)
                    if noise_ratio < 0.8:  # Less than 80% noise
                        try:
                            if n_clusters > 1:
                                # For silhouette score, exclude noise points
                                non_noise_mask = labels != -1
                                if np.sum(non_noise_mask) > 10 and len(set(labels[non_noise_mask])) > 1:
                                    score = silhouette_score(embeddings[non_noise_mask], labels[non_noise_mask], metric='cosine')
                                    algorithms.append(('DBSCAN', labels, score, {
                                        'eps': adjusted_eps, 
                                        'min_samples': min_samples,
                                        'n_clusters': n_clusters,
                                        'noise_ratio': noise_ratio
                                    }))
                        except ValueError:
                            # Skip if silhouette score calculation fails
                            continue
        
        # Try OPTICS with more conservative parameters
        for min_samples in [3, 5, 8, 12]:
            for xi in [0.001, 0.01, 0.05, 0.1, 0.2]:
                try:
                    optics = OPTICS(min_samples=min_samples, xi=xi, metric='cosine')
                    labels = optics.fit_predict(embeddings)
                    
                    unique_labels = set(labels)
                    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
                    
                    if n_clusters >= 2 and n_clusters <= len(trends) // 3:
                        noise_ratio = np.sum(labels == -1) / len(labels)
                        if noise_ratio < 0.8:
                            non_noise_mask = labels != -1
                            if np.sum(non_noise_mask) > 10 and len(set(labels[non_noise_mask])) > 1:
                                score = silhouette_score(embeddings[non_noise_mask], labels[non_noise_mask], metric='cosine')
                                algorithms.append(('OPTICS', labels, score, {
                                    'min_samples': min_samples, 
                                    'xi': xi,
                                    'n_clusters': n_clusters,
                                    'noise_ratio': noise_ratio
                                }))
                except (ValueError, RuntimeError):
                    # Skip if OPTICS fails or silhouette score calculation fails
                    continue
        
        if not algorithms:
            logger.warning("No valid clustering found, falling back to conservative DBSCAN")
            # Fallback: try very conservative DBSCAN
            eps = self._estimate_eps(embeddings, 3) * 0.3  # Very small eps
            dbscan = DBSCAN(eps=eps, min_samples=3, metric='cosine')
            labels = dbscan.fit_predict(embeddings)
            return self._analyze_clusters(trends, embeddings, labels, "DBSCAN_fallback")
        
        # Pick best algorithm based on silhouette score, but prefer more clusters
        # Sort by silhouette score, then by number of clusters (more is better for exploration)
        algorithms.sort(key=lambda x: (x[2], x[3].get('n_clusters', 0)), reverse=True)
        best_algo, best_labels, best_score, best_params = algorithms[0]
        
        logger.info(f"Best algorithm: {best_algo} with score {best_score:.3f}, "
                   f"clusters: {best_params.get('n_clusters', 'unknown')}, params: {best_params}")
        
        result = self._analyze_clusters(trends, embeddings, best_labels, best_algo)
        result["algorithm_comparison"] = {
            "best_algorithm": best_algo,
            "best_silhouette_score": best_score,
            "best_parameters": best_params,
            "algorithms_tried": len(algorithms),
            "alternative_algorithms": algorithms[:3]  # Show top 3 alternatives
        }
        
        return result
    
    def _estimate_eps(self, embeddings: np.ndarray, min_samples: int) -> float:
        """
        Estimate optimal eps parameter using k-distance graph method.
        
        This is the proper way to determine eps for DBSCAN, not arbitrary thresholds.
        """
        # Find k-nearest neighbors (k = min_samples)
        neighbors = NearestNeighbors(n_neighbors=min_samples, metric='cosine')
        neighbors_fit = neighbors.fit(embeddings)
        distances, _ = neighbors_fit.kneighbors(embeddings)
        
        # Sort k-distances (distance to kth nearest neighbor)
        k_distances = np.sort(distances[:, -1])
        
        # Find elbow point (steepest increase)
        # Use second derivative to find inflection point
        if len(k_distances) > 2:
            second_derivative = np.diff(k_distances, 2)
            elbow_idx = np.argmax(second_derivative) + 1
            optimal_eps = k_distances[elbow_idx]
        else:
            optimal_eps = np.mean(k_distances)
        
        return optimal_eps
    
    def _analyze_clusters(self, trends: List[Dict], embeddings: np.ndarray, 
                         cluster_labels: np.ndarray, algorithm: str) -> Dict[str, Any]:
        """Analyze discovered clusters and extract semantic regions."""
        
        unique_labels = set(cluster_labels)
        noise_points = np.sum(cluster_labels == -1)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        
        logger.info(f"Found {n_clusters} clusters, {noise_points} noise points")
        
        regions = []
        cluster_stats = {}
        
        for label in unique_labels:
            if label == -1:  # Skip noise points
                continue
            
            # Get trends in this cluster
            cluster_mask = cluster_labels == label
            cluster_trends = [trends[i] for i in range(len(trends)) if cluster_mask[i]]
            cluster_embeddings = embeddings[cluster_mask]
            
            # Calculate cluster properties
            centroid = np.mean(cluster_embeddings, axis=0)
            
            # Calculate density metrics
            pairwise_distances = []
            for i in range(len(cluster_embeddings)):
                for j in range(i+1, len(cluster_embeddings)):
                    # Use cosine similarity (1 - cosine distance)
                    similarity = 1 - np.dot(cluster_embeddings[i], cluster_embeddings[j]) / (
                        np.linalg.norm(cluster_embeddings[i]) * np.linalg.norm(cluster_embeddings[j])
                    )
                    pairwise_distances.append(similarity)
            
            avg_internal_similarity = 1 - np.mean(pairwise_distances) if pairwise_distances else 0
            
            # Extract semantic themes
            themes = self._extract_cluster_themes(cluster_trends)
            
            # Category distribution
            categories = [t["metadata"]["category"] for t in cluster_trends]
            category_dist = dict(Counter(categories))
            
            # Score statistics
            scores = [t["metadata"]["score"] for t in cluster_trends]
            
            # Date distribution
            dates = [t["metadata"]["date"] for t in cluster_trends]
            
            region = {
                "cluster_id": int(label),
                "size": len(cluster_trends),
                "density_score": float(avg_internal_similarity),
                "themes": themes,
                "category_distribution": category_dist,
                "score_stats": {
                    "mean": float(np.mean(scores)),
                    "std": float(np.std(scores)),
                    "min": float(np.min(scores)),
                    "max": float(np.max(scores))
                },
                "date_range": {
                    "earliest": min(dates) if dates else None,
                    "latest": max(dates) if dates else None,
                    "unique_dates": len(set(dates))
                },
                "sample_trends": [
                    {
                        "text": t["text"][:100] + "..." if len(t["text"]) > 100 else t["text"],
                        "score": t["metadata"]["score"],
                        "category": t["metadata"]["category"]
                    }
                    for t in cluster_trends[:3]  # Top 3 as samples
                ]
            }
            
            regions.append(region)
            cluster_stats[label] = {
                "centroid": centroid,
                "trends": cluster_trends
            }
        
        # Sort regions by density score (most dense first)
        regions.sort(key=lambda x: x["density_score"], reverse=True)
        
        return {
            "algorithm": algorithm,
            "total_trends": len(trends),
            "n_clusters": n_clusters,
            "noise_points": int(noise_points),
            "noise_ratio": float(noise_points / len(trends)),
            "dense_regions": regions,
            "embedding_dimension": int(embeddings.shape[1])
        }
    
    def _extract_cluster_themes(self, cluster_trends: List[Dict]) -> List[str]:
        """Extract semantic themes from a cluster using simple keyword frequency."""
        # Combine all text
        all_text = " ".join([t["text"].lower() for t in cluster_trends])
        
        # Simple keyword extraction (could be enhanced with TF-IDF or more sophisticated methods)
        words = all_text.split()
        
        # Filter out common words and short words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "cannot", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "its", "our", "their"}
        
        filtered_words = [w for w in words if len(w) > 2 and w not in stop_words and w.isalpha()]
        
        # Get most common words
        word_counts = Counter(filtered_words)
        top_themes = [word for word, count in word_counts.most_common(5)]
        
        return top_themes
    
    def find_region_boundaries(self, region_id: int) -> Dict[str, Any]:
        """
        Find the semantic boundaries of a specific dense region.
        
        This helps understand what topics are included vs excluded from a region.
        """
        trends, embeddings = self._get_all_trends_with_embeddings()
        
        # Re-run clustering to get cluster assignments
        result = self.discover_dense_regions_adaptive()
        
        # Find trends in the specified region
        target_region = None
        for region in result["dense_regions"]:
            if region["cluster_id"] == region_id:
                target_region = region
                break
        
        if not target_region:
            return {"error": f"Region {region_id} not found"}
        
        # Find boundary trends (trends close to but not in this cluster)
        # This would require re-running clustering and analyzing distances
        # For now, return the region info
        return {
            "region_id": region_id,
            "region_info": target_region,
            "boundary_analysis": "Not implemented yet - requires distance analysis to cluster boundaries"
        }