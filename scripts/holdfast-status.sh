#!/usr/bin/env bash
# status.sh — run state from the filesystem alone.
# Safe to run from a cold session, another agent, or a human. No context needed.
cd "$(dirname "${BASH_SOURCE[0]}")"
U="units"
[ -d "$U" ] || { echo "no units/ directory here"; exit 0; }

RUN=$(grep -o '"run"[[:space:]]*:[[:space:]]*"[^"]*"' STATE.json 2>/dev/null | head -1 | sed 's/.*"\([^"]*\)"$/\1/')
echo "=== holdfast${RUN:+: $RUN} ==="

ids=$(grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' STATE.json 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
[ -z "$ids" ] && ids=$(ls "$U" 2>/dev/null | sed 's/\.md$//')

tot=0; done_n=0; part=0; pend=0
for id in $ids; do
  tot=$((tot+1)); f="$U/$id.md"
  if [ ! -f "$f" ]; then
    printf "  %-6s pending\n" "$id"; pend=$((pend+1))
  elif grep -qi 'Status:.*COMPLETE' "$f"; then
    n=$(grep -cE '^\|[[:space:]]*[0-9]+[[:space:]]*\|' "$f" 2>/dev/null || echo 0)
    printf "  %-6s COMPLETE  %4s items\n" "$id" "$n"; done_n=$((done_n+1))
  else
    n=$(grep -cE '^\|[[:space:]]*[0-9]+[[:space:]]*\|' "$f" 2>/dev/null || echo 0)
    r=$(grep -m1 -i 'covered\|coberto\|lines read\|linhas' "$f" 2>/dev/null | cut -c1-60)
    printf "  %-6s PARTIAL   %4s items  %s\n" "$id" "$n" "$r"; part=$((part+1))
  fi
done

echo "  ---"
echo "  $done_n complete · $part partial · $pend pending · $tot total"
[ "$part" -gt 0 ] && echo "  → partial units RESUME (append, do not restart)"
[ "$pend" -gt 0 ] && echo "  → pending units dispatch fresh"
exit 0
