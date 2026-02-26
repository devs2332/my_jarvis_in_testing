# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for frontend dev)
- Python 3.12+ (for backend dev)
- PostgreSQL 16 and Redis 7 (or use Docker)
- Stripe account (for billing)
- OpenAI API key

---

## Local Development

### 1. Clone and Configure

```bash
cd platform
cp deploy/.env.example deploy/.env
# Edit deploy/.env with your actual API keys
```

### 2. Start with Docker Compose

```bash
cd deploy/docker
docker-compose up -d
```

This starts: **backend** (port 8000), **frontend** (port 3000), **PostgreSQL** (5432), **Redis** (6379).

### 3. Manual Backend Setup (Alternative)

```bash
cd platform/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 4. Manual Frontend Setup (Alternative)

```bash
cd platform/frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` with API proxy to backend.

---

## Production Deployment (Kubernetes)

### 1. Configure Secrets

Edit `deploy/k8s/secrets.yaml` with production values:
- Database URL
- Redis URL
- JWT secret (generate: `openssl rand -hex 32`)
- OpenAI API key
- Stripe keys

### 2. Build and Push Docker Images

```bash
# Backend
docker build -f deploy/docker/Dockerfile.backend -t ghcr.io/your-org/jarvis-backend:v1.0.0 .
docker push ghcr.io/your-org/jarvis-backend:v1.0.0

# Frontend
docker build -f deploy/docker/Dockerfile.frontend -t ghcr.io/your-org/jarvis-frontend:v1.0.0 .
docker push ghcr.io/your-org/jarvis-frontend:v1.0.0
```

### 3. Deploy to Kubernetes

```bash
cd deploy/k8s

kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml
```

### 4. Verify Deployment

```bash
kubectl get pods -n jarvis-ai
kubectl get services -n jarvis-ai
kubectl get ingress -n jarvis-ai

# Check backend health
kubectl port-forward svc/backend-service 8000:8000 -n jarvis-ai
curl http://localhost:8000/health
```

### 5. Set Up TLS

Install cert-manager and create a ClusterIssuer for Let's Encrypt:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 6. Configure Stripe Webhooks

Point Stripe webhooks to: `https://jarvis.yourdomain.com/api/v1/billing/webhook`

Events to subscribe:
- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_failed`

---

## CI/CD

The GitHub Actions pipeline (`.github/workflows/ci-cd.yml`) handles:

1. **On PR**: Lint + Test
2. **On merge to main**: Lint → Test → Docker Build → Push → Deploy to K8s

Required GitHub Secrets:
- `KUBE_CONFIG` — base64 encoded kubeconfig

---

## Database Migrations (Production)

```bash
cd platform/backend
alembic upgrade head
```

For initial setup without Alembic, the app auto-creates tables on first start (dev mode only).
