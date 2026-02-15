#!/bin/bash
#
# post-user-create ロール用 emacs-package-el-setting.yml 自動生成スクリプト
#
# このスクリプトは、defaults/main.yml で定義された emacs_optional_settings_files リストから、
# post-user-create/tasks/emacs-package-el-setting.yml を自動生成します。
#
# 元々 roles/user-settings/tasks/gen-emacs-tasks.sh で実行していた処理を
# post-user-create ロール用に改造したものです。
#
# 使用方法:
#   bash generate-emacs-settings.sh [ROLE_DIRECTORY]
#
# 引数:
#   ROLE_DIRECTORY  post-user-create ロールのディレクトリパス
#                   デフォルト: "." (current directory)
#                   例: ".." (親ディレクトリ)
#                       このスクリプトは tasks/ ディレクトリに配置されているため、
#                       role ディレクトリを指定する場合は ".." を使用します。
#

ROLE_PATH="${1:-.}"

if [ ! -d "${ROLE_PATH}" ]; then
    echo "Error: Role directory not found: ${ROLE_PATH}" >&2
    exit 1
fi

DEFAULTS_FILE="${ROLE_PATH}/defaults/main.yml"
OUTPUT_FILE="${ROLE_PATH}/tasks/emacs-package-el-setting.yml"

if [ ! -f "${DEFAULTS_FILE}" ]; then
    echo "Error: defaults/main.yml not found: ${DEFAULTS_FILE}" >&2
    exit 1
fi

# emacs_optional_settings_files リストを抽出
# YAML の配列形式を想定: "  - filename.el"
EMACS_FILES=$(sed -n '/^emacs_optional_settings_files:/,/^[^ ]/p' "${DEFAULTS_FILE}" | \
    grep '^ *- ' | \
    sed 's/^ *- //g' | \
    grep -v '^$' || true)

if [ -z "${EMACS_FILES}" ]; then
    echo "Error: emacs_optional_settings_files not found in ${DEFAULTS_FILE}" >&2
    exit 1
fi

# ファイル行数をカウント
FILE_COUNT=$(echo "${EMACS_FILES}" | wc -l)

# タスクファイルの生成開始
{
    cat << 'HEADER'
#  -*- coding:utf-8 mode:yaml -*-
#  Ansible playbook
#  Copyright 2020 Takeharu KATO All Rights Reserved.
#
#  post-user-create ロール
#  既存ユーザへのEmacs設定ファイル（オプション）配布タスク
#
#  本ファイルは scripts/generate-emacs-settings.sh により自動生成されます
#  emacs_optional_settings_files の定義を更新した場合は、
#  このスクリプトを再実行してください。

# ユーザの ~/.emacs.d/user_settings ディレクトリを作成（存在しない場合）
- name: Create user .emacs.d/user_settings directory
  vars:
    outer_user_name: "{{ outer_item.name | default('', true) }}"
    outer_user_group: "{{ outer_item.group | default(outer_item.name | default('', true), true) }}"
    outer_user_home: "{{ outer_item.home | default('/home/' ~ (outer_item.name | default('', true)), true) }}"
  file:
    path: "{{ outer_user_home }}/.emacs.d/user_settings"
    state: directory
    owner: "{{ outer_user_name }}"
    group: "{{ outer_user_group }}"
    mode: "0755"
  when:
    - ( outer_user_name | length ) > 0

# オプション設定ファイルの配布（テンプレートからユーザホームに直接配置）
HEADER

    # 各ファイルのタスク生成
    while IFS= read -r filename; do
        cat << EOF

# ${filename}
- name: Deploy ${filename} from template to user home
  vars:
    outer_user_name: "{{ outer_item.name | default('', true) }}"
    outer_user_home: "{{ outer_item.home | default('/home/' ~ (outer_item.name | default('', true)), true) }}"
  template:
    src: _emacs_d__${filename}.j2
    dest: "{{ outer_user_home }}/.emacs.d/user_settings/${filename}"
    owner: "{{ outer_user_name }}"
    group: "{{ outer_user_name }}"
    mode: 0644
  when:
    - ( outer_user_name | length ) > 0
EOF
    done <<< "${EMACS_FILES}"

} > "${OUTPUT_FILE}"

echo "Generated: ${OUTPUT_FILE}"
echo "Total tasks: $((FILE_COUNT + 1)) (including Create directory task)"
echo "Emacs files: ${FILE_COUNT}"
