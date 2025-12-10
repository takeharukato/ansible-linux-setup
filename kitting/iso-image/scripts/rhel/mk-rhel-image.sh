#!/usr/bin/env bash
#
# AlmaLinux 9.x のインストール ISO イメージをカスタマイズして
# Kickstart ファイルを組み込み, 無人インストール可能な ISO イメージを作成する。
#
# 実行例:
#  env KS_FILE=ks.cfg ISO_IMAGE=AlmaLinux-9.6-x86_64-dvd.iso ./mk-rhel-image.sh
#  出力: AlmaLinux-9.6-x86_64-dvd-ks.iso
# 注意: 既存のファイルは上書きされます。

set -euo pipefail

ISO_BASE_NAME=${ISO_BASE_NAME:-"AlmaLinux-9.6-x86_64-dvd"}
ISO_IMAGE=${ISO_IMAGE:-"${ISO_BASE_NAME}.iso"}
KS_FILE=${KS_FILE:-"ks.cfg"}
OUT_IMAGE=${OUT_IMAGE:-"${ISO_BASE_NAME}-ks.iso"}
IMAGE_URL_PREFIX=${IMAGE_URL:-"https://vault.almalinux.org/9.6/isos/x86_64"}
WORK_DIR=${WORK_DIR:-"work"}
GITHUB_USER=${GITHUB_USER:-""}

check_iso_image() {
    local iso_file="$1"
    if [ ! -f "$iso_file" ]; then
        echo "Error: ISO image '$iso_file' not found." >&2
        return 1
    fi
    # 簡易妥当性チェック ( MIME が iso9660 か, 少なくとも 100MB 以上か )
    if command -v file >/dev/null 2>&1; then
        mime=$(file -b --mime-type "$iso_file" || true)
        case "$mime" in
            application/x-iso9660-image|application/octet-stream) : ;;
            *) echo "Error: File '$iso_file' does not look like an ISO (mime=$mime)" >&2; return 1;;
        esac
    fi
    size_bytes=$(wc -c < "$iso_file")
    if [ "$size_bytes" -lt $((100*1024*1024)) ]; then
        echo "Error: ISO size ($size_bytes bytes) is suspiciously small. Wrong file?" >&2
        return 1
    fi

    return 0
}

main() {
    local ks_file
    local iso_file
    local out_file
    local work_dir="${WORK_DIR}"
    local cwd

    ks_file="${KS_FILE}"
    iso_file="${ISO_IMAGE}"

    cwd=$(pwd)

    if [ ! -d "${work_dir}" ]; then
        mkdir -p "${work_dir}"
    fi

    if [ ! -f "${ks_file}" ]; then
        echo "Error: Kickstart file '${ks_file}' not found." >&2
        exit 1
    fi

    if [ ! -f "${work_dir}/${iso_file}" ]; then

        if [ -f "${iso_file}" ] && check_iso_image "${iso_file}"; then
            echo "Copying local ISO image '${iso_file}' to working directory."
            cp "${iso_file}" "${work_dir}/"
            echo "Copied local ISO image '${iso_file}' to working directory."
        else
            echo "ISO image '${iso_file}' not found or invalid. Downloading from ${IMAGE_URL_PREFIX}/${iso_file} ..."
            curl -fL --retry 5 --retry-connrefused --connect-timeout 10 \
              -o "${work_dir}/${iso_file}" \
              "${IMAGE_URL_PREFIX}/${iso_file}"
        fi
    fi

    # work ディレクトリ内の ISO は毎回チェック
    if [ ! -s "${work_dir}/${iso_file}" ] || ! check_iso_image "${work_dir}/${iso_file}"; then
        echo "Error: Failed to validate source ISO image: ${work_dir}/${iso_file}." >&2
        exit 1
    fi

    cp "${ks_file}" "${work_dir}/"
    out_file="${iso_file%.iso}-ks.iso"

    echo "Source ISO: ${iso_file}"
    echo "Kickstart:  ${ks_file}"
    echo "Output ISO: ${out_file}"

    echo "Creating customized ISO image..."
    # Dockerコンテナ内でmkksisoコマンドを実行してISOイメージを作成
    # --privileged オプションが必要
    # mkksiso は内部で /work を临時作業ディレクトリとして使うため
    # ${cwd}/work のコンテナ内でのマウント先を /src にしている。
    # /src:z の':z'は SELinux 用のオプションで,
    # ホスト側の work ディレクトリに「共有 ( shared ) 」用の SELinux ラベルを付け直す ( relabel )  指示

    docker run --rm --privileged \
      -v "${cwd}/work:/src:z" \
      -e KS_FILE="${ks_file}" \
      -e ISO_FILE="${iso_file}" \
      -e OUT_FILE="${out_file}" \
      almalinux:9 \
      bash -lc '
        set -euo pipefail
        dnf -y install lorax xorriso genisoimage isomd5sum file pykickstart
        # 文法チェック
        ksvalidator --v RHEL9 "/src/${KS_FILE}"
        # 一時作業ディレクトリにコピーしてから検証・実行
        WORKDIR="$(mktemp -d /var/tmp/mkksiso.XXXXXX)"
        trap "rm -rf \"$WORKDIR\"" EXIT
        cp "/src/${ISO_FILE}" "$WORKDIR/in.iso"
        cp "/src/${KS_FILE}"  "$WORKDIR/ks.cfg"
        cd "$WORKDIR"
        # 事前検証：xorriso で TOC が読めるか確認 ( ここで落ちれば ISO 破損 )
        if ! xorriso -indev in.iso -toc >/dev/null 2>&1; then
          echo "Error: xorriso cannot read in.iso (corrupted or not an ISO)" >&2
          exit 2
        fi
        # 参考：MIME も見ておく ( 環境によっては常に application/octet-stream のことあり )
        if command -v file >/dev/null 2>&1; then
          mime=$(file -b --mime-type in.iso || true)
          case "$mime" in
            application/x-iso9660-image|application/octet-stream) : ;;
            *) echo "Error: in.iso mime=$mime (not iso9660?)" >&2; exit 2;;
          esac
        fi
        # デバッグ有効化
        mkksiso --debug --ks ks.cfg in.iso out.iso
        checkisomd5 out.iso || true
        mv -f out.iso "/src/${OUT_FILE}"
      ' || true
    if [ ! -f "$work_dir/$out_file" ]; then
        echo "Error: Failed to create customized ISO image." >&2
        exit 1
    fi
    rm -f "$cwd/$out_file"
    mv "$work_dir/$out_file" "$cwd/$out_file"
    echo "Customized ISO image created: $out_file"

    if [ -d "$work_dir" ]; then
        rm -rf "$work_dir"
    fi
}

main "$@"
