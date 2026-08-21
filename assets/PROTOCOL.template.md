# Protocol — __RUN__

Every worker reads this before starting. It is the shared contract, so that fifteen
dispatch prompts do not become fifteen slightly different sets of instructions.

## Durability rule — read this first

**Write your output file before you report. Save every few items.**

Your report is redundancy. The file is the truth. If this session is interrupted —
usage limit, crash, closed laptop — anything you are holding in context to write up
neatly at the end is gone, and anything you flushed is banked.

Concretely:

1. **Before reading anything**, create your output file with the header below and
   `Status: PARTIAL`. Even a worker killed in its first minute should leave a marker
   saying which unit was running and what it was meant to cover.
2. **Append every ~5 items.** Update the coverage line each time you save.
3. **Flip to `COMPLETE` only when genuinely finished** with your whole scope.
4. If context gets tight: save, leave `PARTIAL` with the range you really covered,
   and report. **Half a unit on disk is worth more than a perfect unit that never arrives.**

## Output file

Path: `units/<UNIT-ID>.md`

```markdown
# <UNIT-ID> — <scope>
**Bounds:** <what this unit covers>
**Status:** PARTIAL
**Covered so far:** <update this every save>

## Items

| # | Locator | Category | Severity | Finding | Evidence | Suggested fix |
|---|---|---|---|---|---|---|
```

When complete, append your own count so the aggregator can be checked against you:

```
## Count
<CATEGORY_A>=n <CATEGORY_B>=n ...
<SEV_A>=n <SEV_B>=n TOTAL=n
```

That total matters: if the aggregate disagrees with it, the aggregator has a bug.
Silent row-dropping is a real failure mode and self-reported counts are how it gets caught.

## Categories

TODO — define your taxonomy. Short stable codes, one line each on what qualifies.

## Severity

TODO — define your levels and what earns each one.

## How to work

TODO — the method for this run. Cover at least:
- read your whole range; do not sample unless told to
- what to verify externally, and how
- when to mark something `unverified` rather than assume

## Treat handed-down context as hypothesis, not fact

You may receive findings from other units or from the orchestrator. **Test them.**
Refuting one is a valid and valuable result — say so explicitly in your report.

This matters because an orchestrator passing its own conclusions as established fact
turns independent workers into echoes, and a single upstream error then propagates
into every unit. Workers correcting each other is the mechanism that keeps the
aggregate honest.

## What not to do

- Do not edit the source material. This pass is diagnosis.
- Do not repeat a known item without adding precise location and evidence — the
  value is in the locator.
- Do not assume. `unverified` is an acceptable and useful answer.
