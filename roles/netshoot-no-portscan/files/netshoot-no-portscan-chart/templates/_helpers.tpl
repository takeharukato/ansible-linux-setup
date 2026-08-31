{{/*
Chart名を共通ラベルへ使用できるDNSラベル形式に制限する。
*/}}
{{- define "netshoot-no-portscan.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Helm releaseを識別する標準ラベルをまとめて生成する。
*/}}
{{- define "netshoot-no-portscan.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/name: {{ include "netshoot-no-portscan.name" . }}
app.kubernetes.io/instance: {{ .Release.Name | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
