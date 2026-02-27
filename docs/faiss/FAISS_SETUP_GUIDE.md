# FAISS School Search Setup Guide

## Overview

This guide explains how to build and use the FAISS index for fast school search functionality in the Gamatrain AI system.

## Architecture

The FAISS integration consists of four main components organized by purpose:

### Modules (`modules/`)
Shared logic used by both scripts and API endpoints:

1. **rap_sql_schools_rag.py** - Fetches school data from SQL Server and generates embeddings
2. **faiss_search_integration.py** - Provides search functionality for the API
3. **smart_response_formatter.py** - Formats responses based on question type

### Scripts (`scripts/`)
Standalone/manual or scheduled tasks:

4. **build_faiss_store.py** - Builds the FAISS index and metadata files

### API (`api/`)
5. **llm_server_production.py** - Main server with FAISS integration

## Files Structure

```
modules/
├── rap_sql_schools_rag.py          # Data fetching & embedding generation
├── faiss_search_integration.py     # Search functions
└── smart_response_formatter.py     # Response formatting

scripts/
└── build_faiss_store.py            # Index builder

api/
└── llm_server_production.py        # Main server with FAISS integration

docs/faiss/
├── FAISS_SETUP_GUIDE.md           # This file
├── FAISS_QUICK_START.md            # Quick reference
└── CHANGELOG_FAISS.md              # Change history

Root directory (after build):
├── faiss_schools.index             # FAISS vector index
└── faiss_schools_meta.pkl          # Metadata (ids, texts, slugs)
```

## Prerequisites

- Python 3.8+
- SQL Server connection configured
- Required packages:
  ```bash
  pip install faiss-cpu numpy sentence-transformers sqlalchemy pyodbc
  ```

## Building the FAISS Index

### Step 1: Verify SQL Connection

The system fetches school data from SQL Server. Ensure your connection string is configured in `modules/rap_sql_schools_rag.py`:

```python
engine = create_engine(
    "mssql+pyodbc://SERVER/DATABASE?driver=ODBC+Driver+18+for+SQL+Server&..."
)
```

### Step 2: Build the Index

Run the build script from the `scripts` directory:

```bash
cd scripts
python build_faiss_store.py
```

This will:
1. Load the embedding model (sentence-transformers/all-MiniLM-L6-v2)
2. Fetch all schools from SQL Server
3. Generate embeddings for each school
4. Build FAISS index with 384-dimensional vectors
5. Save two files to root directory:
   - `../faiss_schools.index` - Vector index
   - `../faiss_schools_meta.pkl` - Metadata dictionary

**Expected Output:**
```
Loading local embedding model...
Model loaded ✔️
* Fetching embeddings from SQL & building vectors...
[OK] Got 22922 schools
[OK] Vector shape: (22922, 384)
[OK] Metadata count: 22922
[OK] FAISS index saved to ../faiss_schools.index
[OK] Metadata saved to ../faiss_schools_meta.pkl

[SUCCESS] FAISS index built with 22922 schools
Dimension: 384
```

## Metadata Format

The metadata file contains a dictionary with three keys:

```python
{
    "ids": [1, 2, 3, ...],           # School IDs
    "texts": ["School: ...", ...],    # Combined text for each school
    "slugs": ["school-slug", ...]     # URL slugs for each school
}
```

## Using FAISS Search

### Starting the Server

```bash
python api/llm_server_production.py
```

The server will automatically load the FAISS index on startup:

```
Loading FAISS index...
✔️  FAISS index loaded (22922 vectors)
Loading FAISS metadata...
✔️  Metadata loaded (22922 entries)
Loading FAISS embedding model...
✔️  Embedding model loaded
[OK]  FAISS search enabled
```

### API Endpoints

#### 1. FAISS Search Endpoint

**POST** `/v1/search/faiss`

Search for schools using semantic similarity.

**Request:**
```json
{
  "query": "schools in Toronto",
  "top_k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "text": "School: West End Alternative School. Address: 5555, Bloor Street West...",
      "slug": "west-end-alternative-school",
      "url": "https://gamatrain.com/school/1/west-end-alternative-school",
      "distance": 0.234
    }
  ],
  "query": "schools in Toronto",
  "count": 5
}
```

#### 2. Health Check

**GET** `/v1/search/faiss/health`

Check FAISS system status.

**Response:**
```json
{
  "status": "healthy",
  "index_size": 22922,
  "metadata_count": 22922,
  "index_path": "faiss_schools.index"
}
```

#### 3. Unified Query Endpoint

**POST** `/v1/query`

The main query endpoint automatically uses FAISS for school-related queries.

**Request:**
```json
{
  "query": "where is Blessed Sacrament Outreach School?",
  "session_id": "user123"
}
```

The system will:
1. Detect if the query is school-related
2. Use FAISS to find relevant schools
3. Format response based on question type (factual vs educational)
4. Include Related Sources with correct URLs

## Smart Response Formatting

The system automatically detects question types:

### Factual Questions
Questions like "where is X?", "when does X open?" get direct answers.

**Example:**
- Query: "where is Blessed Sacrament Outreach School?"
- Response: Direct address with map link

### Educational Questions
Questions like "what is photosynthesis?" get structured responses:
1. Concept Explanation
2. Example
3. Step-by-Step Explanation
4. Check Your Understanding

## Rebuilding the Index

You should rebuild the FAISS index when:
- New schools are added to the database
- School information is updated
- You want to change the embedding model

**Quick Rebuild:**
```bash
cd scripts
python build_faiss_store.py
# Restart server
python api/llm_server_production.py
```

## Troubleshooting

### Issue: Import errors after reorganization

**Symptom:** `ModuleNotFoundError: No module named 'modules'`

**Solution:** Ensure the path is added correctly in imports:
```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modules.module_name import function_name
```

### Issue: Metadata count mismatch

**Symptom:** Server shows different counts for index and metadata
```
✔️  FAISS index loaded (22922 vectors)
✔️  Metadata loaded (1004 entries)
```

**Solution:** Rebuild index
```bash
cd scripts
python build_faiss_store.py
```

### Issue: Wrong URLs in Related Sources

**Symptom:** URLs point to wrong schools or return 404

**Solution:** Ensure slugs are properly fetched from database:
1. Check that `LocalName` column exists in SQL query
2. Rebuild index to include slugs
3. Verify metadata format is correct (dictionary with ids, texts, slugs)

### Issue: FAISS search disabled

**Symptom:** Server logs show "FAISS search disabled"

**Solution:** 
1. Ensure `faiss_schools.index` exists in root directory
2. Ensure `faiss_schools_meta.pkl` exists in root directory
3. Check file permissions
4. Restart server

## Performance

- **Index Size:** ~22,922 schools
- **Vector Dimension:** 384
- **Search Time:** < 100ms for top-5 results
- **Memory Usage:** ~35MB for index + metadata
- **Embedding Model:** all-MiniLM-L6-v2 (lightweight, fast)

## Configuration

### Environment Variables

You can customize paths using environment variables:

```bash
export FAISS_INDEX_PATH="custom_path/faiss_schools.index"
export METADATA_PATH="custom_path/faiss_schools_meta.pkl"
```

### Embedding Model

To change the embedding model, edit `modules/rap_sql_schools_rag.py`:

```python
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# Change to:
model = SentenceTransformer("your-preferred-model")
```

Then rebuild the index.

## Integration with Main Query System

The FAISS search is automatically integrated into `/v1/query` endpoint:

1. Query is analyzed for school-related keywords
2. If school-related, FAISS search is performed
3. Results are combined with RAG context
4. Response is formatted based on question type
5. Related Sources include correct school URLs

## Maintenance

### Regular Tasks

1. **Weekly:** Check index health via `/v1/search/faiss/health`
2. **Monthly:** Rebuild index to include new schools
3. **As needed:** Update when database schema changes

### Backup

Always backup these files before rebuilding:
```bash
cp faiss_schools.index faiss_schools.index.backup
cp faiss_schools_meta.pkl faiss_schools_meta.pkl.backup
```

## Support

For issues or questions:
1. Check server logs for error messages
2. Verify SQL connection is working
3. Ensure all dependencies are installed
4. Check file permissions and paths
5. Verify import paths are correct after reorganization

---

**Last Updated:** February 2026
**Version:** 1.1 (Reorganized Structure)