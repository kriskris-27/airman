# Cost Optimization Report — skynet-ops-audit-service

## Deployment Context
- Platform: GCP Cloud Run
- Environment: dev (pilot)
- Tenants: 1–3 flight training academies

## Workload Assumptions
- 5,000–20,000 requests/day
- Request mix: 55% POST /events, 35% GET /events, 10% GET /health
- Average payload: 1.5 KB inbound, 20 KB outbound
- Data growth: ~100 MB/month

## Monthly Cost Estimate

| Component | Service | Est. Cost |
|---|---|---|
| Compute | Cloud Run (scale-to-zero) | $0–$2 |
| Storage | SQLite on /tmp (ephemeral) | $0 |
| Container Registry | GCR (~500MB image) | ~$0.10 |
| Logging | Cloud Logging (first 50GB free) | $0 |
| Monitoring | Cloud Monitoring (free tier) | $0 |
| Secrets | Secret Manager (<6 versions) | $0 |
| **Total** | | **~$0–$3/month** |

Well within the $25–$75/month pilot budget.

## Why Cloud Run
- Scale-to-zero: no idle compute cost
- Bursty traffic pattern matches serverless model
- 2 million requests/month on free tier
- No VM management overhead

## Cost Controls Implemented
- scale-to-zero (min_instance_count = 0)
- max 2 instances cap
- 512Mi memory limit
- Cloud Logging retention: 7 days (dev)
- No static IPs provisioned
- No load balancer (Cloud Run has built-in ingress)

## Common Cost Traps Avoided
1. Idle compute — avoided via scale-to-zero
2. Overprovisioned DB — avoided by using SQLite on ephemeral storage
3. Excessive log retention — set to 7 days for dev
4. NAT gateway costs — not needed, Cloud Run has direct ingress
5. Static IPs left running — none provisioned
6. Container registry bloat — single image tag, no version accumulation
7. Snapshots and unattached disks — no persistent disks used
8. Cross-region traffic — single region (us-central1) deployment

## Teardown Instructions
```bash
cd infra
terraform destroy
```
This removes all GCP resources. Run after assessment completion.
