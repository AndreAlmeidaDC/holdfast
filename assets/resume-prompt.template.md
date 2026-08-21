# Resume prompt — shape

For a unit interrupted with real work already on disk. The point is to **continue**,
never to restart — the expensive part is reading the material, and that is already paid for.

---

You are **RESUMING** unit **[UNIT-ID]**, interrupted by [reason]. Do not start over.

**Step 1 — read your own file:** `[OUT]/units/[UNIT-ID].md`

It already has **[N] items** and reports `Covered: [range]`. That coverage is real —
the previous session died [during verification / mid-write], not during reading.

**Step 2 — read the contract:** `[OUT]/PROTOCOL.md`

**Append. Never overwrite.** Continue the numbering from **[N+1]**. Save every ~5
new items. When finished, flip to `Status: COMPLETE` and write the count block for
**all** items in the file, not only yours.

**What remains** — the previous session stopped exactly here:
- [remaining task 1]
- [remaining task 2]

**Context from other units — hypothesis to test, not fact:**
- [finding A]

Report: path, final status, total counts for the whole file, the three most serious
items in it, and what you refuted.
