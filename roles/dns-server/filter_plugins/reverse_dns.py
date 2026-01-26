#  -*- coding:utf-8 -*-
#  Ansible custom filter plugins for reverse DNS zone name generation
#  Copyright 2026 Takeharu KATO All Rights Reserved.

from typing import Any, Dict, Union

try:
    from ansible.errors import AnsibleFilterError  # type: ignore
except ImportError:
    # ansible がない環境用のフォールバック
    class AnsibleFilterError(Exception):  # type: ignore
        """Ansible フィルターエラー"""
        pass

import ipaddress


class FilterModule(object):
    """逆引きDNSゾーン名生成用のカスタムフィルタ"""

    def ipv4_reverse_zone(self, network_cidr: str) -> str:
        """
        IPv4 CIDRネットワークを逆引きDNSゾーン名に変換します。

        引数:
            network_cidr (str): CIDR形式のIPv4ネットワーク (例: '192.168.30.0/24')

        戻り値:
            str: 逆引きDNSゾーン名 (例: '30.168.192')

        例外:
            AnsibleFilterError: CIDR形式が無効またはIPv4でない場合

        使用例:
            >>> ipv4_reverse_zone('192.168.30.0/24')
            '30.168.192'
            >>> ipv4_reverse_zone('10.0.0.0/8')
            '0.10'
        """
        try:
            # CIDR表記をパース
            network = ipaddress.IPv4Network(network_cidr, strict=False)
        except ValueError as e:
            raise AnsibleFilterError(
                f"Invalid IPv4 CIDR format: '{network_cidr}'. "
                f"Expected format: X.X.X.X/prefix_length. Error: {str(e)}"
            )
        except TypeError as e:
            raise AnsibleFilterError(
                f"Invalid type for ipv4_reverse_zone: {type(network_cidr)}. "
                f"Expected string in CIDR format (e.g., '192.168.30.0/24')"
            )

        # ネットワークアドレスを取得
        network_addr = str(network.network_address)
        octets = network_addr.split('.')

        # プレフィックス長に基づいて逆順にするオクテット数を決定
        prefix_len = network.prefixlen
        if prefix_len <= 8:
            # /8以下: 最初のオクテットを使用
            reverse_zone = octets[0]
        elif prefix_len <= 16:
            # /9 to /16: 最初の二つのオクテットを逆順に使用
            reverse_zone = f"{octets[1]}.{octets[0]}"
        elif prefix_len <= 24:
            # /17 to /24: 最初の三つのオクテットを逆順に使用
            reverse_zone = f"{octets[2]}.{octets[1]}.{octets[0]}"
        else:
            # /25以上: 全てのオクテットを逆順に使用
            reverse_zone = f"{octets[3]}.{octets[2]}.{octets[1]}.{octets[0]}"

        return reverse_zone

    def ipv6_reverse_zone(self, prefix: str, prefix_len: Union[int, str]) -> str:
        """
        IPv6プレフィックスを逆引きDNSゾーン名（ニブル形式）に変換します。

        引数:
            prefix (str): IPv6プレフィックス (例: 'fd69:6684:61a:2::')
            prefix_len (int): プレフィックス長 (0-128)

        戻り値:
            str: ニブル形式の逆引きDNSゾーン名 (例: '2.0.0.0.a.1.6.0...')

        例外:
            AnsibleFilterError: プレフィックス形式が無効またはprefix_lenが範囲外の場合

        使用例:
            >>> ipv6_reverse_zone('fd69:6684:61a:1::', 64)
            '1.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f'
            >>> ipv6_reverse_zone('fd69:6684:61a:2::', 64)
            '2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f'
        """
        # prefix_lenを検証
        prefix_len_int: int
        if not isinstance(prefix_len, int):
            try:
                prefix_len_int = int(prefix_len)
            except (ValueError, TypeError):
                raise AnsibleFilterError(
                    f"Invalid prefix length type: {type(prefix_len)}. "
                    f"Expected integer (0-128)"
                )
        else:
            prefix_len_int = prefix_len

        if prefix_len_int < 0 or prefix_len_int > 128:
            raise AnsibleFilterError(
                f"IPv6 prefix length must be between 0 and 128, got: {prefix_len_int}"
            )

        try:
            # IPv6Networkオブジェクトを作成
            # 文字列にprefix_lenが含まれていない場合は引数のprefix_lenを使用
            if '/' not in str(prefix):
                network = ipaddress.IPv6Network(f"{prefix}/{prefix_len}", strict=False)
            else:
                network = ipaddress.IPv6Network(prefix, strict=False)
        except ValueError as e:
            raise AnsibleFilterError(
                f"Invalid IPv6 prefix format: '{prefix}'. "
                f"Expected format: xxxx:xxxx:... or xxxx:xxxx::.../prefix_length. Error: {str(e)}"
            )
        except TypeError as e:
            raise AnsibleFilterError(
                f"Invalid type for ipv6_reverse_zone prefix: {type(prefix)}. "
                f"Expected string (e.g., 'fd69:6684:61a:1::')"
            )

        # ネットワークアドレスを取得し、完全な表記に展開
        network_addr = network.network_address
        # すべてのゼロを埋めた完全なアドレスを取得
        addr_full = network_addr.exploded  # 例: 'fd69:6684:061a:0001:0000:0000:0000:0000'

        # コロンを削除して連続した16進数文字列を取得
        addr_hex = addr_full.replace(':', '')

        # 使用するニブル（4ビット16進数桁）の数を計算
        # 各ニブルは4ビットを表すため、prefix_len個のニブル = prefix_len * 4 ビット
        nibbles_to_use = prefix_len_int // 4

        # ニブルを抽出して逆順にする
        nibbles = list(addr_hex[:nibbles_to_use])
        nibbles.reverse()

        # ドットで結合して逆引きゾーン名を作成
        reverse_zone = '.'.join(nibbles)

        return reverse_zone

    def filters(self) -> Dict[str, Any]:
        """フィルター関数を返す"""
        return {
            'ipv4_reverse_zone': self.ipv4_reverse_zone,
            'ipv6_reverse_zone': self.ipv6_reverse_zone,
        }
