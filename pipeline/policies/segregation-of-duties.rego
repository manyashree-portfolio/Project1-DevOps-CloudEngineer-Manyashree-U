# Gate 7 - Segregation of duties (RBI 4.3, PCI-DSS 6.5). Run with: conftest test change-record.json -p pipeline/policies -n compliance.sod
# input: {"author","deployer","approvers":[...],"approver_roles":[...],"environment"}
package compliance.sod

import rego.v1

deny contains "author cannot approve their own change (RBI 4.3)" if input.author in input.approvers

deny contains "author cannot deploy their own change (RBI 4.3)" if input.author == input.deployer

deny contains "deployer cannot approve the change they deploy (RBI 4.3)" if input.deployer in input.approvers

required_prod_roles := {"release_manager", "sre_lead"}

roles := {r | some r in input.approver_roles}

deny contains msg if {
	input.environment == "production"
	missing := required_prod_roles - roles
	count(missing) > 0
	msg := sprintf("production needs dual approval; missing roles: %v", [missing])
}

deny contains msg if {
	input.environment == "production"
	distinct := {a | some a in input.approvers; a != input.author}
	count(distinct) < 2
	msg := "production requires two distinct approvers other than the author"
}
