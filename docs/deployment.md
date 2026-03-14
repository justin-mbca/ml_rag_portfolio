# Deployment Guide

## Kubernetes Deployment

### Prerequisites
- Kubernetes 1.26+
- kubectl configured
- Docker images built and pushed to registry

### 1. Build & Push Images

```bash
# Set your registry
export REGISTRY=ghcr.io/justin-mbca

# Build and push all services
for svc in ingestion-service rag-service graph-service agent-service api-gateway; do
  docker build -t $REGISTRY/$svc:latest services/$svc/
  docker push $REGISTRY/$svc:latest
done
```

### 2. Create Secrets

```bash
kubectl create namespace genai-platform

kubectl create secret generic db-credentials \
  --namespace genai-platform \
  --from-literal=POSTGRES_PASSWORD=<your-password> \
  --from-literal=NEO4J_PASSWORD=<your-password>
```

### 3. Apply Manifests

```bash
# Base infrastructure
kubectl apply -k kubernetes/base/

# Production overlays
kubectl apply -k kubernetes/overlays/production/
```

### 4. Verify Deployment

```bash
kubectl get pods -n genai-platform
kubectl get services -n genai-platform
```

## CI/CD Pipeline

The GitHub Actions workflow at `.github/workflows/ci-cd.yaml` (sourced from `ci/github-actions/ci-cd.yaml`) provides:

1. **test** job: Runs `pytest tests/unit/`
2. **build-and-push** job: Builds Docker images and pushes to `ghcr.io`
3. **deploy** job: Applies Kubernetes manifests using `KUBE_CONFIG_DATA` secret

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `KUBE_CONFIG_DATA` | Base64-encoded kubeconfig |
| `NEO4J_PASSWORD` | Neo4j password for K8s secret |
| `POSTGRES_PASSWORD` | PostgreSQL password for K8s secret |

## Cloud Deployment (Azure AKS)

```bash
# Login to Azure
az login
az aks get-credentials --resource-group <rg> --name <cluster>

# Push to Azure Container Registry
az acr login --name <registry>
docker tag api-gateway:latest <registry>.azurecr.io/api-gateway:latest
docker push <registry>.azurecr.io/api-gateway:latest
```
