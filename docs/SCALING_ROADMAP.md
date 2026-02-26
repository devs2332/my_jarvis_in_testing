# Scaling Roadmap — 100K+ Users

## Current Architecture Capacity

| Component | Current | Scaling Strategy |
|-----------|---------|-----------------|
| Backend | 3 pods, 4 workers each | HPA: 3→20 pods |
| Frontend | 2 pods (Nginx) | HPA: 2→10 pods |
| PostgreSQL | Single instance | → Managed DB (RDS/Cloud SQL) |
| Redis | Single instance | → Redis Cluster / Elasticache |
| Chroma | Local PVC | → Managed vector DB (Pinecone/Weaviate) |

---

## Phase 1: 0–10K Users

**Architecture:** Current K8s setup handles this with HPA.

- Backend: 3–8 pods handle ~500 concurrent connections
- PostgreSQL: Single instance with connection pooling
- Redis: Single instance for rate limiting + cache
- Estimated infra cost: **$200–500/month**

---

## Phase 2: 10K–50K Users

**Key Changes:**

1. **Database** → Migrate to managed PostgreSQL (AWS RDS, GCP Cloud SQL)
   - Read replicas for chat history queries
   - Connection pooling with PgBouncer

2. **Redis** → Redis Cluster or AWS Elasticache
   - Separate instances for cache vs rate limiting

3. **CDN** → CloudFront/Cloudflare for frontend static assets

4. **Backend** → 10–15 pods with optimized worker count

5. **Monitoring** → Datadog or Grafana Cloud for observability

- Estimated infra cost: **$1,000–2,500/month**

---

## Phase 3: 50K–100K+ Users

**Key Changes:**

1. **Multi-Region** → Deploy to 2+ regions (US, EU)
   - Global load balancer (Cloudflare, AWS Global Accelerator)
   - Regional database replicas

2. **Vector DB** → Migrate Chroma to Pinecone or Weaviate Cloud
   - Better performance at scale
   - Managed infrastructure

3. **Message Queue** → Add RabbitMQ/SQS for async processing
   - Background token tracking
   - Webhook processing
   - Email notifications

4. **Caching** → Aggressive LLM response caching
   - Cache common queries
   - Semantic similarity cache

5. **Backend** → 15–20+ pods, consider serverless for webhooks

6. **Database Sharding** → User-based partitioning
   - Conversations table partitioned by user_id
   - Token usage table partitioned by date

- Estimated infra cost: **$5,000–15,000/month**

---

## Key Scaling Principles

1. **Stateless Backend** — No server-side state; all state in PostgreSQL/Redis
2. **Horizontal Scaling** — Add pods, not bigger machines
3. **Externalized Sessions** — JWT tokens + Redis (no sticky sessions)
4. **Connection Pooling** — PgBouncer for database connections
5. **Async Everything** — FastAPI async handlers, background tasks
6. **Cache Aggressively** — Redis cache for repeated LLM queries
7. **Rate Limit Early** — Protect LLM API costs at the gateway level
8. **Observe Everything** — Prometheus metrics, structured logging, tracing

---

## Cost Optimization Strategies

- **LLM Costs**: Route free users to GPT-4o-mini (10x cheaper)
- **Caching**: Cache identical prompts to avoid duplicate API calls
- **Token Limits**: Enforce per-plan limits to control spending
- **Spot Instances**: Use K8s spot/preemptible nodes for non-critical workloads
- **Right-sizing**: Monitor resource usage and adjust pod limits
