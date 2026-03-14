# Ops Runbook — skynet-ops-audit-service

## Service Info
- **Live URL:** https://skynet-ops-audit-service-6c3atqsbya-uc.a.run.app
- **Platform:** GCP Cloud Run
- **Region:** us-central1
- **Project:** gcp-play-1212

---

## Scenario 1: Service Down / Health Check Failing

**Symptoms:** GET /health returns non-200 or times out.

**Steps:**
```bash
# Check service status
gcloud run services describe skynet-ops-audit-service --region=us-central1

# Check recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=skynet-ops-audit-service" --limit=50

# Redeploy
cd infra && terraform apply
```

---

## Scenario 2: Latency Spike

**Symptoms:** Response times exceed 1000ms on GET /events or 500ms on POST /events.

**Steps:**
```bash
# Check logs for slow requests
gcloud logging read "resource.type=cloud_run_revision AND severity>=WARNING" --limit=50

# Test latency manually
curl -w "\nTime: %{time_total}s\n" https://skynet-ops-audit-service-6c3atqsbya-uc.a.run.app/health
```

**Likely causes:**
- Cold start (scale-to-zero) — first request after idle period
- SQLite contention under burst traffic

---

## Scenario 3: Sudden Cost Spike

**Symptoms:** GCP billing alert fires above $10/month.

**Steps:**
1. Go to GCP Console → Billing → Cost breakdown
2. Check Cloud Run request count — unexpected traffic spike?
3. Check Cloud Logging volume — excessive debug logging?
4. Check Container Registry — image accumulation?

**Fix:**
```bash
# Scale down immediately
gcloud run services update skynet-ops-audit-service \
  --max-instances=1 --region=us-central1
```

---

## Scenario 4: DB / Storage Issue

**Symptoms:** POST /events returns 500, logs show SQLite errors.

**Note:** SQLite is stored at `/tmp/events.db` inside the container. Data is ephemeral — it resets on container restart. This is acceptable for pilot/demo.

**Fix:** Restart the service revision:
```bash
gcloud run services update skynet-ops-audit-service \
  --region=us-central1 \
  --set-env-vars APP_ENV=dev
```

---

## Scenario 5: Bad Deployment / Rollback

**Symptoms:** New deployment broke the service.

**Steps:**
```bash
# List revisions
gcloud run revisions list --service=skynet-ops-audit-service --region=us-central1

# Roll back to previous revision
gcloud run services update-traffic skynet-ops-audit-service \
  --to-revisions=PREVIOUS_REVISION=100 \
  --region=us-central1
```

---

## Scenario 6: Accidental Public Exposure / Misconfiguration

**Symptoms:** Sensitive data exposed, unauthorized access detected.

**Immediate steps:**
```bash
# Remove public access immediately
gcloud run services remove-iam-policy-binding skynet-ops-audit-service \
  --region=us-central1 \
  --member=allUsers \
  --role=roles/run.invoker

# Check audit logs
gcloud logging read "protoPayload.serviceName=run.googleapis.com" --limit=50
```

---

## Alert Thresholds

| Alert | Threshold | Rationale |
|---|---|---|
| Error rate | >5% over 5 min | Systematic failure, not a fluke |
| Latency | >2000ms p95 | Exceeds acceptable pilot SLO |
| Instance count | >2 instances | Unexpected traffic spike |

---

## Teardown
```bash
cd infra
terraform destroy
```
