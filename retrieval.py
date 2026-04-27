import chromadb
from sentence_transformers import SentenceTransformer
import re

# LOAD MODEL
model = SentenceTransformer("all-MiniLM-L6-v2")

# LOAD DB
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="event_rag")

print("Vector DB loaded!")

# FILTER EXTRACTION
def extract_filters(query):
    query_lower = query.lower()
    filters = {}

    match = re.search(r"component\s+(\d+)", query_lower)
    if match:
        filters["component_id"] = match.group(1)

    if "critical" in query_lower:
        filters["priority"] = "Critical"
    elif "high" in query_lower:
        filters["priority"] = "High"
    elif "low" in query_lower:
        filters["priority"] = "Low"

    return filters


# BUILD WHERE
def build_where_clause(filters):
    if not filters:
        return None

    conditions = []
    for k, v in filters.items():
        conditions.append({k: v})

    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


# RETRIEVAL
def retrieve(query, top_k=5):
    filters = extract_filters(query)
    where_clause = build_where_clause(filters)

    print("\n🔹 Extracted Filters:", filters)

    query_embedding = model.encode([query])

    # TRY STRICT FILTER
    if where_clause:
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where=where_clause
        )

        # If empty → fallback
        if not results["documents"][0]:
            print("\n No results with strict filters → relaxing filters...")

            # Remove component filter first
            relaxed_filters = {k: v for k, v in filters.items() if k != "component_id"}
            where_clause = build_where_clause(relaxed_filters)

            if where_clause:
                results = collection.query(
                    query_embeddings=query_embedding,
                    n_results=top_k,
                    where=where_clause
                )
            else:
                results = collection.query(
                    query_embeddings=query_embedding,
                    n_results=top_k
                )

    else:
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

    return results


# TEST
query = "Why are there many critical alarms from component 103?"

results = retrieve(query)

print("\n🔹 Query:", query)
print("\n🔹 Top Results:\n")

docs = results["documents"][0]

if not docs:
    print("No results found.")
else:
    for i, doc in enumerate(docs):
        print(f"Result {i+1}:\n{doc}\n")