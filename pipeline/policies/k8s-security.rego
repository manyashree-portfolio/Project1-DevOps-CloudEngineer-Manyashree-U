# Gate 5 - Kubernetes policy (OPA/Conftest at pipeline time; Kyverno re-checks at admission).
# Maps to: RBI 4.2/5.4, PCI-DSS 6.3/6.5 (hardened, approved workloads only).
package main

import rego.v1

# P1 - No privileged containers
deny contains msg if {
	some c in containers
	c.securityContext.privileged == true
	msg := sprintf("%s: privileged container not allowed: %s", [resource_name, c.name])
}

# P2 - CPU and memory limits required (noisy-neighbour / DoS protection)
deny contains msg if {
	some c in containers
	not c.resources.limits.memory
	msg := sprintf("%s: memory limit required: %s", [resource_name, c.name])
}

deny contains msg if {
	some c in containers
	not c.resources.limits.cpu
	msg := sprintf("%s: CPU limit required: %s", [resource_name, c.name])
}

# P3 - Must not run as root
run_as_non_root(c) if c.securityContext.runAsNonRoot == true

run_as_non_root(_) if pod_spec.securityContext.runAsNonRoot == true

deny contains msg if {
	some c in containers
	not run_as_non_root(c)
	msg := sprintf("%s: container must set runAsNonRoot=true: %s", [resource_name, c.name])
}

# P4 - No privilege escalation
deny contains msg if {
	some c in containers
	not c.securityContext.allowPrivilegeEscalation == false
	msg := sprintf("%s: allowPrivilegeEscalation must be false: %s", [resource_name, c.name])
}

# P5 - Images only from the approved registry
deny contains msg if {
	some c in containers
	not startswith(c.image, "novapay.jfrog.io/")
	msg := sprintf("%s: image %s is not from the approved registry novapay.jfrog.io", [resource_name, c.image])
}

# P6 - Never 'latest' or untagged images (SemVer tag or digest required)
last_segment(img) := parts[count(parts) - 1] if parts := split(img, "/")

unpinned(img) if endswith(img, ":latest")

unpinned(img) if {
	indexof(img, "@") == -1
	indexof(last_segment(img), ":") == -1
}

deny contains msg if {
	some c in containers
	unpinned(c.image)
	msg := sprintf("%s: image must use a version tag or digest, never latest/untagged: %s", [resource_name, c.image])
}
