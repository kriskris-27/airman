# AIRMAN Skynet Cloud Ops Intern Assessment — Submission Checklist

## 1) Candidate & Submission Info
- **Name:** Kris
- **Email:** krishnakumars0101@gmail.com
- **Chosen Cloud Platform:** GCP
- **Assessment Level Submitted:** Level 1 only
- **GitHub Repo Link:** (add your repo URL)
- **Demo Video Link:** (add your video URL)
- **Submission Date (UTC):** 2026-03-14

---

## 2) What I Implemented

### Level 1
- [x] Mini service (`/health`, `/events`, `/metrics-demo`)
- [x] Dockerized service
- [x] Cloud deployment (GCP Cloud Run via Terraform)
- [x] Infrastructure as Code (Terraform)
- [x] Cost optimization report
- [x] Observability setup (GCP Cloud Logging, structured JSON logs)
- [x] Security/secrets approach (.env.example, no secrets in repo)
- [x] Ops runbook
- [x] README with setup + teardown

---

## 3) Repository Structure

### Service Code
- Service path: `app/`
- Main entry file: `run.py`
- Local run command: `python run.py`

### Docker
- Dockerfile path: `Dockerfile`
- `.dockerignore` path: `.dockerignore`

### Infrastructure as Code
- IaC tool used: Terraform
- IaC root path: `infra/`
- Environment config files: `infra/terraform.tfvars.example`

### Docs
- README path: `README.md`
- Cost report path: `docs/cost_report.md`
- Runbook path: `docs/runbook.md`
- Observability notes: GCP Cloud Logging (automatic with Cloud Run)
- Security/secrets notes: `.env.example`, no secrets committed

---

## 4) Local Run Instructions

### Prerequisites
- [x] Docker installed
- [x] Python 3.12+ installed
- [x] Terraform installed
- [x] gcloud CLI installed

### Local Setup
```bash
cp .env.example .env
pip install -r requirements.txt
python run.py
```

### Run with Docker
```bash
docker build -t skynet-ops-audit-service .
docker run -p 8080:8080 -e APP_ENV=dev skynet-ops-audit-service
```

### Test Endpoints
```bash
curl http://localhost:8080/health

curl -X POST http://localhost:8080/events \
  -H "Content-Type: application/json" \
  -d '{"type":"roster_update","tenantId":"academy_001","severity":"info","message":"Instructor schedule adjusted","source":"skynet-api"}'

curl http://localhost:8080/events?tenantId=academy_001

curl http://localhost:8080/metrics-demo?mode=error
```

---

## 5) API Endpoint Checklist

### Health
- [x] GET /health works

### Events
- [x] POST /events stores an event
- [x] GET /events returns events
- [x] Validation rejects bad payloads (400)

### Optional
- [x] GET /metrics-demo implemented
- [x] Route simulates latency/errors for observability testing

---

## 6) Cloud Deployment Summary

### Deployment Type
- [x] Real cloud deployment (GCP Cloud Run)

### Cloud Services Used
- **Compute:** GCP Cloud Run
- **Storage/DB:** SQLite (ephemeral, /tmp)
- **Networking/Ingress:** Cloud Run built-in HTTPS ingress
- **Logging/Monitoring:** GCP Cloud Logging + Cloud Monitoring
- **Secrets:** Secret Manager (provisioned via Terraform)
- **Budgeting/Alerts:** GCP Billing alerts
- **Container Registry:** Google Container Registry (GCR)
- **IAM:** allUsers invoker role for public access (demo)

### Why I chose this architecture
- Cloud Run scales to zero — no idle compute cost at pilot scale
- Bursty traffic pattern (70% in 10-hour window) matches serverless model
- Built-in HTTPS ingress — no load balancer cost
- Terraform makes deployment fully reproducible and destroyable
- SQLite is sufficient for pilot-scale audit log storage

### Pilot Cost-Awareness Notes
- Estimated cost: $0–$3/month (within $25–$75 target)
- Scale-to-zero eliminates idle spend
- No persistent disks, no static IPs, no NAT gateway
- Log retention set to 7 days for dev environment

---

## 7) Cost Optimization Report
See [docs/cost_report.md](docs/cost_report.md)

- [x] Monthly estimate included (~$0–$3/month)
- [x] Assumptions documented
- [x] Component-wise cost breakdown included

### Common Cost Traps Accounted For
1. Idle compute — scale-to-zero on Cloud Run
2. Overprovisioned DB — SQLite, no managed DB
3. Excessive log retention — 7 days dev retention
4. NAT gateway costs — not needed with Cloud Run
5. Static IPs left running — none provisioned
6. Container registry bloat — single image tag
7. Snapshots and unattached disks — no persistent disks
8. Cross-region traffic — single region deployment

---

## 8) Observability & Monitoring

### Logging
- [x] Structured JSON logs implemented (python-json-logger)
- [x] Log level configurable via LOG_LEVEL env var
- [x] Logs visible in GCP Cloud Logging

### Metrics
- [x] Error count metric (google_logging_metric in Terraform)
- [x] Request latency visible in Cloud Run metrics
- [x] Health signal monitoring via /health endpoint

### Alerts
- **Alert 1:** Error rate >5% over 5 minutes — indicates systematic failure
- **Alert 2:** Response latency >2000ms p95 — exceeds pilot SLO

---

## 9) Security / Secrets / IAM

### Secrets
- [x] No secrets committed to repo
- [x] .env.example included
- [x] Secret Manager provisioned via Terraform

### IAM
- Cloud Run service uses default compute service account
- allUsers invoker role granted for demo purposes
- In production: restrict to authenticated users only

### Security Basics
- Non-root user inside Docker container
- No sensitive env vars hardcoded in Terraform
- .env excluded via .gitignore

---

## 10) Ops Runbook
See [docs/runbook.md](docs/runbook.md)

- [x] Service down / health checks failing
- [x] Latency spike
- [x] Sudden cost spike
- [x] DB/storage issue
- [x] Bad deployment / rollback
- [x] Accidental public exposure / misconfiguration

---

## 11) IaC Validation

- [x] terraform init works
- [x] terraform validate works
- [x] terraform plan works
- [x] terraform apply successfully deployed
- [x] Variables documented in variables.tf
- [x] Output (service_url) documented in outputs.tf

### Teardown
```bash
cd infra
terraform destroy
```

---

## 12) Known Limitations / Trade-offs

1. SQLite is ephemeral on Cloud Run — data resets on container restart. Acceptable for pilot/demo; production would use Cloud SQL or Firestore.
2. No authentication on endpoints — allUsers access for demo. Production would require API key or OAuth.
3. Single region deployment — no failover. Acceptable for 99% pilot SLO target.
4. No CI/CD pipeline — manual docker build + push. Would add GitHub Actions for production.
5. No persistent monitoring dashboard — relies on GCP Cloud Logging default views.

---

## 13) AI Tool Usage Disclosure

### AI tools used
- [x] Claude

### What I used AI for
- Scaffolding Flask service structure
- Writing Terraform configuration
- Generating cost report and runbook templates

### What I manually verified / tested
- All 4 endpoints tested locally with curl
- Docker container built and run locally
- Terraform plan reviewed before apply
- Live GCP deployment verified with curl

---

## 14) Final Notes
Service is fully deployed and accessible at:
https://skynet-ops-audit-service-6c3atqsbya-uc.a.run.app

Run `terraform destroy` from the `infra/` directory to tear down all GCP resources after evaluation.
