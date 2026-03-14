# Technology Stack

## Core AI / ML

| Component | Technology | Version | Purpose |
|---|---|---|---|
| LLM Orchestration | LangChain | >=0.2 | RAG pipelines, chains, agents |
| Document Indexing | LlamaIndex | >=0.10 | Graph-aware indexing |
| Embeddings | OpenAI `text-embedding-ada-002` / `text-embedding-3-small` | latest | Document and query embeddings |
| LLM | OpenAI GPT-4o / GPT-4-turbo | latest | Answer generation |
| Open-source LLM | HuggingFace Transformers | >=4.38 | Alternative inference |

## Vector Databases

| Technology | Use Case |
|---|---|
| ChromaDB | Development / small-scale vector store |
| FAISS | High-performance similarity search |
| Pinecone (optional) | Managed cloud vector database |

## Knowledge Graph

| Technology | Use Case |
|---|---|
| Neo4j | Primary graph database |
| py2neo / neo4j-driver | Python client |
| Cypher | Graph query language |

## Agentic Frameworks

| Technology | Use Case |
|---|---|
| LangGraph | Stateful multi-agent workflows |
| CrewAI | Role-based agent orchestration |
| LangChain Tools | Tool calling for agents |

## API Layer

| Technology | Use Case |
|---|---|
| FastAPI | REST API for all microservices |
| Uvicorn | ASGI server |
| Pydantic | Request/response validation |

## Data Pipeline

| Technology | Use Case |
|---|---|
| Prefect | Pipeline orchestration |
| Pandas | Data transformation |
| PySpark | Large-scale document processing |
| PyMuPDF / pdfplumber | PDF parsing |
| python-docx | Word document parsing |

## Storage

| Technology | Use Case |
|---|---|
| Amazon S3 / Azure Blob | Document storage |
| PostgreSQL | Metadata store |
| Redis | Caching (query results, embeddings) |

## Machine Learning

| Technology | Use Case |
|---|---|
| scikit-learn | Document classification, risk prediction |
| HuggingFace Transformers | Fine-tuned classification models |
| MLflow | Experiment tracking |

## DevOps & Infrastructure

| Technology | Use Case |
|---|---|
| Docker | Containerisation |
| Docker Compose | Local multi-service orchestration |
| Kubernetes | Production deployment |
| GitHub Actions | CI/CD pipeline |
| Helm | Kubernetes package manager |

## Observability

| Technology | Use Case |
|---|---|
| Prometheus | Metrics collection |
| Grafana | Dashboards and alerting |
| structlog | Structured JSON logging |
| OpenTelemetry | Distributed tracing |

## Cloud Compatibility

The platform is designed to run on:

- **AWS**: EKS, S3, RDS, ElastiCache, Bedrock
- **Azure**: AKS, Blob Storage, Azure Database for PostgreSQL, Azure Cache for Redis, Azure OpenAI
- **GCP**: GKE, Cloud Storage, Cloud SQL, Memorystore, Vertex AI
