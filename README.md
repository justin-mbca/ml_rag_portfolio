# GenAI Financial Knowledge Assistant Platform

[![CI/CD Pipeline](https://github.com/justin-mbca/ml_rag_portfolio/actions/workflows/workflow.yaml/badge.svg)](https://github.com/justin-mbca/ml_rag_portfolio/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

The **GenAI Financial Knowledge Assistant Platform** is a production-quality AI platform that demonstrates how **Generative AI**, **VectorRAG**, **GraphRAG**, and **Agentic workflows** can power enterprise search, analytics, and chat assistants for financial institutions.

This project simulates a banking environment where internal analysts can query financial policies, risk documents, and regulatory materials using a hybrid retrieval-augmented generation (RAG) system backed by a knowledge graph and an agentic AI orchestration layer.

### Audience

- Machine Learning Engineers at financial institutions
- AI/ML Platform architects
- Data Engineers building enterprise AI solutions
- Compliance and Risk technology teams

### Goals

- Demonstrate scalable, hybrid RAG pipelines (vector + graph)
- Showcase multi-agent orchestration for financial workflows
- Provide a production-ready microservices architecture
- Enable cloud-native deployment on AWS / Azure / GCP

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        API Gateway (FastAPI)                        │
│              Routes queries to downstream microservices             │
└───────┬──────────────────┬────────────────────┬────────────────────┘
        │                  │                    │
        ▼                  ▼                    ▼
┌───────────────┐  ┌───────────────┐  ┌────────────────────┐
│  RAG Service  │  │ Agent Service │  │  Ingestion Service │
│ VectorRAG +   │  │ LangGraph /   │  │  Document loading  │
│ GraphRAG      │  │ CrewAI agents │  │  Chunking +        │
│ Hybrid search │  │ Orchestration │  │  Embedding         │
└──────┬────────┘  └──────┬────────┘  └────────────────────┘
       │                  │
       ▼                  ▼
┌───────────────┐  ┌───────────────────────────────────────┐
│ Graph Service │  │            Data Stores                 │
│ Neo4j         │  │  ChromaDB/FAISS  |  Neo4j  |  Redis   │
│ Knowledge     │  │  (Vector DB)     |  (Graph)|  (Cache) │
│ Graph         │  └───────────────────────────────────────┘
└───────────────┘
```

See `docs/architecture_diagram.png` for a full visual diagram.

---

## Key Features

| Capability | Technology |
|---|---|
| Vector RAG | LangChain + ChromaDB / FAISS |
| Graph RAG | Neo4j + LlamaIndex |
| Hybrid Retrieval | Combined vector + graph search |
| Agentic Workflows | LangGraph / CrewAI |
| Document Ingestion | Prefect + Pandas / PySpark |
| REST API | FastAPI |
| Observability | Prometheus + Grafana |
| CI/CD | GitHub Actions |
| Containerisation | Docker + Kubernetes |

---

## Repository Structure

```
ml_rag_portfolio/
├── README.md
├── docs/
│   ├── architecture_diagram.png
│   ├── tech_stack.md
│   └── examples.md
├── services/
│   ├── ingestion-service/
│   ├── rag-service/
│   ├── graph-service/
│   ├── agent-service/
│   └── api-gateway/
├── agents/
│   ├── retrieval_agent.py
│   ├── compliance_agent.py
│   └── report_agent.py
├── data_pipeline/
│   ├── ingestion.py
│   ├── chunking_embeddings.py
│   └── knowledge_graph.py
├── ml_components/
│   ├── document_classification.py
│   └── risk_analysis_model.py
├── tests/
│   ├── services/
│   └── data_pipeline/
├── docker/
│   ├── docker-compose.yml
│   └── base.Dockerfile
├── kubernetes/
│   ├── deployment.yaml
│   └── service.yaml
├── ci_cd/
│   └── workflow.yaml
└── observability/
    ├── prometheus.yaml
    └── grafana_dashboard.json
```

---

## Tech Stack

See `docs/tech_stack.md` for the full list. Key technologies:

- **LangChain** – LLM orchestration and RAG pipelines
- **LlamaIndex** – Graph-aware document indexing
- **ChromaDB / FAISS** – Vector similarity search
- **Neo4j** – Knowledge graph storage and traversal
- **FastAPI** – High-performance REST APIs
- **Prefect** – Data pipeline orchestration
- **LangGraph / CrewAI** – Multi-agent reasoning frameworks
- **OpenAI / HuggingFace** – LLM and embedding models
- **Prometheus + Grafana** – Observability stack

---

## Local Setup

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Neo4j (or run via Docker)
- OpenAI API key (or HuggingFace token)

### Clone the Repository

```bash
git clone https://github.com/justin-mbca/ml_rag_portfolio.git
cd ml_rag_portfolio
```

### Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### Run with Docker Compose

```bash
cd docker
docker-compose up --build
```

Services will be available at:

| Service | URL |
|---|---|
| API Gateway | http://localhost:8000 |
| Ingestion Service | http://localhost:8001 |
| RAG Service | http://localhost:8002 |
| Graph Service | http://localhost:8003 |
| Agent Service | http://localhost:8004 |

### Run Locally (without Docker)

```bash
pip install -r services/rag-service/requirements.txt
uvicorn services.rag-service.app:app --reload --port 8002
```

---

## Usage Examples

See `docs/examples.md` for detailed examples. Quick samples:

### Query via API Gateway

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key compliance risks related to AML regulations?"}'
```

### Python Client

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "Summarise the Basel III capital requirements"}
)
print(response.json()["answer"])
```

### Example Output

```json
{
  "answer": "Basel III requires banks to maintain a minimum Common Equity Tier 1 (CET1) ratio of 4.5%, a Tier 1 capital ratio of 6%, and a total capital ratio of 8%...",
  "sources": ["Basel_III_Framework.pdf", "Capital_Requirements_Policy.pdf"],
  "retrieval_method": "hybrid",
  "agent": "compliance_agent"
}
```

---

## Deployment

### Kubernetes

```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

### CI/CD

The GitHub Actions pipeline in `ci_cd/workflow.yaml` automatically:
1. Runs unit and integration tests
2. Builds Docker images
3. Pushes images to a container registry
4. Deploys to Kubernetes

---

## Observability

- **Prometheus**: Scrapes metrics from all services (`observability/prometheus.yaml`)
- **Grafana**: Dashboards for RAG latency, agent performance, ingestion rates (`observability/grafana_dashboard.json`)
- **Structured Logging**: JSON logs from all FastAPI services

---

## ML Components

- **Document Classification** (`ml_components/document_classification.py`): Classifies documents into categories (policy, regulation, risk report, etc.)
- **Risk Analysis Model** (`ml_components/risk_analysis_model.py`): Predicts risk categories using scikit-learn / HuggingFace transformers

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Push and open a Pull Request

---

## License

MIT License – see [LICENSE](LICENSE) for details.
