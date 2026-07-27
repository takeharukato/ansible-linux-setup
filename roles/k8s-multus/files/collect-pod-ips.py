#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2026 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
#
# OpenAI's ChatGPT partially generated this code.
# Author has modified some parts.
# OpenAIのChatGPTがこのコードの一部を生成しました。
# 著者が修正している部分があります。

"""Kubernetes Pod のアドレス情報を収集して一覧化するツール"""

# pylint: disable=missing-module-docstring,invalid-name

from __future__ import annotations

import argparse
import ipaddress
import json
import logging
import sys
from dataclasses import asdict, dataclass
from typing import Any, Callable, Iterable, cast

import yaml
from kubernetes import client, config # type: ignore
from kubernetes.client import ApiClient # type: ignore
from kubernetes.client.exceptions import ApiException # type: ignore


NETWORK_STATUS_ANNOTATION = "k8s.v1.cni.cncf.io/network-status"

# 参考) 古いMultus環境で使われていたことがある互換用の注釈名
# 原則として, 上記のnetwork-statusを使用する。
LEGACY_NETWORK_STATUS_ANNOTATION = "k8s.v1.cni.cncf.io/networks-status"


def get_pod_metadata(pod: client.V1Pod) -> client.V1ObjectMeta:
    """Pod の metadata を返却する。

    Args:
        pod (client.V1Pod): 解析対象のPod

    Returns:
        client.V1ObjectMeta: Pod の metadata
    """

    # Pod を Any 経由で扱い, Pylance の未知型警告を避ける。
    pod_any: Any = pod
    # metadata を具体型として取り出す。
    metadata: client.V1ObjectMeta | None = cast(client.V1ObjectMeta | None, pod_any.metadata)
    # metadata がない場合は空の metadata を返す。
    if metadata is None:
        return client.V1ObjectMeta()

    # 取得できた metadata をそのまま返す。
    return metadata


def get_pod_status(pod: client.V1Pod) -> client.V1PodStatus:
    """Podの状態を返却する。

    Args:
        pod (client.V1Pod): 解析対象のPod

    Returns:
        client.V1PodStatus: Pod の 状態
    """

    # Pod を Any 経由で扱い, Pylance の未知型警告を避ける。
    pod_any: Any = pod
    # status を具体型として取り出す。
    status: client.V1PodStatus | None = cast(client.V1PodStatus | None, pod_any.status)
    # status がない場合は空の状態を返す。
    if status is None: # Pod.status が None の場合は空の V1PodStatus を返す
        return client.V1PodStatus()

    # 取得できた status をそのまま返す。
    return status


@dataclass(frozen=True)
# pylint: disable=too-many-instance-attributes
class AddressRecord:
    """アドレス情報を表すデータクラス

    Attributes:
        address (str): 正規化済みのIPアドレス文字列
        family (str): IPv4 または IPv6 を表す文字列
        network (str | None): 由来となるネットワーク名
        interface (str | None): インターフェース名
        mac (str | None): MACアドレス
        default_network (bool): 既定ネットワーク由来なら真
        source (str): 情報源を示す識別子
    """

    address: str
    family: str
    network: str | None
    interface: str | None
    mac: str | None
    default_network: bool
    source: str


@dataclass
class PodAddressReport:
    """1つのPodについて収集したアドレス情報を表すデータクラス

    Attributes:
        namespace (str): Pod が属する Namespace
        name (str): Pod 名
        uid (str | None): Pod UID
        node_name (str | None): Pod が配置された Node 名
        phase (str | None): Pod の phase
        addresses (list[AddressRecord]): 収集したアドレス一覧
        interfaces_without_reported_ip (list[dict[str, Any]]): IP が報告されなかった
            インターフェース情報
        warnings (list[str]): 収集時に発生した警告
    """

    namespace: str
    name: str
    uid: str | None
    node_name: str | None
    phase: str | None
    addresses: list[AddressRecord]
    interfaces_without_reported_ip: list[dict[str, Any]]
    warnings: list[str]


def normalize_ip(value: str) -> tuple[str, str]:
    """IPアドレス文字列を正規化する。

    Multus の network-status では通常プレフィックス長なしのアドレスが
    記録されるが, 実装差異を考慮して CIDR 形式も受け付ける。

    Args:
        value (str): 正規化対象のIPアドレス文字列

    Returns:
        tuple[str, str]: 正規化後のアドレスとアドレスファミリ文字列

    Raises:
        ValueError: value が有効なIPアドレスとして解釈できない場合に送出される。

    Examples:
        >>> normalize_ip("192.0.2.1")
        ('192.0.2.1', 'IPv4')
        >>> normalize_ip("2001:db8::1/64")
        ('2001:db8::1', 'IPv6')
    """
    # 前後の空白を除去してから処理する。
    text: str = value.strip()
    # 正規化後のアドレスを入れる変数を用意する。
    address: str

    if "/" in text: # '/' が含まれる場合は CIDR 形式として解釈する
        # CIDR 形式は interface として解釈し, ホスト部だけを取り出す。
        interface: ipaddress.IPv4Interface | ipaddress.IPv6Interface = ipaddress.ip_interface(text)
        address = str(interface.ip)
    else:
        # 単純な IP 文字列はそのまま IP アドレスとして解釈する。
        address = str(ipaddress.ip_address(text))

    # IP の種類から IPv4/IPv6 の表記を決める。
    family: str = "IPv4" if ipaddress.ip_address(address).version == 4 else "IPv6"
    # 正規化結果を返す。
    return address, family


def parse_network_status(
    pod: client.V1Pod,
) -> tuple[list[AddressRecord], list[dict[str, Any]], list[str]]:
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """Multus の network-status 注釈を解析する。

    Args:
        pod (client.V1Pod): 解析対象のPod

    Returns:
        tuple[list[AddressRecord], list[dict[str, Any]], list[str]]: 解析結果
        1つ目はアドレス一覧, 2つ目はIP未報告インターフェース一覧, 3つ目は警告一覧

    Examples:
        >>> from kubernetes import client
        >>> pod = client.V1Pod(metadata=client.V1ObjectMeta(annotations={}))
        >>> parse_network_status(pod)
        ([], [], [])
    """

    # Pod.metadata を取得する。
    metadata: client.V1ObjectMeta = get_pod_metadata(pod)
    # metadata から annotations を取り出すために Any を経由する。
    metadata_any: Any = metadata
    # annotations が None でも扱えるように空辞書へ補正する。
    annotations_value: Any = getattr(metadata_any, "annotations", {}) or {}
    # アノテーションは文字列キーと文字列値の辞書として扱う。
    annotations: dict[str, str] = cast(dict[str, str], annotations_value)
    # 解析中に発生した警告を蓄積する。
    warnings: list[str] = []

    # どの注釈名を使ったかを記録する。
    annotation_name: str | None = None
    # 解析対象の JSON 文字列を保持する。
    raw_status: str | None = None

    # 既定の Multus 注釈を優先して使用する
    if NETWORK_STATUS_ANNOTATION in annotations:
        annotation_name = NETWORK_STATUS_ANNOTATION
        raw_status = annotations[NETWORK_STATUS_ANNOTATION]
    # 旧形式の互換注釈があれば代替として使う。
    elif LEGACY_NETWORK_STATUS_ANNOTATION in annotations:
        annotation_name = LEGACY_NETWORK_STATUS_ANNOTATION
        raw_status = annotations[LEGACY_NETWORK_STATUS_ANNOTATION]
        # 旧形式を使ったことを警告に残す。
        warnings.append(
            f"Used legacy annotation {LEGACY_NETWORK_STATUS_ANNOTATION}."
        )

    # 注釈がなければ空結果を返す。
    if not raw_status:
        return [], [], warnings

    # JSON形式のannotation を Python の値へ変換する。
    decoded_value: Any = json.loads(raw_status)
    # 配列でなければ Multus の期待形式ではないので警告する。
    if not isinstance(decoded_value, list):
        warnings.append(
            f"The value of {annotation_name} is not a JSON array."
        )
        return [], [], warnings

    # 配列要素を順番に処理する。
    decoded: list[Any] = cast(list[Any], decoded_value)

    # 抽出したアドレスを格納する。
    records: list[AddressRecord] = []
    # IP が報告されなかったインターフェースを格納する。
    interfaces_without_ip: list[dict[str, Any]] = []

    # 配列の各要素を検査する。
    index: int
    entry: Any
    for index, entry in enumerate(decoded):
        # JSON オブジェクトでなければ処理できないため,
        # 警告に残して読み飛ばす。
        if not isinstance(entry, dict):
            warnings.append(
                f"{annotation_name}[{index}] is not a JSON object."
            )
            continue

        # 各フィールドを安全な型へ取り出す。
        entry_dict: dict[str, Any] = cast(dict[str, Any], entry)
        network_value: Any = entry_dict.get("name")
        interface_name_value: Any = entry_dict.get("interface")
        mac_value: Any = entry_dict.get("mac")
        default_network_value: Any = entry_dict.get("default", False)
        ips_value: Any = entry_dict.get("ips")
        # ネットワーク名を文字列または None として扱う。
        network: str | None = cast(str | None, network_value)
        # インターフェース名を文字列または None として扱う。
        interface_name: str | None = cast(str | None, interface_name_value)
        # MAC アドレスを文字列または None として扱う。
        mac: str | None = cast(str | None, mac_value)
        # default フラグを真偽値へ変換する。
        default_network: bool = bool(default_network_value)

        # ips がなければ空配列として扱う。
        ips: Any = ips_value if ips_value is not None else []
        # ips は配列でなければならないため,
        # 配列でなければ警告に残して読み飛ばす。
        if not isinstance(ips, list):
            warnings.append(
                f"{annotation_name}[{index}].ips is not an array."
            )
            continue

        # 以降はIPアドレスのリストとして扱えるようにキャストする。
        ips_list: list[Any] = cast(list[Any], ips)

        # IP が空なら, インターフェース情報だけを記録する。
        if not ips_list:
            interfaces_without_ip.append(
                {
                    "network": network,
                    "interface": interface_name,
                    "mac": mac,
                    "default_network": default_network,
                }
            )
            continue

        # 1件ずつ IP を正規化して記録する。
        source: str = annotation_name or ""
        for raw_ip in ips_list:
            # 文字列でなければ IP として扱えないため,
            # 警告に残して読み飛ばす。
            raw_ip_text: str | None = cast(str | None, raw_ip)
            if raw_ip_text is None:
                warnings.append(
                    f"{annotation_name}[{index}].ips contains a non-string value."
                )
                continue

            # IP アドレスとして正規化する。
            try:
                address, family = normalize_ip(raw_ip_text)
            except ValueError:
                # 不正な IP は警告に残して読み飛ばす。
                warnings.append(
                    f"{annotation_name}[{index}] contains an invalid IP address: "
                    f"{raw_ip_text!r}"
                )
                continue

            # 正常に読めた IP を結果へ追加する。
            records.append(
                AddressRecord(
                    address=address,
                    family=family,
                    network=network,
                    interface=interface_name,
                    mac=mac,
                    default_network=default_network,
                    source=source,
                )
            )

    # 解析した結果をまとめて返す。
    return records, interfaces_without_ip, warnings


def extract_pod_status_addresses(
    pod: client.V1Pod,
) -> list[AddressRecord]:
    """Pod.status から既定ネットワークのアドレスを取得する。

    Args:
        pod (client.V1Pod): 解析対象のPod

    Returns:
        list[AddressRecord]: status から抽出したアドレス一覧

    Examples:
        >>> from kubernetes import client
        >>> pod = client.V1Pod(status=client.V1PodStatus(pod_ip="192.0.2.1"))
        >>> extract_pod_status_addresses(pod)[0].address
        '192.0.2.1'
    """

    # status.podIPs からアドレスを抽出した結果を格納する配列
    records: list[AddressRecord] = []

    pod_any: Any = pod
    # 属性としてstatusが存在することを確認する
    pod_status_value: Any = getattr(pod_any, "status", None)
    if pod_status_value is None: # status が存在しない場合は空の結果を返す
        return records

    # status.podIPs (pod_ips) からアドレスを抽出する。
    # status.podIPs は古い Kubernetes バージョンでは pod_i_ps として存在する場合があるため,
    # どちらかの属性を取得する。どちらもなければ空のリストを返す。
    pod_status: Any = pod_status_value
    pod_ips_value: Any = (
        getattr(pod_status, "pod_ips", None)
        or getattr(pod_status, "pod_i_ps", None)
        or []
    )
    pod_ips: list[Any] = cast(list[Any], pod_ips_value)
    pod_ip: Any
    for pod_ip in pod_ips: # pod_ips の各要素を順に処理する
        # pod_ip.ip が存在することを確認する。
        # 存在しない場合は読み飛ばす。
        raw_ip_value: Any = getattr(pod_ip, "ip", None)
        raw_ip: str | None = cast(str | None, raw_ip_value)
        if not raw_ip:
            continue

        # IPアドレスを正規化する。
        # 正規化に失敗した場合は読み飛ばす。
        try:
            address, family = normalize_ip(raw_ip)
        except ValueError:
            continue

        # 正規化済みのアドレスを結果へ追加する。
        records.append(
            AddressRecord(
                address=address,
                family=family,
                network=None,
                interface=None,
                mac=None,
                default_network=True,
                source="status.podIPs",
            )
        )

    # 古いAPI応答や一部環境への互換用の補完
    # pod_ips が空の場合に限り, 単一値の pod_ip を使用する。
    pod_ip_value: Any = getattr(pod_status, "pod_ip", None)
    pod_ip_text: str | None = cast(str | None, pod_ip_value)
    if not records and pod_ip_text:
        try:
            # IPアドレスを正規化する。
            address, family = normalize_ip(pod_ip_text)
        except ValueError:
            return records

        # 正規化済みのアドレスを結果へ追加する。
        records.append(
            AddressRecord(
                address=address,
                family=family,
                network=None,
                interface=None,
                mac=None,
                default_network=True,
                source="status.podIP",
            )
        )

    return records


def has_additional_network_request(annotations: dict[str, str]) -> bool:
    """追加ネットワークの要求注釈(multus配下のネットワークインターフェース)があることを判定する。

    Args:
        annotations (dict[str, str]): Pod の注釈

    Returns:
        bool: 追加ネットワーク要求があるなら真

    Examples:
        >>> has_additional_network_request({"k8s.v1.cni.cncf.io/networks": "net-a"})
        True
        >>> has_additional_network_request({})
        False
    """

    # 追加ネットワーク要求の注釈があるかを返す。
    return "k8s.v1.cni.cncf.io/networks" in annotations


def record_incomplete_report(
    warnings: list[str],
    has_requested_additional_networks: bool,
    multus_records: list[AddressRecord],
    missing_ip_interfaces: list[dict[str, Any]],
) -> None:
    """不足している情報に応じて警告を追加する。

    Args:
        warnings (list[str]): 追記先の警告一覧
        has_requested_additional_networks (bool): 追加ネットワーク要求の有無
        multus_records (list[AddressRecord]): Multus から得たアドレス一覧
        missing_ip_interfaces (list[dict[str, Any]]): IP 未報告のインターフェース一覧

    Returns:
        None: 返値なし

    Examples:
        >>> warnings = []
        >>> record_incomplete_report(warnings, True, [], [{"interface": "net1"}])
        >>> len(warnings)
        2
    """

    # 追加ネットワーク要求があるのに Multus 情報が空なら警告を残す。
    if has_requested_additional_networks and not multus_records:
        warnings.append(
            "An additional network was requested, but no IP address could be "
            "extracted from the network-status annotation."
        )

    # IP が報告されていないインターフェースがあれば警告を残す。
    if missing_ip_interfaces:
        warnings.append(
            "Multus reported interfaces, but some of them did not report an IP address."
        )


def merge_address_records(
    multus_records: Iterable[AddressRecord],
    status_records: Iterable[AddressRecord],
) -> list[AddressRecord]:
    """Multus の情報を優先しつつ不足分を補完する。

    同じIPが Multus 注釈に存在する場合は, インターフェース名やネットワーク名を
    保持するため, status.podIPs 側の重複レコードは追加しない。

    Args:
        multus_records (Iterable[AddressRecord]): Multus から得たアドレス一覧
        status_records (Iterable[AddressRecord]): status から得たアドレス一覧

    Returns:
        list[AddressRecord]: 結合済みのアドレス一覧

    Examples:
        >>> multus = [AddressRecord('192.0.2.1', 'IPv4', 'net-a', 'eth0', None, False, 'status')]
        >>> status = [AddressRecord('192.0.2.1', 'IPv4', None, None, None, True, 'status.podIP')]
        >>> len(merge_address_records(multus, status))
        1
    """
    # Multus の結果を基準にする。
    result: list[AddressRecord] = list(multus_records)
    # 追加済みのアドレスを高速に判定するための集合
    known_addresses: set[str] = {record.address for record in result}

    # status 側のアドレスを順番に確認する。
    for record in status_records:
        # Multus に同じ IP があるなら重複追加しない。
        if record.address in known_addresses:
            continue

        # 未登録の IP だけ結果へ追加する。
        result.append(record)
        known_addresses.add(record.address)

    # 表示順を整えて返す。
    return sorted(
        result,
        key=lambda item: (
            item.interface or "",
            ipaddress.ip_address(item.address).version,
            int(ipaddress.ip_address(item.address)),
        ),
    )


def build_pod_report(pod: client.V1Pod) -> PodAddressReport:
    # pylint: disable=too-many-locals
    """Pod 1件分の報告オブジェクトを組み立てる。

    Args:
        pod (client.V1Pod): 解析対象のPod

    Returns:
        PodAddressReport: 生成した報告オブジェクト

    Examples:
        >>> from kubernetes import client
        >>> pod = client.V1Pod(
        ...     metadata=client.V1ObjectMeta(annotations={}),
        ...     status=client.V1PodStatus(),
        ... )
        >>> report = build_pod_report(pod)
        >>> report.namespace is None
        True
    """

    # Multus 注釈からアドレス情報を取得する。
    multus_records, missing_ip_interfaces, warnings = parse_network_status(pod)
    # status 由来の既定ネットワークアドレスを取得する。
    status_records: list[AddressRecord] = extract_pod_status_addresses(pod)

    # 両方の情報を統合して最終的なアドレス一覧を作る。
    addresses: list[AddressRecord] = merge_address_records(multus_records, status_records)

    # Pod の metadata を Any 経由で取り出す。
    pod_any: Any = pod
    # metadata を取得する。
    metadata_value: Any = getattr(pod_any, "metadata", None)
    # metadata を具体型として扱う。
    metadata: client.V1ObjectMeta | None = cast(client.V1ObjectMeta | None, metadata_value)
    # metadata がない場合は空の metadata を使う。
    if metadata is None:
        metadata = client.V1ObjectMeta()

    # annotations を辞書として取り出す。
    metadata_any: Any = metadata
    annotations_value: Any = getattr(metadata_any, "annotations", {}) or {}
    annotations: dict[str, str] = cast(dict[str, str], annotations_value)
    # 追加ネットワーク要求の有無を判定する。
    has_requested_additional_networks: bool = has_additional_network_request(
        annotations,
    )
    # 不足情報に応じた警告を追加する。
    record_incomplete_report(
        warnings=warnings,
        has_requested_additional_networks=has_requested_additional_networks,
        multus_records=multus_records,
        missing_ip_interfaces=missing_ip_interfaces,
    )

    # spec と status を個別に取り出して出力へ使う。
    pod_spec_value: Any = getattr(pod_any, "spec", None)
    pod_status_value: Any = getattr(pod_any, "status", None)
    pod_spec: client.V1PodSpec | None = cast(client.V1PodSpec | None, pod_spec_value)
    pod_status: client.V1PodStatus | None = cast(client.V1PodStatus | None, pod_status_value)
    # Node 名と phase を取り出す。
    node_name_value: Any = getattr(pod_spec, "node_name", None) if pod_spec is not None else None
    phase_value: Any = getattr(pod_status, "phase", None) if pod_status is not None else None

    # 報告オブジェクトを組み立てて返す。
    return PodAddressReport(
        namespace=cast(str, getattr(metadata_any, "namespace", "") or ""),
        name=cast(str, getattr(metadata_any, "name", "") or ""),
        uid=cast(str | None, getattr(metadata_any, "uid", None)),
        node_name=cast(str | None, node_name_value),
        phase=cast(str | None, phase_value),
        addresses=addresses,
        interfaces_without_reported_ip=missing_ip_interfaces,
        warnings=warnings,
    )


def load_kubernetes_configuration(
    use_in_cluster: bool,
    kubeconfig: str | None,
) -> None:
    """Kubernetes クライアント設定を読み込む。

    Args:
        use_in_cluster (bool): クラスター内設定を使うなら真
        kubeconfig (str | None): kubeconfig ファイルのパス

    Returns:
        None: 返値はない。

    Examples:
        >>> load_kubernetes_configuration  # doctest: +ELLIPSIS
        <function load_kubernetes_configuration at ...>
    """

    # モジュール参照を Any 経由で保持する。
    config_any: Any = config
    # クラスター内設定を読む関数を取得する。
    load_incluster_config: Callable[..., None] = cast(
        Callable[..., None],
        getattr(config_any, "load_incluster_config"),
    )
    # kubeconfig を読む関数を取得する。
    load_kube_config: Callable[..., None] = cast(
        Callable[..., None],
        getattr(config_any, "load_kube_config"),
    )

    # 実行環境に応じて設定読み込み方法を切り替える。
    if use_in_cluster:
        load_incluster_config()
    else:
        # kubeconfig パス指定があればそのファイルを読み込む。
        if kubeconfig:
            load_kube_config(config_file=kubeconfig)
        else:
            load_kube_config()


def list_pods(
    api: client.CoreV1Api,
    namespace: str | None,
    label_selector: str | None,
    field_selector: str | None,
) -> list[client.V1Pod]:
    """条件に一致するPod一覧を取得する。

    Args:
        api (client.CoreV1Api): Kubernetes CoreV1 API クライアント
        namespace (str | None): 対象Namespace全Namespace対象なら None
        label_selector (str | None): ラベル選択条件
        field_selector (str | None): フィールド選択条件

    Returns:
        list[client.V1Pod]: 取得したPod一覧

    Examples:
        >>> def fake_list_pod_for_all_namespaces(**kwargs):
        ...     class Response:
        ...         items = []
        ...     return Response()
        >>> class FakeApi:
        ...     def list_pod_for_all_namespaces(self, **kwargs):
        ...         return fake_list_pod_for_all_namespaces(**kwargs)
        >>> list_pods(FakeApi(), None, None, None)
        []
    """

    common_args: dict[str, Any] = {
        "label_selector": label_selector,
        "field_selector": field_selector,
        "watch": False,
    }

    # API クライアントを Any 経由で扱う。
    response: client.V1PodList
    api_any: Any = api
    # namespace がある場合は名前空間内だけを取得する。
    if namespace:
        response_value: Any = getattr(api_any, "list_namespaced_pod")(
            namespace=namespace,
            **common_args,
        )
        response = cast(client.V1PodList, response_value)
    else:
        # namespace がない場合は全名前空間を対象にする。
        response_value = getattr(api_any, "list_pod_for_all_namespaces")(
            **common_args,
        )
        response = cast(client.V1PodList, response_value)

    # 取得した Pod 一覧を返す。
    items_value: Any = getattr(response, "items", []) or []
    return cast(list[client.V1Pod], items_value)


def report_to_dict(report: PodAddressReport) -> dict[str, Any]:
    """出力用の辞書へ変換する。

    Args:
        report (PodAddressReport): 変換対象の報告

    Returns:
        dict[str, Any]: YAML 出力用の辞書

    Examples:
        >>> report = PodAddressReport(
        ...     'default', 'pod-a', None, None, None, [], [], []
        ... )
        >>> sorted(report_to_dict(report).keys())
        ['addresses', 'interfaces_without_reported_ip', 'name', 'namespace',
         'node_name', 'phase', 'uid', 'warnings']
    """

    # 出力用の辞書を組み立てる。
    return {
        "namespace": report.namespace,
        "name": report.name,
        "uid": report.uid,
        "node_name": report.node_name,
        "phase": report.phase,
        "addresses": [asdict(address) for address in report.addresses],
        "interfaces_without_reported_ip": (
            report.interfaces_without_reported_ip
        ),
        "warnings": report.warnings,
    }


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数を解析する。

    Returns:
        argparse.Namespace: 解析済み引数

    Examples:
        >>> parse_arguments  # doctest: +ELLIPSIS
        <function parse_arguments at ...>
    """

    parser = argparse.ArgumentParser(
        description=(
            "List Pod IP addresses reported by Kubernetes and Multus, grouped by interface."
        )
    )
    # 対象 namespace を受け付ける。
    parser.add_argument(
        "--namespace",
        help="Target namespace. If omitted, all namespaces are included.",
    )
    # ラベル選択条件を受け付ける。
    parser.add_argument(
        "--label-selector",
        help="Kubernetes label selector.",
    )
    # フィールド選択条件を受け付ける。
    parser.add_argument(
        "--field-selector",
        help="Kubernetes field selector.",
    )
    # クラスター内認証の利用有無を受け付ける。
    parser.add_argument(
        "--in-cluster",
        action="store_true",
        help="Use the ServiceAccount credentials from inside the Pod.",
    )
    # kubeconfig ファイルのパス指定を受け付ける。
    parser.add_argument(
        "--kubeconfig",
        help=(
            "Path to kubeconfig file. "
            "Ignored when --in-cluster is set."
        ),
    )
    # 空の Pod も含めるよう指示する
    parser.add_argument(
        "--include-empty",
        action="store_true",
        help="Include Pods for which no IP address could be retrieved.",
    )
    # 警告がある場合に失敗扱いにするかを受け付ける。
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return exit code 1 when warnings or interfaces without reported IPs are present.",
    )
    # 詳細ログを有効にするかを受け付ける。
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose logging.",
    )
    # 解析結果を返す。
    return parser.parse_args()


def main() -> int:
    """コマンドラインツールの実行入口

    Returns:
        int: 終了コード

    Examples:
        >>> main  # doctest: +ELLIPSIS
        <function main at ...>
    """

    # コマンドライン引数を解析する。
    args: argparse.Namespace = parse_arguments()

    # ログ出力の基本設定を行う。
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    if args.in_cluster and args.kubeconfig:
        logging.warning(
            "--kubeconfig is ignored because --in-cluster is enabled."
        )

    try:
        # Kubernetes 設定を読み込む。
        load_kubernetes_configuration(args.in_cluster, args.kubeconfig)
        # API クライアントを生成する。
        api: client.CoreV1Api = client.CoreV1Api(ApiClient())

        # 条件に一致する Pod を取得する。
        pods: list[client.V1Pod] = list_pods(
            api=api,
            namespace=args.namespace,
            label_selector=args.label_selector,
            field_selector=args.field_selector,
        )
    except config.ConfigException as exc:
        # 設定読み込みに失敗したらエラーを出して終了する。
        logging.error("Failed to load Kubernetes connection configuration: %s", exc)
        return 2
    except ApiException as exc:
        # Kubernetes API 呼び出し失敗時の状態と理由を文字列化する。
        status_text: str = str(getattr(exc, "status", ""))
        reason_text: str = str(getattr(exc, "reason", ""))
        # API 呼び出し失敗をログに残して終了する。
        logging.error(
            "Failed to call the Kubernetes API: status=%s, reason=%s",
            status_text,
            reason_text,
        )
        return 2

    # 出力対象の報告一覧を格納する。
    reports: list[PodAddressReport] = []
    # strict モード用に不完全データの有無を追跡する。
    incomplete: bool = False

    # 各 Pod を順に報告へ変換する。
    for pod in pods:
        # Pod 1件分の報告を生成する。
        report: PodAddressReport = build_pod_report(pod)

        # 警告または未報告インターフェースがあれば不完全とみなす。
        if (
            report.warnings
            or report.interfaces_without_reported_ip
        ):
            incomplete = True

        # include-empty が有効か, アドレスがある Pod だけを残す。
        if args.include_empty or report.addresses:
            reports.append(report)

    # YAML に変換する出力辞書を組み立てる。
    output: dict[str, Any] = {
        "apiVersion": "pod-network-report.example/v1",
        "kind": "PodNetworkAddressList",
        "items": [report_to_dict(report) for report in reports],
    }

    # 結果を標準出力へ YAML 形式で出力する。
    yaml.safe_dump(
        output,
        stream=sys.stdout,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )

    # strict モードで不完全なら失敗終了する。
    if args.strict and incomplete:
        return 1

    # 正常終了コードを返す。
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
