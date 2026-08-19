#!/usr/bin/env python3
# -*- mode: python; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
#
# OpenAI's ChatGPT partially generated this code.
# Author has modified some parts.
# OpenAIのChatGPTがこのコードの一部を生成しました。
# 著者が修正している部分があります。

"""Ansible playbook から管理対象ノード上の管理ファイル一覧を抽出する。
書式:
    ansible_backup_audit.py [OPTIONS] PLAYBOOK_FILE
    OPTIONS:
        -i INVENTORY_FILE, --inventory INVENTORY_FILE
            playbook実行時のインベントリ指定。省略時はinventory/hostsを使用する。
            例: -i inventory/hosts
        -l LIMIT_PATTERN, --limit LIMIT_PATTERN
            playbook実行時のホスト絞り込み指定。省略時は全ホストを対象とする。
            例: -l mgmt-server
        -r ROLE_NAME, --role ROLE_NAME
            監査対象とするロール名。複数指定可能。省略時はすべてのロールを対象とする。
            例: -r common -r nfs-server
        -v, --verbose
            詳細メッセージを標準エラー出力へ出す指定。
        --version
            バージョン情報を表示して終了する。
        -h, --help
            ヘルプメッセージを表示して終了する。
        playbookから出力されるファイル, ディレクトリのパスをComma Separated Values (CSV) 形式で標準出力へ出力する。
        CSVの列は, ホスト名, ロール名, 操作種別(create_or_modify, modify, delete), 出力先パスの順である。
        create_or_modifyは新規作成又は変更, modifyは変更のみ, deleteは削除を意味する。

典型的な使用例:
    1.  inventory/hosts内の全てのホストに対して, 作成,変更, 削除されるファイル一覧を抽出し, 標準出力へCSV形式で出力する。
        警告, および, エラーメッセージを標準エラー出力へ出す。エラーはerror.logへリダイレクトし,
        出力結果はbackup-audit.csvへ保存する:

    $ ./ansible_backup_audit.py -i inventory/hosts playbooks/site.yml  -i inventory/hosts site.yml 2> error.log | tee backup-audit.csv
"""

from __future__ import annotations

import argparse
from ast import literal_eval, parse
import csv
import glob
import grp
from io import StringIO
import json
import os
import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from functools import wraps
from itertools import chain, islice
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import tokenize
from types import GeneratorType
from typing import Any, Iterable, Mapping, Sequence, cast

from ansible import __version__ as ansible_version_string
from ansible.errors import AnsibleError
from ansible.plugins.loader import filter_loader, test_loader
import yaml
from jinja2 import StrictUndefined, TemplateError
from jinja2.nativetypes import NativeEnvironment, NativeTemplate


#
# 呼び出し元が終了理由を機械的に判定できるように, 正常終了と各異常状態へ
# 個別の終了コードを割り当てる。外部コマンドの制御値は環境に応じて変更できる。
#
EXIT_OK: int = 0
EXIT_INPUT_ERROR: int = 1
EXIT_UNRESOLVED: int = 2
EXIT_PARSE_ERROR: int = 3
EXIT_UNSUPPORTED: int = 4
DEFAULT_INVENTORY: str = "inventory/hosts"
DEFAULT_TIMEOUT_SECONDS: float = 120.0
DEFAULT_RETRIES: int = 2
DEFAULT_RETRY_INTERVAL_SECONDS: float = 1.0
MAX_TEMPLATE_PASSES: int = 20
ALLOWED_ENV_LOOKUP_NAMES: frozenset[str] = frozenset({"HOME", "USER"})
OMIT_VALUE: str = "__ANSIBLE_BACKUP_AUDIT_OMIT__"

#
# タスク属性とモジュール名を区別するための予約名である。監査対象外モジュールでも
# register結果を後続タスクへ渡す必要があるため, 任意モジュール検出時に使用する。
#
TASK_ATTRIBUTE_KEYS: frozenset[str] = frozenset(
    {
        "action",
        "any_errors_fatal",
        "args",
        "always",
        "become",
        "become_flags",
        "become_method",
        "become_user",
        "block",
        "changed_when",
        "check_mode",
        "collections",
        "connection",
        "debugger",
        "delay",
        "delegate_facts",
        "delegate_to",
        "diff",
        "environment",
        "failed_when",
        "ignore_errors",
        "ignore_unreachable",
        "loop",
        "loop_control",
        "name",
        "no_log",
        "notify",
        "poll",
        "register",
        "rescue",
        "remote_user",
        "retries",
        "run_once",
        "tags",
        "throttle",
        "timeout",
        "until",
        "vars",
        "when",
        "with_items",
    }
)

#
# モジュールごとに対象パスを保持する引数名が異なるため, 監査対象と引数候補を
# ここへ集約する。複数候補は左から順に調べ, 最初に存在する値を採用する。
#
DIRECT_MODULE_PATH_KEYS: dict[str, tuple[str, ...]] = {
    "ansible.builtin.template": ("dest",),
    "ansible.builtin.copy": ("dest",),
    "ansible.builtin.lineinfile": ("path", "dest"),
    "ansible.builtin.blockinfile": ("path",),
    "ansible.builtin.replace": ("path",),
    "ansible.builtin.get_url": ("dest",),
    "ansible.builtin.patch": ("dest",),
    "ansible.posix.patch": ("dest",),
    "ansible.posix.authorized_key": ("path",),
    "ansible.posix.sysctl": ("sysctl_file",),
}
TARGET_MODULES: set[str] = set(DIRECT_MODULE_PATH_KEYS) | {
    "ansible.builtin.file",
    "ansible.builtin.tempfile",
    "ansible.builtin.apt_repository",
    "ansible.builtin.deb822_repository",
    "ansible.builtin.yum_repository",
}
CONTROL_MODULES: set[str] = {
    "ansible.builtin.assert",
    "ansible.builtin.include_tasks",
    "ansible.builtin.import_tasks",
    "ansible.builtin.include_role",
    "ansible.builtin.import_role",
    "ansible.builtin.include_vars",
    "ansible.builtin.set_fact",
}
#
# Playbookでは完全修飾名と短縮名の両方が使われるため, 同じ処理へ正規化する
# 対応表を監査対象及び制御対象のモジュールから生成する。
#
SHORT_MODULE_NAMES: dict[str, str] = {
    module_name.rsplit(".", 1)[-1]: module_name
    for module_name in TARGET_MODULES | CONTROL_MODULES
}


@dataclass(frozen=True)
class AuditRecord:
    """CSVへ出力する監査対象を表す。

    Attributes:
        host (str): ファイル操作の対象ホスト名。
        role (str): ファイル操作を定義するロール名。
        operation (str): create_or_modify, modify, delete のいずれか。
        path (str): 解決済みの対象パス。

    Examples:
        >>> AuditRecord("host1", "common", "modify", "/etc/fstab").path
        '/etc/fstab'
    """

    host: str
    role: str
    operation: str
    path: str


@dataclass(frozen=True)
class RuntimeSettings:
    """外部コマンド実行時の制御値を保持する。

    Attributes:
        timeout_seconds (float): 1回の外部コマンド実行に許可する秒数。
        retries (int): 初回失敗後の再試行回数。
        retry_interval_seconds (float): 再試行前に待機する秒数。

    Examples:
        >>> RuntimeSettings(10.0, 2, 1.0).retries
        2
    """

    timeout_seconds: float
    retries: int
    retry_interval_seconds: float


class AuditError(Exception):
    """監査処理を継続できない入力又は解析エラーを表す。

    Examples:
        >>> isinstance(AuditError("x"), Exception)
        True
    """


class UnresolvedValueError(AuditError):
    """Jinja2式又は実行時値を確定できない状態を表す。

    Examples:
        >>> isinstance(UnresolvedValueError("x"), AuditError)
        True
    """


class UnknownConditionError(AuditError):
    """実行時値に依存するため真偽を静的に確定できない状態を表す。"""


@dataclass(frozen=True)
class UnknownValue:
    """register由来の静的に確定できない値を伝播させる。"""

    reason: str

    def _derived(self, operation: str) -> UnknownValue:
        """操作履歴を加えた未知値を返す。"""
        return UnknownValue(f"{self.reason}.{operation}")

    def __getattr__(self, name: str) -> UnknownValue:
        """未知値の属性参照を別の未知値として保持する。"""
        return self._derived(name)

    def __getitem__(self, key: object) -> UnknownValue:
        """未知値の要素参照を別の未知値として保持する。"""
        return self._derived(f"[{key!r}]")

    def __call__(self, *args: Any, **kwargs: Any) -> UnknownValue:
        """未知のメソッド呼び出し結果を未知値として保持する。"""
        del args, kwargs
        return self._derived("call")

    def __bool__(self) -> bool:
        """未知値の誤った真偽確定を防ぐ。"""
        raise UnknownConditionError(f"Condition depends on runtime value: {self.reason}")

    def __len__(self) -> int:
        """未知値の長さを既知の整数へ固定しない。"""
        raise UnknownConditionError(f"Length depends on runtime value: {self.reason}")

    def __iter__(self) -> Iterator[UnknownValue]:
        """未知値を確定済みの反復列として扱わない。"""
        raise UnknownConditionError(
            f"Iteration depends on runtime value: {self.reason}"
        )

    def __contains__(self, item: object) -> bool:
        """未知値への包含判定を未確定として通知する。"""
        del item
        raise UnknownConditionError(
            f"Membership depends on runtime value: {self.reason}"
        )

    def __str__(self) -> str:
        """Jinja2式と誤認されない診断専用表現を返す。"""
        return f"<unknown:{self.reason}>"

    def _derived_binary(self, operation: str, other: object) -> UnknownValue:
        """二項演算の相手を評価せず未知値を伝播させる。"""
        del other
        return self._derived(operation)

    def __add__(self, other: object) -> UnknownValue:
        """未知値を含む加算結果を未知値として返す。"""
        return self._derived_binary("add", other)

    def __radd__(self, other: object) -> UnknownValue:
        """未知値を含む右加算結果を未知値として返す。"""
        return self._derived_binary("radd", other)

    def __sub__(self, other: object) -> UnknownValue:
        """未知値を含む減算結果を未知値として返す。"""
        return self._derived_binary("sub", other)

    def __rsub__(self, other: object) -> UnknownValue:
        """未知値を含む右減算結果を未知値として返す。"""
        return self._derived_binary("rsub", other)

    def __mul__(self, other: object) -> UnknownValue:
        """未知値を含む乗算結果を未知値として返す。"""
        return self._derived_binary("mul", other)

    def __rmul__(self, other: object) -> UnknownValue:
        """未知値を含む右乗算結果を未知値として返す。"""
        return self._derived_binary("rmul", other)

    def __truediv__(self, other: object) -> UnknownValue:
        """未知値を含む除算結果を未知値として返す。"""
        return self._derived_binary("truediv", other)

    def __rtruediv__(self, other: object) -> UnknownValue:
        """未知値を含む右除算結果を未知値として返す。"""
        return self._derived_binary("rtruediv", other)

    def __floordiv__(self, other: object) -> UnknownValue:
        """未知値を含む整数除算結果を未知値として返す。"""
        return self._derived_binary("floordiv", other)

    def __rfloordiv__(self, other: object) -> UnknownValue:
        """未知値を含む右整数除算結果を未知値として返す。"""
        return self._derived_binary("rfloordiv", other)

    def __mod__(self, other: object) -> UnknownValue:
        """未知値を含む剰余結果を未知値として返す。"""
        return self._derived_binary("mod", other)

    def __rmod__(self, other: object) -> UnknownValue:
        """未知値を含む右剰余結果を未知値として返す。"""
        return self._derived_binary("rmod", other)

    def __neg__(self) -> UnknownValue:
        """未知値の符号反転結果を未知値として返す。"""
        return self._derived("neg")

    def _raise_unknown_comparison(self, operation: str, other: object) -> bool:
        """未知値を既知の真偽値へ変換せず条件評価へ通知する。"""
        del other
        raise UnknownConditionError(
            f"Comparison depends on runtime value: {self.reason}.{operation}"
        )

    def __eq__(self, other: object) -> bool:
        """未知値の等価比較を未確定として通知する。"""
        return self._raise_unknown_comparison("eq", other)

    def __ne__(self, other: object) -> bool:
        """未知値の不等価比較を未確定として通知する。"""
        return self._raise_unknown_comparison("ne", other)

    def __lt__(self, other: object) -> bool:
        """未知値の大小比較を未確定として通知する。"""
        return self._raise_unknown_comparison("lt", other)

    def __le__(self, other: object) -> bool:
        """未知値の大小比較を未確定として通知する。"""
        return self._raise_unknown_comparison("le", other)

    def __gt__(self, other: object) -> bool:
        """未知値の大小比較を未確定として通知する。"""
        return self._raise_unknown_comparison("gt", other)

    def __ge__(self, other: object) -> bool:
        """未知値の大小比較を未確定として通知する。"""
        return self._raise_unknown_comparison("ge", other)


class UnknownMapping(dict[str, Any]):
    """存在しないキーも未知値として返すregister結果辞書である。"""

    def __init__(self, reason: str, initial: Mapping[str, Any] | None = None) -> None:
        """未知値の理由と既知フィールドを保持する。"""
        super().__init__(initial or {})
        self.reason: str = reason

    def __missing__(self, key: str) -> UnknownValue:
        """未登録フィールドを実行時依存の未知値として返す。"""
        return UnknownValue(f"{self.reason}.{key}")

    def get(self, key: str, default: Any = None) -> Any:
        """既定値で実行時フィールドの存在可能性を消さず未知値として返す。"""
        del default
        if key in self:
            return super().get(key)
        return self.__missing__(key)


class MarkedLoader(yaml.SafeLoader):
    """YAMLマッピングへ元ファイルの行番号を付加する読み込み器である。

    Examples:
        >>> isinstance(MarkedLoader, type)
        True
    """


def _construct_mapping(
    loader: MarkedLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[str, Any]:
    """YAMLマッピングを行番号付き辞書へ変換する。

    Args:
        loader (MarkedLoader): YAML読み込み器。
        node (yaml.nodes.MappingNode): 変換対象ノード。
        deep (bool): 子要素を再帰的に構築する指定。

    Returns:
        dict[str, Any]: ``__line__`` を含む辞書。

    Examples:
        >>> True
        True
    """
    #
    # PyYAMLが生成した辞書へ定義元の行番号を付け, 後段の未解決タスク報告で
    # 利用者が該当箇所を直接確認できるようにする。
    #
    mapping: dict[str, Any] = cast(
        dict[str, Any], yaml.SafeLoader.construct_mapping(loader, node, deep=deep)
    )
    mapping["__line__"] = int(node.start_mark.line) + 1
    return mapping


MarkedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


class Analyzer:
    """Playbookとロールをホスト別に評価し監査対象を抽出する。

    Args:
        repository_root (Path): Ansibleリポジトリのルートディレクトリ。
        inventory_path (Path): インベントリ指定。
        limit_pattern (str | None): Ansibleのホスト絞り込み指定。
        selected_roles (set[str]): 利用者が指定したロール名。
        runtime_settings (RuntimeSettings): 外部コマンド実行制御値。
        verbose (bool): 詳細メッセージを標準エラー出力へ出す指定。

    Examples:
        >>> True
        True
    """

    def __init__(
        self,
        repository_root: Path,
        inventory_path: Path,
        limit_pattern: str | None,
        selected_roles: set[str],
        runtime_settings: RuntimeSettings,
        verbose: bool,
    ) -> None:
        #
        # 入力設定と解析中に蓄積する状態を分けて保持する。監査レコードには集合を
        # 使用し, 同じホスト・ロール・操作・パスが複数回現れても重複出力を防ぐ。
        #
        self.repository_root: Path = repository_root
        self.inventory_path: Path = inventory_path
        self.limit_pattern: str | None = limit_pattern
        self.selected_roles: set[str] = selected_roles
        self.runtime_settings: RuntimeSettings = runtime_settings
        self.verbose: bool = verbose
        self.environment: NativeEnvironment = _create_environment()
        self.inventory_vars: dict[str, dict[str, Any]] = {}
        self.inventory_groups: dict[str, list[str]] = {}
        self.host_group_names: dict[str, list[str]] = {}
        self.host_facts: dict[str, dict[str, Any]] = {}
        self.host_passwd_facts: dict[str, dict[str, Any]] = {}
        self.shared_hostvars: dict[str, dict[str, Any]] = {}
        self.runtime_hostvars: dict[str, dict[str, Any]] = {}
        self.records: set[AuditRecord] = set()
        self.unresolved_messages: list[str] = []
        self._unresolved_message_set: set[str] = set()
        self._warning_messages: set[str] = set()
        self._role_stack: list[str] = []
        self._task_file_stack: list[Path] = []
        self.environment.globals["lookup"] = self._lookup

    def analyze(self, playbook_path: Path) -> list[AuditRecord]:
        """指定Playbookから監査対象一覧を生成する。

        Args:
            playbook_path (Path): 解析対象Playbook。

        Returns:
            list[AuditRecord]: ホスト, ロール, 操作, パスで並べた監査対象。

        Raises:
            AuditError: Playbook又はインベントリを解析できない場合。

        Examples:
            >>> True
            True
        """
        #
        # 先に全Playの対象ホストを確定し, 事実情報の取得を一括で実行する。
        # Play単位で同じホストへ繰り返し問い合わせる処理を避けるためである。
        #
        plays: list[dict[str, Any]] = self._load_playbook_tree(playbook_path)
        play_hosts: dict[int, list[str]] = {}
        all_hosts: set[str] = set()
        play_index: int
        play: dict[str, Any]
        for play_index, play in enumerate(plays):
            host_pattern_value: object = play.get("hosts", "")
            host_pattern: str = _host_pattern_to_string(host_pattern_value)
            if not host_pattern:
                continue
            hosts: list[str] = self._resolve_hosts(host_pattern)
            play_hosts[play_index] = hosts
            all_hosts.update(hosts)

        #
        # インベントリ変数と対象ホストの事実情報をそろえてからPlayを解析し,
        # Jinja2式を実際のホスト値に近い条件で評価できるようにする。
        #
        self.inventory_vars = self._load_inventory_vars()
        self.host_facts = self._gather_facts(sorted(all_hosts))
        self.host_passwd_facts = self._gather_passwd_facts(sorted(all_hosts))
        self._initialize_shared_hostvars(sorted(all_hosts))

        for play_index, play in enumerate(plays):
            hosts: list[str] = play_hosts.get(play_index, [])
            if not hosts:
                continue
            self._analyze_play(play, hosts)

        #
        # 集合で除去した重複を, 実行ごとに同じ順序となるように並べ替えて返す。
        #
        return sorted(
            self.records,
            key=lambda record: (
                record.host,
                record.role,
                record.path,
                record.operation,
            ),
        )

    def _load_playbook_tree(self, playbook_path: Path) -> list[dict[str, Any]]:
        """import_playbookを再帰的に展開する。

        Args:
            playbook_path (Path): 読み込み対象Playbook。

        Returns:
            list[dict[str, Any]]: 展開後のPlay定義。

        Raises:
            AuditError: YAML形式又はimport先が不正な場合。

        Examples:
            >>> True
            True
        """
        #
        # import_playbookを含むファイルも通常のPlaybookと同様に扱えるように,
        # 参照先を現在のファイルからの相対パスとして再帰的に展開する。
        #
        loaded: object = _load_yaml_file(playbook_path)
        if not isinstance(loaded, list):
            raise AuditError(f"Playbook must contain a YAML list: {playbook_path}")

        plays: list[dict[str, Any]] = []
        item: object
        for item in loaded:
            if not isinstance(item, dict):
                raise AuditError(f"Invalid play entry: {playbook_path}")
            play: dict[str, Any] = cast(dict[str, Any], item)
            import_value: object = play.get("import_playbook")
            if import_value is None:
                plays.append(play)
                continue
            import_path: Path = (playbook_path.parent / str(import_value)).resolve()
            plays.extend(self._load_playbook_tree(import_path))
        return plays

    def _resolve_hosts(self, host_pattern: str) -> list[str]:
        """Ansible自身のホストパターン解釈を利用して対象ホストを得る。

        Args:
            host_pattern (str): Playのhosts指定。

        Returns:
            list[str]: 対象ホスト名。

        Raises:
            AuditError: ansibleコマンドが失敗する場合。

        Examples:
            >>> True
            True
        """
        #
        # Ansible固有のホストパターンを独自実装せず, Ansible自身へ解釈させる。
        # これによりグループ, 除外, limit指定を実行時と同じ規則で処理する。
        #
        command: list[str] = [
            "ansible",
            "-i",
            str(self.inventory_path),
            host_pattern,
            "--list-hosts",
        ]
        if self.limit_pattern:
            command.extend(["--limit", self.limit_pattern])
        result: subprocess.CompletedProcess[str] = _run_command(
            command,
            self.runtime_settings,
        )
        #
        # --list-hostsの見出しと空行を除き, 実際のホスト名だけを収集する。
        #
        hosts: list[str] = []
        line: str
        for line in result.stdout.splitlines():
            stripped: str = line.strip()
            if not stripped or stripped.startswith("hosts ("):
                continue
            hosts.append(stripped)
        return hosts

    def _load_inventory_vars(self) -> dict[str, dict[str, Any]]:
        """ansible-inventoryからホスト別変数を取得する。

        Returns:
            dict[str, dict[str, Any]]: ホスト名をキーとする変数辞書。

        Raises:
            AuditError: ansible-inventoryの出力を解釈できない場合。

        Examples:
            >>> True
            True
        """
        #
        # Ansibleが統合したhostvarsをJSONで取得し, YAMLファイルを個別に読む場合の
        # 優先順位の再実装を避ける。
        #
        command: list[str] = [
            "ansible-inventory",
            "-i",
            str(self.inventory_path),
            "--list",
        ]
        result: subprocess.CompletedProcess[str] = _run_command(
            command,
            self.runtime_settings,
        )
        try:
            payload: object = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise AuditError("ansible-inventory returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise AuditError("ansible-inventory JSON root must be an object")
        root: dict[str, Any] = cast(dict[str, Any], payload)
        #
        # groups及びgroup_names組み込み変数を後段で利用できるように, グループの
        # 子グループを再帰展開してホスト一覧と所属グループ一覧を保存する。
        #
        self.inventory_groups, self.host_group_names = _build_inventory_groups(root)
        meta_value: object = root.get("_meta", {})
        if not isinstance(meta_value, dict):
            return {}
        meta: dict[str, Any] = cast(dict[str, Any], meta_value)
        hostvars_value: object = meta.get("hostvars", {})
        if not isinstance(hostvars_value, dict):
            return {}
        hostvars: dict[str, Any] = cast(dict[str, Any], hostvars_value)
        #
        # 想定どおり辞書で返されたホスト変数だけを採用し, 後段の型を統一する。
        #
        normalized: dict[str, dict[str, Any]] = {}
        host_name: str
        raw_vars: Any
        for host_name, raw_vars in hostvars.items():
            if isinstance(raw_vars, dict):
                normalized[host_name] = cast(dict[str, Any], raw_vars)
        return normalized

    def _gather_facts(self, hosts: Sequence[str]) -> dict[str, dict[str, Any]]:
        """対象ホストへsetupモジュールを実行して事実情報を取得する。

        Args:
            hosts (Sequence[str]): 事実情報を取得するホスト名。

        Returns:
            dict[str, dict[str, Any]]: ホスト別の事実情報。

        Raises:
            AuditError: 対象ホストへの事実情報取得が失敗する場合。

        Examples:
            >>> True
            True
        """
        #
        # 対象ホストがない場合は外部コマンドを起動せず, 空の結果を返す。
        #
        if not hosts:
            return {}
        #
        # --treeの出力先には自動削除される一時ディレクトリを使い, 実行後に
        # ホスト別の事実情報ファイルを作業場所へ残さない。
        #
        with tempfile.TemporaryDirectory(prefix="ansible-backup-audit-") as tree_dir:
            tree_path: Path = Path(tree_dir)
            limit_value: str = ",".join(hosts)
            command: list[str] = [
                "ansible",
                "-i",
                str(self.inventory_path),
                "all",
                "--limit",
                limit_value,
                "-m",
                "ansible.builtin.setup",
                "--tree",
                str(tree_path),
            ]
            _run_command(command, self.runtime_settings)
            #
            # コマンドが正常終了しても各ホストの結果を個別に確認し, 欠落や不正な
            # JSONを監査結果へ混在させず明示的な解析エラーとして扱う。
            #
            facts_by_host: dict[str, dict[str, Any]] = {}
            host: str
            for host in hosts:
                fact_file: Path = tree_path / host
                if not fact_file.is_file():
                    raise AuditError(f"Fact result is missing for host: {host}")
                try:
                    raw_payload: object = json.loads(fact_file.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    raise AuditError(f"Failed to read facts for host: {host}") from exc
                if not isinstance(raw_payload, dict):
                    raise AuditError(f"Invalid fact result for host: {host}")
                payload: dict[str, Any] = cast(dict[str, Any], raw_payload)
                facts_value: object = payload.get("ansible_facts", {})
                if not isinstance(facts_value, dict):
                    raise AuditError(f"ansible_facts is missing for host: {host}")
                facts_by_host[host] = cast(dict[str, Any], facts_value)
            return facts_by_host

    def _gather_passwd_facts(
        self,
        hosts: Sequence[str],
    ) -> dict[str, dict[str, Any]]:
        """対象ホストのpasswdデータベースを一括取得する。

        Args:
            hosts (Sequence[str]): passwd情報を取得するホスト名。

        Returns:
            dict[str, dict[str, Any]]: ホスト別のgetent_passwd辞書。

        Raises:
            AuditError: getent実行結果が欠落又は不正な場合。

        Examples:
            >>> True
            True
        """
        if not hosts:
            return {}
        #
        # Playbook中のgetentをホスト・ユーザごとに再実行すると問い合わせ回数が増える。
        # passwd全体をホスト群へ1回だけ要求し, 後続のregister結果へ必要部分を反映する。
        #
        with tempfile.TemporaryDirectory(
            prefix="ansible-backup-audit-passwd-"
        ) as tree_dir:
            tree_path: Path = Path(tree_dir)
            command: list[str] = [
                "ansible",
                "-i",
                str(self.inventory_path),
                "all",
                "--limit",
                ",".join(hosts),
                "-m",
                "ansible.builtin.getent",
                "-a",
                "database=passwd",
                "--tree",
                str(tree_path),
            ]
            _run_command(command, self.runtime_settings)
            passwd_by_host: dict[str, dict[str, Any]] = {}
            host: str
            for host in hosts:
                fact_file: Path = tree_path / host
                if not fact_file.is_file():
                    raise AuditError(f"Passwd result is missing for host: {host}")
                try:
                    raw_payload: object = json.loads(
                        fact_file.read_text(encoding="utf-8")
                    )
                except (OSError, json.JSONDecodeError) as exc:
                    raise AuditError(
                        f"Failed to read passwd facts for host: {host}"
                    ) from exc
                if not isinstance(raw_payload, dict):
                    raise AuditError(f"Invalid passwd result for host: {host}")
                payload: dict[str, Any] = cast(dict[str, Any], raw_payload)
                facts_value: object = payload.get("ansible_facts", {})
                if not isinstance(facts_value, dict):
                    raise AuditError(f"Passwd facts are missing for host: {host}")
                facts: dict[str, Any] = cast(dict[str, Any], facts_value)
                passwd_value: object = facts.get("getent_passwd", {})
                if not isinstance(passwd_value, dict):
                    raise AuditError(f"Invalid passwd facts for host: {host}")
                passwd_by_host[host] = cast(dict[str, Any], passwd_value)
            return passwd_by_host

    def _initialize_shared_hostvars(self, hosts: Sequence[str]) -> None:
        """インベントリ変数と事実情報から共有hostvarsを初期化する。

        Args:
            hosts (Sequence[str]): 解析対象の全ホスト名。

        Examples:
            >>> True
            True
        """
        self.shared_hostvars = {}
        self.runtime_hostvars = {}
        host: str
        for host in hosts:
            host_variables: dict[str, Any] = dict(self.inventory_vars.get(host, {}))
            facts: dict[str, Any] = dict(self.host_facts.get(host, {}))
            normalized_facts: dict[str, Any] = {}
            fact_name: str
            fact_value: Any
            for fact_name, fact_value in facts.items():
                if fact_name.startswith("ansible_"):
                    normalized_name: str = fact_name.removeprefix("ansible_")
                    normalized_facts[normalized_name] = fact_value
                    host_variables[fact_name] = fact_value
                else:
                    normalized_facts[fact_name] = fact_value
                    host_variables[f"ansible_{fact_name}"] = fact_value
            normalized_facts["getent_passwd"] = self.host_passwd_facts.get(host, {})
            host_variables["ansible_facts"] = normalized_facts
            host_variables["inventory_hostname"] = host
            host_variables["group_names"] = self.host_group_names.get(host, [])
            self.shared_hostvars[host] = host_variables
            self.runtime_hostvars[host] = {}

        #
        # localhostはインベントリに明示されない場合もdelegate_factsの保存先になる。
        # 制御ノードで安全に取得できる基本情報だけを初期値として用意する。
        #
        controller_user: str = os.environ.get("USER", "")
        controller_home: str = os.environ.get("HOME", "")
        self.shared_hostvars.setdefault(
            "localhost",
            {
                "ansible_facts": {},
                "ansible_user_id": controller_user,
                "inventory_hostname": "localhost",
                "controller_home": controller_home,
            },
        )
        self.runtime_hostvars.setdefault("localhost", {})

    def _lookup(self, plugin_name: Any, *terms: Any, **options: Any) -> Any:
        """現在のタスク位置を含めて安全なlookup実装を呼び出す。"""
        current_file: Path | None = (
            self._task_file_stack[-1] if self._task_file_stack else None
        )
        return _audit_lookup(
            plugin_name,
            *terms,
            repository_root=self.repository_root,
            current_file=current_file,
            **options,
        )

    def _analyze_play(self, play: dict[str, Any], hosts: Sequence[str]) -> None:
        """Playに定義されたロールを対象ホストごとに解析する。

        Args:
            play (dict[str, Any]): Play定義。
            hosts (Sequence[str]): Playの対象ホスト。

        Examples:
            >>> True
            True
        """
        roles_value: object = play.get("roles", [])
        #
        # roles節が配列でないPlayは安全に展開できないため, 解析対象外とする。
        #
        if not isinstance(roles_value, list):
            return
        #
        # 同じPlayでも変数と事実情報はホストごとに異なるため, ホスト別に初期変数を
        # 構築してから各ロールを解析する。
        #
        host: str
        for host in hosts:
            base_variables: dict[str, Any] = self._build_host_variables(
                host,
                play,
                hosts,
            )
            role_entry: object
            for role_entry in roles_value:
                self._analyze_role_entry(host, role_entry, base_variables)

    def _build_host_variables(
        self,
        host: str,
        play: Mapping[str, Any],
        play_hosts: Sequence[str],
    ) -> dict[str, Any]:
        """インベントリ, 事実情報, Play変数から初期変数集合を作る。

        Args:
            host (str): 対象ホスト名。
            play (Mapping[str, Any]): 対象Play。
            play_hosts (Sequence[str]): 対象Playで選択された全ホスト。

        Returns:
            dict[str, Any]: ロール解析前の変数集合。

        Examples:
            >>> True
            True
        """
        #
        # Ansibleの利用形態に合わせ, インベントリ変数を土台として事実情報と
        # Play変数を順番に重ねる。後から反映した値が同名の既存値を上書きする。
        #
        variables: dict[str, Any] = dict(self.shared_hostvars.get(host, {}))
        facts: dict[str, Any] = dict(self.host_facts.get(host, {}))
        normalized_facts: dict[str, Any] = {}
        fact_name: str
        fact_value: Any
        for fact_name, fact_value in facts.items():
            #
            # ansible_facts配下の短い名前と, 互換性のためのansible_接頭辞付き変数を
            # 両方用意し, どちらの記法を使うPlaybookも評価できるようにする。
            #
            if fact_name.startswith("ansible_"):
                normalized_facts[fact_name.removeprefix("ansible_")] = fact_value
                variables[fact_name] = fact_value
            else:
                normalized_facts[fact_name] = fact_value
                variables[f"ansible_{fact_name}"] = fact_value
        normalized_facts["getent_passwd"] = self.host_passwd_facts.get(host, {})
        variables["ansible_facts"] = normalized_facts
        variables["inventory_hostname"] = host
        variables["playbook_dir"] = str(self.repository_root)
        variables["groups"] = self.inventory_groups
        variables["group_names"] = self.host_group_names.get(host, [])
        variables["hostvars"] = self.shared_hostvars
        #
        # serialによるバッチ分割は実行しない静的監査であるため, Playで選択された
        # ホスト全体をplay_hosts, play_batch及びplay_hosts_allへ一貫して設定する。
        #
        selected_play_hosts: list[str] = list(play_hosts)
        variables["ansible_play_hosts_all"] = selected_play_hosts
        variables["ansible_play_hosts"] = selected_play_hosts
        variables["ansible_play_batch"] = selected_play_hosts
        #
        # 本ツールはAnsibleの確認実行ではなく読み取り専用の静的監査であるため,
        # ansible_check_modeはfalseとして評価する。
        #
        variables["ansible_check_mode"] = False
        variables["omit"] = OMIT_VALUE
        #
        # ansible_versionはsetupモジュールの事実情報ではなく制御側が提供する
        # 組み込み変数であるため, 実行中のAnsible版数から明示的に作成する。
        #
        variables["ansible_version"] = _build_ansible_version_mapping(
            str(ansible_version_string)
        )
        play_vars_value: object = play.get("vars", {})
        if isinstance(play_vars_value, dict):
            cleaned_play_vars: Any = _strip_internal_line_metadata(play_vars_value)
            if isinstance(cleaned_play_vars, dict):
                variables.update(cast(dict[str, Any], cleaned_play_vars))
        #
        # 変数同士が参照し合う場合に備え, 可能な値を反復して解決してから返す。
        #
        resolved_variables: dict[str, Any] = _resolve_variable_map(
            self.environment,
            variables,
        )
        shared_variables: dict[str, Any] = self.shared_hostvars.setdefault(host, {})
        variable_name: str
        variable_value: Any
        for variable_name, variable_value in resolved_variables.items():
            if variable_name != "hostvars":
                shared_variables[variable_name] = variable_value
        resolved_variables["hostvars"] = self.shared_hostvars
        return resolved_variables

    def _analyze_role_entry(
        self,
        host: str,
        role_entry: object,
        base_variables: Mapping[str, Any],
    ) -> None:
        """roles節の1要素を解析する。

        Args:
            host (str): 対象ホスト名。
            role_entry (object): roles節の1要素。
            base_variables (Mapping[str, Any]): Playまでに確定した変数集合。

        Examples:
            >>> True
            True
        """
        #
        # roles節は文字列形式と辞書形式の両方を許すため, ロール名, 条件,
        # その場で指定された変数を共通の内部表現へ変換する。
        #
        role_name: str
        role_variables: dict[str, Any] = dict(base_variables)
        role_when: object = None
        if isinstance(role_entry, str):
            role_name = role_entry
        elif isinstance(role_entry, dict):
            role_mapping: dict[str, Any] = cast(dict[str, Any], role_entry)
            role_name = str(role_mapping.get("role", ""))
            role_when = role_mapping.get("when")
            inline_vars_value: object = role_mapping.get("vars", {})
            if isinstance(inline_vars_value, dict):
                cleaned_inline_vars: Any = _strip_internal_line_metadata(
                    inline_vars_value
                )
                if isinstance(cleaned_inline_vars, dict):
                    role_variables.update(
                        cast(dict[str, Any], cleaned_inline_vars)
                    )
        else:
            return
        #
        # 先行ロールのset_fact及びregisterはホスト変数として後続ロールのwhenにも
        # 利用できる。ロール指定変数より高い実行時値として条件評価前に反映する。
        #
        role_variables.update(self.runtime_hostvars.get(host, {}))
        role_variables["hostvars"] = self.shared_hostvars
        if not role_name:
            return
        if self.selected_roles and role_name not in self.selected_roles:
            return
        #
        # ロール全体のwhen条件を先に評価し, 条件を満たさないロールのファイルを
        # 不要に読み込まない。
        #
        if role_when is not None and not _evaluate_when(
            self.environment, role_when, role_variables
        ):
            return
        self._analyze_role(host, role_name, role_variables, "main")

    def _analyze_role(
        self,
        host: str,
        role_name: str,
        incoming_variables: Mapping[str, Any],
        tasks_from: str,
    ) -> None:
        """ロール既定値とロール変数を反映してタスクを解析する。

        Args:
            host (str): 対象ホスト名。
            role_name (str): ロール名。
            incoming_variables (Mapping[str, Any]): 呼び出し元変数集合。
            tasks_from (str): 開始するタスクファイル名。

        Raises:
            AuditError: ロールの再帰呼び出し又はタスクファイル不正時。

        Examples:
            >>> True
            True
        """
        #
        # include_roleの循環による無限再帰を防ぐため, 現在解析中のロール名を
        # 呼び出し履歴と照合する。
        #
        if role_name in self._role_stack:
            chain: str = " -> ".join([*self._role_stack, role_name])
            raise AuditError(f"Recursive role inclusion detected: {chain}")
        role_path: Path = self.repository_root / "roles" / role_name
        if not role_path.is_dir():
            raise AuditError(f"Role directory is missing: {role_name}")
        variables: dict[str, Any] = {}
        defaults_path: Path = role_path / "defaults" / "main.yml"
        vars_path: Path = role_path / "vars" / "main.yml"
        #
        # Ansibleの変数優先順位に合わせ, defaults, 呼び出し元, varsの順で反映する。
        # role_pathもテンプレート評価で参照できるように追加する。
        #
        variables.update(_load_optional_mapping(defaults_path))
        variables.update(dict(incoming_variables))
        variables.update(_load_optional_mapping(vars_path))
        #
        # set_factで作成したホスト変数はロール既定値及びロール変数より優先される。
        # 専用領域だけを最後に重ね, インベントリ変数全体の優先順位を変えない。
        #
        variables.update(self.runtime_hostvars.get(host, {}))
        variables["role_path"] = str(role_path)
        variables = _resolve_variable_map(self.environment, variables)
        #
        # tasks_fromに拡張子が含まれる場合はその名前を使用し, 未指定の場合だけ
        # .ymlと.yamlを順に補う。xxx.yml.ymlという誤ったパス生成を防ぐ。
        #
        tasks_from_path: Path = Path(tasks_from)
        if tasks_from_path.suffix in {".yml", ".yaml"}:
            task_file: Path = role_path / "tasks" / tasks_from_path
        else:
            task_file = role_path / "tasks" / f"{tasks_from}.yml"
            if not task_file.is_file():
                alternative: Path = role_path / "tasks" / f"{tasks_from}.yaml"
                task_file = alternative if alternative.is_file() else task_file
        if not task_file.is_file():
            raise AuditError(f"Role task file is missing: {role_name}/{tasks_from}")
        #
        # 例外発生時にも解析履歴を必ず戻し, 後続ロールへ誤った再帰状態を残さない。
        #
        self._role_stack.append(role_name)
        try:
            self._process_task_file(host, role_name, task_file, variables)
        finally:
            self._role_stack.pop()

    def _process_task_file(
        self,
        host: str,
        role_name: str,
        task_file: Path,
        variables: dict[str, Any],
    ) -> None:
        """タスクファイルを記載順に評価する。

        Args:
            host (str): 対象ホスト名。
            role_name (str): 現在のロール名。
            task_file (Path): 読み込むタスクファイル。
            variables (dict[str, Any]): 現時点の変数集合。

        Raises:
            AuditError: タスクファイル形式が不正な場合。

        Examples:
            >>> True
            True
        """
        #
        # 空のタスクファイルは処理対象なしとして扱う。配列以外のYAMLはタスクを
        # 順番に評価できないため, 入力形式の誤りとして報告する。
        #
        loaded: object = _load_yaml_file(task_file)
        if loaded is None:
            return
        if not isinstance(loaded, list):
            raise AuditError(f"Task file must contain a YAML list: {task_file}")
        task_value: object
        #
        # Ansibleの実行順序に合わせて上から評価し, set_factやinclude_varsで
        # 更新した変数を後続タスクへ引き継ぐ。
        #
        for task_value in loaded:
            if not isinstance(task_value, dict):
                continue
            task: dict[str, Any] = cast(dict[str, Any], task_value)
            self._process_task(host, role_name, task_file, task, variables)

    def _process_task(
        self,
        host: str,
        role_name: str,
        task_file: Path,
        task: dict[str, Any],
        variables: dict[str, Any],
    ) -> None:
        """単一タスクを評価し, 静的に未解決のタスクを記録する。

        Args:
            host (str): 対象ホスト名。
            role_name (str): 現在のロール名。
            task_file (Path): タスクの定義元。
            task (dict[str, Any]): タスク定義。
            variables (dict[str, Any]): 現時点の変数集合。

        Examples:
            >>> True
            True
        """
        module_name: str = _find_module_name(task) or "<control>"
        line_number: int = int(task.get("__line__", 0))
        self._task_file_stack.append(task_file)
        try:
            #
            # when式及びループ式も含めてタスク全体を保護し, 実行時のregister値へ
            # 依存するタスクがあっても他の監査対象の解析を継続する。
            #
            self._process_task_body(
                host,
                role_name,
                task_file,
                task,
                variables,
            )
        except (AnsibleError, AuditError, TemplateError, ValueError, TypeError) as exc:
            register_name: str = str(task.get("register", "")).strip()
            if register_name and register_name not in variables:
                self._store_fallback_register_result(
                    host,
                    task,
                    module_name,
                    variables,
                    variables,
                )
            message: str = (
                f"Unresolved task: host={host} role={role_name} "
                f"source={task_file}:{line_number} module={module_name}: {exc}"
            )
            self._record_unresolved_message(message)
        finally:
            self._task_file_stack.pop()

    def _process_task_body(
        self,
        host: str,
        role_name: str,
        task_file: Path,
        task: dict[str, Any],
        variables: dict[str, Any],
    ) -> None:
        """単一タスクを条件, ループ, モジュールの順で評価する内部処理である。

        Args:
            host (str): 対象ホスト名。
            role_name (str): 現在のロール名。
            task_file (Path): タスクの定義元。
            task (dict[str, Any]): タスク定義。
            variables (dict[str, Any]): 現時点の変数集合。

        Examples:
            >>> True
            True
        """
        #
        # block, rescue, alwaysは自身にモジュールを持たない入れ物であるため,
        # 含まれるタスクを同じ規則で再帰的に解析する。
        #
        block_values: list[list[Any]] = []
        block_key: str
        for block_key in ("block", "rescue", "always"):
            block_value: object = task.get(block_key)
            if isinstance(block_value, list):
                block_values.append(block_value)
        if block_values:
            #
            # block全体のwhenは子タスクへ入る前に評価する。通常タスクのwhenは
            # ループ変数itemを設定した後で評価するため, ここでは処理しない。
            #
            if not _evaluate_when(self.environment, task.get("when"), variables):
                return
            child_tasks: list[Any]
            for child_tasks in block_values:
                child_value: Any
                for child_value in child_tasks:
                    if isinstance(child_value, dict):
                        self._process_task(
                            host,
                            role_name,
                            task_file,
                            cast(dict[str, Any], child_value),
                            variables,
                        )
        #
        # 本ツールが扱うモジュールだけを検出し, その他のタスクは監査対象外とする。
        #
        module_name: str | None = _find_module_name(task)
        if module_name is None:
            return
        module_args: dict[str, Any] = _module_args_from_task(task, module_name)
        #
        # ループなしも1回分の専用値として扱い, 通常タスクとループタスクを同じ
        # 処理経路へ流す。各反復では元の変数を汚さない一時辞書を使用する。
        #
        #
        # タスク固有varsをループ式からも参照できるように基礎変数へ加える。
        # item依存値は各反復でitem設定後に改めて描画する。
        #
        base_task_variables: dict[str, Any] = dict(variables)
        task_vars_value: object = task.get("vars", {})
        task_vars: dict[str, Any] = {}
        if isinstance(task_vars_value, dict):
            cleaned_task_vars: Any = _strip_internal_line_metadata(task_vars_value)
            if isinstance(cleaned_task_vars, dict):
                task_vars = cast(dict[str, Any], cleaned_task_vars)
            base_task_variables.update(task_vars)
            base_task_variables = _resolve_variable_map(
                self.environment,
                base_task_variables,
            )
        loop_values: list[Any] = _resolve_loop_values(
            self.environment,
            task,
            base_task_variables,
        )
        if not loop_values:
            self._store_empty_loop_register_result(
                host,
                task,
                variables,
            )
            return
        loop_value: Any
        for loop_value in loop_values:
            #
            # ループ付きset_factは直前反復で更新した永続変数を次の反復から参照する。
            # 各反復をループ開始前の写しから作ると辞書や配列の累積結果が失われるため,
            # 現時点の永続変数を基礎とし, タスク固有varsを改めて上書きする。
            #
            task_variables: dict[str, Any] = dict(variables)
            if task_vars:
                task_variables.update(task_vars)
            if loop_value is not _NO_LOOP:
                loop_var_name: str = _loop_variable_name(task)
                task_variables[loop_var_name] = loop_value
            if task_vars:
                task_variables = _resolve_variable_map(
                    self.environment,
                    task_variables,
                )
            #
            # when式がitemなどのループ変数を参照する場合に備え, 各反復値を追加した
            # 変数集合で条件を再評価する。
            #
            if not _evaluate_when(self.environment, task.get("when"), task_variables):
                self._store_skipped_register_result(
                    host,
                    task,
                    module_name,
                    variables,
                    task_variables,
                )
                continue
            self._process_module(
                host,
                role_name,
                task_file,
                task,
                module_name,
                module_args,
                variables,
                task_variables,
            )

    def _process_module(
        self,
        host: str,
        role_name: str,
        task_file: Path,
        task: Mapping[str, Any],
        module_name: str,
        module_args: Mapping[str, Any],
        persistent_variables: dict[str, Any],
        task_variables: dict[str, Any],
    ) -> None:
        """制御モジュール又はファイル操作モジュールを処理する。

        Args:
            host (str): 対象ホスト名。
            role_name (str): 現在のロール名。
            task_file (Path): タスクの定義元。
            task (Mapping[str, Any]): タスク定義。
            module_name (str): 正規化済みモジュール名。
            module_args (Mapping[str, Any]): モジュール引数。
            persistent_variables (dict[str, Any]): 後続タスクへ引き継ぐ変数集合。
            task_variables (dict[str, Any]): ループ値を含む一時変数集合。

        Examples:
            >>> True
            True
        """
        #
        # エラー報告へ定義元を含めるため, YAML読み込み時に付与した行番号を保持する。
        #
        line_number: int = int(task.get("__line__", 0))
        try:
            #
            # 変数や参照先を更新する制御モジュールは個別処理へ渡し, ファイル操作の
            # パス抽出処理とは分離する。
            #
            if module_name == "ansible.builtin.assert":
                self._process_assert(
                    task,
                    module_args,
                    task_variables,
                    persistent_variables,
                )
                self._sync_registered_variable(host, task, persistent_variables)
                return
            if module_name == "ansible.builtin.include_vars":
                self._process_include_vars(
                    module_args,
                    task_variables,
                    persistent_variables,
                )
                return
            if module_name == "ansible.builtin.set_fact":
                fact_target: dict[str, Any] = self._resolve_fact_target(
                    host,
                    task,
                    task_variables,
                    persistent_variables,
                )
                self._process_set_fact(
                    module_args,
                    task_variables,
                    fact_target,
                )
                self._sync_fact_values(
                    host,
                    task,
                    module_args,
                    fact_target,
                    task_variables,
                )
                return
            if module_name in {
                "ansible.builtin.include_tasks",
                "ansible.builtin.import_tasks",
            }:
                self._process_include_tasks(
                    host,
                    role_name,
                    task_file,
                    module_args,
                    task_variables,
                )
                #
                # include_tasks内のinclude_vars及びset_factによる更新を後続タスクへ
                # 引き継ぐ。ループ変数は反復専用であるため永続変数へ混入させない。
                #
                has_explicit_loop: bool = "loop" in task or "with_items" in task
                loop_variable_name: str | None = (
                    _loop_variable_name(task) if has_explicit_loop else None
                )
                variable_name: str
                variable_value: Any
                for variable_name, variable_value in task_variables.items():
                    if loop_variable_name is None or variable_name != loop_variable_name:
                        persistent_variables[variable_name] = variable_value
                return
            if module_name in {
                "ansible.builtin.include_role",
                "ansible.builtin.import_role",
            }:
                self._process_include_role(host, module_args, task_variables)
                return
            self._apply_runtime_facts(
                host,
                module_name,
                persistent_variables,
            )
            if module_name not in TARGET_MODULES:
                self._store_register_result(
                    host,
                    task,
                    module_name,
                    module_args,
                    persistent_variables,
                    task_variables,
                )
                return
            #
            # 別ホストへ委譲された操作は現在の対象ホスト上の管理ファイルではないため,
            # このホストの監査結果には含めない。
            #
            if self._is_delegated_elsewhere(host, task, task_variables):
                self._store_register_result(
                    host,
                    task,
                    module_name,
                    module_args,
                    persistent_variables,
                    task_variables,
                )
                return
            extracted: list[tuple[str, str]] = self._extract_paths(
                module_name,
                module_args,
                task_variables,
                host,
            )
            operation: str
            path_value: str
            #
            # 集合へ登録することで, includeや複数経路から同じ操作へ到達した場合も
            # CSVには1件だけ出力する。
            #
            for operation, path_value in extracted:
                self.records.add(AuditRecord(host, role_name, operation, path_value))
            self._store_register_result(
                host,
                task,
                module_name,
                module_args,
                persistent_variables,
                task_variables,
            )
        #
        # 実行済みタスクのregister値へ依存する式は静的監査では確定できない。
        # Ansible又はJinja2の評価例外を未解決タスクとして記録し, 他の解析を継続する。
        #
        except (AnsibleError, AuditError, TemplateError, ValueError, TypeError) as exc:
            #
            # 実行時にしか決まらない値があるタスクだけを未解決として記録し,
            # 他の静的に解析できるタスクの収集は継続する。
            #
            register_value: object = task.get("register")
            register_name: str = (
                str(register_value).strip() if register_value is not None else ""
            )
            if register_name and register_name not in persistent_variables:
                self._store_fallback_register_result(
                    host,
                    task,
                    module_name,
                    persistent_variables,
                    task_variables,
                )
            message: str = (
                f"Unresolved task: host={host} role={role_name} "
                f"source={task_file}:{line_number} module={module_name}: {exc}"
            )
            self._record_unresolved_message(message)

    def _apply_runtime_facts(
        self,
        host: str,
        module_name: str,
        persistent_variables: dict[str, Any],
    ) -> None:
        """事実収集モジュールが追加する既知構造を変数集合へ反映する。"""
        short_module_name: str = module_name.rsplit(".", 1)[-1]
        fact_name: str | None = None
        if short_module_name == "service_facts":
            fact_name = "services"
        elif short_module_name == "package_facts":
            fact_name = "packages"
        if fact_name is None:
            return
        facts_value: object = persistent_variables.get("ansible_facts", {})
        facts: dict[str, Any] = (
            cast(dict[str, Any], facts_value)
            if isinstance(facts_value, dict)
            else {}
        )
        facts[fact_name] = UnknownMapping(f"ansible_facts.{fact_name}")
        persistent_variables["ansible_facts"] = facts
        self.shared_hostvars.setdefault(host, {})["ansible_facts"] = facts
        self.runtime_hostvars.setdefault(host, {})["ansible_facts"] = facts

    def _resolve_fact_target(
        self,
        host: str,
        task: Mapping[str, Any],
        task_variables: Mapping[str, Any],
        persistent_variables: dict[str, Any],
    ) -> dict[str, Any]:
        """set_factの保存先をdelegate_facts規則に従って返す。"""
        delegate_facts_enabled: bool = bool(task.get("delegate_facts", False))
        delegate_value: object = task.get("delegate_to")
        if not delegate_facts_enabled or delegate_value is None:
            return persistent_variables
        rendered_delegate: Any = _render_value(
            self.environment,
            delegate_value,
            task_variables,
        )
        delegate_host: str = str(rendered_delegate)
        if not delegate_host:
            raise UnresolvedValueError("delegate_facts target is empty")
        return self.shared_hostvars.setdefault(delegate_host, {})

    def _sync_fact_values(
        self,
        host: str,
        task: Mapping[str, Any],
        module_args: Mapping[str, Any],
        fact_target: Mapping[str, Any],
        task_variables: Mapping[str, Any],
    ) -> None:
        """確定したset_fact値を実行時変数と共有hostvarsへ反映する。"""
        delegate_facts_enabled: bool = bool(task.get("delegate_facts", False))
        delegate_value: object = task.get("delegate_to")
        target_host: str = host
        if delegate_facts_enabled and delegate_value is not None:
            rendered_delegate: Any = _render_value(
                self.environment,
                delegate_value,
                task_variables,
            )
            target_host = str(rendered_delegate)
            if not target_host:
                raise UnresolvedValueError("delegate_facts target is empty")
        shared_variables: dict[str, Any] = self.shared_hostvars.setdefault(
            target_host,
            {},
        )
        runtime_variables: dict[str, Any] = self.runtime_hostvars.setdefault(
            target_host,
            {},
        )
        fact_name: str
        for fact_name in module_args:
            if fact_name != "__line__" and fact_name in fact_target:
                shared_variables[fact_name] = fact_target[fact_name]
                runtime_variables[fact_name] = fact_target[fact_name]

    def _sync_registered_variable(
        self,
        host: str,
        task: Mapping[str, Any],
        persistent_variables: Mapping[str, Any],
    ) -> None:
        """register結果を現在ホストの共有hostvarsへ反映する。"""
        register_value: object = task.get("register")
        if register_value is None:
            return
        register_name: str = str(register_value).strip()
        if register_name and register_name in persistent_variables:
            registered_result: Any = persistent_variables[register_name]
            self.shared_hostvars.setdefault(host, {})[register_name] = registered_result
            self.runtime_hostvars.setdefault(host, {})[register_name] = registered_result

    def _store_register_result(
        self,
        host: str,
        task: Mapping[str, Any],
        module_name: str,
        module_args: Mapping[str, Any],
        persistent_variables: dict[str, Any],
        task_variables: Mapping[str, Any],
    ) -> None:
        """モジュールのregister結果を既知部分と未知部分に分けて保存する。"""
        register_value: object = task.get("register")
        if register_value is None:
            return
        register_name: str = str(register_value).strip()
        if not register_name:
            raise UnresolvedValueError("register name is empty")
        item_result: UnknownMapping = self._build_register_result(
            host,
            module_name,
            module_args,
            task_variables,
        )
        if module_name.rsplit(".", 1)[-1] == "getent":
            facts_value: object = item_result.get("ansible_facts")
            if isinstance(facts_value, dict):
                current_facts_value: object = persistent_variables.get(
                    "ansible_facts",
                    {},
                )
                current_facts: dict[str, Any] = (
                    cast(dict[str, Any], current_facts_value)
                    if isinstance(current_facts_value, dict)
                    else {}
                )
                current_facts.update(cast(dict[str, Any], facts_value))
                persistent_variables["ansible_facts"] = current_facts
                self.shared_hostvars.setdefault(host, {})["ansible_facts"] = (
                    current_facts
                )
        has_loop: bool = "loop" in task or "with_items" in task
        if has_loop:
            loop_variable_name: str = _loop_variable_name(task)
            item_result["item"] = task_variables.get(
                loop_variable_name,
                UnknownValue(f"{register_name}.item"),
            )
            existing_value: object = persistent_variables.get(register_name)
            if isinstance(existing_value, dict):
                existing_mapping: dict[str, Any] = cast(
                    dict[str, Any],
                    existing_value,
                )
                results_value: object = existing_mapping.get("results")
                if isinstance(results_value, list):
                    results: list[Any] = results_value
                else:
                    results = []
                    existing_mapping["results"] = results
                results.append(item_result)
            else:
                aggregate_result: UnknownMapping = UnknownMapping(
                    register_name,
                    {
                        "changed": UnknownValue(f"{register_name}.changed"),
                        "failed": UnknownValue(f"{register_name}.failed"),
                        "results": [item_result],
                        "skipped": False,
                    },
                )
                persistent_variables[register_name] = aggregate_result
        else:
            persistent_variables[register_name] = item_result
        self._sync_registered_variable(host, task, persistent_variables)

    def _store_skipped_register_result(
        self,
        host: str,
        task: Mapping[str, Any],
        module_name: str,
        persistent_variables: dict[str, Any],
        task_variables: Mapping[str, Any],
    ) -> None:
        """when条件で実行されないタスクのregister結果を保存する。"""
        register_value: object = task.get("register")
        if register_value is None:
            return
        register_name: str = str(register_value).strip()
        if not register_name:
            raise UnresolvedValueError("register name is empty")
        skipped_result: dict[str, Any] = {
            "changed": False,
            "failed": False,
            "skipped": True,
        }
        has_loop: bool = "loop" in task or "with_items" in task
        if has_loop:
            loop_variable_name: str = _loop_variable_name(task)
            skipped_result["item"] = task_variables.get(
                loop_variable_name,
                UnknownValue(f"{register_name}.item"),
            )
            existing_value: object = persistent_variables.get(register_name)
            if isinstance(existing_value, dict):
                existing_mapping: dict[str, Any] = cast(
                    dict[str, Any],
                    existing_value,
                )
                results_value: object = existing_mapping.get("results")
                if isinstance(results_value, list):
                    results: list[Any] = results_value
                else:
                    results = []
                    existing_mapping["results"] = results
                results.append(skipped_result)
            else:
                persistent_variables[register_name] = UnknownMapping(
                    register_name,
                    {
                        "changed": False,
                        "failed": False,
                        "results": [skipped_result],
                        "skipped": True,
                    },
                )
        else:
            persistent_variables[register_name] = skipped_result
        self._sync_registered_variable(host, task, persistent_variables)

    def _store_empty_loop_register_result(
        self,
        host: str,
        task: Mapping[str, Any],
        persistent_variables: dict[str, Any],
    ) -> None:
        """反復対象が空の場合もAnsible相当のregister結果を保存する。

        Args:
            host (str): register結果を保存する対象ホスト名。
            task (Mapping[str, Any]): register指定を含むタスク定義。
            persistent_variables (dict[str, Any]): 後続タスクへ渡す変数集合。

        Examples:
            >>> True
            True
        """
        register_name: str = str(task.get("register", "")).strip()
        if not register_name:
            return
        persistent_variables[register_name] = {
            "changed": False,
            "failed": False,
            "results": [],
            "skipped": True,
            "skipped_reason": "No items in the list",
        }
        self._sync_registered_variable(host, task, persistent_variables)

    def _store_fallback_register_result(
        self,
        host: str,
        task: Mapping[str, Any],
        module_name: str,
        persistent_variables: dict[str, Any],
        task_variables: Mapping[str, Any],
    ) -> None:
        """モジュール解析失敗時にも後続参照用のregister辞書を保存する。"""
        register_name: str = str(task.get("register", "")).strip()
        if not register_name:
            return
        fallback_reason: str = f"register:{module_name}:unresolved"
        try:
            fallback_module_args: dict[str, Any] = _module_args_from_task(
                task,
                module_name,
            )
            fallback_result: UnknownMapping = self._build_register_result(
                host,
                module_name,
                fallback_module_args,
                task_variables,
            )
        except (AnsibleError, AuditError, TemplateError, ValueError, TypeError):
            fallback_result = UnknownMapping(
                fallback_reason,
                {
                    "changed": UnknownValue(f"{register_name}.changed"),
                    "failed": UnknownValue(f"{register_name}.failed"),
                    "skipped": False,
                },
            )
        if "loop" in task or "with_items" in task:
            loop_variable_name: str = _loop_variable_name(task)
            fallback_result["item"] = task_variables.get(
                loop_variable_name,
                UnknownValue(f"{register_name}.item"),
            )
            persistent_variables[register_name] = UnknownMapping(
                register_name,
                {
                    "changed": UnknownValue(f"{register_name}.changed"),
                    "failed": UnknownValue(f"{register_name}.failed"),
                    "results": [fallback_result],
                    "skipped": False,
                },
            )
        else:
            persistent_variables[register_name] = fallback_result
        self._sync_registered_variable(host, task, persistent_variables)

    def _build_register_result(
        self,
        host: str,
        module_name: str,
        module_args: Mapping[str, Any],
        task_variables: Mapping[str, Any],
    ) -> UnknownMapping:
        """モジュール種別ごとの既知フィールドを持つregister辞書を作る。"""
        short_module_name: str = module_name.rsplit(".", 1)[-1]
        reason: str = f"register:{short_module_name}"
        result: UnknownMapping = UnknownMapping(
            reason,
            {
                "changed": UnknownValue(f"{reason}.changed"),
                "failed": UnknownValue(f"{reason}.failed"),
                "rc": UnknownValue(f"{reason}.rc"),
                "skipped": False,
                "stderr": UnknownValue(f"{reason}.stderr"),
                "stdout": UnknownValue(f"{reason}.stdout"),
            },
        )
        if short_module_name == "stat":
            rendered_stat_path: Any = _render_value(
                self.environment,
                module_args.get("path", module_args.get("name", "")),
                task_variables,
            )
            result["stat"] = UnknownMapping(
                f"{reason}.stat",
                {
                    "exists": UnknownValue(f"{reason}.stat.exists"),
                    "isdir": UnknownValue(f"{reason}.stat.isdir"),
                    "islnk": UnknownValue(f"{reason}.stat.islnk"),
                    "isreg": UnknownValue(f"{reason}.stat.isreg"),
                    "path": rendered_stat_path,
                    "readable": UnknownValue(f"{reason}.stat.readable"),
                },
            )
        elif short_module_name == "find":
            result["files"] = self._build_find_file_results(
                module_args,
                task_variables,
                reason,
            )
            result["matched"] = UnknownValue(f"{reason}.matched")
        elif short_module_name in {"command", "shell"}:
            result["stdout_lines"] = [UnknownValue(f"{reason}.stdout_lines.item")]
        elif short_module_name == "uri":
            result["json"] = UnknownMapping(f"{reason}.json")
            result["status"] = UnknownValue(f"{reason}.status")
        elif short_module_name == "tempfile":
            result["path"] = self._build_tempfile_runtime_path(
                module_args,
                task_variables,
            )
        elif short_module_name == "slurp":
            result["content"] = UnknownValue(f"{reason}.content")
        elif short_module_name == "getent":
            database_value: Any = _render_value(
                self.environment,
                module_args.get("database", ""),
                task_variables,
            )
            if str(database_value) != "passwd":
                result["ansible_facts"] = UnknownMapping(
                    f"{reason}.ansible_facts"
                )
            else:
                passwd_facts: dict[str, Any] = dict(
                    self.host_passwd_facts.get(host, {})
                )
                requested_key_value: Any = _render_value(
                    self.environment,
                    module_args.get("key", ""),
                    task_variables,
                )
                requested_key: str = str(requested_key_value).strip()
                if requested_key and requested_key not in passwd_facts:
                    supplemented_entry: list[Any] | None = (
                        self._build_supplemented_passwd_entry(
                            requested_key,
                            task_variables,
                        )
                    )
                    if supplemented_entry is not None:
                        passwd_facts[requested_key] = supplemented_entry
                result["ansible_facts"] = {"getent_passwd": passwd_facts}
                result["changed"] = False
                result["failed"] = False
                result["rc"] = 0
        elif short_module_name == "user":
            result["home"] = self._resolve_registered_user_home(
                host,
                module_args,
                task_variables,
            )
        return result

    def _build_tempfile_runtime_path(
        self,
        module_args: Mapping[str, Any],
        task_variables: Mapping[str, Any],
    ) -> str:
        """tempfileの実行時パスを既知の構成要素からglobとして生成する。

        Args:
            module_args (Mapping[str, Any]): tempfileモジュールの引数。
            task_variables (Mapping[str, Any]): 引数の評価用変数集合。

        Returns:
            str: 実行時に生成される名前をアスタリスクで表した絶対パス。

        Raises:
            UnresolvedValueError: 基準ディレクトリを絶対パスへ解決できない場合。

        Examples:
            >>> True
            True
        """
        base_value: Any = _render_value(
            self.environment,
            module_args.get("path", "/tmp"),
            task_variables,
        )
        prefix_value: Any = _render_value(
            self.environment,
            module_args.get("prefix", "ansible."),
            task_variables,
        )
        suffix_value: Any = _render_value(
            self.environment,
            module_args.get("suffix", ""),
            task_variables,
        )
        if isinstance(
            base_value,
            (UnknownValue, UnknownMapping),
        ) or isinstance(
            prefix_value,
            (UnknownValue, UnknownMapping),
        ) or isinstance(
            suffix_value,
            (UnknownValue, UnknownMapping),
        ):
            raise UnresolvedValueError("tempfile path components are unresolved")
        base_path: str = str(base_value)
        if not Path(base_path).is_absolute():
            raise UnresolvedValueError(
                f"tempfile base path is not absolute: {base_path}"
            )
        pattern_path: str = str(
            Path(base_path) / f"{prefix_value}*{suffix_value}"
        )
        self._write_warning_once(
            "Warning: tempfile runtime path is represented as a glob: "
            f"{pattern_path}"
        )
        return pattern_path

    def _build_supplemented_passwd_entry(
        self,
        requested_key: str,
        task_variables: Mapping[str, Any],
    ) -> list[Any] | None:
        """既知のオペレータホームから要求ユーザーのpasswd配列を補完する。

        Args:
            requested_key (str): getentが要求したユーザー名。
            task_variables (Mapping[str, Any]): 解決済みホームを含む変数集合。

        Returns:
            list[Any] | None: ホームを添字4へ格納した配列又は補完不可を示すNone。

        Examples:
            >>> True
            True
        """
        operator_user_value: object = task_variables.get("k8s_operator_user")
        if operator_user_value is None or str(operator_user_value) != requested_key:
            return None
        home_variable_name: str
        for home_variable_name in (
            "k8s_operator_home_resolved",
            "k8s_operator_home",
        ):
            home_value: object = task_variables.get(home_variable_name)
            if home_value is None or isinstance(
                home_value,
                (UnknownValue, UnknownMapping),
            ):
                continue
            home_path: str = str(home_value)
            if Path(home_path).is_absolute():
                reason: str = f"getent_passwd[{requested_key}]"
                return [
                    "x",
                    UnknownValue(f"{reason}.uid"),
                    UnknownValue(f"{reason}.gid"),
                    "",
                    home_path,
                    UnknownValue(f"{reason}.shell"),
                ]
        return None

    def _build_find_file_results(
        self,
        module_args: Mapping[str, Any],
        task_variables: Mapping[str, Any],
        reason: str,
    ) -> list[UnknownMapping]:
        """findの検索条件から実行時一致ファイルを表すglob一覧を作る。

        Args:
            module_args (Mapping[str, Any]): findモジュールの引数。
            task_variables (Mapping[str, Any]): 検索条件の評価用変数集合。
            reason (str): 未知値へ付加する診断理由。

        Returns:
            list[UnknownMapping]: pathを既知glob又は未知値で保持する結果。

        Examples:
            >>> True
            True
        """
        rendered_paths: Any = _render_value(
            self.environment,
            module_args.get("paths", []),
            task_variables,
        )
        rendered_patterns: Any = _render_value(
            self.environment,
            module_args.get("patterns", "*"),
            task_variables,
        )
        rendered_use_regex: Any = _render_value(
            self.environment,
            module_args.get("use_regex", False),
            task_variables,
        )
        if (
            isinstance(rendered_paths, (UnknownValue, UnknownMapping))
            or isinstance(rendered_patterns, (UnknownValue, UnknownMapping))
            or isinstance(rendered_use_regex, (UnknownValue, UnknownMapping))
            or bool(rendered_use_regex)
        ):
            return [
                UnknownMapping(
                    f"{reason}.files.item",
                    {"path": UnknownValue(f"{reason}.files.item.path")},
                )
            ]

        path_values: list[Any] = (
            list(rendered_paths)
            if isinstance(rendered_paths, (list, tuple))
            else [rendered_paths]
        )
        if isinstance(rendered_patterns, (list, tuple)):
            pattern_values: list[Any] = list(rendered_patterns)
        elif isinstance(rendered_patterns, str):
            #
            # Ansible findはglob文字列のカンマを複数patternsの区切りとして扱う。
            # 配列要素内のカンマは利用者の明示値なので分割せずそのまま保持する。
            #
            pattern_values = [
                pattern_part.strip()
                for pattern_part in rendered_patterns.split(",")
                if pattern_part.strip()
            ]
        else:
            pattern_values = [rendered_patterns]
        recurse_value: Any = _render_value(
            self.environment,
            module_args.get("recurse", False),
            task_variables,
        )
        if isinstance(recurse_value, (UnknownValue, UnknownMapping)):
            return [
                UnknownMapping(
                    f"{reason}.files.item",
                    {"path": UnknownValue(f"{reason}.files.item.path")},
                )
            ]
        recurse_enabled: bool = bool(recurse_value)
        results: list[UnknownMapping] = []
        path_value: Any
        pattern_value: Any
        for path_value in path_values:
            base_path: str = str(path_value).rstrip("/")
            if not base_path or not Path(base_path).is_absolute():
                continue
            for pattern_value in pattern_values:
                pattern: str = _replace_unknown_diagnostics_with_glob(
                    str(pattern_value).strip()
                )
                if not pattern:
                    continue
                relative_pattern: str = f"**/{pattern}" if recurse_enabled else pattern
                symbolic_path: str = str(Path(base_path) / relative_pattern)
                self._write_warning_once(
                    "Warning: find runtime matches are represented as a glob: "
                    f"{symbolic_path}"
                )
                results.append(
                    UnknownMapping(
                        f"{reason}.files.item",
                        {"path": symbolic_path},
                    )
                )
        if results:
            return results
        return [
            UnknownMapping(
                f"{reason}.files.item",
                {"path": UnknownValue(f"{reason}.files.item.path")},
            )
        ]

    def _resolve_registered_user_home(
        self,
        host: str,
        module_args: Mapping[str, Any],
        task_variables: Mapping[str, Any],
    ) -> Any:
        """userモジュール結果のhomeを明示値又はpasswd情報から解決する。"""
        name_value: Any = _render_value(
            self.environment,
            module_args.get("name", ""),
            task_variables,
        )
        user_name: str = str(name_value)
        home_value: object = module_args.get("home")
        if home_value is not None:
            rendered_home: Any = _render_value(
                self.environment,
                home_value,
                task_variables,
            )
            home_path: str = str(rendered_home)
            if Path(home_path).is_absolute():
                return home_path
        passwd_entry: object = self.host_passwd_facts.get(host, {}).get(user_name)
        if isinstance(passwd_entry, list) and len(passwd_entry) > 4:
            return passwd_entry[4]
        return UnknownValue(f"register:user.home[{user_name}]")

    def _process_assert(
        self,
        task: Mapping[str, Any],
        module_args: Mapping[str, Any],
        task_variables: Mapping[str, Any],
        persistent_variables: dict[str, Any],
    ) -> None:
        """静的に判定できるassert結果をregister変数へ反映する。

        Args:
            task (Mapping[str, Any]): register指定を含むタスク定義。
            module_args (Mapping[str, Any]): assertモジュール引数。
            task_variables (Mapping[str, Any]): assert条件の評価用変数集合。
            persistent_variables (dict[str, Any]): 後続タスクへ渡す変数集合。

        Raises:
            UnresolvedValueError: that指定がない又は形式が不正な場合。

        Examples:
            >>> True
            True
        """
        condition_value: object = module_args.get("that")
        if condition_value is None:
            raise UnresolvedValueError("assert that is missing")
        if not isinstance(condition_value, (str, list)):
            raise UnresolvedValueError("assert that must be a string or list")

        #
        # assertの全条件をAnsibleのwhenと同じ規則で評価する。ignore_errorsの有無に
        # かかわらずregister値には成否が格納されるため, failedを常に明示する。
        #
        assertion_succeeded: bool = _evaluate_when(
            self.environment,
            condition_value,
            task_variables,
        )
        register_value: object = task.get("register")
        if register_value is None:
            return
        register_name: str = str(register_value).strip()
        if not register_name:
            raise UnresolvedValueError("assert register name is empty")
        persistent_variables[register_name] = {
            "changed": False,
            "failed": not assertion_succeeded,
        }

    def _record_unresolved_message(self, message: str) -> None:
        """未解決メッセージを重複させず記録する。

        Args:
            message (str): ホスト, ロール, 定義元及び原因を含む診断メッセージ。

        Examples:
            >>> True
            True
        """
        if message in self._unresolved_message_set:
            return
        self._unresolved_message_set.add(message)
        self.unresolved_messages.append(message)
        if self.verbose:
            print(message, file=sys.stderr)

    def _write_warning_once(self, message: str) -> None:
        """同じ警告を1回だけ標準エラー出力へ書き出す。

        Args:
            message (str): 利用者へ通知する警告メッセージ。

        Examples:
            >>> True
            True
        """
        if message in self._warning_messages:
            return
        self._warning_messages.add(message)
        print(message, file=sys.stderr)

    def _process_include_vars(
        self,
        module_args: Mapping[str, Any],
        task_variables: Mapping[str, Any],
        persistent_variables: dict[str, Any],
    ) -> None:
        """include_varsで指定された変数ファイルを後続タスクへ反映する。

        Args:
            module_args (Mapping[str, Any]): include_vars引数。
            task_variables (Mapping[str, Any]): 現在の変数集合。
            persistent_variables (dict[str, Any]): 更新対象変数集合。

        Raises:
            AuditError: 読み込み対象を確定できない場合。

        Examples:
            >>> True
            True
        """
        #
        # file引数と自由形式引数の両記法に対応し, 指定がない場合は変数集合を
        # 変更せず終了する。
        #
        source_value: object = module_args.get("file", module_args.get("_raw_params"))
        if source_value is None:
            return
        rendered: Any = _render_value(self.environment, source_value, task_variables)
        source_path: Path = Path(str(rendered))
        if not source_path.is_absolute():
            #
            # 相対パスは解析対象リポジトリのルートを基準にして実ファイルへ変換する。
            #
            source_path = self.repository_root / source_path
        loaded_mapping: dict[str, Any] = _load_optional_mapping(source_path)
        namespace_value: object = module_args.get("name")
        #
        # name指定がある場合は読み込んだ辞書を名前空間の下へ置き, 指定がない場合は
        # Ansibleと同様に変数を現在の階層へ展開する。
        #
        if namespace_value is None:
            persistent_variables.update(loaded_mapping)
        else:
            namespace: str = str(
                _render_value(self.environment, namespace_value, task_variables)
            )
            persistent_variables[namespace] = loaded_mapping
        #
        # 新たに読み込んだ値から参照可能になった変数式を解決し, 同じ辞書を参照する
        # 後続タスクへ結果を反映する。
        #
        resolved: dict[str, Any] = _resolve_variable_map(
            self.environment,
            persistent_variables,
        )
        persistent_variables.clear()
        persistent_variables.update(resolved)

    def _process_set_fact(
        self,
        module_args: Mapping[str, Any],
        task_variables: Mapping[str, Any],
        persistent_variables: dict[str, Any],
    ) -> None:
        """静的に評価可能なset_factを後続タスクへ反映する。

        Args:
            module_args (Mapping[str, Any]): set_fact引数。
            task_variables (Mapping[str, Any]): 現在の変数集合。
            persistent_variables (dict[str, Any]): 更新対象変数集合。

        Raises:
            UndefinedError: 実行時値へ依存して評価できない場合。

        Examples:
            >>> True
            True
        """
        #
        # set_factの各値を現在のループ値を含む変数集合で評価し, 後続タスクが参照する
        # 永続側の変数辞書へ保存する。行番号用の内部項目は変数として扱わない。
        #
        fact_name: str
        fact_value: Any
        for fact_name, fact_value in module_args.items():
            if fact_name == "__line__":
                continue
            try:
                persistent_variables[fact_name] = _render_value(
                    self.environment,
                    fact_value,
                    task_variables,
                )
            except UnknownConditionError as exc:
                #
                # 1つのfactが実行時値へ依存しても, 同じset_fact内の独立した値と
                # 後続タスクの解析を失わないよう専用未知値として保存する。
                #
                persistent_variables[fact_name] = UnknownValue(
                    f"set_fact:{fact_name}:{exc}"
                )
        #
        # 複数のfact間に参照関係がある場合に備え, 追加後の全変数を反復解決する。
        #
        resolved: dict[str, Any] = _resolve_variable_map(
            self.environment,
            persistent_variables,
        )
        persistent_variables.clear()
        persistent_variables.update(resolved)

    def _process_include_tasks(
        self,
        host: str,
        role_name: str,
        current_file: Path,
        module_args: Mapping[str, Any],
        task_variables: dict[str, Any],
    ) -> None:
        """include_tasks又はimport_tasksの参照先を同一ロールとして解析する。

        Args:
            host (str): 対象ホスト名。
            role_name (str): 現在のロール名。
            current_file (Path): include元ファイル。
            module_args (Mapping[str, Any]): include_tasks引数。
            task_variables (dict[str, Any]): 現在の変数集合。

        Raises:
            AuditError: include先ファイルを確定できない場合。

        Examples:
            >>> True
            True
        """
        #
        # file引数と自由形式引数を共通化し, 参照先を現在のタスクファイルからの
        # 相対パスとして解決する。
        #
        file_value: object = module_args.get("file", module_args.get("_raw_params"))
        if file_value is None:
            raise AuditError("include_tasks file is missing")
        rendered: Any = _render_value(self.environment, file_value, task_variables)
        include_path: Path = Path(str(rendered))
        if not include_path.is_absolute():
            include_path = current_file.parent / include_path
        if not include_path.is_file():
            raise AuditError(f"Included task file is missing: {include_path}")
        #
        # include先も同じロール及び現在の変数集合で解析し, 結果の所属を維持する。
        #
        self._process_task_file(host, role_name, include_path, task_variables)

    def _process_include_role(
        self,
        host: str,
        module_args: Mapping[str, Any],
        task_variables: Mapping[str, Any],
    ) -> None:
        """include_role又はimport_roleの参照先ロールを解析する。

        Args:
            host (str): 対象ホスト名。
            module_args (Mapping[str, Any]): include_role引数。
            task_variables (Mapping[str, Any]): 現在の変数集合。

        Raises:
            AuditError: ロール名を確定できない場合。

        Examples:
            >>> True
            True
        """
        #
        # ロール名と開始タスク名はJinja2式を含められるため, 現在の変数集合で
        # 評価してから参照先ロールを解析する。
        #
        role_value: object = module_args.get("name")
        if role_value is None:
            raise AuditError("include_role name is missing")
        role_name: str = str(
            _render_value(self.environment, role_value, task_variables)
        )
        if self.selected_roles and role_name not in self.selected_roles:
            return
        tasks_from_value: object = module_args.get("tasks_from", "main")
        tasks_from: str = str(
            _render_value(self.environment, tasks_from_value, task_variables)
        )
        self._analyze_role(host, role_name, task_variables, tasks_from)

    def _is_delegated_elsewhere(
        self,
        host: str,
        task: Mapping[str, Any],
        task_variables: Mapping[str, Any],
    ) -> bool:
        """対象ホスト以外へのdelegate_toであることを判定する。

        Args:
            host (str): Play上の対象ホスト名。
            task (Mapping[str, Any]): タスク定義。
            task_variables (Mapping[str, Any]): 現在の変数集合。

        Returns:
            bool: 対象ホスト以外へ委譲する場合はTrue。

        Examples:
            >>> True
            True
        """
        #
        # delegate_to未指定のタスクはPlayの対象ホスト自身で実行されるため,
        # 委譲による除外対象ではない。
        #
        delegate_value: object = task.get("delegate_to")
        if delegate_value is None:
            return False
        rendered: str = str(
            _render_value(self.environment, delegate_value, task_variables)
        )
        #
        # 実際のホスト名又は未展開のinventory_hostname表記は対象ホスト自身とみなし,
        # それ以外の委譲先だけを監査対象外と判定する。
        #
        return rendered not in {host, "{{ inventory_hostname }}"}

    def _extract_paths(
        self,
        module_name: str,
        module_args: Mapping[str, Any],
        variables: Mapping[str, Any],
        host: str | None = None,
    ) -> list[tuple[str, str]]:
        """対象モジュール引数から操作種別と実パスを抽出する。

        Args:
            module_name (str): FQCN形式のモジュール名。
            module_args (Mapping[str, Any]): モジュール引数。
            variables (Mapping[str, Any]): 現在の変数集合。
            host (str | None): passwd情報を参照する対象ホスト名。

        Returns:
            list[tuple[str, str]]: ``(操作種別, パス)`` の一覧。

        Raises:
            UnresolvedValueError: パスを確定できない場合。

        Examples:
            >>> True
            True
        """
        #
        # authorized_keyのpath省略時は対象ユーザの実ホームからAnsible既定配置先を
        # 算出する。/home固定の推測は行わず, 一括取得済みpasswd情報だけを使用する。
        #
        if module_name == "ansible.posix.authorized_key":
            if "path" in module_args:
                authorized_key_path: str = self._render_required_path(
                    module_args,
                    ("path",),
                    variables,
                )
            else:
                user_value: object = module_args.get("user")
                if user_value is None:
                    raise UnresolvedValueError(
                        "authorized_key user and path are missing"
                    )
                rendered_user: Any = _render_value(
                    self.environment,
                    user_value,
                    variables,
                )
                user_name: str = str(rendered_user)
                passwd_entry: object = (
                    self.host_passwd_facts.get(host, {}).get(user_name)
                    if host is not None
                    else None
                )
                if not isinstance(passwd_entry, list) or len(passwd_entry) <= 4:
                    raise UnresolvedValueError(
                        f"authorized_key home is unresolved for user: {user_name}"
                    )
                home_path: Path = Path(str(passwd_entry[4]))
                if not home_path.is_absolute():
                    raise UnresolvedValueError(
                        f"authorized_key home is not absolute: {home_path}"
                    )
                authorized_key_path = str(home_path / ".ssh" / "authorized_keys")
            authorized_key_state: str = str(
                _render_value(
                    self.environment,
                    module_args.get("state", "present"),
                    variables,
                )
            )
            authorized_key_operation: str = (
                "delete" if authorized_key_state == "absent" else "create_or_modify"
            )
            return [(authorized_key_operation, authorized_key_path)]

        #
        # fileモジュールはディレクトリ操作を監査対象外とし, absentだけを削除,
        # その他の状態を作成又は変更として分類する。
        #
        if module_name == "ansible.builtin.file":
            state: str = str(_render_value(self.environment, module_args.get("state", "file"), variables))
            if state == "directory":
                return []
            path: str = self._render_required_path(module_args, ("path", "dest", "name"), variables)
            operation: str = "delete" if state == "absent" else "create_or_modify"
            return [(operation, path)]
        #
        # tempfileの実ファイル名は実行時に決まるため, 静的に確定できる接頭辞と
        # 接尾辞からglob表現を作り, 推定値であることを標準エラー出力へ通知する。
        #
        if module_name == "ansible.builtin.tempfile":
            state: str = str(_render_value(self.environment, module_args.get("state", "file"), variables))
            if state == "directory":
                return []
            pattern_path: str = self._build_tempfile_runtime_path(
                module_args,
                variables,
            )
            return [("create_or_modify", pattern_path)]
        #
        # リポジトリ管理モジュールは指定名から各管理方式の標準配置先を組み立てる。
        # 拡張子が既に指定されている場合は重複して付加しない。
        #
        if module_name == "ansible.builtin.apt_repository":
            filename: str = self._render_required_name(
                module_args,
                ("filename",),
                variables,
            )
            state: str = str(_render_value(self.environment, module_args.get("state", "present"), variables))
            suffix: str = filename if filename.endswith(".list") else f"{filename}.list"
            operation: str = "delete" if state == "absent" else "create_or_modify"
            return [(operation, f"/etc/apt/sources.list.d/{suffix}")]
        if module_name == "ansible.builtin.deb822_repository":
            name: str = self._render_required_name(
                module_args,
                ("name",),
                variables,
            )
            state: str = str(_render_value(self.environment, module_args.get("state", "present"), variables))
            operation: str = "delete" if state == "absent" else "create_or_modify"
            return [(operation, f"/etc/apt/sources.list.d/{name}.sources")]
        if module_name == "ansible.builtin.yum_repository":
            reposdir: str = str(_render_value(self.environment, module_args.get("reposdir", "/etc/yum.repos.d"), variables))
            file_value: object = module_args.get("file", module_args.get("name"))
            if file_value is None:
                raise UnresolvedValueError("yum_repository file/name is missing")
            filename: str = str(_render_value(self.environment, file_value, variables))
            suffix: str = filename if filename.endswith(".repo") else f"{filename}.repo"
            state: str = str(_render_value(self.environment, module_args.get("state", "present"), variables))
            operation: str = "delete" if state == "absent" else "create_or_modify"
            return [(operation, str(Path(reposdir) / suffix))]
        #
        # 単一のパス引数を直接持つ残りのモジュールは対応表から候補キーを取得する。
        # replace及びpatchは既存ファイルの変更だけを行うものとして分類する。
        #
        keys: tuple[str, ...] | None = DIRECT_MODULE_PATH_KEYS.get(module_name)
        if keys is None:
            return []
        path: str = self._render_required_path(module_args, keys, variables)
        operation: str = "modify" if module_name in {
            "ansible.builtin.replace",
            "ansible.builtin.patch",
            "ansible.posix.patch",
        } else "create_or_modify"
        return [(operation, path)]

    def _render_required_name(
        self,
        module_args: Mapping[str, Any],
        keys: Sequence[str],
        variables: Mapping[str, Any],
    ) -> str:
        """リポジトリ管理モジュールの論理ファイル名を評価する。

        Args:
            module_args (Mapping[str, Any]): モジュール引数。
            keys (Sequence[str]): 論理名を保持する候補キー。
            variables (Mapping[str, Any]): 現在の変数集合。

        Returns:
            str: 空でなくディレクトリ要素を含まない論理名。

        Raises:
            UnresolvedValueError: 論理名がない又は安全な単一名でない場合。

        Examples:
            >>> True
            True
        """
        key: str
        for key in keys:
            if key not in module_args:
                continue
            rendered: Any = _render_value(
                self.environment,
                module_args[key],
                variables,
            )
            name: str = str(rendered).strip()
            if not name:
                raise UnresolvedValueError(f"Logical name is empty: {key}")
            if "{{" in name or "{%" in name or "<unknown:" in name:
                raise UnresolvedValueError(
                    f"Unresolved expression remains in logical name: {name}"
                )
            #
            # filename及びnameは配置先ではなく単一の論理名である。絶対パスや
            # ディレクトリ移動を許すと標準配置先の外を誤って監査するため拒否する。
            #
            if Path(name).is_absolute() or Path(name).name != name or name in {".", ".."}:
                raise UnresolvedValueError(f"Logical name is not a file name: {name}")
            return name
        raise UnresolvedValueError(f"Logical name is missing: {','.join(keys)}")

    def _render_required_path(
        self,
        module_args: Mapping[str, Any],
        keys: Sequence[str],
        variables: Mapping[str, Any],
    ) -> str:
        """候補キーから最初に存在するパスを評価する。

        Args:
            module_args (Mapping[str, Any]): モジュール引数。
            keys (Sequence[str]): パス候補キー。
            variables (Mapping[str, Any]): 現在の変数集合。

        Returns:
            str: 解決済みパス。

        Raises:
            UnresolvedValueError: パス引数がない又は絶対パスに解決できない場合。

        Examples:
            >>> True
            True
        """
        #
        # モジュールごとの候補キーを優先順に調べ, 最初に指定されたパスをJinja2で
        # 評価する。式が残る値は誤った実パスとして出力せず未解決扱いとする。
        #
        key: str
        for key in keys:
            if key not in module_args:
                continue
            raw_path_value: Any = module_args[key]
            self._validate_leading_path_expression(raw_path_value, variables)
            rendered: Any = _render_value(
                self.environment,
                raw_path_value,
                variables,
            )
            path: str = str(rendered)
            if "{{" in path or "{%" in path or "<unknown:" in path:
                raise UnresolvedValueError(
                    f"Unresolved expression remains in path: {path}"
                )
            #
            # 管理対象ノード上のファイル監査では絶対パスだけを有効とする。
            # False/nameなど誤って評価された相対値をCSVへ混入させない。
            #
            if not Path(path).is_absolute():
                raise UnresolvedValueError(f"Path is not absolute: {path}")
            return path
        raise UnresolvedValueError(f"Path argument is missing: {','.join(keys)}")

    def _validate_leading_path_expression(
        self,
        raw_path_value: Any,
        variables: Mapping[str, Any],
    ) -> None:
        """パス先頭のJinja2式が空値へ解決されないことを確認する。

        Args:
            raw_path_value (Any): Jinja2評価前のパス引数。
            variables (Mapping[str, Any]): 現在の変数集合。

        Raises:
            UnresolvedValueError: 先頭式が空値又はFalseへ解決される場合。

        Examples:
            >>> True
            True
        """
        if not isinstance(raw_path_value, str):
            return
        stripped_value: str = raw_path_value.lstrip()
        if not stripped_value.startswith("{{"):
            return
        expression_end_index: int = stripped_value.find("}}")
        if expression_end_index < 0:
            return
        leading_expression: str = stripped_value[: expression_end_index + 2]
        rendered_base: Any = _render_value(
            self.environment,
            leading_expression,
            variables,
        )
        if rendered_base is None or rendered_base is False or rendered_base == "":
            raise UnresolvedValueError(
                "Leading path expression resolved to an empty value: "
                f"{leading_expression}"
            )


#
# ループ未指定と, ループ要素として明示的に指定されたNoneなどを区別するための
# 専用値である。外部入力と一致しないように新しいobjectを使用する。
#
_NO_LOOP: object = object()
_UNKNOWN_DIAGNOSTIC_PATTERN: re.Pattern[str] = re.compile(
    r"<unknown:[^>]+>"
)
_NUMERIC_TEXT_PREFIX_PATTERN: re.Pattern[str] = re.compile(
    r"^[+-]?(?:\d|\.\d)"
)


def _replace_unknown_diagnostics_with_glob(pattern: str) -> str:
    """findのglob内にある未知値の診断表現をワイルドカードへ変換する。

    Args:
        pattern (str): findモジュールが使用するglobパターン。

    Returns:
        str: ``<unknown:...>``の各部分を``*``へ置換したglobパターン。

    Examples:
        >>> value = "<unknown:register:shell.stdout>_1.0_*.deb"
        >>> _replace_unknown_diagnostics_with_glob(value)
        '*_1.0_*.deb'
    """
    return _UNKNOWN_DIAGNOSTIC_PATTERN.sub("*", pattern)


def _has_valid_numeric_token_shape(raw: str) -> bool:
    """数値で始まる文字列が単一のPython数値リテラル形式であることを確認する。

    Args:
        raw (str): Jinja2が生成した文字列。

    Returns:
        bool: 単一数値, 符号付き単一数値又は複素数形式の場合はTrue。

    Examples:
        >>> _has_valid_numeric_token_shape("1.25")
        True
        >>> _has_valid_numeric_token_shape("1.25.11")
        False
    """
    try:
        tokens: list[tokenize.TokenInfo] = [
            token
            for token in tokenize.generate_tokens(StringIO(raw).readline)
            if token.type
            not in {
                tokenize.ENDMARKER,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.NEWLINE,
                tokenize.NL,
            }
        ]
    except (IndentationError, tokenize.TokenError):
        return False
    if len(tokens) == 1:
        return tokens[0].type == tokenize.NUMBER
    if len(tokens) == 2:
        has_sign: bool = tokens[0].type == tokenize.OP and tokens[0].string in {
            "+",
            "-",
        }
        return has_sign and tokens[1].type == tokenize.NUMBER
    if len(tokens) == 3:
        has_numeric_parts: bool = (
            tokens[0].type == tokenize.NUMBER
            and tokens[1].type == tokenize.OP
            and tokens[1].string in {"+", "-"}
            and tokens[2].type == tokenize.NUMBER
        )
        return has_numeric_parts and tokens[2].string.lower().endswith("j")
    return False


def _native_concat_without_backslash_parsing(values: Iterable[Any]) -> Any | None:
    """Jinja2の描画結果をバックスラッシュ文字列へ配慮して結合する。

    Jinja2標準のnative_concatは文字列をPython式として解析する。Python 3.12では
    正規表現の``\\[``などが無効なエスケープとしてSyntaxWarningを発生させるため,
    バックスラッシュを含む文字列はPython式へ変換せずそのまま返す。

    Args:
        values (Iterable[Any]): Jinja2が生成した描画結果の並び。

    Returns:
        Any | None: 単一のネイティブ値, 結合した文字列, 又は出力なしを表すNone。

    Examples:
        >>> _native_concat_without_backslash_parsing(iter([r"^\\["]))
        '^\\\\['
        >>> _native_concat_without_backslash_parsing(iter(["[1, 2]"]))
        [1, 2]
    """
    #
    # Jinja2標準実装と同様に先頭2件だけを確認し, 単一の非文字列値は型を変えず
    # そのまま返す。これにより配列, 辞書, 数値及び真偽値の型を維持する。
    #
    head: list[Any] = list(islice(values, 2))
    if not head:
        return None
    if len(head) == 1:
        raw_value: Any = head[0]
        if not isinstance(raw_value, str):
            return raw_value
        raw: str = raw_value
    else:
        #
        # valuesが生成器の場合は先に取り出した2件を戻してから残りを結合する。
        # 通常の反復可能値は再走査できるため, 元の値を先頭から使用する。
        #
        if isinstance(values, GeneratorType):
            values = chain(head, values)
        text_parts: list[str] = []
        value: Any
        for value in values:
            text_parts.append(str(value))
        raw = "".join(text_parts)

    #
    # バックスラッシュを含む値は正規表現やシェル用文字列である可能性があるため,
    # Python式として解析しない。これがinvalid escape sequence警告を防ぐ処理である。
    #
    if "\\" in raw:
        return raw
    if _NUMERIC_TEXT_PREFIX_PATTERN.match(raw) and not _has_valid_numeric_token_shape(
        raw
    ):
        #
        # 1.25.11などは版数文字列でありPython数値ではない。ast.parseへ渡すと
        # invalid decimal literal警告が出るため, 字句段階で通常文字列と判定する。
        #
        return raw

    try:
        #
        # バックスラッシュを含まない値にはJinja2標準と同じ変換を適用し,
        # 文字列表現の配列, 辞書, 数値及び真偽値を元のPython型へ戻す。
        #
        return literal_eval(parse(raw, mode="eval"))
    except (ValueError, SyntaxError, MemoryError):
        #
        # Pythonリテラルでない通常の文字列は変換せずに返す。
        #
        return raw


class AuditNativeEnvironment(NativeEnvironment):
    """バックスラッシュ文字列をPython式として解析しないJinja2評価環境である。"""

    concat: Callable[[Iterable[Any]], Any | None] = staticmethod(
        _native_concat_without_backslash_parsing
    )


class AuditNativeTemplate(NativeTemplate):
    """監査用のネイティブ型変換を使用するJinja2テンプレートである。"""

    environment_class: type[NativeEnvironment] = AuditNativeEnvironment


#
# NativeTemplate.renderはenvironment_classの結合処理を参照するため, 環境側でも
# 監査用テンプレートを明示し, from_stringで必ず専用の組み合わせを生成する。
#
AuditNativeEnvironment.template_class = AuditNativeTemplate


#
# Jinja2文字列内でPythonが有効と認識する1文字エスケープの集合である。
# x, u, U, Nは後続文字を伴うエスケープの開始文字として扱う。
#
_VALID_JINJA_ESCAPE_PREFIXES: frozenset[str] = frozenset(
    "\\\\'\"abfnrtvxuUN\n\r"
)
_EXPLICIT_STRING_RESULT_PATTERN: re.Pattern[str] = re.compile(
    r"\|\s*(?:ansible\.builtin\.)?string\b"
    r"(?:\s*\|\s*(?:ansible\.builtin\.)?trim\b)*\s*\}\}\s*$"
)


def _escape_invalid_jinja_string_sequences(template_source: str) -> str:
    r"""Jinja2式内の文字列にある無効なPythonエスケープを二重化する。

    Jinja2は引用符内の文字列をunicode-escapeで復号する。Python 3.12では``\[``や
    ``\d``がSyntaxWarningを発生させるため, Jinja2へ渡す前に``\\[``及び``\\d``へ
    変換する。復号後の文字列は変換前と同じバックスラッシュを1文字含む。

    Args:
        template_source (str): Jinja2へ渡す変換前の文字列。

    Returns:
        str: Jinja2式内の無効なエスケープだけを二重化した文字列。

    Examples:
        >>> source = r"{{ value | regex_replace('\[', '') }}"
        >>> escaped = _escape_invalid_jinja_string_sequences(source)
        >>> escaped == r"{{ value | regex_replace('\\[', '') }}"
        True
        >>> _escape_invalid_jinja_string_sequences(escaped) == escaped
        True
        >>> _escape_invalid_jinja_string_sequences(r"outside\[{{ value }}")
        'outside\\\\[{{ value }}'
    """
    result_parts: list[str] = []
    index: int = 0
    expression_end: str | None = None
    quote_character: str | None = None

    while index < len(template_source):
        #
        # Jinja2式の外側はテンプレート本文であるため変更しない。変数式又は制御式の
        # 開始記号を見つけた場合だけ, 対応する終了記号まで文字列リテラルを調べる。
        #
        if expression_end is None:
            if template_source.startswith("{{", index):
                expression_end = "}}"
                result_parts.append("{{")
                index += 2
                continue
            if template_source.startswith("{%", index):
                expression_end = "%}"
                result_parts.append("{%")
                index += 2
                continue
            result_parts.append(template_source[index])
            index += 1
            continue

        #
        # 引用符の外側で終了記号へ到達した場合はJinja2式を閉じる。引用符の内側に
        # 同じ記号が現れても文字列の一部として扱う。
        #
        if quote_character is None and template_source.startswith(expression_end, index):
            result_parts.append(expression_end)
            index += len(expression_end)
            expression_end = None
            continue

        current_character: str = template_source[index]
        if quote_character is None:
            if current_character in {"'", '"'}:
                quote_character = current_character
            result_parts.append(current_character)
            index += 1
            continue

        #
        # 引用符内のバックスラッシュは次の文字と組み合わせて判定する。文字列末尾の
        # 単独バックスラッシュはJinja2自身が構文エラーとして報告できるよう保持する。
        #
        if current_character == "\\" and index + 1 < len(template_source):
            next_character: str = template_source[index + 1]
            is_octal_escape: bool = "0" <= next_character <= "7"
            is_valid_escape: bool = (
                next_character in _VALID_JINJA_ESCAPE_PREFIXES or is_octal_escape
            )
            if not is_valid_escape:
                #
                # Jinja2の復号後にバックスラッシュ1文字が残るように, 入力側では
                # バックスラッシュを2文字へ増やす。次の文字は次周回で通常処理する。
                #
                result_parts.append("\\\\")
                index += 1
                continue

            #
            # 有効なエスケープ及び既に二重化済みのバックスラッシュは変更せず,
            # 次の引用符を文字列終端と誤認しないよう2文字をまとめて追加する。
            #
            result_parts.append(current_character)
            result_parts.append(next_character)
            index += 2
            continue

        result_parts.append(current_character)
        if current_character == quote_character:
            quote_character = None
        index += 1

    return "".join(result_parts)


def _create_environment() -> NativeEnvironment:
    """Ansibleフィルタを使用するJinja2評価環境を生成する。

    Returns:
        NativeEnvironment: Ansibleフィルタと厳格な未定義変数検出を使用する評価環境。

    Examples:
        >>> environment = _create_environment()
        >>> environment.from_string("{{ 1 + 1 }}").render()
        2
        >>> "regex_escape" in environment.filters
        True
    """
    #
    # バックスラッシュを含む描画結果でPython 3.12のSyntaxWarningを発生させない
    # 監査専用環境を使用する。
    #
    environment: NativeEnvironment = AuditNativeEnvironment(undefined=StrictUndefined)

    #
    # Playbook実行時と監査処理時でフィルタの意味が異なることを防ぐため,
    # Ansible本体が読み込んだフィルタ関数を同じJinja2評価環境へ登録する。
    #
    _register_ansible_filters(environment)
    _register_materializing_filters(environment)
    _register_unknown_preserving_filters(environment)
    #
    # failed, succeeded, skippedなどはフィルタではなくJinja2テストとして提供される。
    # Playbookのis演算子をAnsible実行時と同じ意味で評価するため, テストも登録する。
    #
    _register_ansible_tests(environment)
    #
    # 対象Playbookのパス生成で使用する制御ノード環境変数だけをlookupとして公開する。
    # 任意の環境変数を許可すると秘密情報を意図せず評価するため, 名前を限定する。
    #
    environment.globals["lookup"] = _audit_lookup
    return environment


def _register_materializing_filters(environment: NativeEnvironment) -> None:
    """遅延反復フィルタの結果を再利用可能な配列へ正規化する。"""
    filter_name: str
    for filter_name in (
        "map",
        "select",
        "selectattr",
        "reject",
        "rejectattr",
        "unique",
    ):
        filter_value: object = environment.filters.get(filter_name)
        if not callable(filter_value):
            continue
        original_filter: Callable[..., Any] = cast(Callable[..., Any], filter_value)

        @wraps(original_filter)
        def materialize_generator(
            *args: Any,
            _original_filter: Callable[..., Any] = original_filter,
            **kwargs: Any,
        ) -> Any:
            """generatorだけを配列化し, 他の戻り値は型を維持する。"""
            result: Any = _original_filter(*args, **kwargs)
            if isinstance(result, GeneratorType):
                return list(result)
            return result

        environment.filters[filter_name] = materialize_generator


def _register_unknown_preserving_filters(
    environment: NativeEnvironment,
) -> None:
    """型変換フィルタが未知値を既知の偽値へ変換しないようにする。"""
    filter_name: str
    for filter_name in (
        "bool",
        "ansible.builtin.bool",
        "int",
        "float",
        "string",
        "ternary",
        "ansible.builtin.ternary",
        "from_json",
        "ansible.builtin.from_json",
        "b64decode",
        "ansible.builtin.b64decode",
        "regex_search",
        "ansible.builtin.regex_search",
        "regex_findall",
        "ansible.builtin.regex_findall",
        "trim",
        "list",
        "first",
    ):
        filter_value: object = environment.filters.get(filter_name)
        if not callable(filter_value):
            continue
        original_filter: Callable[..., Any] = cast(Callable[..., Any], filter_value)

        @wraps(original_filter)
        def preserve_unknown(
            *args: Any,
            _original_filter: Callable[..., Any] = original_filter,
            **kwargs: Any,
        ) -> Any:
            """未知値は保持し, 既知値だけを元のフィルタへ渡す。"""
            pass_argument: object = getattr(
                _original_filter,
                "jinja_pass_arg",
                None,
            )
            value_index: int = 1 if pass_argument is not None else 0
            if len(args) <= value_index:
                return _original_filter(*args, **kwargs)
            value: Any = args[value_index]
            if isinstance(value, (UnknownValue, UnknownMapping)):
                return value
            return _original_filter(*args, **kwargs)

        environment.filters[filter_name] = preserve_unknown


def _audit_lookup(
    plugin_name: Any,
    *terms: Any,
    repository_root: Path | None = None,
    current_file: Path | None = None,
    **options: Any,
) -> Any:
    """監査に必要な範囲へ限定してAnsibleのlookupを評価する。

    Args:
        plugin_name (Any): lookupプラグイン名。
        *terms (Any): プラグインへ渡す検索語。
        **options (Any): env lookupの任意指定。defaultだけを許可する。

    Returns:
        Any: lookupプラグインに応じた文字列又は文字列配列。

    Raises:
        UnresolvedValueError: 未対応プラグイン, 引数又は環境変数を指定した場合。

    Examples:
        >>> isinstance(_audit_lookup('env', 'HOME'), str)
        True
    """
    normalized_plugin_name: str = str(plugin_name)
    if normalized_plugin_name in {"env", "ansible.builtin.env"}:
        if len(terms) != 1:
            raise UnresolvedValueError(
                "env lookup requires exactly one variable name"
            )
        unsupported_options: set[str] = set(options) - {"default"}
        if unsupported_options:
            option_names: str = ",".join(sorted(unsupported_options))
            raise UnresolvedValueError(
                f"Unsupported env lookup options: {option_names}"
            )
        variable_name: str = str(terms[0]).strip()
        if variable_name not in ALLOWED_ENV_LOOKUP_NAMES:
            raise UnresolvedValueError(
                f"Environment lookup is not allowed: {variable_name}"
            )
        default_value: Any = options.get("default", "")
        resolved_value: str | None = os.environ.get(variable_name)
        if resolved_value is not None:
            return resolved_value
        return str(default_value)

    if normalized_plugin_name in {
        "fileglob",
        "ansible.builtin.fileglob",
    }:
        if len(terms) != 1:
            raise UnresolvedValueError(
                "fileglob lookup requires exactly one pattern"
            )
        unsupported_options = set(options) - {"wantlist"}
        if unsupported_options:
            option_names = ",".join(sorted(unsupported_options))
            raise UnresolvedValueError(
                f"Unsupported fileglob options: {option_names}"
            )
        pattern: str = str(terms[0])
        if "\0" in pattern:
            raise UnresolvedValueError("fileglob pattern contains a null byte")
        matches: list[str] = sorted(glob.glob(pattern, recursive=False))
        wantlist: bool = bool(options.get("wantlist", False))
        return matches if wantlist else ",".join(matches)

    if normalized_plugin_name in {
        "first_found",
        "ansible.builtin.first_found",
    }:
        if len(terms) != 1 or not isinstance(terms[0], Mapping):
            raise UnresolvedValueError(
                "first_found lookup requires one parameter mapping"
            )
        if options:
            option_names = ",".join(sorted(options))
            raise UnresolvedValueError(
                f"Unsupported first_found options: {option_names}"
            )
        parameters: Mapping[str, Any] = cast(Mapping[str, Any], terms[0])
        files: list[str] = _normalize_lookup_sequence(parameters.get("files", []))
        paths: list[str] = _normalize_lookup_sequence(parameters.get("paths", [""]))
        skip_missing: bool = bool(parameters.get("skip", False))
        if repository_root is None or current_file is None:
            raise UnresolvedValueError(
                "first_found lookup requires repository and task context"
            )
        root_path: Path = repository_root.resolve()
        file_name: str
        search_path: str
        for file_name in files:
            direct_candidate: Path = Path(file_name)
            if direct_candidate.is_absolute():
                candidates: list[Path] = [direct_candidate]
            else:
                candidates = []
                for search_path in paths:
                    relative_search_path: Path = Path(search_path)
                    candidates.extend(
                        [
                            current_file.parent / relative_search_path / file_name,
                            current_file.parent.parent
                            / relative_search_path
                            / file_name,
                            root_path / relative_search_path / file_name,
                        ]
                    )
            candidate: Path
            for candidate in candidates:
                resolved_candidate: Path = candidate.resolve()
                try:
                    resolved_candidate.relative_to(root_path)
                except ValueError:
                    continue
                if resolved_candidate.is_file():
                    return str(resolved_candidate)
        if skip_missing:
            return ""
        raise UnresolvedValueError(
            f"first_found did not find a file: {','.join(files)}"
        )

    if normalized_plugin_name in {"pipe", "ansible.builtin.pipe"}:
        if len(terms) != 1 or str(terms[0]).strip() != "id -gn":
            raise UnresolvedValueError(
                "pipe lookup permits only the read-only command: id -gn"
            )
        if options:
            option_names = ",".join(sorted(options))
            raise UnresolvedValueError(
                f"Unsupported pipe lookup options: {option_names}"
            )
        try:
            group_name: str = grp.getgrgid(os.getgid()).gr_name
        except KeyError as exc:
            raise UnresolvedValueError(
                "Controller primary group could not be resolved"
            ) from exc
        return group_name

    raise UnresolvedValueError(
        f"Unsupported lookup plugin: {normalized_plugin_name}"
    )


def _normalize_lookup_sequence(value: object) -> list[str]:
    """lookup引数の文字列又は配列を文字列配列へ正規化する。"""
    if isinstance(value, (list, tuple)):
        item: object
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def _register_ansible_filters(environment: NativeEnvironment) -> None:
    """Ansibleが提供するフィルタをJinja2評価環境へ登録する。

    ``filter_loader.all()`` は同じ名前を持つフィルタを複数返す場合があるため,
    一度登録した名前は上書きしない。``ansible.builtin`` のフィルタはPlaybookで
    短縮名が使用されるため,FQCNと短縮名の両方を登録する。

    Args:
        environment (NativeEnvironment): フィルタの登録先となるJinja2評価環境。

    Raises:
        RuntimeError: フィルタ名又は実行関数を取得できない場合。

    Examples:
        >>> environment = NativeEnvironment(undefined=StrictUndefined)
        >>> _register_ansible_filters(environment)
        >>> "regex_escape" in environment.filters
        True
        >>> "ansible.builtin.regex_escape" in environment.filters
        True
    """
    registered_names: set[str] = set(environment.filters)
    builtin_prefix: str = "ansible.builtin."

    #
    # Ansibleが決定した読み込み順を維持するため,同名フィルタは最初に取得した
    # 実装を採用し,後続の重複した候補で上書きしない。
    #
    plugin: Any
    for plugin in filter_loader.all():
        ansible_name_value: Any = getattr(plugin, "ansible_name", None)
        j2_function_value: Any = getattr(plugin, "j2_function", None)

        if not isinstance(ansible_name_value, str) or not ansible_name_value:
            raise RuntimeError("Ansible filter plugin has no valid name")

        if not callable(j2_function_value):
            raise RuntimeError(
                "Ansible filter plugin has no callable Jinja2 function: "
                f"{ansible_name_value}"
            )

        ansible_name: str = ansible_name_value
        j2_function: Callable[..., Any] = j2_function_value
        _register_filter_name(
            environment,
            registered_names,
            ansible_name,
            j2_function,
        )

        #
        # ansible.builtinのフィルタは短縮名で記述されるPlaybookを評価するため,
        # FQCN末尾の名前も同じ関数へ割り当てる。
        #
        if ansible_name.startswith(builtin_prefix):
            short_name: str = ansible_name.removeprefix(builtin_prefix)
            _register_filter_name(
                environment,
                registered_names,
                short_name,
                j2_function,
            )


def _register_filter_name(
    environment: NativeEnvironment,
    registered_names: set[str],
    filter_name: str,
    filter_function: Callable[..., Any],
) -> None:
    """フィルタ名を重複させずJinja2評価環境へ登録する。

    Args:
        environment (NativeEnvironment): フィルタの登録先となるJinja2評価環境。
        registered_names (set[str]): 登録済みフィルタ名の集合。
        filter_name (str): 登録するフィルタ名。
        filter_function (Callable[..., Any]): 登録するフィルタ関数。

    Examples:
        >>> environment = NativeEnvironment(undefined=StrictUndefined)
        >>> names = set(environment.filters)
        >>> _register_filter_name(environment, names, "example", str)
        >>> "example" in environment.filters
        True
    """
    if filter_name in registered_names:
        return

    environment.filters[filter_name] = filter_function
    registered_names.add(filter_name)


def _register_ansible_tests(environment: NativeEnvironment) -> None:
    """Ansibleが提供するテストをJinja2評価環境へ登録する。

    ``failed``や``succeeded``などはPlaybookのwhen式及びJinja2式でis演算子と
    ともに使用される。``ansible.builtin`` のテストは完全修飾名と短縮名の両方を
    登録し, Playbook上のいずれの記法も評価可能にする。

    Args:
        environment (NativeEnvironment): テストの登録先となるJinja2評価環境。

    Raises:
        RuntimeError: テスト名又は実行関数を取得できない場合。

    Examples:
        >>> environment = NativeEnvironment(undefined=StrictUndefined)
        >>> _register_ansible_tests(environment)
        >>> "failed" in environment.tests
        True
        >>> "ansible.builtin.failed" in environment.tests
        True
    """
    registered_names: set[str] = set(environment.tests)
    builtin_prefix: str = "ansible.builtin."

    #
    # Ansibleが決定した読み込み順を維持し, 同名のテストが複数ある場合は最初に
    # 読み込まれた実装を使用する。後続候補による意図しない上書きを防ぐためである。
    #
    plugin: Any
    for plugin in test_loader.all():
        ansible_name_value: Any = getattr(plugin, "ansible_name", None)
        j2_function_value: Any = getattr(plugin, "j2_function", None)

        if not isinstance(ansible_name_value, str) or not ansible_name_value:
            raise RuntimeError("Ansible test plugin has no valid name")

        if not callable(j2_function_value):
            raise RuntimeError(
                "Ansible test plugin has no callable Jinja2 function: "
                f"{ansible_name_value}"
            )

        ansible_name: str = ansible_name_value
        j2_function: Callable[..., Any] = j2_function_value
        _register_test_name(
            environment,
            registered_names,
            ansible_name,
            j2_function,
        )

        #
        # ansible.builtinのテストはPlaybookでfailedのような短縮名が使われるため,
        # 完全修飾名の末尾も同じテスト関数へ割り当てる。
        #
        if ansible_name.startswith(builtin_prefix):
            short_name: str = ansible_name.removeprefix(builtin_prefix)
            _register_test_name(
                environment,
                registered_names,
                short_name,
                j2_function,
            )


def _register_test_name(
    environment: NativeEnvironment,
    registered_names: set[str],
    test_name: str,
    test_function: Callable[..., Any],
) -> None:
    """テスト名を重複させずJinja2評価環境へ登録する。

    Args:
        environment (NativeEnvironment): テストの登録先となるJinja2評価環境。
        registered_names (set[str]): 登録済みテスト名の集合。
        test_name (str): 登録するテスト名。
        test_function (Callable[..., Any]): 登録するテスト関数。

    Examples:
        >>> environment = NativeEnvironment(undefined=StrictUndefined)
        >>> names = set(environment.tests)
        >>> _register_test_name(environment, names, "example", bool)
        >>> "example" in environment.tests
        True
    """
    if test_name in registered_names:
        return

    environment.tests[test_name] = test_function
    registered_names.add(test_name)


def _load_yaml_file(path: Path) -> object:
    """UTF-8 YAMLファイルを行番号付きで読み込む。

    Args:
        path (Path): 読み込み対象。

    Returns:
        object: YAMLから構築した値。

    Raises:
        AuditError: ファイル読み込み又はYAML解析が失敗する場合。

    Examples:
        >>> True
        True
    """
    try:
        #
        # 読み込み時に行番号を付ける独自Loaderを使い, 後段の診断情報へ定義位置を
        # 引き継ぐ。入力ファイルは明示的にUTF-8として扱う。
        #
        text: str = path.read_text(encoding="utf-8")
        return yaml.load(text, Loader=MarkedLoader)
    except (OSError, yaml.YAMLError) as exc:
        raise AuditError(f"Failed to load YAML file: {path}: {exc}") from exc


def _strip_internal_line_metadata(value: Any) -> Any:
    """YAML行番号用の内部項目を利用者データから再帰的に除去する。

    Args:
        value (Any): YAMLから読み込んだ変数値。

    Returns:
        Any: 辞書内の``__line__``を除去し, 元の配列構造を維持した値。

    Examples:
        >>> value = {"__line__": 1, "body": {"__line__": 2, "name": "x"}}
        >>> _strip_internal_line_metadata(value)
        {'body': {'name': 'x'}}
    """
    if isinstance(value, dict):
        cleaned_mapping: dict[str, Any] = {}
        item_name: str
        item_value: Any
        for item_name, item_value in cast(dict[str, Any], value).items():
            if item_name == "__line__":
                continue
            cleaned_mapping[item_name] = _strip_internal_line_metadata(item_value)
        return cleaned_mapping
    if isinstance(value, list):
        item: Any
        return [_strip_internal_line_metadata(item) for item in value]
    if isinstance(value, tuple):
        tuple_item: Any
        return tuple(
            _strip_internal_line_metadata(tuple_item) for tuple_item in value
        )
    return value


def _load_optional_mapping(path: Path) -> dict[str, Any]:
    """存在するYAML辞書を読み込み, 存在しない場合は空辞書を返す。

    Args:
        path (Path): 読み込み対象。

    Returns:
        dict[str, Any]: 読み込んだ変数辞書。

    Raises:
        AuditError: YAMLルートが辞書でない場合。

    Examples:
        >>> _load_optional_mapping(Path('/path/that/does/not/exist'))
        {}
    """
    #
    # defaultsやvarsは任意ファイルであるため, 存在しない場合及び空の場合は
    # 呼び出し側がそのままupdateできる空辞書を返す。
    #
    if not path.is_file():
        return {}
    loaded: object = _load_yaml_file(path)
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise AuditError(f"Variable file must contain a YAML mapping: {path}")
    mapping: dict[str, Any] = cast(dict[str, Any], loaded)
    #
    # 行番号は解析用の内部情報でありAnsible変数ではないため, 変数集合へ混入する
    # 前に入れ子を含めて取り除く。
    #
    cleaned_mapping: Any = _strip_internal_line_metadata(mapping)
    return cast(dict[str, Any], cleaned_mapping)


def _build_inventory_groups(
    inventory_root: Mapping[str, Any],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """ansible-inventoryの出力からグループとホスト所属情報を作る。

    Args:
        inventory_root (Mapping[str, Any]): ansible-inventory --listのルート辞書。

    Returns:
        tuple[dict[str, list[str]], dict[str, list[str]]]: グループ別ホスト一覧と
        ホスト別所属グループ一覧。

    Examples:
        >>> root = {"web": {"hosts": ["h1"]}, "_meta": {"hostvars": {}}}
        >>> _build_inventory_groups(root)[0]["web"]
        ['h1']
    """
    resolved_groups: dict[str, list[str]] = {}

    def resolve_group(group_name: str, resolving: set[str]) -> list[str]:
        """子グループを含むホスト一覧を循環させず解決する。"""
        if group_name in resolved_groups:
            return resolved_groups[group_name]
        if group_name in resolving:
            return []
        next_resolving: set[str] = {*resolving, group_name}
        group_value: object = inventory_root.get(group_name, {})
        if not isinstance(group_value, dict):
            resolved_groups[group_name] = []
            return []
        group_mapping: dict[str, Any] = cast(dict[str, Any], group_value)
        host_names: set[str] = set()
        hosts_value: object = group_mapping.get("hosts", [])
        if isinstance(hosts_value, list):
            host_value: Any
            for host_value in hosts_value:
                host_names.add(str(host_value))
        children_value: object = group_mapping.get("children", [])
        if isinstance(children_value, list):
            child_value: Any
            for child_value in children_value:
                child_name: str = str(child_value)
                host_names.update(resolve_group(child_name, next_resolving))
        resolved_hosts: list[str] = sorted(host_names)
        resolved_groups[group_name] = resolved_hosts
        return resolved_hosts

    group_name: str
    for group_name in inventory_root:
        if group_name != "_meta":
            resolve_group(group_name, set())

    host_group_names: dict[str, list[str]] = {}
    group_hosts: list[str]
    for group_name, group_hosts in resolved_groups.items():
        if group_name in {"all", "ungrouped"}:
            continue
        host_name: str
        for host_name in group_hosts:
            host_group_names.setdefault(host_name, []).append(group_name)
    group_name_list: list[str]
    for group_name_list in host_group_names.values():
        group_name_list.sort()
    return resolved_groups, host_group_names


def _normalize_module_name(name: str) -> str:
    """短いモジュール名を本ツールが扱うFQCNへ正規化する。

    Args:
        name (str): YAML上のモジュール名。

    Returns:
        str: 正規化したモジュール名。

    Examples:
        >>> _normalize_module_name('file')
        'ansible.builtin.file'
    """
    #
    # 対応表に登録された短縮名だけを完全修飾名へ変換し, 未知の名前は診断や
    # 将来の判定に利用できるよう元の文字列を保持する。
    #
    return SHORT_MODULE_NAMES.get(name, name)


def _find_module_name(task: Mapping[str, Any]) -> str | None:
    """タスク辞書から本ツールが処理するモジュール名を検出する。

    Args:
        task (Mapping[str, Any]): タスク定義。

    Returns:
        str | None: 対象モジュール名。該当なしはNone。

    Examples:
        >>> _find_module_name({'ansible.builtin.copy': {'dest': '/x'}})
        'ansible.builtin.copy'
    """
    #
    # nameやwhenなどのタスク属性を飛ばし, 最初のモジュールを返す。監査対象外の
    # モジュールもregister結果を構築する必要があるため検出対象に含める。
    #
    key: str
    for key in task:
        normalized: str = _normalize_module_name(key)
        if normalized in TARGET_MODULES or normalized in CONTROL_MODULES:
            return normalized
        if key == "__line__" or key in TASK_ATTRIBUTE_KEYS:
            continue
        return key
    return None


def _module_args_from_task(
    task: Mapping[str, Any],
    module_name: str,
) -> dict[str, Any]:
    """正規化前後のモジュール名から引数を取得する。

    Args:
        task (Mapping[str, Any]): タスク定義。
        module_name (str): 検出済みモジュール名。

    Returns:
        dict[str, Any]: 辞書へ正規化したモジュール引数。
    """
    if module_name in task:
        return _normalize_module_args(task[module_name])
    short_name: str = module_name.rsplit(".", 1)[-1]
    if short_name in task:
        return _normalize_module_args(task[short_name])
    return {}


def _normalize_module_args(value: object) -> dict[str, Any]:
    """モジュール引数を辞書形式へ正規化する。

    Args:
        value (object): YAML上のモジュール引数。

    Returns:
        dict[str, Any]: 正規化後引数。

    Examples:
        >>> _normalize_module_args('x.yml')['_raw_params']
        'x.yml'
    """
    #
    # 辞書形式では行番号用の内部項目を除去する。自由形式の引数は後続処理が共通に
    # 参照できる_raw_paramsへ格納し, 未指定は空辞書にそろえる。
    #
    if isinstance(value, dict):
        result: dict[str, Any] = dict(cast(dict[str, Any], value))
        result.pop("__line__", None)
        return result
    if value is None:
        return {}
    return {"_raw_params": value}


def _render_value(
    environment: NativeEnvironment,
    value: Any,
    variables: Mapping[str, Any],
) -> Any:
    """値中のJinja2式を安定するまで再帰的に評価する。

    Args:
        environment (NativeEnvironment): Jinja2評価環境。
        value (Any): 評価対象値。
        variables (Mapping[str, Any]): 評価用変数集合。

    Returns:
        Any: 評価後の値。

    Raises:
        UnresolvedValueError: 規定回数内に評価結果が安定しない場合。
        UndefinedError: 未定義変数を参照した場合。

    Examples:
        >>> env = _create_environment()
        >>> _render_value(env, '{{ base }}/x', {'base': '/etc'})
        '/etc/x'
    """
    #
    # 配列と辞書は内部の各要素へ同じ評価を再帰適用し, 元の入れ子構造を維持する。
    # YAMLの行番号用項目はテンプレート変数として扱わない。
    #
    if isinstance(value, list):
        return [_render_value(environment, item, variables) for item in value]
    if isinstance(value, tuple):
        return tuple(_render_value(environment, item, variables) for item in value)
    if isinstance(value, dict):
        rendered_mapping: dict[str, Any] = {}
        item_key: str
        item_value: Any
        for item_key, item_value in cast(dict[str, Any], value).items():
            if item_key == "__line__":
                continue
            rendered_mapping[item_key] = _render_value(
                environment,
                item_value,
                variables,
            )
        return rendered_mapping
    if not isinstance(value, str):
        return value
    #
    # 変数の値が別のJinja2式を返す場合に備えて反復評価する。値が変わらない場合や
    # 式が消えた場合は収束したものとして直ちに返す。
    #
    current: Any = value
    pass_index: int
    for pass_index in range(MAX_TEMPLATE_PASSES):
        del pass_index
        if not isinstance(current, str) or ("{{" not in current and "{%" not in current):
            return current
        #
        # Jinja2の字句解析前に式内の無効なPythonエスケープを二重化し, 正規表現の
        # 意味を維持したままPython 3.12のSyntaxWarningを防ぐ。
        #
        template_source: str = _escape_invalid_jinja_string_sequences(current)
        rendered: Any = environment.from_string(template_source).render(
            **dict(variables)
        )
        if (
            _EXPLICIT_STRING_RESULT_PATTERN.search(template_source)
            and rendered is None
        ):
            rendered = "None"
        elif (
            _EXPLICIT_STRING_RESULT_PATTERN.search(template_source)
            and isinstance(rendered, (bool, int, float))
        ):
            #
            # NativeEnvironmentは文字列フィルタの結果が数値表現の場合もPythonの
            # 数値へ再変換する。明示されたstringの意味を優先し文字列へ戻す。
            #
            rendered = str(rendered)
        if isinstance(rendered, (UnknownValue, UnknownMapping)):
            return rendered
        if isinstance(rendered, (list, tuple, dict)):
            #
            # Jinja2式が配列又は辞書を返した場合, 内部要素に残るJinja2式も同じ
            # 変数集合で評価する。ループ要素を式の文字列のまま扱うことを防ぐ。
            #
            return _render_value(environment, rendered, variables)
        if rendered == current:
            return rendered
        current = rendered
    raise UnresolvedValueError(f"Template did not converge: {value}")


def _resolve_variable_map(
    environment: NativeEnvironment,
    variables: Mapping[str, Any],
) -> dict[str, Any]:
    """単純な文字列変数間参照を可能な範囲で反復解決する。

    配列及び辞書の内部値, バックスラッシュを含む式, password_hashを含む式は,
    実際にタスクの条件又は引数から参照されるまで評価を保留する。監査対象と
    無関係な正規表現のPythonリテラル変換及びパスワードハッシュ生成を防ぐためである。

    Args:
        environment (NativeEnvironment): Jinja2評価環境。
        variables (Mapping[str, Any]): 元変数集合。

    Returns:
        dict[str, Any]: 解決可能な値を反映した変数集合。

    Examples:
        >>> env = _create_environment()
        >>> _resolve_variable_map(env, {'a': '/etc', 'b': '{{ a }}/x'})['b']
        '/etc/x'
        >>> values = {'pattern': r"{{ '^\\[' }}"}
        >>> _resolve_variable_map(env, values)['pattern'] == values['pattern']
        True
        >>> values = {'secret': "{{ 'x' | password_hash('sha512') }}"}
        >>> _resolve_variable_map(env, values)['secret'] == values['secret']
        True
    """
    #
    # 各周回の開始時点を写し取り, 走査中の値更新によって辞書の反復状態が変わる
    # ことを防ぐ。未定義変数を含む値は後の周回で解決できるため保留する。
    #
    resolved: dict[str, Any] = dict(variables)
    pass_index: int
    for pass_index in range(MAX_TEMPLATE_PASSES):
        del pass_index
        changed: bool = False
        name: str
        raw_value: Any
        snapshot: dict[str, Any] = dict(resolved)
        for name, raw_value in snapshot.items():
            if isinstance(raw_value, (list, tuple)) and all(
                not isinstance(item, (list, tuple, dict))
                for item in raw_value
            ):
                try:
                    rendered_sequence: Any = _render_value(
                        environment,
                        raw_value,
                        resolved,
                    )
                    if rendered_sequence != raw_value:
                        resolved[name] = rendered_sequence
                        changed = True
                except (AnsibleError, AuditError, TemplateError, ValueError, TypeError):
                    continue
                continue
            #
            # 複合値は必要な要素が参照された時に評価する。ここで内部を一括評価すると,
            # 監査に使わない正規表現や高負荷なフィルタまで実行されるためである。
            #
            if not isinstance(raw_value, str):
                continue
            #
            # NativeEnvironmentは描画結果をPythonリテラルとして解釈するため,
            # 正規表現の\[などがPython 3.12のSyntaxWarningを発生させる。
            # バックスラッシュを含む値は元の表現を保持し, 利用時の評価へ回す。
            #
            if "\\" in raw_value:
                continue
            #
            # password_hashは入力が定数でもハッシュ生成を実行する。監査対象パスと
            # 無関係な秘密値をホスト及びロールごとに生成しないよう先行評価を避ける。
            #
            if "password_hash" in raw_value:
                continue
            if _should_defer_empty_path_base(environment, raw_value, resolved):
                continue
            try:
                rendered: Any = _render_value(environment, raw_value, resolved)
            #
            # 実行時のregister値やAnsible固有値へ依存して評価できない変数は元の
            # 表現を保持し, 実際にタスクから参照された時に未解決として記録する。
            #
            except (AnsibleError, TemplateError, UnknownConditionError):
                continue
            if isinstance(rendered, (UnknownValue, UnknownMapping)):
                if resolved.get(name) is not rendered:
                    resolved[name] = rendered
                    changed = True
                continue
            if rendered != resolved.get(name):
                resolved[name] = rendered
                changed = True
        if not changed:
            #
            # 1周して値の変化がなければ, これ以上の反復で新たに解決されないため
            # 処理を終了する。
            #
            break
    return resolved


def _should_defer_empty_path_base(
    environment: NativeEnvironment,
    raw_value: str,
    variables: Mapping[str, Any],
) -> bool:
    """空の先頭式へパスを連結する変数評価を後続のset_factまで保留する。

    Args:
        environment (NativeEnvironment): Jinja2評価環境。
        raw_value (str): 評価前の変数値。
        variables (Mapping[str, Any]): 現在の変数集合。

    Returns:
        bool: 先頭式が空で, その後へ絶対パス要素を連結している場合はTrue。
    """
    stripped_value: str = raw_value.lstrip()
    if not stripped_value.startswith("{{"):
        return False
    expression_end_index: int = stripped_value.find("}}")
    if expression_end_index < 0:
        return False
    suffix: str = stripped_value[expression_end_index + 2 :].lstrip()
    if not suffix.startswith("/"):
        return False
    leading_expression: str = stripped_value[: expression_end_index + 2]
    try:
        rendered_base: Any = _render_value(
            environment,
            leading_expression,
            variables,
        )
    except (AnsibleError, AuditError, TemplateError, ValueError, TypeError):
        return False
    if rendered_base is None or rendered_base is False:
        return True
    return isinstance(rendered_base, str) and not rendered_base.strip()


def _evaluate_when(
    environment: NativeEnvironment,
    when_value: object,
    variables: Mapping[str, Any],
) -> bool:
    """Ansibleのwhen相当式をJinja2式として評価する。

    Args:
        environment (NativeEnvironment): Jinja2評価環境。
        when_value (object): when値。
        variables (Mapping[str, Any]): 評価用変数集合。

    Returns:
        bool: 条件を満たす場合はTrue。

    Raises:
        UndefinedError: 条件が実行時値へ依存する場合。

    Examples:
        >>> env = _create_environment()
        >>> _evaluate_when(env, 'x == 1', {'x': 1})
        True
    """
    #
    # when未指定はAnsibleと同様に実行対象とする。配列指定は全条件を満たす必要が
    # あるため, 単一条件も1要素の配列へそろえて順に評価する。
    #
    if when_value is None:
        return True
    conditions: list[object] = when_value if isinstance(when_value, list) else [when_value]
    condition: object
    for condition in conditions:
        expression: str = str(condition).strip()
        if not expression:
            continue
        if "{{" in expression or "{%" in expression:
            #
            # テンプレート記法を含む旧来のwhen表現は通常の値として描画し,
            # その真偽値を判定する。
            #
            try:
                rendered: Any = _render_value(environment, expression, variables)
                if not bool(rendered):
                    return False
            except UnknownConditionError:
                #
                # 実行時値に依存する条件は真の場合も偽の場合もあり得る。バックアップ
                # 対象を落とさないため, この条件を満たす可能性があるものとして続行する。
                #
                continue
            continue
        #
        # テンプレート記法のない式はJinja2の式評価器を使い, 比較式や論理式を
        # 文字列のまま真と誤判定しないようにする。
        #
        #
        # when式にも正規表現文字列を記載できるため, 通常の描画処理と同じ変換を
        # 適用してから式評価器を生成する。
        #
        normalized_expression: str = _escape_invalid_jinja_string_sequences(
            "{{ " + expression + " }}"
        )[3:-3]
        evaluator: Any = environment.compile_expression(
            normalized_expression,
            undefined_to_none=False,
        )
        try:
            result: Any = evaluator(**dict(variables))
            if not bool(result):
                return False
        except UnknownConditionError:
            continue
    return True


def _resolve_loop_values(
    environment: NativeEnvironment,
    task: Mapping[str, Any],
    variables: Mapping[str, Any],
) -> list[Any]:
    """loop又はwith_itemsを静的に展開する。

    Args:
        environment (NativeEnvironment): Jinja2評価環境。
        task (Mapping[str, Any]): タスク定義。
        variables (Mapping[str, Any]): 評価用変数集合。

    Returns:
        list[Any]: ループ要素一覧。ループなしは専用値1件。

    Raises:
        UnresolvedValueError: ループ値が配列に解決できない場合。

    Examples:
        >>> env = _create_environment()
        >>> _resolve_loop_values(env, {'loop': '{{ xs }}'}, {'xs': [1, 2]})
        [1, 2]
    """
    #
    # loopを優先し, 未指定時だけwith_itemsを参照する。両方がない場合は専用値を
    # 1件返して通常タスクを1回処理する。
    #
    loop_value: object = task.get("loop", task.get("with_items", _NO_LOOP))
    if loop_value is _NO_LOOP:
        return [_NO_LOOP]
    rendered: Any = _render_value(environment, loop_value, variables)
    #
    # Jinja2の評価結果がtupleになる場合もAnsibleの反復対象として扱えるように,
    # 後段で共通利用するlistへ変換する。
    #
    if isinstance(rendered, tuple):
        return list(rendered)
    if isinstance(rendered, list):
        return rendered
    if isinstance(rendered, UnknownValue):
        #
        # 実行時に決まる反復列は空と決め付けず, 象徴的な1要素として後続処理へ
        # 渡す。registerの既知構造と静的に確定できる後続タスクを保持するためである。
        #
        return [rendered]
    raise UnresolvedValueError(f"Loop value is not a list: {rendered!r}")


def _loop_variable_name(task: Mapping[str, Any]) -> str:
    """loop_control.var指定を考慮してループ変数名を返す。

    Args:
        task (Mapping[str, Any]): タスク定義。

    Returns:
        str: ループ変数名。

    Examples:
        >>> _loop_variable_name({})
        'item'
    """
    #
    # loop_controlが辞書でない不正な入力では既定のitemを使用する。辞書の場合は
    # 利用者が指定したloop_varを優先する。
    #
    loop_control_value: object = task.get("loop_control", {})
    if not isinstance(loop_control_value, dict):
        return "item"
    loop_control: dict[str, Any] = cast(dict[str, Any], loop_control_value)
    return str(loop_control.get("loop_var", "item"))


def _host_pattern_to_string(value: object) -> str:
    """Playのhosts値をansibleコマンドへ渡す文字列へ変換する。

    Args:
        value (object): YAML上のhosts値。

    Returns:
        str: Ansibleホストパターン。

    Examples:
        >>> _host_pattern_to_string(['a', 'b'])
        'a:b'
    """
    #
    # YAML配列で複数ホストパターンが指定された場合は, Ansibleが解釈できる
    # コロン区切りへ変換する。単一値は文字列表現をそのまま使用する。
    #
    if isinstance(value, list):
        return ":".join(str(item) for item in value)
    return str(value)


def _build_ansible_version_mapping(version_string: str) -> dict[str, Any]:
    """Ansible版数文字列からansible_version組み込み変数を作る。

    Args:
        version_string (str): 実行中のAnsible版数文字列。

    Returns:
        dict[str, Any]: full, string, major, minor, revisionを持つ版数辞書。

    Examples:
        >>> mapping = _build_ansible_version_mapping("2.16.3")
        >>> (mapping["major"], mapping["minor"], mapping["revision"])
        (2, 16, 3)
        >>> _build_ansible_version_mapping("2.17.0rc1")["revision"]
        0
    """
    numeric_parts: list[int] = []
    raw_part: str
    for raw_part in version_string.split(".")[:3]:
        digit_characters: list[str] = []
        character: str
        for character in raw_part:
            if not character.isdigit():
                break
            digit_characters.append(character)
        numeric_parts.append(int("".join(digit_characters) or "0"))
    while len(numeric_parts) < 3:
        numeric_parts.append(0)
    return {
        "full": version_string,
        "string": version_string,
        "major": numeric_parts[0],
        "minor": numeric_parts[1],
        "revision": numeric_parts[2],
    }


def _run_command(
    command: Sequence[str],
    settings: RuntimeSettings,
) -> subprocess.CompletedProcess[str]:
    """外部コマンドをタイムアウト付きで実行し一時障害時に再試行する。

    Args:
        command (Sequence[str]): 実行する引数配列。
        settings (RuntimeSettings): タイムアウトと再試行設定。

    Returns:
        subprocess.CompletedProcess[str]: 正常終了した実行結果。

    Raises:
        AuditError: 全試行が失敗する場合。

    Examples:
        >>> True
        True
    """
    #
    # 初回実行を含めてretries + 1回まで試行する。最後に報告できるように,
    # 例外又は異常終了時のメッセージを各試行で更新する。
    #
    attempt: int
    last_error: str = ""
    for attempt in range(settings.retries + 1):
        try:
            #
            # 引数配列のまま実行してシェル展開を避け, 標準出力と標準エラー出力を
            # 文字列として回収する。タイムアウトにより永久停止を防ぐ。
            #
            result: subprocess.CompletedProcess[str] = subprocess.run(
                list(command),
                check=False,
                capture_output=True,
                text=True,
                timeout=settings.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            #
            # コマンド起動失敗と時間切れは再試行可能な失敗として同じ経路で扱う。
            #
            last_error = str(exc)
        else:
            if result.returncode == 0:
                return result
            #
            # 異常終了時は標準エラー出力を優先し, 空の場合だけ標準出力を診断へ使う。
            #
            last_error = result.stderr.strip() or result.stdout.strip()
        if attempt < settings.retries:
            #
            # 最終試行の後には待機せず, 次の試行がある場合だけ指定された間隔を空ける。
            #
            time.sleep(settings.retry_interval_seconds)
    raise AuditError(
        f"Command failed after retries: {' '.join(command)}: {last_error}"
    )


def _runtime_settings_from_environment() -> RuntimeSettings:
    """環境変数から外部コマンド実行設定を読み込む。

    Returns:
        RuntimeSettings: 検証済み設定値。

    Raises:
        AuditError: 数値が不正又は許容範囲外の場合。

    Examples:
        >>> settings = _runtime_settings_from_environment()
        >>> settings.timeout_seconds > 0
        True
    """
    try:
        #
        # 環境変数が未設定の場合は既定値を文字列として取得し, 利用時の数値型へ
        # 明示的に変換する。
        #
        timeout_seconds: float = float(
            os.environ.get(
                "ANSIBLE_BACKUP_AUDIT_TIMEOUT",
                str(DEFAULT_TIMEOUT_SECONDS),
            )
        )
        retries: int = int(
            os.environ.get(
                "ANSIBLE_BACKUP_AUDIT_RETRIES",
                str(DEFAULT_RETRIES),
            )
        )
        retry_interval_seconds: float = float(
            os.environ.get(
                "ANSIBLE_BACKUP_AUDIT_RETRY_INTERVAL",
                str(DEFAULT_RETRY_INTERVAL_SECONDS),
            )
        )
    except ValueError as exc:
        raise AuditError("Runtime control environment variable must be numeric") from exc
    #
    # タイムアウトは正数, 再試行回数と待機時間は0以上に制限し, subprocessや
    # rangeへ不適切な値が渡る前に利用者へ設定誤りを通知する。
    #
    if timeout_seconds <= 0.0:
        raise AuditError("ANSIBLE_BACKUP_AUDIT_TIMEOUT must be greater than zero")
    if retries < 0:
        raise AuditError("ANSIBLE_BACKUP_AUDIT_RETRIES must be zero or greater")
    if retry_interval_seconds < 0.0:
        raise AuditError("ANSIBLE_BACKUP_AUDIT_RETRY_INTERVAL must be zero or greater")
    return RuntimeSettings(timeout_seconds, retries, retry_interval_seconds)


def _build_argument_parser() -> argparse.ArgumentParser:
    """コマンドライン引数解析器を生成する。

    Returns:
        argparse.ArgumentParser: 引数解析器。

    Examples:
        >>> parser = _build_argument_parser()
        >>> parser.parse_args(['site.yml']).playbook
        'site.yml'
    """
    #
    # 必須のPlaybookを位置引数とし, インベントリ, ホスト絞り込み, ロール絞り込み,
    # 詳細表示を任意指定として公開する。
    #
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="ansible-backup-audit",
        description=(
            "Extract files explicitly managed on Ansible target hosts and output CSV."
        ),
    )
    parser.add_argument("playbook", help="Ansible playbook to analyze")
    parser.add_argument(
        "-i",
        "--inventory",
        default=DEFAULT_INVENTORY,
        help=f"Inventory source (default: {DEFAULT_INVENTORY})",
    )
    parser.add_argument(
        "-l",
        "--limit",
        default=None,
        help="Limit selected hosts using an Ansible host pattern",
    )
    parser.add_argument(
        "-r",
        "--role",
        action="append",
        default=[],
        help="Analyze only the specified role; may be repeated",
    )
    #
    # verboseは未解決タスクを検出時点でも表示するための真偽値として扱う。
    #
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Write detailed diagnostics to stderr",
    )
    return parser


def _write_csv(records: Iterable[AuditRecord]) -> None:
    """監査対象を標準出力へCSV形式で出力する。

    Args:
        records (Iterable[AuditRecord]): 出力対象。

    Examples:
        >>> True
        True
    """
    #
    # 標準出力だけを別ファイルへ転送しても正しいCSVとなるように, 診断出力とは
    # 分離し, 見出しを必ず最初の1行として出力する。
    #
    writer: csv.writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(["HOST", "ROLE", "OP", "PATH"])
    record: AuditRecord
    for record in records:
        writer.writerow([record.host, record.role, record.operation, record.path])


def main(argv: Sequence[str] | None = None) -> int:
    """コマンドライン入力を解析し監査対象CSVを標準出力へ生成する。

    Args:
        argv (Sequence[str] | None): テスト時に差し替える引数列。

    Returns:
        int: 正常終了時0, 入力不正時1, 未解決値あり時2, 解析失敗時3。

    Examples:
        >>> callable(main)
        True
    """
    #
    # コマンドライン入力を解析して絶対パスへ変換し, 実行場所に依存しない形で
    # 後続処理へ渡す。
    #
    parser: argparse.ArgumentParser = _build_argument_parser()
    args: argparse.Namespace = parser.parse_args(argv)
    playbook_path: Path = Path(args.playbook).resolve()
    inventory_path: Path = Path(args.inventory).resolve()
    #
    # 必須入力の不足は解析開始前に検出し, 入力エラー専用の終了コードを返す。
    # インベントリはディレクトリや動的な参照元も許すためexistsで確認する。
    #
    if not playbook_path.is_file():
        print(f"Playbook file is missing: {playbook_path}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    if not inventory_path.exists():
        print(f"Inventory source is missing: {inventory_path}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    repository_root: Path = playbook_path.parent
    #
    # --roleは複数回指定できるため集合へ変換し, ロール選択時の重複と探索時間を
    # 抑える。未指定の空集合は全ロールを対象とする意味で使用する。
    #
    selected_roles: set[str] = {str(role_name) for role_name in cast(list[str], args.role)}
    try:
        #
        # 外部コマンド制御値を検証してAnalyzerを構築し, 入力Playbookの解析を開始する。
        # 解析を継続できないエラーは共通の終了コードと診断へ変換する。
        #
        runtime_settings: RuntimeSettings = _runtime_settings_from_environment()
        analyzer: Analyzer = Analyzer(
            repository_root=repository_root,
            inventory_path=inventory_path,
            limit_pattern=cast(str | None, args.limit),
            selected_roles=selected_roles,
            runtime_settings=runtime_settings,
            verbose=bool(args.verbose),
        )
        records: list[AuditRecord] = analyzer.analyze(playbook_path)
    except AuditError as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        return EXIT_PARSE_ERROR

    #
    # 静的に解決できたレコードは未解決タスクの有無にかかわらず出力し, 利用可能な
    # 監査結果を失わない。未解決が残る場合は専用終了コードで完全ではないと示す。
    #
    _write_csv(records)
    if analyzer.unresolved_messages:
        message: str
        for message in analyzer.unresolved_messages:
            print(message, file=sys.stderr)
        return EXIT_UNRESOLVED
    return EXIT_OK


if __name__ == "__main__":
    #
    # import時には実行せず, コマンドとして起動された場合だけmainの終了コードを
    # プロセスへ返す。
    #
    raise SystemExit(main())
