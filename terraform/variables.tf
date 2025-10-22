variable "grafana_url" {
  type        = string
  description = "Grafana URL with protocol and port (e.g., http://localhost:3002)"
  
  validation {
    condition     = can(regex("^https?://", var.grafana_url))
    error_message = "Grafana URL must start with http:// or https://"
  }
}

variable "grafana_admin_user" {
  type        = string
  description = "Grafana admin username"
  default     = "admin"
}

variable "grafana_admin_password" {
  type        = string
  description = "Grafana admin password"
  sensitive   = true
}

variable "users" {
  type = list(object({
    name     = string
    login    = string
    email    = string
    password = string
    role     = optional(string, "Viewer")
  }))
  description = "List of users to create in Grafana"
  default = [
    {
      name     = "Platform Engineer"
      login    = "platform_engineer"
      email    = "platform@example.com"
      password = "PlatformPass123"
      role     = "Viewer"
    },
    {
      name     = "Consultant"
      login    = "consultant"
      email    = "consultant@example.com"
      password = "ConsultantPass123"
      role     = "Viewer"
    }
  ]
  sensitive = false
}

variable "teams" {
  type = map(object({
    members = list(string)
  }))
  description = "Map of team names to their member logins"
  default = {
    "platform_engineer" = {
      members = ["platform_engineer"]
    }
    "consultant" = {
      members = ["consultant"]
    }
  }
}