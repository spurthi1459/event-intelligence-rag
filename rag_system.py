import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer
import re

# INIT 
model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="event_rag")

# IMPORTANT: use correct absolute path
conn = sqlite3.connect(r"D:\Projects\Trinity_mobility\events.db")

print("Event Intelligence RAG System Ready!")
print("Type 'exit' to quit.\n")


# HELPERS
def extract_event_id(query):
    query = query.upper()

    # Extract INC ID
    match = re.search(r"INC0*(\d+)", query)
    if match:
        return match.group(1)

    # Extract numeric ID
    match = re.search(r"\b(\d{3,})\b", query)
    if match:
        return match.group(1)

    return None


def is_analytical(query):
    return "how many" in query.lower()


# EVENT QUERY
def get_event_details(event_id, query):

    padded_id = f"INC{event_id.zfill(6)}"
    numeric_id = int(event_id) if event_id.isdigit() else None

    #  FIRST: SEARCH USING EVENT_ID
    rows = conn.execute("""
        SELECT PRIORITY, COMPONENT_ID, ALARM_GENERATED_TIME,
               SECONDARY_AGENCY, BPM_ESCULATION_COUNT,
               STEP_NAME, EVENT_ID
        FROM event_details
        WHERE EVENT_ID = ?
    """, (padded_id,)).fetchall()

    # FALLBACK: SEARCH USING ALARM_ID
    if not rows and numeric_id:
        rows = conn.execute("""
            SELECT PRIORITY, COMPONENT_ID, ALARM_GENERATED_TIME,
                   SECONDARY_AGENCY, BPM_ESCULATION_COUNT,
                   STEP_NAME, EVENT_ID
            FROM event_details
            WHERE ALARM_ID = ?
        """, (numeric_id,)).fetchall()

    #  NOT FOUND
    if not rows:
        return f""" Event {padded_id} not found in dataset.

 Checked both EVENT_ID and ALARM_ID."""

    steps = list(set([
        r[5] for r in rows
        if r[5] not in ["Not Available", None, ""]
    ]))

    row = rows[0]
    q = query.lower()

    # PRIORITY 
    if "priority" in q:
        return f"Priority of {row[6]}: {row[0]}"

    # ACTIONS
    if "action" in q or "step" in q:
        return "🛠 Actions:\n" + ("\n".join(steps) if steps else "No actions recorded.")

    # SOP
    if "sop" in q:
        return " SOP:\n" + ("\n".join(steps) if steps else "Not available.")

    # DEFAULT
    return f"""
 Incident Details

- Event ID: {row[6]}
- Priority: {row[0]}
- Component: {row[1]}
- Time: {row[2]}
- Handled by: {row[3]}
- Escalations: {row[4]}
"""


# SQL ANALYTICS 
def handle_sql(query):

    q = query.lower()

    # LAST WEEK
    if "last week" in q:
        max_date = conn.execute("""
            SELECT MAX(ALARM_GENERATED_TIME)
            FROM event_details
        """).fetchone()[0]

        result = conn.execute("""
            SELECT COUNT(*) FROM event_details
            WHERE datetime(ALARM_GENERATED_TIME) >= datetime(?, '-7 days')
        """, (max_date,)).fetchone()[0]

        return f"""
Events in last week: {result}

Based on dataset end date: {max_date}
"""

    # CRITICAL
    if "critical" in q:
        result = conn.execute("""
            SELECT COUNT(*) FROM event_details
            WHERE LOWER(PRIORITY) = 'critical'
        """).fetchone()[0]

        return f"Critical events: {result}"

    return " Query not supported."


# RAG
def retrieve(query):
    embedding = model.encode([query])
    results = collection.query(query_embeddings=embedding, n_results=5)
    return results["documents"][0]


def generate_answer(query, docs):
    context = "\n\n".join(docs)

    if not context.strip():
        return "No relevant information found."

    return f"\n Retrieved Info:\n{context}"


# ROUTER
def ask(query):

    event_id = extract_event_id(query)

    if event_id:
        print("→ EVENT QUERY")
        return get_event_details(event_id, query)

    if is_analytical(query):
        print("→ ANALYTICAL QUERY")
        return handle_sql(query)

    print("→ RAG QUERY")
    docs = retrieve(query)
    return generate_answer(query, docs)


# LOOP
while True:
    q = input("\nEnter your query: ")

    if q.lower() == "exit":
        break

    print("\n==========================")
    print(ask(q))