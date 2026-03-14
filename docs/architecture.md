# Architecture

## Overview

The GenAI Financial Knowledge Assistant Platform is a microservices-based AI system that combines:

- **VectorRAG** — semantic search over document embeddings stored in ChromaDB
- **GraphRAG** — knowledge graph-based retrieval via Neo4j
- **Agentic AI** — multi-agent orchestration for compliance and risk analysis

## Services

### API Gateway (Port 8000)
- Entry point for all external requests
- Handles authentication (API Key / JWT placeholder)
- Routes `/query` to Agent Service

### Agent Service (Port 8004)
- Orchestrates multi-agent workflows
- **RetrievalAgent**: Calls RAG Service for relevant context
- **ComplianceAgent**: Summarizes compliance-relevant content
- **RiskAnalysisAgent**: Loads `risk_model.joblib` for ML-based risk scoring

### RAG Service (Port 8002)
- Hybrid retrieval engine
- `vector_search`: Queries ChromaDB using sentence-transformers embeddings
- `graph_hint_search`: Queries Neo4j for entity-linked documents
- `hybrid_retrieve`: Combines and deduplicates results

### Ingestion Service (Port 8001)
- Walks a folder and ingests `.txt`/`.md` files
- Chunks text into 512-token windows with 50-token overlap
- Embeds with `all-MiniLM-L6-v2`
- Upserts vectors to ChromaDB

### Graph Service (Port 8003)
- Uses spaCy `en_core_web_sm` for Named Entity Recognition
- Extracts entities (ORG, PERSON, GPE, LAW) and co-occurrence relations
- Merges nodes and relationships into Neo4j

## Data Flow

```
Documents → Ingestion Service → ChromaDB (vectors) + Neo4j (graph)
                                        ↓
User Query → API Gateway → Agent Service → RAG Service (hybrid retrieve)
                                        ↓
                            Structured Answer ← ComplianceAgent + RiskAgent
```

## ML Component

- `train_risk_classifier.py` trains a `TfidfVectorizer + LogisticRegression` pipeline
- Model saved as `risk_model.joblib` and loaded by the RiskAnalysisAgent
- Training data: `data_pipeline/sample_data/training.csv`

## Database Architecture

| Database | Purpose | Port |
|---|---|---|
| ChromaDB | Vector embeddings | 7000 |
| Neo4j | Knowledge graph | 7687 (bolt), 7474 (HTTP) |
| PostgreSQL | Document metadata | 5432 |
| Redis | Response caching | 6379 |
