import psycopg2
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# 1. Connect to your Remote Postgres Node
conn = psycopg2.connect("host=192.168.1.XX dbname=dev_db user=postgres password=pass")
cur = conn.cursor()

# 2. Introspect: Get all tables and their column descriptions
cur.execute("""
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'public'
""")
schema_data = cur.fetchall()

# 3. Vectorize for Qdrant
model = SentenceTransformer('all-MiniLM-L6-v2') # Fast & lightweight for 5060 Ti
client = QdrantClient("localhost", port=6333)

for table, col, dtype in schema_data:
    text_to_embed = f"Table: {table}, Column: {col}, Type: {dtype}"
    vector = model.encode(text_to_embed).tolist()
    
    client.upsert(
        collection_name="schema_collection",
        points=[{
            "id": hash(f"{table}_{col}"), # Simplified ID
            "vector": vector,
            "payload": {"table": table, "column": col, "type": dtype}
        }]
    )