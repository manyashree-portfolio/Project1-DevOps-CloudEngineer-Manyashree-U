# One customer-managed key per environment: encrypts Kubernetes secrets (EKS), logs and Secrets Manager.
resource "aws_kms_key" "this" {
  description             = "NovaPay ${var.environment} data and secrets key"
  enable_key_rotation     = true
  deletion_window_in_days = 30
}

resource "aws_kms_alias" "this" {
  name          = "alias/novapay-${var.environment}"
  target_key_id = aws_kms_key.this.key_id
}

# Secret containers only. VALUES are never in Git or Terraform state: they are set out-of-band
# and rotated by Secrets Manager rotation Lambdas (90 days for database passwords, 30 days for API keys).
resource "aws_secretsmanager_secret" "db_password" {
  name       = "novapay/${var.environment}/db-password"
  kms_key_id = aws_kms_key.this.arn
  tags       = { RotationDays = "90" }
}

resource "aws_secretsmanager_secret" "api_keys" {
  name       = "novapay/${var.environment}/payment-gateway-api-key"
  kms_key_id = aws_kms_key.this.arn
  tags       = { RotationDays = "30" }
}
