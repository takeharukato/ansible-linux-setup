#!/usr/bin/env python3
# -*- mode: python; coding: utf-8; line-endings: unix -*-

"""ansible_backup_auditの回帰テスト。
実行方法:

    $ python3 -m unittest tools/audit-output-files/test_ansible_backup_audit.py
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
from types import ModuleType
from typing import Any, cast
import unittest
import warnings
from unittest.mock import patch


MODULE_PATH: Path = Path(__file__).with_name("ansible_backup_audit.py")


def _load_target_module() -> ModuleType:
    """テスト対象を実ファイルから読み込む。

    Returns:
        ModuleType: 読み込み済みの監査スクリプト。

    Raises:
        RuntimeError: モジュール仕様又はローダーを生成できない場合。
    """
    specification: Any = importlib.util.spec_from_file_location(
        "ansible_backup_audit",
        MODULE_PATH,
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Failed to load test target: {MODULE_PATH}")
    module: ModuleType = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


TARGET: ModuleType = _load_target_module()


class StageSevenRegressionTests(unittest.TestCase):
    """第7段階までに修正した解析動作を検証する。"""

    def setUp(self) -> None:
        """各テスト専用のAnalyzerとJinja2環境を生成する。"""
        analyzer_class: Any = getattr(TARGET, "Analyzer")
        self.analyzer: Any = analyzer_class.__new__(analyzer_class)
        self.analyzer.environment = TARGET._create_environment()
        self.analyzer._warning_messages = set()
        self.analyzer.host_passwd_facts = {}
        self.analyzer.shared_hostvars = {"localhost": {}}
        self.analyzer.runtime_hostvars = {"localhost": {}}
        self.analyzer.repository_root = MODULE_PATH.parent
        self.analyzer.selected_roles = set()
        self.analyzer._role_stack = []
        self.analyzer._task_file_stack = []

    def test_deb822_name_is_combined_with_standard_directory(self) -> None:
        """deb822の論理名から標準配置先を生成できることを確認する。"""
        records: list[tuple[str, str]] = self.analyzer._extract_paths(
            "ansible.builtin.deb822_repository",
            {"name": "Docker"},
            {},
        )
        self.assertEqual(
            records,
            [("create_or_modify", "/etc/apt/sources.list.d/Docker.sources")],
        )

    def test_apt_filename_keeps_existing_extension(self) -> None:
        """aptの論理名へ.listを重複付加しないことを確認する。"""
        records: list[tuple[str, str]] = self.analyzer._extract_paths(
            "ansible.builtin.apt_repository",
            {"filename": "vendor.list"},
            {},
        )
        self.assertEqual(
            records,
            [("create_or_modify", "/etc/apt/sources.list.d/vendor.list")],
        )

    def test_logical_name_rejects_directory_component(self) -> None:
        """論理名を使った標準配置先からの逸脱を拒否することを確認する。"""
        error_class: type[Exception] = cast(
            type[Exception],
            TARGET.UnresolvedValueError,
        )
        with self.assertRaisesRegex(error_class, "not a file name"):
            self.analyzer._render_required_name(
                {"name": "../Docker"},
                ("name",),
                {},
            )

    def test_env_lookup_returns_allowed_controller_value(self) -> None:
        """許可した制御ノード環境変数だけを取得できることを確認する。"""
        with patch.dict(os.environ, {"HOME": "/home/controller"}, clear=True):
            resolved: str = TARGET._audit_lookup("env", "HOME")
        self.assertEqual(resolved, "/home/controller")

    def test_env_lookup_uses_explicit_default(self) -> None:
        """許可変数が未設定の場合にdefaultを返すことを確認する。"""
        with patch.dict(os.environ, {}, clear=True):
            resolved: str = TARGET._audit_lookup("env", "USER", default="ansible")
        self.assertEqual(resolved, "ansible")

    def test_env_lookup_rejects_unapproved_variable(self) -> None:
        """秘密情報になり得る任意環境変数の参照を拒否することを確認する。"""
        error_class: type[Exception] = cast(
            type[Exception],
            TARGET.UnresolvedValueError,
        )
        with self.assertRaisesRegex(error_class, "not allowed"):
            TARGET._audit_lookup("env", "API_TOKEN")

    def test_assert_registers_successful_result(self) -> None:
        """成功したassertのregister値をfailedテストへ渡せることを確認する。"""
        persistent_variables: dict[str, Any] = {}
        self.analyzer._process_assert(
            {"register": "validation_result"},
            {"that": ["major == 1", "minor == 31"]},
            {"major": 1, "minor": 31},
            persistent_variables,
        )
        self.assertEqual(
            persistent_variables["validation_result"],
            {"changed": False, "failed": False},
        )
        is_failed: bool = TARGET._evaluate_when(
            self.analyzer.environment,
            "validation_result is failed",
            persistent_variables,
        )
        self.assertFalse(is_failed)

    def test_assert_registers_failed_result(self) -> None:
        """失敗したassertのregister値にfailed=Trueを設定することを確認する。"""
        persistent_variables: dict[str, Any] = {}
        self.analyzer._process_assert(
            {"register": "validation_result"},
            {"that": "major == 1"},
            {"major": 2},
            persistent_variables,
        )
        self.assertTrue(persistent_variables["validation_result"]["failed"])

    def test_empty_leading_path_expression_is_rejected(self) -> None:
        """空の基点変数からルート直下の誤パスを生成しないことを確認する。"""
        error_class: type[Exception] = cast(
            type[Exception],
            TARGET.UnresolvedValueError,
        )
        with self.assertRaisesRegex(error_class, "empty value"):
            self.analyzer._render_required_path(
                {"path": "{{ operator_home }}/.kube/config"},
                ("path",),
                {"operator_home": ""},
            )

    def test_default_filter_can_supply_leading_path_expression(self) -> None:
        """defaultで補完された有効な基点は拒否しないことを確認する。"""
        path_value: str = self.analyzer._render_required_path(
            {"path": "{{ operator_home | default('/tmp', true) }}/result"},
            ("path",),
            {"operator_home": ""},
        )
        self.assertEqual(path_value, "/tmp/result")

    def test_play_magic_variables_contain_selected_hosts(self) -> None:
        """Play単位のマジック変数へ選択済みホストを設定することを確認する。"""
        self.analyzer.inventory_vars = {"host1": {}}
        self.analyzer.host_facts = {"host1": {}}
        self.analyzer.inventory_groups = {"all": ["host1", "host2"]}
        self.analyzer.host_group_names = {"host1": ["workers"]}
        self.analyzer.shared_hostvars = {"host1": {}, "host2": {}, "localhost": {}}
        variables: dict[str, Any] = self.analyzer._build_host_variables(
            "host1",
            {},
            ["host1", "host2"],
        )
        self.assertEqual(
            variables["ansible_play_hosts_all"],
            ["host1", "host2"],
        )
        self.assertEqual(variables["ansible_play_hosts"], ["host1", "host2"])
        self.assertEqual(variables["ansible_play_batch"], ["host1", "host2"])

    def test_fileglob_returns_sorted_list_without_command_execution(self) -> None:
        """fileglobが一致ファイルを並べ替えて返すことを確認する。"""
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory_path: Path = Path(temporary_directory)
            (directory_path / "b.repo").touch()
            (directory_path / "a.repo").touch()
            lookup_result: Any = TARGET._audit_lookup(
                "ansible.builtin.fileglob",
                str(directory_path / "*.repo"),
                wantlist=True,
            )
        self.assertEqual(
            lookup_result,
            [
                str(directory_path / "a.repo"),
                str(directory_path / "b.repo"),
            ],
        )

    def test_first_found_uses_role_tasks_directory(self) -> None:
        """first_foundが現在ロールのtasksディレクトリを探索することを確認する。"""
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_root: Path = Path(temporary_directory)
            tasks_directory: Path = repository_root / "roles" / "repo" / "tasks"
            tasks_directory.mkdir(parents=True)
            current_file: Path = tasks_directory / "main.yml"
            found_file: Path = tasks_directory / "redhat.yml"
            current_file.touch()
            found_file.touch()
            lookup_result: Any = TARGET._audit_lookup(
                "ansible.builtin.first_found",
                {"files": ["redhat.yml"], "paths": ["tasks"]},
                repository_root=repository_root,
                current_file=current_file,
            )
        self.assertEqual(lookup_result, str(found_file.resolve()))

    def test_pipe_lookup_rejects_arbitrary_command(self) -> None:
        """pipe lookupが許可外コマンドを実行前に拒否することを確認する。"""
        error_class: type[Exception] = cast(
            type[Exception],
            TARGET.UnresolvedValueError,
        )
        with self.assertRaisesRegex(error_class, "permits only"):
            TARGET._audit_lookup("pipe", "uname -a")

    def test_unknown_condition_is_conservatively_included(self) -> None:
        """未知条件のタスクを監査候補から除外しないことを確認する。"""
        unknown_value: Any = TARGET.UnknownValue("stat.exists")
        condition_result: bool = TARGET._evaluate_when(
            self.analyzer.environment,
            "runtime_value",
            {"runtime_value": unknown_value},
        )
        self.assertTrue(condition_result)
        negative_condition_result: bool = TARGET._evaluate_when(
            self.analyzer.environment,
            "not runtime_value",
            {"runtime_value": unknown_value},
        )
        self.assertTrue(negative_condition_result)

    def test_generic_module_is_detected_for_register_processing(self) -> None:
        """監査対象外モジュールもregister処理用に検出することを確認する。"""
        module_name: str | None = TARGET._find_module_name(
            {"name": "stat file", "ansible.builtin.stat": {"path": "/etc/x"}}
        )
        self.assertEqual(module_name, "ansible.builtin.stat")

    def test_stat_register_contains_unknown_stat_mapping(self) -> None:
        """statのregister値が辞書属性参照に耐えることを確認する。"""
        result: Any = self.analyzer._build_register_result(
            "host1",
            "ansible.builtin.stat",
            {"path": "/etc/example"},
            {},
        )
        self.assertIsInstance(result["stat"], TARGET.UnknownMapping)
        with self.assertRaises(TARGET.UnknownConditionError):
            bool(result["stat"]["exists"])

    def test_getent_register_uses_collected_passwd_fact(self) -> None:
        """getentのregister値へ実測したpasswd情報を反映することを確認する。"""
        self.analyzer.host_passwd_facts = {
            "host1": {"kube": ["x", "1000", "1000", "", "/home/kube", "/bin/bash"]}
        }
        result: Any = self.analyzer._build_register_result(
            "host1",
            "ansible.builtin.getent",
            {"database": "passwd", "key": "kube"},
            {},
        )
        passwd_entry: list[str] = result["ansible_facts"]["getent_passwd"]["kube"]
        self.assertEqual(passwd_entry[4], "/home/kube")

    def test_getent_register_resolves_operator_home_path(self) -> None:
        """getent結果から空基点ではないオペレータホームを生成することを確認する。"""
        self.analyzer.host_passwd_facts = {
            "host1": {"kube": ["x", "1000", "1000", "", "/home/kube", "/bin/bash"]}
        }
        getent_result: Any = self.analyzer._build_register_result(
            "host1",
            "ansible.builtin.getent",
            {"database": "passwd", "key": "kube"},
            {},
        )
        task_variables: dict[str, Any] = {
            "k8s_operator_user": "kube",
            "operator_getent": getent_result,
        }
        persistent_variables: dict[str, Any] = dict(task_variables)
        self.analyzer._process_set_fact(
            {
                "k8s_operator_home": (
                    "{{ operator_getent.ansible_facts.getent_passwd"
                    "[k8s_operator_user][4] }}"
                )
            },
            task_variables,
            persistent_variables,
        )
        resolved_path: str = self.analyzer._render_required_path(
            {"path": "{{ k8s_operator_home }}/.kube/config"},
            ("path",),
            persistent_variables,
        )
        self.assertEqual(resolved_path, "/home/kube/.kube/config")

    def test_skipped_loop_still_defines_register_results(self) -> None:
        """全反復がskipされた場合もregister.resultsを定義することを確認する。"""
        persistent_variables: dict[str, Any] = {}
        self.analyzer._store_skipped_register_result(
            "host1",
            {"register": "user_results", "loop": ["alice"]},
            "ansible.builtin.user",
            persistent_variables,
            {"item": "alice"},
        )
        results: list[Any] = persistent_variables["user_results"]["results"]
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["skipped"])

    def test_delegate_facts_targets_localhost_mapping(self) -> None:
        """localhostへ委譲したset_factを共有hostvarsへ保存することを確認する。"""
        task: dict[str, Any] = {
            "delegate_to": "localhost",
            "delegate_facts": True,
        }
        module_args: dict[str, Any] = {
            "cache_dir": "/home/controller/.ansible/cache"
        }
        current_variables: dict[str, Any] = {
            "hostvars": self.analyzer.shared_hostvars,
        }
        fact_target: dict[str, Any] = self.analyzer._resolve_fact_target(
            "host1",
            task,
            current_variables,
            current_variables,
        )
        self.analyzer._process_set_fact(
            module_args,
            current_variables,
            fact_target,
        )
        self.analyzer._sync_fact_values(
            "host1",
            task,
            module_args,
            fact_target,
            current_variables,
        )
        self.assertEqual(
            self.analyzer.shared_hostvars["localhost"]["cache_dir"],
            "/home/controller/.ansible/cache",
        )
        self.assertEqual(
            self.analyzer.runtime_hostvars["localhost"]["cache_dir"],
            "/home/controller/.ansible/cache",
        )

    def test_unknown_string_is_not_a_jinja_expression(self) -> None:
        """未知値の診断表現をJinja2式として再解析しないことを確認する。"""
        unknown_text: str = str(TARGET.UnknownValue("register:command.stdout"))
        self.assertEqual(unknown_text, "<unknown:register:command.stdout>")
        self.assertNotIn("{{", unknown_text)

    def test_unknown_arithmetic_remains_unknown(self) -> None:
        """未知値を含む加算で型エラーを起こさず未知値を伝播することを確認する。"""
        unknown_value: Any = TARGET.UnknownValue("register:find.files")
        added_value: Any = ["known"] + unknown_value
        self.assertIsInstance(added_value, TARGET.UnknownValue)

    def test_empty_path_base_is_deferred_until_home_is_resolved(self) -> None:
        """空ホームを含む派生パスを先行してルート直下へ確定しないことを確認する。"""
        variables: dict[str, Any] = {
            "operator_home": "",
            "output_dir": "{{ operator_home }}/.kube",
        }
        unresolved: dict[str, Any] = TARGET._resolve_variable_map(
            self.analyzer.environment,
            variables,
        )
        self.assertEqual(unresolved["output_dir"], "{{ operator_home }}/.kube")
        unresolved["operator_home"] = "/home/kube"
        resolved: dict[str, Any] = TARGET._resolve_variable_map(
            self.analyzer.environment,
            unresolved,
        )
        self.assertEqual(resolved["output_dir"], "/home/kube/.kube")

    def test_simple_sequence_elements_are_recursively_rendered(self) -> None:
        """配列内に残るJinja2式を実際の値へ再帰評価することを確認する。"""
        variables: dict[str, Any] = {
            "ansible_user": "ansible",
            "users": ["{{ ansible_user }}", "kube"],
        }
        resolved: dict[str, Any] = TARGET._resolve_variable_map(
            self.analyzer.environment,
            variables,
        )
        self.assertEqual(resolved["users"], ["ansible", "kube"])

    def test_generator_filters_can_be_added_as_lists(self) -> None:
        """map等の遅延結果を配列化して加算可能にすることを確認する。"""
        rendered: Any = TARGET._render_value(
            self.analyzer.environment,
            "{{ (values | map('string')) + (values | map('string')) }}",
            {"values": [1, 2]},
        )
        self.assertEqual(rendered, ["1", "2", "1", "2"])

    def test_find_register_exposes_symbolic_file_list(self) -> None:
        """findの実行時一致ファイルを検索条件のglobで保持することを確認する。"""
        result: Any = self.analyzer._build_register_result(
            "host1",
            "ansible.builtin.find",
            {"paths": ["/srv/packages"], "patterns": ["*.deb", "*.rpm"]},
            {},
        )
        files: list[Any] = result["files"]
        self.assertEqual(
            [item["path"] for item in files],
            ["/srv/packages/*.deb", "/srv/packages/*.rpm"],
        )

    def test_stat_register_keeps_known_path_and_unknown_state(self) -> None:
        """stat結果が既知パスと未知の存在状態を保持することを確認する。"""
        result: Any = self.analyzer._build_register_result(
            "host1",
            "ansible.builtin.stat",
            {"path": "{{ item }}"},
            {"item": "/etc/example.conf"},
        )
        self.assertEqual(result["stat"]["path"], "/etc/example.conf")
        self.assertIsInstance(result["stat"]["exists"], TARGET.UnknownValue)

    def test_fallback_loop_register_keeps_stat_result_shape(self) -> None:
        """解析失敗時もループ付きstatの結果構造を後続タスクへ残すことを確認する。"""
        self.analyzer.shared_hostvars = {"host1": {}}
        variables: dict[str, Any] = {}
        unknown_item: Any = TARGET.UnknownValue("runtime.stat.path")
        task: dict[str, Any] = {
            "ansible.builtin.stat": {"path": "/etc/example.conf"},
            "loop": "{{ runtime_paths }}",
            "register": "stat_results",
        }
        self.analyzer._store_fallback_register_result(
            "host1",
            task,
            "ansible.builtin.stat",
            variables,
            {"item": unknown_item},
        )
        registered: Any = variables["stat_results"]
        self.assertEqual(
            registered["results"][0]["stat"]["path"],
            "/etc/example.conf",
        )
        self.assertIs(registered["results"][0]["item"], unknown_item)

    def test_explicit_string_filter_keeps_numeric_text_as_string(self) -> None:
        """stringとtrimを通した版数文字列を浮動小数に戻さないことを確認する。"""
        rendered: Any = TARGET._render_value(
            self.analyzer.environment,
            "{{ version | string | trim }}",
            {"version": "1.25"},
        )
        self.assertEqual(rendered, "1.25")
        self.assertIsInstance(rendered, str)

    def test_later_integer_filter_keeps_integer_result(self) -> None:
        """string後のintによる明示的な整数変換を文字列へ戻さないことを確認する。"""
        rendered: Any = TARGET._render_value(
            self.analyzer.environment,
            "{{ version | string | int }}",
            {"version": "25"},
        )
        self.assertEqual(rendered, 25)
        self.assertIsInstance(rendered, int)

    def test_unknown_loop_uses_one_symbolic_iteration(self) -> None:
        """未知の反復列が後続解析用の象徴要素1件になることを確認する。"""
        unknown_value: Any = TARGET.UnknownValue("register:command.stdout")
        values: list[Any] = TARGET._resolve_loop_values(
            self.analyzer.environment,
            {"loop": "{{ runtime_items }}"},
            {"runtime_items": unknown_value},
        )
        self.assertEqual(len(values), 1)
        self.assertIs(values[0], unknown_value)

    def test_runtime_fact_overrides_later_role_vars(self) -> None:
        """先行ロールのset_fact相当値が後続ロール変数より優先されることを確認する。"""
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_root: Path = Path(temporary_directory)
            role_path: Path = repository_root / "roles" / "next-role"
            (role_path / "tasks").mkdir(parents=True)
            (role_path / "vars").mkdir(parents=True)
            (role_path / "tasks" / "main.yml").write_text("---\n[]\n", encoding="utf-8")
            (role_path / "vars" / "main.yml").write_text(
                "shared_path: /from-role-vars\n",
                encoding="utf-8",
            )
            self.analyzer.repository_root = repository_root
            self.analyzer.runtime_hostvars = {
                "host1": {"shared_path": "/from-set-fact"}
            }
            with patch.object(self.analyzer, "_process_task_file") as process_file:
                self.analyzer._analyze_role(
                    "host1",
                    "next-role",
                    {},
                    "main",
                )
            analyzed_variables: dict[str, Any] = process_file.call_args.args[3]
            self.assertEqual(analyzed_variables["shared_path"], "/from-set-fact")

    def test_task_vars_are_resolved_iteratively(self) -> None:
        """同一タスクのvars内にある変数依存を反復解決することを確認する。"""
        task: dict[str, Any] = {
            "ansible.builtin.debug": {"msg": "{{ combined }}"},
            "vars": {
                "base_items": ["a"],
                "combined": "{{ base_items + ['b'] }}",
            },
        }
        with patch.object(self.analyzer, "_process_module") as process_module:
            self.analyzer._process_task_body(
                "host1",
                "sample-role",
                MODULE_PATH,
                task,
                {},
            )
        task_variables: dict[str, Any] = process_module.call_args.args[7]
        self.assertEqual(task_variables["combined"], ["a", "b"])

    def test_task_vars_can_defer_reference_to_own_register(self) -> None:
        """タスク自身のregister参照を保留してモジュール処理を継続することを確認する。"""
        task: dict[str, Any] = {
            "ansible.builtin.command": {"argv": ["example", "status"]},
            "register": "status_result",
            "vars": {
                "status_json": "{{ status_result.stdout | default('') }}",
            },
        }
        with patch.object(self.analyzer, "_process_module") as process_module:
            self.analyzer._process_task_body(
                "host1",
                "sample-role",
                MODULE_PATH,
                task,
                {},
            )
        self.assertTrue(process_module.called)

    def test_looped_set_fact_uses_previous_iteration_value(self) -> None:
        """ループ付きset_factが直前反復の累積値を参照することを確認する。"""
        variables: dict[str, Any] = {"accumulated_users": []}
        self.analyzer._process_task_body(
            "host1",
            "sample-role",
            MODULE_PATH,
            {
                "ansible.builtin.set_fact": {
                    "accumulated_users": "{{ accumulated_users + [item] }}",
                },
                "loop": ["alice", "kube"],
            },
            variables,
        )
        self.assertEqual(variables["accumulated_users"], ["alice", "kube"])

    def test_nested_line_metadata_is_removed_from_task_vars(self) -> None:
        """タスク変数の入れ子から内部行番号を再帰的に除去することを確認する。"""
        task: dict[str, Any] = {
            "ansible.builtin.debug": {"msg": "unused"},
            "vars": {
                "__line__": 10,
                "package_policy": {
                    "__line__": 11,
                    "body": {
                        "__line__": 12,
                        "inputs": {
                            "__line__": 13,
                            "system-logfile": {"__line__": 14, "enabled": False},
                        },
                    },
                },
            },
        }
        with patch.object(self.analyzer, "_process_module") as process_module:
            self.analyzer._process_task_body(
                "host1",
                "sample-role",
                MODULE_PATH,
                task,
                {},
            )
        task_variables: dict[str, Any] = process_module.call_args.args[7]
        self.assertEqual(
            task_variables["package_policy"],
            {
                "body": {
                    "inputs": {
                        "system-logfile": {"enabled": False},
                    },
                },
            },
        )

    def test_tempfile_register_uses_same_runtime_glob_for_directory(self) -> None:
        """tempfileのディレクトリ結果にも後続参照用globを保持することを確認する。"""
        result: Any = self.analyzer._build_register_result(
            "host1",
            "ansible.builtin.tempfile",
            {"state": "directory", "path": "/tmp", "prefix": "merge-"},
            {},
        )
        self.assertEqual(result["path"], "/tmp/merge-*")

    def test_getent_supplements_known_operator_home(self) -> None:
        """取得済みpasswdにない対象ユーザーを既知ホームで補完することを確認する。"""
        result: Any = self.analyzer._build_register_result(
            "host1",
            "ansible.builtin.getent",
            {"database": "passwd", "key": "kube"},
            {
                "k8s_operator_user": "kube",
                "k8s_operator_home": "/srv/kube",
            },
        )
        passwd_entry: list[Any] = result["ansible_facts"]["getent_passwd"]["kube"]
        self.assertEqual(passwd_entry[4], "/srv/kube")

    def test_getent_does_not_guess_unresolved_operator_home(self) -> None:
        """絶対パスが判明しないホームを推測しないことを確認する。"""
        result: Any = self.analyzer._build_register_result(
            "host1",
            "ansible.builtin.getent",
            {"database": "passwd", "key": "kube"},
            {"k8s_operator_user": "kube", "k8s_operator_home": ""},
        )
        passwd_mapping: dict[str, Any] = result["ansible_facts"]["getent_passwd"]
        self.assertNotIn("kube", passwd_mapping)

    def test_empty_loop_defines_empty_register_results(self) -> None:
        """反復対象が0件でもregisterに空のresultsを保存することを確認する。"""
        self.analyzer.shared_hostvars["host1"] = {}
        self.analyzer.runtime_hostvars["host1"] = {}
        variables: dict[str, Any] = {}
        self.analyzer._process_task_body(
            "host1",
            "sample-role",
            MODULE_PATH,
            {
                "ansible.builtin.debug": {"msg": "unused"},
                "loop": [],
                "register": "empty_result",
            },
            variables,
        )
        self.assertEqual(variables["empty_result"]["results"], [])
        self.assertTrue(variables["empty_result"]["skipped"])

    def test_find_splits_comma_separated_glob_patterns(self) -> None:
        """findの文字列patternsをglobのカンマ区切りで展開することを確認する。"""
        results: list[Any] = self.analyzer._build_find_file_results(
            {
                "paths": ["/etc/network", "/etc/NetworkManager"],
                "patterns": "ifcfg-*,*.nmconnection",
            },
            {},
            "register:find",
        )
        self.assertEqual(
            [item["path"] for item in results],
            [
                "/etc/network/ifcfg-*",
                "/etc/network/*.nmconnection",
                "/etc/NetworkManager/ifcfg-*",
                "/etc/NetworkManager/*.nmconnection",
            ],
        )

    def test_find_keeps_commas_inside_pattern_list_items(self) -> None:
        """findの配列patternsに明示したカンマを分割しないことを確認する。"""
        results: list[Any] = self.analyzer._build_find_file_results(
            {"paths": "/tmp", "patterns": ["report,{old,new}.txt"]},
            {},
            "register:find",
        )
        self.assertEqual(results[0]["path"], "/tmp/report,{old,new}.txt")

    def test_find_replaces_unknown_diagnostic_inside_glob_pattern(self) -> None:
        """findのglobに埋め込まれた未知部分をワイルドカードへ変換することを確認する。"""
        unknown_package: str = str(
            TARGET.UnknownValue("register:shell.stdout")
        )
        results: list[Any] = self.analyzer._build_find_file_results(
            {
                "paths": "/tmp",
                "patterns": f"{unknown_package}_2.1.148-1+frr2_*.deb",
            },
            {},
            "register:find",
        )
        self.assertEqual(
            results[0]["path"],
            "/tmp/*_2.1.148-1+frr2_*.deb",
        )

    def test_find_regex_keeps_unknown_result_unresolved(self) -> None:
        """正規表現検索では未知部分をglobへ変換しないことを確認する。"""
        results: list[Any] = self.analyzer._build_find_file_results(
            {
                "paths": "/tmp",
                "patterns": str(TARGET.UnknownValue("runtime.pattern")),
                "use_regex": True,
            },
            {},
            "register:find",
        )
        self.assertIsInstance(results[0]["path"], TARGET.UnknownValue)

    def test_direct_path_still_rejects_unknown_diagnostic(self) -> None:
        """直接指定パスでは未知値の診断表現を引き続き拒否することを確認する。"""
        error_class: type[Exception] = cast(
            type[Exception],
            TARGET.UnresolvedValueError,
        )
        unknown_name: str = str(TARGET.UnknownValue("register:shell.stdout"))
        with self.assertRaisesRegex(error_class, "Unresolved expression"):
            self.analyzer._render_required_path(
                {"path": f"/tmp/{unknown_name}.deb"},
                ("path",),
                {},
            )

    def test_version_like_text_avoids_invalid_decimal_warning(self) -> None:
        """複数ドットの版数文字列を警告なしで保持することを確認する。"""
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            rendered: Any = TARGET._native_concat_without_backslash_parsing(
                iter(["1.25.11"])
            )
        self.assertEqual(rendered, "1.25.11")
        self.assertEqual(caught_warnings, [])

    def test_valid_numeric_text_still_uses_native_type(self) -> None:
        """有効な単一数値文字列のネイティブ変換を維持することを確認する。"""
        rendered: Any = TARGET._native_concat_without_backslash_parsing(
            iter(["1.25"])
        )
        self.assertEqual(rendered, 1.25)
        self.assertIsInstance(rendered, float)

    def test_service_facts_adds_symbolic_services_mapping(self) -> None:
        """service_facts後にansible_facts.servicesを参照できることを確認する。"""
        persistent_variables: dict[str, Any] = {"ansible_facts": {}}
        self.analyzer._apply_runtime_facts(
            "host1",
            "ansible.builtin.service_facts",
            persistent_variables,
        )
        services: Any = persistent_variables["ansible_facts"]["services"]
        self.assertIsInstance(services, TARGET.UnknownMapping)

    def test_authorized_key_default_path_uses_passwd_home(self) -> None:
        """authorized_keyのpath省略時に実測ホームから既定パスを算出することを確認する。"""
        self.analyzer.host_passwd_facts = {
            "host1": {"alice": ["x", "1000", "1000", "", "/srv/alice", "/bin/bash"]}
        }
        records: list[tuple[str, str]] = self.analyzer._extract_paths(
            "ansible.posix.authorized_key",
            {"user": "alice", "key": "ssh-ed25519 example"},
            {},
            "host1",
        )
        self.assertEqual(
            records,
            [("create_or_modify", "/srv/alice/.ssh/authorized_keys")],
        )
        deleted_records: list[tuple[str, str]] = self.analyzer._extract_paths(
            "ansible.posix.authorized_key",
            {"user": "alice", "state": "absent"},
            {},
            "host1",
        )
        self.assertEqual(
            deleted_records,
            [("delete", "/srv/alice/.ssh/authorized_keys")],
        )


if __name__ == "__main__":
    unittest.main()
