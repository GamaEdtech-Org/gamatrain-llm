import os
from typing import List, Tuple

from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer

# —————— Load Environment Variables ——————

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_SERVER = os.getenv("DB_SERVER", "DESKTOP-B0M5LVO")
DB_NAME = os.getenv("DB_NAME", "stagegamacoreapp")

# Create connection to SQL Server (Windows Auth)
CONNECTION_STRING = (
    "mssql+pyodbc://"
    f"{DB_SERVER}/{DB_NAME}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)

engine = create_engine(CONNECTION_STRING)

# —————— Load HuggingFace Embedding Model ——————

print("Loading local embedding model...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded ✔️")

# —————— Data Fetch Functions ——————

def fetch_schools_data(limit: int = None) -> List[dict]:
    """
    Read id, name, and address from Schools table.
    If limit is None, select all rows.
    """
    if limit is None:
        sql_query = """
        SELECT
              id,
              name,
              address,
              LocalName
          FROM Schools
          """
    else:
        sql_query = f"""
        SELECT TOP {limit}
              id,
              name,
              address,
              LocalName
          FROM Schools
        """

    with engine.connect() as conn:
        rows = conn.execute(text(sql_query)).fetchall()

    results = []
    for row in rows:
        results.append({
            "id": row.id,
            "name": row.name,
            "address": row.address,
            "slug": row.LocalName if hasattr(row, 'LocalName') and row.LocalName else ""
        })
    return results
# —————— Embedding with HF ——————

def create_local_embedding(text: str) -> List[float]:
    """
    Create embedding vector using a local HuggingFace model.
    """
    vector = embed_model.encode(text)
    return vector.tolist()

def build_school_embeddings(limit: int = None) -> List[Tuple[int, str, str, List[float]]]:
    """
    Fetch school data, combine text fields, and build embeddings locally.
    """
    schools = fetch_schools_data(limit)
    embeddings = []

    for school in schools:
        combined_text = f"School: {school['name']}. Address: {school['address']}."
        vector = create_local_embedding(combined_text)
        embeddings.append((school["id"], combined_text, school.get("slug", ""), vector))

    return embeddings

# —————— Main Execution ——————

if __name__ == "__main__":
    print("=== STARTING SCRIPT ===")

    # 1) Test SQL Connection
    print("=== TEST: SQL CONNECTION ===")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test")).fetchall()
            print("SQL Connection OK:", result)
    except Exception as e:
        print("SQL Connection FAILED:", e)

    # 2) Fetch sample school rows
    print("\n=== FETCH SAMPLE SCHOOLS ===")
    try:
        schools = fetch_schools_data(limit=10)
        print("Fetched rows count:", len(schools))
        for s in schools:
            print(s)
    except Exception as e:
        print("FETCH ERROR:", e)

    # 3) Build embeddings locally
    print("\n=== BUILD EMBEDDINGS SAMPLE ===")
    try:
        embs = build_school_embeddings(limit=10)
        print("Embeddings count:", len(embs))
        for sid, text_val, vec in embs:
            print("\nSCHOOL ID:", sid)
            print("Text snippet:", text_val[:100], "...")
            print("Embedding vector length:", len(vec))
    except Exception as e:
        print("LOCAL EMBEDDING ERROR:", e)

    print("\n=== SCRIPT FINISHED ===")