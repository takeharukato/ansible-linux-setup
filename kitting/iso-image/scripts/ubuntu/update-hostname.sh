#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Please run with sudo:  sudo ./update-hostname.sh <new-hostname>" >&2
  exit 1
fi

if [[ $# -lt 1 || -z "${1:-}" ]]; then
  echo "Usage: sudo ./update-hostname.sh <new-hostname>" >&2
  exit 2
fi

NEW_HOST="$1"
# RFC1123 簡易チェック
if ! [[ "$NEW_HOST" =~ ^[A-Za-z0-9]([-A-Za-z0-9]{0,62})(\.[A-Za-z0-9]([-A-Za-z0-9]{0,62}))*$ ]]; then
  echo "Invalid hostname: '$NEW_HOST'" >&2
  exit 3
fi

# /etc/hosts の健全性チェック (空なら中断)
if [[ ! -s /etc/hosts ]]; then

  if [[ -e /etc/hosts && ! -s /etc/hosts ]]; then
      echo "Warning: /etc/hosts exists and is empty, create forcefully its Ubuntu specific host entry with 'ubuntu-vm'. " >&2
      cat >/etc/hosts <<EOF
127.0.0.1   localhost
127.0.1.1   ubuntu-vm
::1         localhost ip6-localhost ip6-loopback
ff02::1     ip6-allnodes
ff02::2     ip6-allrouters
EOF
  else
      echo "Warning: /etc/hosts does not exist and is empty. " >&2
  fi
fi

# ロック
exec 9>/etc/hosts.lock
flock -x 9

OLD_HOST="$(hostname)"
echo "Changing hostname: ${OLD_HOST} -> ${NEW_HOST}"
hostnamectl set-hostname "$NEW_HOST"

SHORT=${NEW_HOST%%.*}
if [[ "$NEW_HOST" == *.* && "$SHORT" != "$NEW_HOST" ]]; then
    NAMES="$NEW_HOST $SHORT"
else
    NAMES="$NEW_HOST"
fi

# 127.0.1.1 があるか事前確認
if ! grep -Eq '^[[:space:]]*127\.0\.1\.1([[:space:]]|$)' /etc/hosts; then
    echo "No 127.0.1.1 entry found. Leaving /etc/hosts untouched."
    exit 0
fi

# 退避
bak="/etc/hosts.bak.$(date +%F_%T)"
cp -a /etc/hosts "$bak"

tmp="$(mktemp /etc/hosts.new.XXXXXX)"
cleanup() { rm -f "$tmp"; }
trap cleanup EXIT

# 127.0.1.1 の行だけを置換。コメントは保持。
awk -v names="$NAMES" '
  {
    line=$0
    c=index(line,"#"); comment=(c?substr(line,c):"")
    if (line ~ /^[[:space:]]*127\.0\.1\.1([[:space:]]|$)/) {
      printf "127.0.1.1\t%s%s\n", names, (comment? " " comment : "")
    } else {
      print line
    }
  }
' /etc/hosts >"$tmp"

# --- 検証フェーズ ---
# 1) 出力が空でないこと
if [[ ! -s "$tmp" ]]; then
    echo "ERROR: generated hosts is empty; restoring backup." >&2
    cp -a "$bak" /etc/hosts
    exit 5
fi

# 2) 元に 127.0.1.1 があったので, 出力にも 127.0.1.1 が残っていること
if ! grep -Eq '^[[:space:]]*127\.0\.1\.1([[:space:]]|$)' "$tmp"; then
    echo "ERROR: 127.0.1.1 missing in new hosts; restoring backup." >&2
    cp -a "$bak" /etc/hosts
    exit 6
fi

# 3) 非コメント行が最低1行あること
if ! grep -Eq '^[[:space:]]*[^#[:space:]]' "$tmp"; then
    echo "ERROR: no effective entries; restoring backup." >&2
    cp -a "$bak" /etc/hosts
    exit 7
fi

# 原子的に置換
install -o root -g root -m 0644 "$tmp" /etc/hosts
sync
echo "Done. /etc/hosts updated safely."


echo "Restarting avahi-daemon..."
systemctl restart avahi-daemon

echo "=== Hostname ==="
SYSTEMD_PAGER= hostnamectl status | sed -n '1,3p'
echo

echo "=== IP Addresses (global) ==="
if command -v ip >/dev/null 2>&1; then
  ip -4 addr show scope global | awk '/inet /{print "IPv4: "$2" dev "$7}'
  ip -6 addr show scope global | awk '/inet6 /{print "IPv6: "$2" dev "$7}'
fi
echo

echo "=== Media Access Control (MAC) Addresses ==="
if command -v ip >/dev/null 2>&1; then

  PHYS_IFACES=()

  # NICの一覧を_all_ifacesに格納
  set +e
  mapfile -t _all_ifaces < <(ip -o link show | awk -F': ' '{print $2}')
  set -e

  for IF in "${_all_ifaces[@]}"
  do
    # @の前を切り出す. 例ens160@if3 をens160に変換
    _base_if="${IF%%@*}"
    if [[ -e "/sys/class/net/${_base_if}/device" ]]; then

      # 重複がない様にしてPHYS_IFACES配列に追加
      [[ " ${PHYS_IFACES[*]} " =~ " ${_base_if} " ]] || PHYS_IFACES+=("${_base_if}")
    fi
  done

  for _nic in "${PHYS_IFACES[@]}"; do

    set +e
    _mac="$(cat "/sys/class/net/${_nic}/address" 2>/dev/null)"
    set -e
    [[ -n "${_mac}" ]] && printf "%s : %s\n" "${_nic}" "${_mac}"
  done

  echo

fi

echo "=== mDNS resolution via Avahi ==="

if command -v avahi-resolve-host-name >/dev/null 2>&1; then
  set +e
  avahi-resolve-host-name -4 "${NEW_HOST}.local" || true
  avahi-resolve-host-name -6 "${NEW_HOST}.local" || true
  set -e
fi

echo
echo "Done. Try:  ssh ansible@${NEW_HOST}.local"
