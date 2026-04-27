import pandas as pd
import sqlite3
from sentence_transformers import SentenceTransformer
import chromadb

# Load chunks
conn = sqlite3.connect("events.db")
df = pd.read_sql("SELECT * FROM event_chunks", conn)

print("Loaded chunks:", df.shape)

# Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Persistent DB
client = chromadb.PersistentClient(path="./chroma_db")

# Reset collection
try:
    client.delete_collection("event_rag")
except:
    pass

collection = client.get_or_create_collection(name="event_rag")

# Prepare data
documents = df["chunk_text"].tolist()

metadatas = [
    {
        "alarm_id": str(row["alarm_id"]),
        "chunk_type": row["chunk_type"],
        "component_id": str(row["component_id"]),
        "priority": str(row["priority"]),
        "severity": str(row["severity"]),
        "urgency": str(row["urgency"])
    }
    for _, row in df.iterrows()
]

ids = [str(i) for i in range(len(documents))]

# Generate embeddings
embeddings = model.encode(documents, show_progress_bar=True)

# Batch insert
batch_size = 5000

for i in range(0, len(documents), batch_size):
    collection.add(
        documents=documents[i:i+batch_size],
        embeddings=embeddings[i:i+batch_size],
        metadatas=metadatas[i:i+batch_size],
        ids=ids[i:i+batch_size]
    )
    print(f"Inserted batch {i} to {i+batch_size}")

print(" Embeddings stored in persistent ChromaDB!")