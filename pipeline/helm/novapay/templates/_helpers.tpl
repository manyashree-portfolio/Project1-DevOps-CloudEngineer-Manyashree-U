{{/*
Values contract used by these templates (all optional, safe defaults applied):
  nameOverride, image.repository, image.digest (preferred) | image.tag,
  replicaCount, service.port, resources.*, autoscaling.*, pdb.minAvailable,
  config.* (non-secret env), existingSecret, istio.*, networkPolicy.*
Environment differences live ONLY in values-<env>.yaml, never in templates.
*/}}
{{- define "novapay.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "novapay.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "novapay.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "novapay.labels" -}}
app.kubernetes.io/name: {{ include "novapay.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | quote }}
novapay.io/environment: {{ default "dev" .Values.environment | quote }}
{{- end -}}

{{- define "novapay.selectorLabels" -}}
app.kubernetes.io/name: {{ include "novapay.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/* Same artefact everywhere: image is pinned by digest. A tag-only image is allowed
     only outside production, and 'latest' is rejected in every environment. */}}
{{- define "novapay.image" -}}
{{- $img := default dict .Values.image -}}
{{- $repo := required "image.repository is required" $img.repository -}}
{{- if $img.digest -}}
{{- printf "%s@%s" $repo $img.digest -}}
{{- else -}}
{{- $tag := toString (required "image.digest or image.tag is required" $img.tag) -}}
{{- if eq $tag "latest" }}{{ fail "image tag 'latest' is not allowed" }}{{ end -}}
{{- if eq (default "dev" .Values.environment) "production" }}{{ fail "production requires image.digest (same-artefact rule)" }}{{ end -}}
{{- printf "%s:%s" $repo $tag -}}
{{- end -}}
{{- end -}}
