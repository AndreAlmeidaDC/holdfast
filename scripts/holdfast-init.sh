#!/usr/bin/env bash
# holdfast-init.sh — scaffold a durable partitioned run.
# Usage: holdfast-init.sh <run-name> <output-dir>
set -euo pipefail
RUN="${1:?usage: holdfast-init.sh <run-name> <output-dir>}"
OUT="${2:?usage: holdfast-init.sh <run-name> <output-dir>}"
SKILL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$OUT/units"

cat > "$OUT/STATE.json" << EOF
{
  "run": "$RUN",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "objective": "TODO: one sentence — what this run produces",
  "inputs": {},
  "units": [
    {"id": "U1", "scope": "TODO", "bounds": "TODO", "status": "pending"},
    {"id": "U2", "scope": "TODO", "bounds": "TODO", "status": "pending"}
  ]
}
EOF

sed -e "s|__RUN__|$RUN|g" "$SKILL/assets/PROTOCOL.template.md" > "$OUT/PROTOCOL.md" 2>/dev/null \
  || cp "$SKILL/assets/PROTOCOL.template.md" "$OUT/PROTOCOL.md"
cp "$SKILL/assets/HANDOFF.template.md" "$OUT/HANDOFF.md"
cp "$SKILL/scripts/holdfast-status.sh" "$OUT/status.sh"
cp "$SKILL/scripts/holdfast-collect.py" "$OUT/collect.py"
chmod +x "$OUT/status.sh" 2>/dev/null || true

echo "holdfast: scaffolded '$RUN' at $OUT"
echo
echo "next:"
echo "  1. edit $OUT/STATE.json      — declare your units"
echo "  2. edit $OUT/PROTOCOL.md     — declare the shared contract"
echo "  3. dispatch wave 1 (see assets/dispatch-prompt.template.md)"
echo "  4. bash $OUT/status.sh       — anytime, from any session"
