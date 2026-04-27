import pandas as pd
import sqlite3

# Connect to DB
conn = sqlite3.connect("events.db")

# Load data
df = pd.read_sql("SELECT * FROM event_details", conn)

print("Loaded from DB:", df.shape)

# HELPER FUNCTION
def clean(val):
    if pd.isna(val) or str(val) in ["Not Available", "None", "nan"]:
        return None
    return str(val)

# Group by ALARM_ID
grouped = df.groupby("ALARM_ID")

event_data = []

for alarm_id, group in grouped:
    
    row = group.iloc[0]

    # CLEAN VALUES
    priority = clean(row.get("PRIORITY"))
    severity = clean(row.get("SEVERITY"))
    urgency = clean(row.get("URGENCY"))
    agency = clean(row.get("SECONDARY_AGENCY"))
    sop = clean(row.get("SOP_DOCUMENT_URL"))
    component = clean(row.get("COMPONENT_ID"))
    escalation = clean(row.get("BPM_ESCULATION_COUNT"))

    time = row.get("ALARM_GENERATED_TIME")
    time = str(time) if pd.notna(time) else "Unknown time"

    # STEP CLEANING
    steps = [
        str(step).strip()
        for step in group["STEP_NAME"].unique().tolist()
        if step not in ["Not Available", None, ""]
    ]

    if steps:
        steps_text = "\n".join([f"- {step}" for step in steps])
    else:
        steps_text = None

    # BUILD DETAILS DYNAMICALLY
    details = []

    if urgency:
        details.append(f"Urgency level: {urgency}")

    if escalation and escalation != "0":
        details.append(f"Escalation count: {escalation}")

    if agency:
        details.append(f"Handled by: {agency}")

    details_text = "\n".join(details) if details else "Additional details not available."

    # FINAL EVENT TEXT 
    event_text = f"""
Incident {alarm_id} with priority {priority or 'Unknown'} 
was generated at {time} for component {component or 'Unknown'}.

{details_text}

Steps taken:
{steps_text if steps_text else "No specific steps recorded."}

{f"SOP Reference: {sop}" if sop else ""}
"""

    #METADATA
    metadata = {
        "alarm_id": str(alarm_id),
        "priority": priority or "",
        "component_id": component or "",
        "severity": severity or "",
        "urgency": urgency or "",
    }

    event_data.append({
        "alarm_id": alarm_id,
        "event_text": event_text.strip(),
        "metadata": str(metadata)
    })

# Convert to DataFrame
event_df = pd.DataFrame(event_data)

print("Generated events:", event_df.shape)

# Save to DB
event_df.to_sql("event_texts", conn, index=False, if_exists="replace")

print("Event text generation completed!")

# SAMPLE OUTPUT
print("\n Sample Event Text:\n")
print(event_df.head(1)["event_text"].values[0])