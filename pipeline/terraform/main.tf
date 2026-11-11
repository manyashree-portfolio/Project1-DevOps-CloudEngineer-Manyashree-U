module "secrets" {
  source      = "./modules/secrets"
  environment = var.environment
}

module "network" {
  source      = "./modules/network"
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
  azs         = var.azs
}

module "eks" {
  source              = "./modules/eks"
  environment         = var.environment
  kubernetes_version  = var.kubernetes_version
  private_subnet_ids  = module.network.private_subnet_ids
  kms_key_arn         = module.secrets.kms_key_arn
  node_instance_types = var.node_instance_types
  node_min_size       = var.node_min_size
  node_max_size       = var.node_max_size
  admin_cidrs         = var.admin_cidrs
}
