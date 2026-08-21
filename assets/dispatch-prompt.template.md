# Dispatch prompt — shape

Substitute the bracketed parts. Keep it short: the contract lives in `PROTOCOL.md`,
not in this prompt. That is what keeps fifteen dispatches consistent.

---

You are the worker for unit **[UNIT-ID]**.

**Step 0 — before reading anything**, create `[OUT]/units/[UNIT-ID].md` with the
header from the protocol and `Status: PARTIAL`. Append results **every ~5 items**.
Flip to `COMPLETE` only when your whole scope is finished. If context gets tight:
save, leave `PARTIAL` with the range you really covered, and report.

Half a unit on disk beats a perfect unit that never arrives — this run has already
lost work to interruptions, and the flush is what prevents it.

**Step 1 — read the contract:** `[OUT]/PROTOCOL.md` (taxonomy, severity, output format).

**Your scope:** [source] · [bounds] · [what this unit covers]

**Priority order** — work in this sequence, so an interruption preserves the most
valuable part first:
1. [highest-value work]
2. [next]
3. [lowest]

**Context from other units — treat as hypothesis to test, not fact:**
- [finding A]
- [finding B]

Refuting any of these is a valid, wanted result. Report what you refuted.

Mark `unverified` when you cannot confirm something. Never assume.

**Report at the end:** file path, status, counts by category and severity, the three
most serious items, and which hypotheses you refuted.
