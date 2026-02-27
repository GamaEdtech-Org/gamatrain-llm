# FAISS Quick Start Guide

## Quick Build & Deploy

### 1. Build Index
```bash
cd scripts
python build_faiss_store.py
```

### 2. Start Server
```bash
python api/llm_server_production.py
```

## Verify Installation

Check health endpoint:
```bash
curl http://localhost:8000/v1/search/faiss/health
```

Expected response:
```json
{
  "status": "healthy",
  "index_size": 22922,
  "metadata_count": 22922
}
```

## Test Search

```bash
curl -X POST http://localhost:8000/v1/search/faiss \
  -H "Content-Type: application/json" \
  -d '{"query": "schools in Toronto", "top_k": 3}'
```

## Core Files

| File | Purpose | Location |
|------|---------|----------|
| `build_faiss_store.py` | Build index | `scripts/` |
| `faiss_search_integration.py` | Search functions | `modules/` |
| `rap_sql_schools_rag.py` | Data fetching | `modules/` |
| `smart_response_formatter.py` | Response formatting | `modules/` |
| `faiss_schools.index` | Vector index | Root |
| `faiss_schools_meta.pkl` | Metadata | Root |

## Common Commands

**Rebuild index:**
```bash
cd scripts && python build_faiss_store.py
```

**Check metadata:**
```bash
python -c "import pickle; m=pickle.load(open('faiss_schools_meta.pkl','rb')); print(f'Entries: {len(m[\"ids\"])}')"
```

**Backup files:**
```bash
cp faiss_schools.index faiss_schools.index.backup
cp faiss_schools_meta.pkl faiss_schools_meta.pkl.backup
```

## Troubleshooting

**Problem:** Metadata count mismatch  
**Solution:** `cd scripts && python build_faiss_store.py`

**Problem:** FAISS search disabled  
**Solution:** Ensure both `.index` and `.pkl` files exist in root directory

**Problem:** Wrong URLs in results  
**Solution:** Rebuild index to include slugs from database

## See Also

- Full documentation: [FAISS_SETUP_GUIDE.md](./FAISS_SETUP_GUIDE.md)
- API documentation: Check `/docs` endpoint on running server