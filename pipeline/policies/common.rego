# Shared helpers for NovaPay Conftest policies (input = one rendered Kubernetes resource).
package main

import rego.v1

workload_kinds := {"Deployment", "StatefulSet", "DaemonSet", "Job", "ReplicaSet", "Rollout"}

pod_spec := input.spec.template.spec if input.kind in workload_kinds

pod_spec := input.spec if input.kind == "Pod"

pod_spec := input.spec.jobTemplate.spec.template.spec if input.kind == "CronJob"

containers contains c if some c in pod_spec.containers

containers contains c if some c in pod_spec.initContainers

resource_name := sprintf("%s/%s", [input.kind, input.metadata.name])
