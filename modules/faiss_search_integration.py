"""
FAISS Search Integration for LLM Servers
=========================================

This module provides FAISS-based semantic search for schools.
Add these endpoints to your LLM server to enable FAISS search.

Usage:
    1. Make sure FAISS index is built (run build_faiss_store.py)
    2. Import this module in your LLM server
    3. Add the endpoints to your FastAPI app
"""

import os
import pickle
import numpy as np
import faiss
from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# =============================================================================
# Configuration
# =============================================================================
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_schools.index")
METADATA_PATH = os.getenv("METADATA_PATH", "faiss_schools_meta.pkl")

# Global variables
faiss_index = None
faiss_metadata = None
faiss_embed_model = None


# =============================================================================
# Data Models
# =============================================================================
class FAISSSearchRequest(BaseModel):
    query: str
    k: int = 5  # number of results
    min_score: float = 0.0  # minimum similarity score


class FAISSSearchResult(BaseModel):
    school_id: int
    text: str
    similarity_score: float


# =============================================================================
# FAISS Initialization
# =============================================================================
def load_faiss_index():
    """Load FAISS index and metadata on startup."""
    global faiss_index, faiss_metadata, faiss_embed_model
    
    if not os.path.exists(FAISS_INDEX_PATH):
        print(f"⚠️  FAISS index not found at {FAISS_INDEX_PATH}")
        print("   Run 'python build_faiss_store.py' to create the index")
        return False
    
    if not os.path.exists(METADATA_PATH):
        print(f"⚠️  FAISS metadata not found at {METADATA_PATH}")
        return False
    
    try:
        print("Loading FAISS index...")
        faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        print(f"✔️  FAISS index loaded ({faiss_index.ntotal} vectors)")
        
        print("Loading FAISS metadata...")
        with open(METADATA_PATH, "rb") as f:
            faiss_metadata = pickle.load(f)
        print(f"✔️  Metadata loaded ({len(faiss_metadata['ids'])} entries)")
        
        print("Loading FAISS embedding model...")
        faiss_embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✔️  Embedding model loaded")
        
        return True
    except Exception as e:
        print(f"❌ Error loading FAISS: {e}")
        return False


def search_faiss(query: str, k: int = 5, min_score: float = 0.0) -> List[dict]:
    """
    Perform semantic search using FAISS.
    
    Args:
        query: Search query text
        k: Number of results to return
        min_score: Minimum similarity score (0-1, lower is better for L2 distance)
    
    Returns:
        List of search results with school_id, text, and similarity_score
    """
    global faiss_index, faiss_metadata, faiss_embed_model
    
    if faiss_index is None or faiss_metadata is None or faiss_embed_model is None:
        raise HTTPException(
            status_code=503,
            detail="FAISS index not loaded. Run build_faiss_store.py first."
        )
    
    # Create embedding for query
    q_vector = faiss_embed_model.encode(query).astype("float32")
    q_vector = np.expand_dims(q_vector, axis=0)
    
    # Search in FAISS
    distances, indices = faiss_index.search(q_vector, k)
    
    # Build results
    results = []
    ids = faiss_metadata["ids"]
    texts = faiss_metadata["texts"]
    slugs = faiss_metadata.get("slugs", [])  # Load slugs from metadata
    
    for dist, idx in zip(distances[0], indices[0]):
        if idx < len(texts) and idx >= 0:
            # Convert L2 distance to similarity score (lower distance = higher similarity)
            # Normalize to 0-1 range (approximate)
            similarity = 1.0 / (1.0 + float(dist))
            
            if similarity >= min_score:
                results.append({
                    "school_id": ids[idx],
                    "text": texts[idx],
                    "slug": slugs[idx] if idx < len(slugs) else "",
                    "similarity_score": round(similarity, 4),
                    "distance": round(float(dist), 4)
                })
    
    return results


# =============================================================================
# FastAPI Endpoints (add these to your app)
# =============================================================================
async def faiss_search_endpoint(request: FAISSSearchRequest):
    """
    Semantic search endpoint using FAISS.
    
    Example:
        POST /v1/search/faiss
        {
            "query": "schools in Tehran",
            "k": 5,
            "min_score": 0.3
        }
    """
    if not request.query or len(request.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    
    if request.k < 1 or request.k > 100:
        raise HTTPException(status_code=400, detail="k must be between 1 and 100")
    
    try:
        results = search_faiss(request.query, request.k, request.min_score)
        
        return {
            "query": request.query,
            "results_count": len(results),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


async def faiss_health_endpoint():
    """
    Check FAISS index health.
    
    Example:
        GET /v1/search/faiss/health
    """
    global faiss_index, faiss_metadata
    
    if faiss_index is None or faiss_metadata is None:
        return {
            "status": "unavailable",
            "message": "FAISS index not loaded"
        }
    
    return {
        "status": "healthy",
        "index_size": faiss_index.ntotal,
        "metadata_count": len(faiss_metadata["ids"]),
        "index_path": FAISS_INDEX_PATH
    }


# =============================================================================
# Integration Helper
# =============================================================================
def add_faiss_endpoints(app):
    """
    Add FAISS endpoints to your FastAPI app.
    
    Usage in your LLM server:
        from faiss_search_integration import add_faiss_endpoints, load_faiss_index
        
        # In lifespan or startup:
        load_faiss_index()
        
        # Add endpoints:
        add_faiss_endpoints(app)
    """
    app.post("/v1/search/faiss")(faiss_search_endpoint)
    app.get("/v1/search/faiss/health")(faiss_health_endpoint)
    
    print("✔️  FAISS endpoints added:")
    print("   POST /v1/search/faiss")
    print("   GET  /v1/search/faiss/health")
