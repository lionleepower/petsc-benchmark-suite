#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

input_md="runtime_scaling_tables.md"
output_html="runtime_scaling_tables.html"
output_pdf="runtime_scaling_tables.pdf"
css_file="runtime_scaling_tables_pdf.css"

command -v pandoc >/dev/null 2>&1 || {
  echo "pandoc is required. Install it with: sudo apt install pandoc" >&2
  exit 1
}

command -v prince >/dev/null 2>&1 || {
  echo "PrinceXML is required. Install it from https://www.princexml.com/download/" >&2
  exit 1
}

pandoc "$input_md" \
  --standalone \
  --metadata title="Runtime Scaling Tables" \
  --css "$css_file" \
  -o "$output_html"

prince "$output_html" -o "$output_pdf"

echo "Wrote: $(pwd)/$output_html"
echo "Wrote: $(pwd)/$output_pdf"
