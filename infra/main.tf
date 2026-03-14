terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_project_service" "run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_cloud_run_v2_service" "audit_service" {
  name       = "skynet-ops-audit-service"
  location   = var.region
  depends_on = [google_project_service.run]

  template {
    containers {
      image = var.image

      env {
        name  = "APP_ENV"
        value = "dev"
      }
      env {
        name  = "LOG_LEVEL"
        value = "info"
      }
      env {
        name  = "SERVICE_NAME"
        value = "skynet-ops-audit-service"
      }
      env {
        name  = "SQLITE_PATH"
        value = "/tmp/events.db"
      }

      resources {
        limits = {
          cpu    = "1"
          "memory" = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.audit_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_logging_metric" "error_count" {
  name   = "skynet-error-count"
  filter = "resource.type=cloud_run_revision AND severity>=ERROR"

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}
