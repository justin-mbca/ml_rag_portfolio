# Running Locally

## Prerequisites

- Docker 24+ and Docker Compose v2+
- Python 3.10+
- Git

## Step 1: Clone Repository

```bash
git clone https://github.com/justin-mbca/ml_rag_portfolio.git
cd ml_rag_portfolio
```

## Step 2: Environment Variables

Create `docker/.env` with:

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=genai_platform

# Neo4j
NEO4J_AUTH=neo4j/changeme
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=changeme

# Redis
REDIS_URL=redis://redis:6379

# API
API_KEY=dev-secret-key

# Optional: OpenAI
# OPENAI_API_KEY=sk-...
```

## Step 3: Start Services

```bash
cd docker
docker compose up --build -d
```

Wait for all services to be healthy:

```bash
docker compose ps
```

## Step 4: Ingest Sample Data

```bash
curl -X POST http://localhost:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/data/sample"}'
```

## Step 5: Query the Platform

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -d '{"question": "What are the AML compliance requirements?"}'
```

## Step 6: Train ML Model (Optional)

```bash
cd models/training
pip install pandas scikit-learn joblib
python train_risk_classifier.py
```

## Step 7: Access UIs

| Service | URL | Credentials |
|---|---|---|
| Neo4j Browser | http://localhost:7474 | neo4j / changeme |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | — |

## Running Tests

```bash
pip install pytest pytest-asyncio httpx
pytest tests/unit/ -v
```

## Stopping Services

```bash
cd docker
docker compose down -v
```
