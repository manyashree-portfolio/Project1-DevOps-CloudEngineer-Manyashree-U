# Gate 5/6 - Encryption in transit (RBI 5.4): TLS 1.3 on every Istio Gateway, no plain HTTP without redirect.
package main

import rego.v1

tls13(s) if s.tls.minProtocolVersion == "TLSV1_3"

deny contains msg if {
	input.kind == "Gateway"
	some s in input.spec.servers
	s.port.protocol == "HTTPS"
	not tls13(s)
	msg := sprintf("Gateway/%s: HTTPS server '%s' must set tls.minProtocolVersion: TLSV1_3 (RBI 5.4)", [input.metadata.name, s.port.name])
}

deny contains msg if {
	input.kind == "Gateway"
	some s in input.spec.servers
	s.port.protocol == "HTTP"
	not s.tls.httpsRedirect == true
	msg := sprintf("Gateway/%s: HTTP server '%s' must redirect to HTTPS", [input.metadata.name, s.port.name])
}
