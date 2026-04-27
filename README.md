# Event Intelligence RAG System

## Overview
A Retrieval-Augmented Generation (RAG) system built on operational incident data to answer natural language queries using hybrid retrieval (semantic search + SQL).

## Key Features
- Data ingestion from CSV into SQLite
- Feature engineering to generate event narratives
- Chunking strategy (full + section-based)
- Embeddings using SentenceTransformers
- Vector storage with ChromaDB
- Hybrid retrieval (RAG + SQL fallback)
- Query routing (event / analytical / semantic)

## Tech Stack
- Python
- SQLite
- SentenceTransformers
- ChromaDB

## Architecture
Pipeline:
1. Load data → SQLite
2. Generate event text + metadata
3. Chunk text
4. Generate embeddings
5. Store in vector DB
6. Retrieve using hybrid approach

## Example Queries
- "Give me details of event INC020147"
- "Why are there many critical alarms from component 103?"
- "How many events occurred last week?"

## How to Run

```bash
python main.py
python feature_engineering.py
python chunking.py
python embedding.py
python rag_system.py

Notes
Built as a timed assignment (3 hours)
Focused on practical system design and retrieval accuracy


---

## Step 4: Push README

```bash
git add README.md
git commit -m "Add README"
git push
