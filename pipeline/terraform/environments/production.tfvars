environment   = "production"
vpc_cidr      = "10.40.0.0/16"
azs           = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
node_min_size = 6
node_max_size = 24
admin_cidrs   = [] # private endpoint only; access via VPN / bastion
