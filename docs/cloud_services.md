# Cloud Services Guide

This document describes the cloud services needed to deploy and operate the GenAI Financial Knowledge Assistant Platform, across both local/self-hosted and cloud-managed configurations.

---

## Summary

The platform is **cloud-agnostic** — it can run fully on-premises with Docker Compose or be deployed to any managed Kubernetes service. No specific cloud provider is required for local development.

For production deployments, you will need:

| Service Category | Required? | Purpose |
|---|---|---|
| Container registry | ✅ Required | Store Docker images |
| Kubernetes cluster | ✅ Required | Run microservices |
| External secrets manager | Recommended | Secure credentials in production |
| Managed PostgreSQL | Optional | Replace self-hosted container |
| Managed Redis | Optional | Replace self-hosted container |
| Managed vector/graph DB | Optional | Replace self-hosted ChromaDB/Neo4j |
| OpenAI / Azure OpenAI API | Optional | LLM integration (roadmap) |
| Object storage (S3/Blob) | Optional | Large-scale document ingestion |

---

## 1. Container Registry

Docker images for all five microservices must be stored in a container registry so that Kubernetes can pull them.

### GitHub Container Registry (GHCR) — Default

The CI/CD pipeline pushes images to **GitHub Container Registry** automatically on every merge to `main`.

- **Registry URL:** `ghcr.io/<github-username>`
- **Authentication:** `GITHUB_TOKEN` (automatically provided in GitHub Actions)
- **No additional setup required** when using GitHub Actions

### Azure Container Registry (ACR)

```bash
az acr login --name <registry-name>
docker tag api-gateway:latest <registry-name>.azurecr.io/api-gateway:latest
docker push <registry-name>.azurecr.io/api-gateway:latest
```

### Amazon Elastic Container Registry (ECR)

```bash
aws ecr get-login-password --region <region> | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.<region>.amazonaws.com

docker tag api-gateway:latest \
  <account-id>.dkr.ecr.<region>.amazonaws.com/api-gateway:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/api-gateway:latest
```

### Google Artifact Registry (GAR)

```bash
gcloud auth configure-docker <region>-docker.pkg.dev
docker tag api-gateway:latest \
  <region>-docker.pkg.dev/<project-id>/genai-platform/api-gateway:latest
docker push <region>-docker.pkg.dev/<project-id>/genai-platform/api-gateway:latest
```

---

## 2. Kubernetes Cluster

All five application services and supporting infrastructure (PostgreSQL, Redis, Neo4j, ChromaDB) are deployed as Kubernetes workloads.

### Supported Platforms

| Platform | Provider | Setup Command |
|---|---|---|
| Azure Kubernetes Service (AKS) | Microsoft Azure | `az aks get-credentials --resource-group <rg> --name <cluster>` |
| Amazon Elastic Kubernetes Service (EKS) | AWS | `aws eks update-kubeconfig --name <cluster> --region <region>` |
| Google Kubernetes Engine (GKE) | Google Cloud | `gcloud container clusters get-credentials <cluster> --region <region>` |
| Self-managed | Any / On-premises | Configure `~/.kube/config` manually |

### Minimum Requirements

- Kubernetes 1.26+
- At least **4 vCPU** and **8 GB RAM** across the cluster
- `kubectl` configured with cluster access
- A base64-encoded kubeconfig stored as the `KUBE_CONFIG_DATA` GitHub secret for CI/CD

---

## 3. Required GitHub Secrets

The CI/CD pipeline (`ci/github-actions/ci-cd.yaml`) uses the following GitHub repository secrets:

| Secret | Description | Where Used |
|---|---|---|
| `KUBE_CONFIG_DATA` | Base64-encoded kubeconfig for deployment target | Deploy job |
| `NEO4J_PASSWORD` | Neo4j database password | K8s secret creation |
| `POSTGRES_PASSWORD` | PostgreSQL database password | K8s secret creation |
| `GITHUB_TOKEN` | Auto-provided — no action needed | Push images to GHCR |

```bash
# Encode your kubeconfig
cat ~/.kube/config | base64 | tr -d '\n'
```

---

## 4. Self-Hosted Infrastructure (Included)

The following infrastructure services run as containers and do **not** require external cloud accounts by default:

| Service | Docker Image | Port | Purpose |
|---|---|---|---|
| ChromaDB | `chromadb/chroma` | 8000 | Vector embeddings store |
| Neo4j | `neo4j:5` | 7474, 7687 | Knowledge graph database |
| PostgreSQL | `postgres:15` | 5432 | Document metadata |
| Redis | `redis:7` | 6379 | Response caching |

These are defined in `docker/docker-compose.yml` for local development and in `kubernetes/base/` for Kubernetes deployments.

---

## 5. Optional Managed Cloud Services

For production workloads requiring high availability and reduced operational overhead, you can replace the self-hosted containers with managed equivalents:

### Managed Vector Database
- **Pinecone** — drop-in replacement for ChromaDB with managed scaling
- **Weaviate Cloud** — managed vector store with GraphQL API
- **Azure AI Search** — managed vector + full-text search on Azure

### Managed Graph Database
- **Neo4j AuraDB** — fully managed Neo4j on any major cloud provider
  - Connection: update `NEO4J_URI` in your environment to point at the AuraDB endpoint

### Managed Relational Database
- **Amazon RDS for PostgreSQL**
- **Azure Database for PostgreSQL – Flexible Server**
- **Google Cloud SQL for PostgreSQL**

### Managed Cache
- **Amazon ElastiCache for Redis**
- **Azure Cache for Redis**
- **Google Cloud Memorystore**

---

## 6. LLM API (Roadmap)

LLM integration is on the roadmap. When implemented, the platform will support:

| Service | Provider | Environment Variable |
|---|---|---|
| OpenAI GPT-4o / GPT-4 | OpenAI | `OPENAI_API_KEY` |
| Azure OpenAI Service | Microsoft Azure | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |

Add the relevant key to `docker/.env` or as a Kubernetes secret when this feature is enabled.

---

## 7. Object Storage (Optional, for Large-Scale Ingestion)

For ingesting large document libraries, you can stage files in object storage and point the Ingestion Service at the bucket:

| Service | Provider |
|---|---|
| Amazon S3 | AWS |
| Azure Blob Storage | Microsoft Azure |
| Google Cloud Storage | GCP |

This replaces the local filesystem source currently used by the Ingestion Service.

---

## 8. Observability (Included)

The observability stack runs as self-hosted containers and requires no external cloud services:

| Service | Port | Purpose |
|---|---|---|
| Prometheus | 9090 | Metrics collection from all services |
| Grafana | 3000 | Pre-built dashboards (admin / admin) |

For production, you may forward metrics to managed observability platforms such as **Datadog**, **Azure Monitor**, or **AWS CloudWatch** by adding exporters to `observability/prometheus.yml`.

---

## Quick Reference: Minimum Cloud Requirements for Production

```
1. Container Registry  →  GHCR (free with GitHub) or cloud-provider registry
2. Kubernetes Cluster  →  AKS / EKS / GKE (choose one) OR self-managed cluster
3. GitHub Secrets      →  KUBE_CONFIG_DATA, NEO4J_PASSWORD, POSTGRES_PASSWORD
```

Everything else runs inside the cluster using the Kubernetes manifests in `kubernetes/`.

See [deployment.md](deployment.md) for step-by-step deployment instructions.
