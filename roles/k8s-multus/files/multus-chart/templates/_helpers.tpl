{{/*
チャート名の展開
*/}}
{{- define "multus-cni.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
デフォルトの完全修飾アプリケーション名(fully qualified app name).
*/}}
{{- define "multus-cni.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
チャートラベルで使用されるチャート名とバージョンを定義
*/}}
{{- define "multus-cni.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
共通ラベル名
*/}}
{{- define "multus-cni.labels" -}}
helm.sh/chart: {{ include "multus-cni.chart" . }}
{{ include "multus-cni.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
tier: {{ .Values.labels.tier }}
app: {{ .Values.labels.app }}
{{- end }}

{{/*
セレクタラベル
*/}}
{{- define "multus-cni.selectorLabels" -}}
app.kubernetes.io/name: {{ include "multus-cni.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
name: {{ .Values.labels.name }}
{{- end }}

{{/*
サービスアカウント名の定義
*/}}
{{- define "multus-cni.serviceAccountName" -}}
{{- default "multus" .Values.serviceAccount.name }}
{{- end }}
