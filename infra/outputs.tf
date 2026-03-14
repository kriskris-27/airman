output "service_url" {
  description = "Live URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.audit_service.uri
}
