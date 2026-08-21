---
name: holdfast
description: Runs long multi-unit work so an interruption costs almost nothing. Partitions the job into independent units, makes each worker write its output to disk BEFORE reporting back, and keeps a cold-resumable state file so a fresh session picks up exactly where the last one died. Use this whenever a task is large enough to risk hitting a usage limit, a context ceiling, a crash, or a closed laptop — full-codebase audits, bulk file processing, batch migrations, large document reviews, dataset passes, anything fanned out across many subagents. Also use it when the user says things like "don't lose work if the limit hits", "keep a handoff updated", "this is going to take a while", or when they've already been interrupted once and are restarting. Reach for it BEFORE dispatching the work, not after something is lost.
---

# Holdfast

## Origin version check

At the start of a meaningful use, when network access and HTTP or Git tooling are available, check whether this skill has a newer upstream version before performing the main task. The canonical source is:

```text
https://github.com/AndreAlmeidaDC/holdfast
```

Read the upstream `README.md` and `CHANGELOG.md` when available. Compare the local copy against the upstream default branch (`master`) using the lightest safe method — plain HTTPS retrieval of `metadata.json`, `git ls-remote`, or `git fetch`. If there are relevant differences, summarize what changed, note whether it affects the current task, and ask the user before updating.

Never perform silent self-update. Never overwrite local edits without explicit approval. If the repository cannot be reached or the task is too small to justify the check, continue with the local version. For the detailed protocol, read `references/version-check.md`.

Author: André Almeida · License: MIT

> A holdfast is what anchors kelp to rock. Waves take the water; the grip stays.

## What this is for

Long agent runs die. Usage limits reset mid-flight, context windows fill, laptops close, processes get killed. The default failure mode is brutal: an agent that has done forty minutes of good work but hasn't reported yet takes all of it with it.

The fix is not to make runs shorter. It's to make the **unit of durability smaller than the unit of dispatch**, and to keep state in files rather than in any runtime's memory.

That single move is what this skill implements. Everything else follows from it.

## The core rule

**A worker writes its output to disk before it reports.**

The report is redundancy. The file is the truth.

This inverts the normal instinct — accumulate results, then present them — and it is the whole reason the pattern works. When a limit hits, the runtime dies. The disk does not. A worker that has flushed its findings has banked them; a worker holding everything in context to write a beautiful final summary loses all of it.

Everything below exists to make that rule practical at scale.

## When to use this

Reach for it when the work is **partitionable and long**:

- auditing or reviewing a large codebase, corpus, or document set
- bulk transforms across many files
- batch data processing or extraction
- migrations that touch many modules
- anything you'd naturally fan out across several subagents

The signal is not "this is complicated" — it's "this has many similar pieces and will take a while." A single hard problem with one deliverable does not need holdfast. A dozen similar medium ones do.

Also reach for it when the user names the fear directly: *"don't lose work if the limit hits"*, *"keep the handoff updated"*, *"we got cut off yesterday, continue"*.

## The six practices

### 1. Partition before dispatching

Write the units down in a state file **first**, with explicit scope and boundaries. Without this there is no resumption — only restart, because nothing records what "done" means per piece.

Good units are independent (no unit needs another's output), similar in size, and small enough that losing one is cheap. If units must be ordered, that is a pipeline, not a partition — run the phases in sequence and partition within each.

Aim for units that take roughly 5–15 minutes of agent work. Much smaller and coordination overhead dominates; much larger and a single loss hurts.

### 2. One protocol file, not N copies in prompts

Put the shared contract — output format, taxonomy, rules, quality bar — in a single file that every worker reads. Dispatch prompts then carry only what is unique to that unit.

This keeps prompts short, makes the contract auditable, and removes the drift you get when the same instructions are retyped fifteen times with small variations.

### 3. Workers flush early and often

Instruct each worker to:

- **create its output file with a header and a `PARTIAL` status before reading anything**, so even an instant death leaves a marker saying which unit was in flight and what it covered
- **append results every few items**, not at the end
- **flip to `COMPLETE` only when genuinely finished**

Tell workers explicitly that partial-saved beats perfect-lost. Without that framing, a capable model will optimize for a polished single write at the end, which is exactly the behavior that loses everything.

### 4. A status command that works from zero context

Ship a script that reports run state by reading the filesystem — no conversation history, no memory, no runtime state. A fresh session, a different agent, or a human should be able to run one command and know what is done, what is partial, and what never started.

This is what converts "I have no idea where we were" into "three units left, here they are."

### 5. Waves with checkpoints between them

Dispatch in waves rather than all at once. A wave boundary is the only moment when nothing is in flight, which makes it the cheapest place to consolidate, update the handoff, and decide whether to continue.

Wave size is a real tradeoff: wider waves finish sooner but lose more when a limit hits mid-wave. Three to five parallel units is a reasonable default. If you take a hard interruption, narrow the next wave rather than widening it.

### 6. Partial completion is a first-class outcome

A unit that covered 60% of its scope and said so is a **success**, not a failure. It resumes cheaply because the expensive part — reading and understanding the material — is already paid for.

Design the resume prompt to exploit this: tell the resuming worker to read its own existing file, continue the numbering, and append. Never let it start over. This repeatedly turns what looks like a total loss into a short continuation.

## Workflow

**1. Scaffold**

```bash
bash scripts/holdfast-init.sh <run-name> <output-dir>
```

Creates `STATE.json`, `PROTOCOL.md`, `status.sh`, `collect.py` and the `units/` directory. Edit `STATE.json` to declare your units and `PROTOCOL.md` to declare the shared contract.

**2. Dispatch a wave**

Give each worker: the protocol path, its unit id and scope, its output path, and the flush rules from practice 3. Use `assets/dispatch-prompt.template.md` as the shape.

**3. Checkpoint between waves**

```bash
bash <output-dir>/status.sh
python <output-dir>/collect.py
```

Update the handoff. Decide whether to continue, narrow, or stop.

**4. On interruption, triage before redispatching**

Check the disk, not the notifications. Notifications routinely understate what was saved — a worker that reported "writing batch 2" may already have forty items on disk. Units with `PARTIAL` status and real content get **resume** prompts; units with only a stub get fresh dispatch.

**5. Close out**

Aggregate, write the handoff, and state plainly which units are complete, which are partial, and what remains.

## Things that will bite you

**Trusting the report over the disk.** Agent reports get truncated, garbled, or simply never arrive. Verify on disk before concluding anything — including before concluding that work was lost.

**Aggregating a file that is still being written.** A worker mid-flush looks like a finished worker with fewer results. If a count looks wrong, re-check after the unit reports complete. Better: have `collect.py` distinguish `PARTIAL` from `COMPLETE` and label accordingly.

**A parser that silently drops rows.** If aggregation uses pattern matching over worker output, formatting variation will eat results without erroring. Have workers emit their own counts so aggregate and self-reported numbers can be compared — a mismatch is a parser bug, and it is invisible otherwise.

**Contaminating workers with unverified context.** Passing your own conclusions into worker prompts as established fact turns independent workers into echoes. Pass context as *hypothesis to test*, and ask workers to report what they refuted. Without it, an error in the orchestrator's own briefing propagates into every unit.

## Runtime requirements

Three things, none exotic: a filesystem, a shell, and a way to run work in parallel.

The pattern is runtime-agnostic by construction — state lives in files, and files do not care which agent reads them. What differs between runtimes is only **how work is dispatched and how completion is detected**. Some have in-process subagents with automatic notification; others only have a shell and need polling, which makes the status script load-bearing rather than convenient.

See `references/runtimes.md` before running this on anything other than Claude Code.

## Reference material

- `references/runtimes.md` — dispatch and completion detection per runtime, and what needs adapting
- `assets/dispatch-prompt.template.md` — the shape of a worker prompt
- `assets/resume-prompt.template.md` — the shape of a resume prompt
