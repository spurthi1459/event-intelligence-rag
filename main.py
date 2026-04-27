import pandas as pd
import sqlite3

# Load CSV
df = pd.read_csv("V_EVENT_DETAILS_202512311554.csv")

print("Original shape:", df.shape)
print("Columns:", df.columns.tolist())

# REQUIRED COLUMNS 
required_cols = [
    "ALARM_ID",
    "EVENT_ID",
    "PRIORITY",
    "COMPONENT_ID",
    "ALARM_GENERATED_TIME",
    "SECONDARY_AGENCY",
    "BPM_ESCULATION_COUNT",
    "STEP_NAME"
]

optional_cols = [
    "CATEGORY",
    "CATEGORY_1",
    "CATEGORY_2",
    "DEVICE_NAME",
    "DEVICE_N"
]

existing_required = [col for col in required_cols if col in df.columns]
existing_optional = [col for col in optional_cols if col in df.columns]

final_cols = existing_required + existing_optional

df = df[final_cols]

df = df.fillna("Not Available")

print("Final columns used:", final_cols)
print("Cleaned shape:", df.shape)


conn = sqlite3.connect("events.db")
df.to_sql("event_details", conn, if_exists="replace", index=False)
conn.close()

print(" Data loaded into SQLite successfully!")