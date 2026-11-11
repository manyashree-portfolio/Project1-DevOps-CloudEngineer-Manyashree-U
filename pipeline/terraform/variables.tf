variable "region" {
  description = "AWS region (Mumbai by default for RBI data-localisation intent)."
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "One of dev, staging, preprod, production."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "preprod", "production"], var.environment)
    error_message = "environment must be dev, staging, preprod or production."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for the environment VPC."
  type        = string
}

variable "azs" {
  description = "Availability zones (at least 3 for production)."
  type        = list(string)
}

variable "kubernetes_version" {
  description = "EKS version (brief: Kubernetes 1.29+)."
  type        = string
  default     = "1.29"
}

variable "node_instance_types" {
  type    = list(string)
  default = ["m6i.large"]
}

variable "node_min_size" {
  type    = number
  default = 3
}

variable "node_max_size" {
  type    = number
  default = 12
}

variable "admin_cidrs" {
  description = "CIDR ranges allowed to reach the private API endpoint (VPN / bastion only)."
  type        = list(string)
  default     = []
}
