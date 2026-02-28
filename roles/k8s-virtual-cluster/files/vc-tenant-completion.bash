# -*- mode: shell-script; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。

# VirtualCluster テナント操作スクリプト用の bash 補完スクリプト
# vc-tenant-*.sh スクリプト群に対してテナント名、リソース名、オプションの補完を提供します。

# 共通ヘルパー関数: テナント名一覧を取得
_vc_tenant_get_tenant_list() {
    kubectl get virtualclusters.tenancy.x-k8s.io -n vc-manager -o jsonpath='{.items[*].metadata.name}' 2>/dev/null
}

# 共通ヘルパー関数: テナント名から namespace を取得
_vc_tenant_get_namespace() {
    local tenant_name="$1"
    kubectl get virtualclusters.tenancy.x-k8s.io -n vc-manager "$tenant_name" \
        -o jsonpath='{.status.clusterNamespace}' 2>/dev/null
}

# 共通ヘルパー関数: 指定リソース型の名前一覧を取得
_vc_tenant_get_resources() {
    local tenant_ns="$1"
    local resource_type="$2"
    kubectl -n "$tenant_ns" get "$resource_type" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null
}

# 共通ヘルパー関数: Pod 名一覧を取得
_vc_tenant_get_pods() {
    local tenant_ns="$1"
    kubectl -n "$tenant_ns" get pods -o jsonpath='{.items[*].metadata.name}' 2>/dev/null
}

# 共通ヘルパー関数: Pod 内のコンテナ名一覧を取得
_vc_tenant_get_containers() {
    local tenant_ns="$1"
    local pod_name="$2"
    kubectl -n "$tenant_ns" get pod "$pod_name" \
        -o jsonpath='{.spec.containers[*].name}' 2>/dev/null
}

# vc-tenant-apply.sh の補完関数
_vc_tenant_apply_completion() {
    local cur prev words cword
    _init_completion || return

    case $cword in
        1)
            # 第1引数: テナント名
            COMPREPLY=($(compgen -W "$(_vc_tenant_get_tenant_list)" -- "$cur"))
            ;;
        *)
            # 第2引数以降: オプション補完
            case $prev in
                -f|--filename)
                    # ファイルパス補完
                    _filedir '@(yaml|yml|json)'
                    return
                    ;;
                --vc-manager-ns)
                    # namespace 補完
                    COMPREPLY=($(compgen -W "vc-manager" -- "$cur"))
                    return
                    ;;
            esac
            # オプション候補
            local opts="-f --filename -h --help --dry-run --validate --vc-manager-ns"
            COMPREPLY=($(compgen -W "$opts" -- "$cur"))
            ;;
    esac
}

# vc-tenant-get.sh の補完関数
_vc_tenant_get_completion() {
    local cur prev words cword
    _init_completion || return

    case $cword in
        1)
            # 第1引数: テナント名
            COMPREPLY=($(compgen -W "$(_vc_tenant_get_tenant_list)" -- "$cur"))
            ;;
        2)
            # 第2引数: リソース型
            local resource_types="pods po services svc deployments deploy replicasets rs statefulsets sts daemonsets ds jobs cronjobs cj configmaps cm secrets persistentvolumeclaims pvc persistentvolumes pv storageclasses sc ingresses ing networkpolicies netpol nodes no namespaces ns"
            COMPREPLY=($(compgen -W "$resource_types" -- "$cur"))
            ;;
        3)
            # 第3引数: リソース名（動的取得）
            local tenant_name="${words[1]}"
            local resource_type="${words[2]}"
            local tenant_ns
            tenant_ns=$(_vc_tenant_get_namespace "$tenant_name")
            if [[ -n "$tenant_ns" && -n "$resource_type" ]]; then
                local resources
                resources=$(_vc_tenant_get_resources "$tenant_ns" "$resource_type")
                COMPREPLY=($(compgen -W "$resources" -- "$cur"))
            fi
            ;;
        *)
            # 第4引数以降: オプション
            case $prev in
                -o|--output)
                    COMPREPLY=($(compgen -W "json yaml wide name" -- "$cur"))
                    return
                    ;;
                --vc-manager-ns)
                    COMPREPLY=($(compgen -W "vc-manager" -- "$cur"))
                    return
                    ;;
            esac
            local opts="-o --output -w --watch -h --help --vc-manager-ns"
            COMPREPLY=($(compgen -W "$opts" -- "$cur"))
            ;;
    esac
}

# vc-tenant-delete.sh の補完関数
_vc_tenant_delete_completion() {
    local cur prev words cword
    _init_completion || return

    case $cword in
        1)
            # 第1引数: テナント名
            COMPREPLY=($(compgen -W "$(_vc_tenant_get_tenant_list)" -- "$cur"))
            ;;
        2)
            # 第2引数: リソース型
            local resource_types="pods po services svc deployments deploy replicasets rs statefulsets sts daemonsets ds jobs cronjobs cj configmaps cm secrets persistentvolumeclaims pvc ingresses ing"
            COMPREPLY=($(compgen -W "$resource_types" -- "$cur"))
            ;;
        3)
            # 第3引数: リソース名（動的取得）
            local tenant_name="${words[1]}"
            local resource_type="${words[2]}"
            local tenant_ns
            tenant_ns=$(_vc_tenant_get_namespace "$tenant_name")
            if [[ -n "$tenant_ns" && -n "$resource_type" ]]; then
                local resources
                resources=$(_vc_tenant_get_resources "$tenant_ns" "$resource_type")
                COMPREPLY=($(compgen -W "$resources" -- "$cur"))
            fi
            ;;
        *)
            # 第4引数以降: オプション
            case $prev in
                --grace-period)
                    COMPREPLY=($(compgen -W "0 30 60 120" -- "$cur"))
                    return
                    ;;
                --vc-manager-ns)
                    COMPREPLY=($(compgen -W "vc-manager" -- "$cur"))
                    return
                    ;;
            esac
            local opts="--all --grace-period --force -h --help --vc-manager-ns"
            COMPREPLY=($(compgen -W "$opts" -- "$cur"))
            ;;
    esac
}

# vc-tenant-exec.sh の補完関数
_vc_tenant_exec_completion() {
    local cur prev words cword
    _init_completion || return

    case $cword in
        1)
            # 第1引数: テナント名
            COMPREPLY=($(compgen -W "$(_vc_tenant_get_tenant_list)" -- "$cur"))
            ;;
        2)
            # 第2引数: Pod 名（動的取得）
            local tenant_name="${words[1]}"
            local tenant_ns
            tenant_ns=$(_vc_tenant_get_namespace "$tenant_name")
            if [[ -n "$tenant_ns" ]]; then
                local pods
                pods=$(_vc_tenant_get_pods "$tenant_ns")
                COMPREPLY=($(compgen -W "$pods" -- "$cur"))
            fi
            ;;
        *)
            # 第3引数以降: オプション
            case $prev in
                -c|--container)
                    # コンテナ名補完
                    local tenant_name="${words[1]}"
                    local pod_name="${words[2]}"
                    local tenant_ns
                    tenant_ns=$(_vc_tenant_get_namespace "$tenant_name")
                    if [[ -n "$tenant_ns" && -n "$pod_name" ]]; then
                        local containers
                        containers=$(_vc_tenant_get_containers "$tenant_ns" "$pod_name")
                        COMPREPLY=($(compgen -W "$containers" -- "$cur"))
                    fi
                    return
                    ;;
                --vc-manager-ns)
                    COMPREPLY=($(compgen -W "vc-manager" -- "$cur"))
                    return
                    ;;
            esac
            local opts="-i --stdin -t --tty -c --container -h --help --vc-manager-ns --"
            COMPREPLY=($(compgen -W "$opts" -- "$cur"))
            ;;
    esac
}

# vc-tenant-logs.sh の補完関数
_vc_tenant_logs_completion() {
    local cur prev words cword
    _init_completion || return

    case $cword in
        1)
            # 第1引数: テナント名
            COMPREPLY=($(compgen -W "$(_vc_tenant_get_tenant_list)" -- "$cur"))
            ;;
        2)
            # 第2引数: Pod 名（動的取得）
            local tenant_name="${words[1]}"
            local tenant_ns
            tenant_ns=$(_vc_tenant_get_namespace "$tenant_name")
            if [[ -n "$tenant_ns" ]]; then
                local pods
                pods=$(_vc_tenant_get_pods "$tenant_ns")
                COMPREPLY=($(compgen -W "$pods" -- "$cur"))
            fi
            ;;
        *)
            # 第3引数以降: オプション
            case $prev in
                -c|--container)
                    # コンテナ名補完
                    local tenant_name="${words[1]}"
                    local pod_name="${words[2]}"
                    local tenant_ns
                    tenant_ns=$(_vc_tenant_get_namespace "$tenant_name")
                    if [[ -n "$tenant_ns" && -n "$pod_name" ]]; then
                        local containers
                        containers=$(_vc_tenant_get_containers "$tenant_ns" "$pod_name")
                        COMPREPLY=($(compgen -W "$containers" -- "$cur"))
                    fi
                    return
                    ;;
                --tail)
                    COMPREPLY=($(compgen -W "10 50 100 200" -- "$cur"))
                    return
                    ;;
                --since)
                    COMPREPLY=($(compgen -W "1m 5m 10m 30m 1h 2h 24h" -- "$cur"))
                    return
                    ;;
                --vc-manager-ns)
                    COMPREPLY=($(compgen -W "vc-manager" -- "$cur"))
                    return
                    ;;
            esac
            local opts="-f --follow -c --container --tail --since --timestamps -h --help --vc-manager-ns"
            COMPREPLY=($(compgen -W "$opts" -- "$cur"))
            ;;
    esac
}

# 各スクリプトに補完関数を関連付け
complete -F _vc_tenant_apply_completion vc-tenant-apply.sh
complete -F _vc_tenant_get_completion vc-tenant-get.sh
complete -F _vc_tenant_delete_completion vc-tenant-delete.sh
complete -F _vc_tenant_exec_completion vc-tenant-exec.sh
complete -F _vc_tenant_logs_completion vc-tenant-logs.sh
