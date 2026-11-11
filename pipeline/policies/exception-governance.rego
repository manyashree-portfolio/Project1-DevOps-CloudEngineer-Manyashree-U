# Exception workflow guardrails: every exception is time-bound, approved by the right roles, and auto-expires.
# Run with: conftest test exception.json -p pipeline/policies -n compliance.exceptions
# input: {"id","gate","approved_at","expires_at","approver_roles":[...]}  (RFC 3339 timestamps)
package compliance.exceptions

import rego.v1

day_ns := ((24 * 60) * 60) * 1000000000

max_days := {"sast": 7, "dast": 14, "dependency": 3, "licence": 30, "policy": 7, "infra": 30}

required_roles := {
	"sast": {"ciso"},
	"dast": {"risk_owner", "trc"},
	"dependency": {"ciso"},
	"licence": {"legal"},
	"policy": {"release_manager", "sre_lead"},
	"infra": {"tech_lead"},
}

roles := {r | some r in input.approver_roles}

deny contains msg if {
	not max_days[input.gate]
	msg := sprintf("unknown gate '%s'", [input.gate])
}

deny contains msg if {
	validity := time.parse_rfc3339_ns(input.expires_at) - time.parse_rfc3339_ns(input.approved_at)
	validity > max_days[input.gate] * day_ns
	msg := sprintf("exception %s exceeds the maximum validity of %d days for gate %s", [input.id, max_days[input.gate], input.gate])
}

deny contains msg if {
	time.now_ns() > time.parse_rfc3339_ns(input.expires_at)
	msg := sprintf("exception %s has expired - the gate applies again", [input.id])
}

deny contains msg if {
	missing := required_roles[input.gate] - roles
	count(missing) > 0
	msg := sprintf("exception %s lacks approval from: %v", [input.id, missing])
}
