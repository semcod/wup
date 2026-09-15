#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
unit_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
unit_path="$unit_dir/wup-watcher.service"
wup_bin="$project_root/.venv/bin/wup"
planfile_bin=$(command -v planfile)

if [[ ! -x "$wup_bin" ]]; then
  echo "WUP executable not found: $wup_bin" >&2
  exit 1
fi

unit_content=$(cat <<UNIT
[Unit]
Description=WUP TestQL watcher and Planfile incident reporter
After=network-online.target

[Service]
Type=simple
WorkingDirectory=$project_root
Environment=PATH=$(dirname "$planfile_bin"):${HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$wup_bin watch .
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
UNIT
)

if [[ ${1:-} == "--dry-run" ]]; then
  printf '%s\n' "$unit_content"
  exit 0
fi

mkdir -p "$unit_dir"
printf '%s\n' "$unit_content" > "$unit_path"
systemctl --user daemon-reload
systemctl --user enable --now wup-watcher.service
systemctl --user --no-pager --full status wup-watcher.service
