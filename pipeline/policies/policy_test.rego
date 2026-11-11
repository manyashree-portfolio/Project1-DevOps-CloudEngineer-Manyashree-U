# Unit tests: run `opa test pipeline/policies -v` or `conftest verify -p pipeline/policies`
package main

import rego.v1

good_deployment := {
	"kind": "Deployment",
	"metadata": {"name": "good"},
	"spec": {"template": {"spec": {
		"securityContext": {"runAsNonRoot": true},
		"containers": [{
			"name": "app",
			"image": "novapay.jfrog.io/novapay-docker/novapay-app:2.4.1-build.a1b2c3d",
			"securityContext": {"allowPrivilegeEscalation": false},
			"resources": {"limits": {"cpu": "1", "memory": "1Gi"}},
		}],
	}}},
}

test_good_deployment_passes if count(deny) == 0 with input as good_deployment

test_privileged_denied if {
	bad := object.union(good_deployment, {"spec": {"template": {"spec": {"containers": [{
		"name": "app",
		"image": "novapay.jfrog.io/novapay-docker/novapay-app:2.4.1",
		"securityContext": {"privileged": true, "allowPrivilegeEscalation": false},
		"resources": {"limits": {"cpu": "1", "memory": "1Gi"}},
	}]}}}})
	count(deny) > 0 with input as bad
}

test_latest_tag_denied if {
	bad := object.union(good_deployment, {"spec": {"template": {"spec": {"containers": [{
		"name": "app",
		"image": "novapay.jfrog.io/novapay-docker/novapay-app:latest",
		"securityContext": {"allowPrivilegeEscalation": false},
		"resources": {"limits": {"cpu": "1", "memory": "1Gi"}},
	}]}}}})
	count(deny) > 0 with input as bad
}

test_missing_limits_denied if {
	bad := object.union(good_deployment, {"spec": {"template": {"spec": {"containers": [{
		"name": "app",
		"image": "novapay.jfrog.io/novapay-docker/novapay-app:2.4.1",
		"securityContext": {"allowPrivilegeEscalation": false},
	}]}}}})
	count(deny) > 0 with input as bad
}

test_gateway_without_tls13_denied if {
	gw := {"kind": "Gateway", "metadata": {"name": "gw"}, "spec": {"servers": [{"port": {"name": "https", "protocol": "HTTPS"}, "tls": {"minProtocolVersion": "TLSV1_2"}}]}}
	count(deny) > 0 with input as gw
}
