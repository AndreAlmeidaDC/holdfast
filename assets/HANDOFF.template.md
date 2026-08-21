# Handoff — <run name>

**Updated:** <date>
**Status:** <one line: where this stands>

> Self-contained on purpose. A fresh session, another agent, or a human should be
> able to resume from this file alone.

## Resume here

```bash
bash status.sh      # what is done, partial, pending
python collect.py   # regenerate the aggregate from disk
```

## What is done

| Wave | Units | Result |
|---|---|---|

## What remains

| Unit | Scope | State | Action |
|---|---|---|---|

Partial units **resume** — the worker reads its own file, continues the numbering
and appends. Pending units dispatch fresh. Never restart a partial unit: the
expensive part is already paid for.

## Decisions needed from a human

<things that block progress and are not technical>

## Known caveats

<errors made during the run, corrections applied, anything a future reader should
distrust. Be specific — a caveat you cannot act on is not a caveat.>

## Files

```
<run-dir>/
├── STATE.json        units and their scope
├── PROTOCOL.md       the shared contract
├── HANDOFF.md        this file
├── status.sh         state from disk, zero context
├── collect.py        aggregation, deterministic
├── COLLECTED.md      the aggregate
└── units/*.md        one file per unit
```
