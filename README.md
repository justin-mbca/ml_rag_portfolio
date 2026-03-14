# 🏦 GenAI Financial Knowledge Assistant Platform

> A production-quality, end-to-end Generative AI platform for financial institutions — combining VectorRAG, GraphRAG, Agentic AI, and enterprise-grade MLOps.

[![CI/CD](https://github.com/justin-mbca/ml_rag_portfolio/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/justin-mbca/ml_rag_portfolio/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

---

## 📌 Problem Statement

Large financial institutions manage thousands of regulatory documents, risk policies, AML guidelines, and compliance frameworks. Analysts waste hours manually searching these documents.

This platform demonstrates how **Generative AI + Knowledge Graphs + Agentic Workflows** can power:
- Instant regulatory Q&A
- Risk document analysis
- Compliance gap detection
- Automated report generation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        API Gateway (FastAPI)                        │
│                    Auth · Rate Limiting · Routing                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │      Agent Service          │
              │  RetrievalAgent             │
              │  ComplianceAgent            │
              │  RiskAnalysisAgent          │
              └──────────────┬──────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │              RAG Service                │
        │   VectorSearch · GraphSearch · Hybrid   │
        └────────┬───────────────────┬────────────┘
                 │                   │
    ┌────────────▼──────┐  ┌─────────▼──────────┐
    │  ChromaDB (Vector)│  │  Neo4j (Graph)      │
    └────────────┬──────┘  └─────────┬──────────┘
                 │                   │
        ┌────────▼───────────────────▼────────┐
        │         Ingestion Service            │
        │   Chunking · Embedding · Indexing    │
        └─────────────────────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │         Graph Service               │
        │   NER · Entity/Relation Extraction  │
        └─────────────────────────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │         Data Sources                │
        │  AML Docs · Risk Policies · Reports │
        └─────────────────────────────────────┘
```

See [architecture_diagrams/architecture-ascii.txt](architecture_diagrams/architecture-ascii.txt) for the full diagram.

---

## 🛠️ Technologies

| Layer | Technologies |
|---|---|
| **AI/ML** | sentence-transformers, scikit-learn, spaCy |
| **Vector DB** | ChromaDB |
| **Graph DB** | Neo4j |
| **Orchestration** | Prefect |
| **API Framework** | FastAPI + Uvicorn |
| **Caching** | Redis |
| **Metadata DB** | PostgreSQL |
| **Containers** | Docker + Docker Compose |
| **Orchestration** | Kubernetes |
| **CI/CD** | GitHub Actions |
| **Observability** | Prometheus + Grafana |
| **ML Pipeline** | scikit-learn Pipeline + joblib |

---

## 📁 Project Structure

```
ml_rag_portfolio/
├── README.md
├── LICENSE
├── architecture_diagrams/
│   └── architecture-ascii.txt
├── ci/
│   └── github-actions/
│       └── ci-cd.yaml
├── data_pipeline/
│   ├── prefect/flows/ingest_flow.py
│   └── sample_data/
│       ├── aml_regulations_sample.txt
│       └── training.csv
├── docker/
│   └── docker-compose.yml
├── docs/
│   ├── architecture.md
│   ├── cloud_services.md
│   ├── deployment.md
│   └── run_local.md
├── kubernetes/
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── postgres-deployment.yaml
│   │   ├── redis-deployment.yaml
│   │   └── neo4j-deployment.yaml
│   └── overlays/production/
│       └── rag-service-deployment.yaml
├── models/
│   ├── training/
│   │   └── train_risk_classifier.py
│   └── saved_models/
│       └── .gitkeep
├── notebooks/
│   └── poc_vector_vs_graph_rag.ipynb
├── observability/
│   ├── prometheus.yml
│   └── grafana/dashboard.json
├── services/
│   ├── ingestion-service/
│   ├── rag-service/
│   ├── graph-service/
│   ├── agent-service/
│   └── api-gateway/
└── tests/
    ├── unit/
    │   ├── test_chunking.py
    │   └── test_rag_retrieval.py
    └── integration/
        └── test_end_to_end.py
```

---

## 🚀 Quick Start (Local via Docker Compose)

### Prerequisites
- Docker 24+
- Docker Compose v2+
- Python 3.10+

### 1. Clone the repository
```bash
git clone https://github.com/justin-mbca/ml_rag_portfolio.git
cd ml_rag_portfolio
```

### 2. Configure environment variables
```bash
cp docker/.env.example docker/.env
# Edit docker/.env with your settings
```

### 3. Start all services
```bash
cd docker
docker compose up --build
```

### 4. Access the platform
| Service | URL |
|---|---|
| API Gateway | http://localhost:8000 |
| Ingestion Service | http://localhost:8001 |
| RAG Service | http://localhost:8002 |
| Graph Service | http://localhost:8003 |
| Agent Service | http://localhost:8004 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Neo4j Browser | http://localhost:7474 |

### 5. Example Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -d '{"question": "What are the key compliance risks related to AML regulations?"}'
```

---

## 🔐 Secrets & Configuration

| Secret | Where to Set | Description |
|---|---|---|
| `NEO4J_PASSWORD` | GitHub Secrets + `.env` | Neo4j database password |
| `POSTGRES_PASSWORD` | GitHub Secrets + `.env` | PostgreSQL password |
| `OPENAI_API_KEY` | GitHub Secrets + `.env` | Optional LLM integration |
| `KUBE_CONFIG_DATA` | GitHub Secrets | Base64-encoded kubeconfig for deployment |
| `GHCR_TOKEN` | GitHub Secrets (auto) | GITHUB_TOKEN for container registry |

See [docs/run_local.md](docs/run_local.md) for detailed local setup instructions.

---

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Unit tests
pytest tests/unit/ -v

# Integration tests (requires running services)
pytest tests/integration/ -v

# All tests
pytest tests/ -v
```

---

## ☁️ Cloud Services

See [docs/cloud_services.md](docs/cloud_services.md) for a full breakdown of required and optional cloud services (container registry, Kubernetes cluster, managed databases, LLM APIs, and more).

---

## ☸️ Kubernetes Deployment

See [docs/deployment.md](docs/deployment.md) for full Kubernetes deployment instructions.

```bash
# Apply base manifests
kubectl apply -k kubernetes/base/

# Apply production overlays
kubectl apply -k kubernetes/overlays/production/
```

---

## 📊 Observability

- **Prometheus** scrapes `/metrics` from all services
- **Grafana** dashboards at `http://localhost:3000` (admin/admin)
- Structured JSON logging across all services

---

## 📓 PoC Notebook

Open [notebooks/poc_vector_vs_graph_rag.ipynb](notebooks/poc_vector_vs_graph_rag.ipynb) to see a head-to-head comparison of VectorRAG vs GraphRAG performance on financial documents.

---

## 🗺️ Roadmap

- [ ] Add LLM integration (OpenAI / Azure OpenAI)
- [ ] Streamlit / React frontend dashboard
- [ ] PySpark-based large-scale data pipeline
- [ ] HuggingFace fine-tuned financial embeddings
- [ ] Multi-tenant support

---

## 📸 Screenshots

> _Screenshots will be added after UI development is complete._

![Architecture Diagram](architecture_diagrams/architecture-ascii.txt)

---

## 📄 License

[MIT License](LICENSE) © 2024 GenAI Financial Knowledge Assistant Platform Contributors
