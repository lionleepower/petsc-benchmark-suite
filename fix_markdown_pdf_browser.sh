#!/usr/bin/env bash
set -euo pipefail

settings_file="$HOME/.vscode-server/data/User/settings.json"
chrome_deb="/tmp/google-chrome-stable_current_amd64.deb"
chrome_url="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"

echo "This script fixes the VS Code Markdown PDF browser on WSL."
echo "It installs Google Chrome Stable inside Ubuntu and points Markdown PDF to it."
echo

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required but was not found." >&2
  exit 1
fi

if ! command -v google-chrome-stable >/dev/null 2>&1; then
  echo "Downloading Google Chrome Stable..."
  if command -v curl >/dev/null 2>&1; then
    curl -L "$chrome_url" -o "$chrome_deb"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$chrome_deb" "$chrome_url"
  else
    echo "curl or wget is required to download Chrome." >&2
    exit 1
  fi

  echo "Installing Google Chrome Stable. You may be asked for your sudo password."
  sudo apt update
  sudo apt install -y "$chrome_deb"
else
  echo "Google Chrome Stable is already installed."
fi

echo
echo "Chrome version:"
google-chrome-stable --version

mkdir -p "$(dirname "$settings_file")"
python3 - "$settings_file" <<'PY'
import json
import sys
from pathlib import Path

settings_path = Path(sys.argv[1])
if settings_path.exists():
    try:
        settings = json.loads(settings_path.read_text() or "{}")
    except json.JSONDecodeError:
        backup = settings_path.with_suffix(".json.bak")
        backup.write_text(settings_path.read_text())
        print(f"Existing settings.json was invalid JSON; backed up to {backup}")
        settings = {}
else:
    settings = {}

settings["markdown-pdf.executablePath"] = "/usr/bin/google-chrome-stable"
settings["markdown-pdf.chromium.autoDownload"] = False

settings_path.write_text(json.dumps(settings, indent=2) + "\n")
print(f"Updated {settings_path}")
PY

echo
echo "Testing Chrome headless launch..."
tmp_profile="/tmp/markdown-pdf-chrome-test-profile"
rm -rf "$tmp_profile"
set +e
google-chrome-stable \
  --headless=new \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --user-data-dir="$tmp_profile" \
  --dump-dom "data:text/html,<html><body><h1>Markdown PDF browser OK</h1></body></html>" \
  >/tmp/markdown-pdf-chrome-test.out \
  2>/tmp/markdown-pdf-chrome-test.err
status=$?
set -e

if [ "$status" -ne 0 ]; then
  echo "Chrome installed, but the headless launch test failed." >&2
  echo "stderr:" >&2
  sed -n '1,80p' /tmp/markdown-pdf-chrome-test.err >&2
  exit "$status"
fi

grep -q "Markdown PDF browser OK" /tmp/markdown-pdf-chrome-test.out
echo "Headless Chrome test passed."
echo
echo "Done. Restart VS Code or reload the VS Code window, then try Markdown PDF export again."
