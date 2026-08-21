# Runtimes — what ports, what needs adapting

Holdfast keeps state in files, so most of it is indifferent to which agent runs it. What differs between runtimes is narrow and specific: **how work is dispatched, and how completion is detected.**

This file is the adaptation map. Read the section for your runtime before the first run.

---

## What is portable without changes

These carry across every runtime, because they are plain files and POSIX shell:

| Piece | Why it ports |
|---|---|
| `STATE.json` | plain JSON; nothing reads it but you |
| `PROTOCOL.md` | plain markdown handed to workers |
| `status.sh` | `grep`, `for`, `printf`, `test` — no runtime coupling |
| `collect.py` | Python standard library only (`glob`, `os`, `re`, `json`) |
| Unit output files | markdown the workers write |
| The handoff | markdown plus a JSON twin |
| **The six practices themselves** | conceptual |

No package installs, no SDK, no network. This is deliberate: dependencies are things that break when you resume on a different machine six weeks later.

---

## What always needs adapting

Exactly two things.

### 1. The dispatch primitive

How you start N pieces of work running in parallel.

### 2. Completion detection

How you learn a piece finished. This splits runtimes into two families, and the difference matters more than anything else in this file.

**Push runtimes** notify the orchestrator when a child finishes. You dispatch, do something else, and a notification arrives carrying the worker's report.

**Pull runtimes** have no notification channel. You dispatch into the background and must *ask* whether work is done. Here `status.sh` stops being a convenience and becomes the completion detector — the mechanism the whole run depends on.

---

## Per-runtime

### Claude Code — push · reference implementation

The pattern was built here.

- **Dispatch:** the `Agent` tool with `run_in_background: true`. Several calls in one message run concurrently.
- **Completion:** automatic task notification carrying the worker's final report.
- **Watch out:** a notification can fire more than once for the same task, and an early one may carry a truncated or garbled report while the work is still in flight. Treat a report that contradicts the disk as *not finished yet*, not as failure.

No adaptation needed.

---

### Codex — push

- **Dispatch:** agents declared in config (`[agents]`), invoked as subagents.
- **Completion:** the runtime returns the subagent result.
- **Adapt:** worker instructions live in config rather than being passed inline per call. Point the agent definition at `PROTOCOL.md` and pass only unit id, scope and output path per invocation — which is what practice 2 asks for anyway, so this runtime fits the pattern naturally.

---

### Antigravity — push

- **Dispatch:** dynamic subagents.
- **Completion:** runtime-returned.
- **Adapt:** minimal. Confirm background subagents survive the parent moving on before relying on wide waves; if they do not, narrow the wave to whatever runs synchronously and lean harder on flush frequency.

---

### Cursor — push, with caveats

- **Dispatch:** background agents.
- **Completion:** surfaced in the agent panel rather than as an inline notification to a driving agent.
- **Adapt:** Cursor's background agents are oriented toward autonomous branch work rather than orchestrated fan-out. Two viable shapes:
  1. one background agent per unit, with the human or a driving agent reading `status.sh` between waves
  2. a single agent looping units in series, relying on flush-per-unit for durability

Shape (2) loses parallelism but keeps every durability property. If in doubt, start there.

---

### OpenClaw · Hermes · Gemini-CLI — **pull · the family that needs real work**

These are the runtimes where holdfast changes shape, so this section is longer.

**There is no in-process subagent.** Delegation is a shell command that launches a child CLI in the background. Nothing tells you when it finishes.

- **Dispatch:** `bash` with a backgrounding flag, launching a child agent process per unit.
- **Completion:** you must poll — either process state, or the output files themselves.

**What has to change:**

**The status script becomes infrastructure, not convenience.** In push runtimes it answers "where are we?" for a human. Here it answers "is the wave done?" for the orchestrator, on a loop. Budget for it accordingly: it must be cheap, correct, and safe to run every few seconds.

**Add a wait loop between waves.** Something equivalent to:

```bash
# poll until every unit in the wave reports COMPLETE, or the deadline passes
deadline=$(( $(date +%s) + 1800 ))
while :; do
  done_n=$(grep -l 'Status:.*COMPLETE' units/*.md 2>/dev/null | wc -l)
  [ "$done_n" -ge "$WAVE_TARGET" ] && break
  [ "$(date +%s)" -ge "$deadline" ] && { echo "deadline; triaging partials"; break; }
  sleep 20
done
```

The deadline matters: a child that dies silently in a pull runtime produces no signal at all, and without a deadline the orchestrator waits forever on a corpse.

**Prefer file-based detection over process-based.** A live PID does not mean progress, and a dead PID does not mean failure — the worker may have flushed everything and exited cleanly a second before you looked. Since every worker already writes status into its file, read that. It is the same source of truth the resume logic uses, which keeps the two consistent.

**Flush more aggressively.** With no notification, the gap between "worker died" and "orchestrator noticed" is however long your poll interval is. Shorter flush intervals directly reduce what that gap can cost. Where a push runtime is fine flushing every ten items, flush every three to five here.

**Hermes specifically:** it has a self-improvement loop that can rewrite its own skills between runs. Pin the protocol file and treat it as read-only input to workers, or a long run can end with different units audited against silently different contracts — which corrupts the aggregate without any error appearing anywhere.

---

### Kimi CLI · Grok CLI · pi — pull, assume the OpenClaw shape

Same family. Verify whether the runtime offers any completion signal before assuming it does; if not, use the wait-loop pattern above.

---

## Adapting to a runtime not listed here

Answer three questions:

1. **How do I start N things in parallel?** If the answer is "I can't," run units in series — you lose throughput but keep every durability property. This is a legitimate configuration, not a degraded one.
2. **How do I know something finished?** If there is no push signal, you are in the pull family: add the wait loop and shorten flush intervals.
3. **Can a child outlive the parent's turn?** If not, waves must fit inside one turn, which caps wave width. Narrow waves and flush often.

If you can answer those three, the rest of the pattern transfers unchanged.

---

## Honest limits of this document

The pattern was exercised only on Claude Code. Everything written above about other
runtimes is **inference from their documented dispatch model**, not observation. It is
sound reasoning, and it is not evidence.

If you run holdfast on another runtime, the test worth doing is the one that actually
matters: start a wave, kill the session mid-flight, and measure what survives. That
single experiment tells you more than any amount of reading — and it is the same
standard this skill would want applied to anything else claiming resilience.
