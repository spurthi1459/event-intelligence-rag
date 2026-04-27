import pandas as pd
import sqlite3
import ast

# Connect DB
conn = sqlite3.connect("events.db")

# Load event_texts
df = pd.read_sql("SELECT * FROM event_texts", conn)

print("Loaded events:", df.shape)

chunks = []

for _, row in df.iterrows():
    alarm_id = row["alarm_id"]
    text = row["event_text"]

    # Convert metadata string → dict
    metadata = ast.literal_eval(row["metadata"])

    # FULL EVENT CHUNK
    chunks.append({
        "alarm_id": alarm_id,
        "chunk_text": text,
        "chunk_type": "full_event",
        "component_id": metadata.get("component_id", ""),
        "priority": metadata.get("priority", ""),
        "severity": metadata.get("severity", ""),
        "urgency": metadata.get("urgency", "")
    })

    # SEMANTIC SECTION CHUNKS
    sections = text.split("\n\n")

    for section in sections:
        section = section.strip()

        if len(section) > 30:
            chunks.append({
                "alarm_id": alarm_id,
                "chunk_text": section,
                "chunk_type": "section",
                "component_id": metadata.get("component_id", ""),
                "priority": metadata.get("priority", ""),
                "severity": metadata.get("severity", ""),
                "urgency": metadata.get("urgency", "")
            })

# Convert to DataFrame
chunk_df = pd.DataFrame(chunks)

print("Total chunks created:", chunk_df.shape)

# Save
chunk_df.to_sql("event_chunks", conn, index=False, if_exists="replace")

print("Chunking completed!")

# Sample
print("\n🔹 Sample Chunks:\n")
print(chunk_df.head(5))