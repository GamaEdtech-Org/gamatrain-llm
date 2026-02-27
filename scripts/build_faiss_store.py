#!/usr/bin/env python3
"""
FAISS Index Builder for School Search
Builds FAISS index from school embeddings with proper metadata (id, slug)

Purpose: Build FAISS index from school embeddings
Placement: scripts/ - Standalone/manual or scheduled task
Usage: Run manually or via cron job to rebuild search index
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import faiss
import numpy as np
import pickle
from modules.rap_sql_schools_rag import build_school_embeddings

def build_faiss():
    """Build FAISS index from school embeddings"""
    print("Loading local embedding model...")
    
    # Fetch embeddings from SQL & build vectors
    print("* Fetching embeddings from SQL & building vectors...")
    rows = build_school_embeddings()
    
    if not rows:
        print("[ERROR] No embeddings returned")
        return
    
    print(f"[OK] Got {len(rows)} schools")
    
    # Extract vectors from row[3] (id, text, slug, vector)
    vectors = np.array([row[3] for row in rows]).astype("float32")
    
    # Build metadata in correct format for faiss_search_integration
    metadata = {
        "ids": [row[0] for row in rows],
        "texts": [row[1] for row in rows],
        "slugs": [row[2] if row[2] else "" for row in rows]
    }
    
    print(f"[OK] Vector shape: {vectors.shape}")
    print(f"[OK] Metadata count: {len(metadata['ids'])}")
    
    # Create FAISS index
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)
    
    # Save index to root directory (where server expects it)
    faiss.write_index(index, "../faiss_schools.index")
    print("[OK] FAISS index saved to ../faiss_schools.index")
    
    # Save metadata with correct filename
    with open("../faiss_schools_meta.pkl", "wb") as f:
        pickle.dump(metadata, f)
    print("[OK] Metadata saved to ../faiss_schools_meta.pkl")
    
    print(f"\n[SUCCESS] FAISS index built with {len(rows)} schools")
    print(f"Dimension: {dimension}")

if __name__ == "__main__":
    build_faiss()