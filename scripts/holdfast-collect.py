#!/usr/bin/env python3
"""collect.py — aggregate unit outputs into one file. Deterministic, re-runnable.

Reads units/*.md, extracts pipe-table rows, writes COLLECTED.md + COLLECTED.json.
Tolerant of bold markers (**P0**) — a strict parser silently drops rows, which is
a real failure mode: it once hid the three most severe findings of a whole unit.
"""
import glob, json, os, re, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
UNITS = os.path.join(ROOT, "units")
ROW = re.compile(r'^\|\s*\**(\d+)\**\s*\|(.+)$')

def main():
    rows, units, mismatch = [], [], []
    for path in sorted(glob.glob(os.path.join(UNITS, "*.md"))):
        uid = os.path.basename(path)[:-3]
        txt = open(path, encoding="utf-8", errors="ignore").read()
        status = "COMPLETE" if re.search(r'Status:.*COMPLETE', txt, re.I) else "PARTIAL"
        found = []
        for line in txt.splitlines():
            m = ROW.match(line)
            if m:
                cells = [c.strip().strip('*') for c in m.group(2).split('|')]
                found.append({"unit": uid, "n": int(m.group(1)), "cells": cells})
        # cross-check against the unit's self-reported count, if present
        claim = re.findall(r'TOTAL\s*=\s*(\d+)', txt)
        if claim and int(claim[-1]) != len(found):
            mismatch.append({"unit": uid, "self_reported": int(claim[-1]), "parsed": len(found)})
        rows.extend(found)
        units.append({"unit": uid, "status": status, "items": len(found)})

    out = [f"# Collected — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
           f"\n**{len(rows)} items from {len(units)} units**\n",
           "| Unit | Status | Items |", "|---|---|---|"]
    out += [f"| `{u['unit']}` | {u['status']} | {u['items']} |" for u in units]
    if mismatch:
        out += ["\n## ⚠ Count mismatches (probable parser bug — investigate before trusting totals)\n",
                "| Unit | Self-reported | Parsed |", "|---|---|---|"]
        out += [f"| `{m['unit']}` | {m['self_reported']} | {m['parsed']} |" for m in mismatch]
    out.append("\n## Items\n")
    for r in rows:
        out.append(f"| `{r['unit']}` | {r['n']} | " + " | ".join(r["cells"]) + " |")

    open(os.path.join(ROOT, "COLLECTED.md"), "w", encoding="utf-8").write("\n".join(out))
    json.dump({"generated": datetime.now(timezone.utc).isoformat(), "total": len(rows),
               "units": units, "count_mismatches": mismatch},
              open(os.path.join(ROOT, "COLLECTED.json"), "w", encoding="utf-8"), indent=2)

    print(f"COLLECTED.md — {len(rows)} items from {len(units)} units")
    if mismatch:
        print(f"WARNING: {len(mismatch)} unit(s) disagree with the parser — see COLLECTED.md")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
