#cloud-config
hostname: ${hostname}
preserve_hostname: false
prefer_fqdn_over_hostname: false
fqdn: ${hostname}.${domain}
manage_etc_hosts: true
runcmd:
  - [ sh, -c, "if command -v apt-get >/dev/null 2>&1; then apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y avahi-daemon; elif command -v dnf >/dev/null 2>&1; then dnf -y install avahi-daemon || dnf -y install avahi; elif command -v yum >/dev/null 2>&1; then yum -y install avahi-daemon || yum -y install avahi; fi" ]
  - [ sh, -c, "systemctl enable --now avahi-daemon.service || true" ]
  - [ sh, -c, "systemctl restart avahi-daemon.service || systemctl start avahi-daemon.service || true" ]
