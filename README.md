# holdfast

**A skill for running long agent work so that an interruption costs almost nothing.**

Partitions a big job into independent units, makes each worker write its output to disk *before* it reports back, and keeps a state file any cold session can read. When the usage limit hits — and it will — you lose the units in flight, not the run.

---

## Why "holdfast"

A holdfast is the root-like structure that anchors kelp to rock. It is not a root — it absorbs nothing, it only grips. Surge comes through, the blade whips around, water leaves. The grip stays.

That is the property this skill is about. It does not make long runs faster, cheaper, or less likely to be interrupted. It makes the finished part **stay finished** when the interruption comes.

The word is also an old command — *hold fast* — and a woodworking clamp, and in both senses it means the same thing: keep your grip on what you already have.

The alternative names all missed something. *Checkpoint* is generic and describes a mechanism instead of a property. *Ratchet* is close — progress that only moves one way — but already means something else in developer tooling. *Blackbox* survives the crash but implies opacity, and this skill's whole point is that state is legible from outside. Holdfast is a thing that grips and does not let go, which is exactly the promise.

---

## Install

```bash
git clone https://github.com/AndreAlmeidaDC/holdfast.git ~/.claude/skills/holdfast
```

Or copy the directory into wherever your runtime loads skills from.

**Dependencies:** a filesystem, a shell, Python 3 (standard library only), and some way to run work in parallel. No packages, no SDK, no network.

That poverty is deliberate. Dependencies are things that break when you resume on a different machine six weeks later.

---

## Quick start

```bash
bash ~/.claude/skills/holdfast/scripts/holdfast-init.sh my-run ./work
```

Then:

1. Edit `work/STATE.json` — declare your units
2. Edit `work/PROTOCOL.md` — declare the shared contract workers follow
3. Dispatch wave 1 using `assets/dispatch-prompt.template.md`
4. `bash work/status.sh` — anytime, from any session, with no context

---

## The idea in one line

> The unit of durability must be smaller than the unit of dispatch, and state belongs in files rather than in any runtime's memory.

Everything else follows. A worker that flushed its findings has banked them. A worker holding forty minutes of work in context to write one beautiful summary loses all of it when the limit hits.

---

## The six practices

| # | Practice | Why |
|---|---|---|
| 1 | Partition before dispatching | without a written unit list there is no resumption, only restart |
| 2 | One protocol file, not N copies in prompts | short prompts, auditable contract, no drift across workers |
| 3 | Workers flush early and often | the rule that does the actual saving |
| 4 | Status command that works from zero context | turns "where were we?" into one command |
| 5 | Waves with checkpoints between them | the only moment nothing is in flight is the cheapest place to consolidate |
| 6 | Partial completion is first-class | reading the material is the expensive part; if it is recorded, resuming is cheap |

Detail in `SKILL.md`.

---

## Runtime support — read this before running it anywhere but Claude Code

The pattern is runtime-agnostic *by construction*: state lives in files, and files do not care which agent reads them. What differs is narrow — **how work is dispatched, and how completion is detected**.

That second one splits runtimes into two families, and the difference is the whole story.

### Push runtimes — works as written

**Claude Code · Codex · Antigravity**

The runtime notifies the orchestrator when a child finishes. Dispatch, do something else, get told.

- **Claude Code** — reference implementation, no adaptation needed. One caveat: a notification can fire more than once for the same task, and an early one may carry a truncated report while work is still in flight. If a report contradicts the disk, believe the disk.
- **Codex** — worker instructions live in `[agents]` config rather than inline. Point the agent definition at `PROTOCOL.md` and pass only unit id, scope and output path per call — which is what practice 2 wants anyway.
- **Antigravity** — minimal changes. Confirm background subagents survive the parent moving on before using wide waves.

### Cursor — works, with a shape change

Background agents are oriented toward autonomous branch work rather than orchestrated fan-out, and completion surfaces in the agent panel rather than to a driving agent. Two viable shapes: one agent per unit with a human reading `status.sh` between waves, or a single agent looping units in series. The second loses parallelism and keeps every durability property. Start there if unsure.

### Pull runtimes — needs real adaptation

**OpenClaw · Hermes · Gemini-CLI · Kimi CLI · Grok CLI · pi**

These have **no in-process subagent**. Delegation is a shell command launching a child process, and **nothing tells you when it finishes**. Four things change:

**The status script stops being a convenience and becomes infrastructure.** In push runtimes it answers "where are we?" for a human. Here it answers "is the wave done?" for the orchestrator, on a loop, every few seconds. It has to be cheap and correct.

**You need a wait loop with a deadline between waves.** A child that dies silently produces no signal at all — without a deadline the orchestrator waits forever on a corpse. Pattern in `references/runtimes.md`.

**Detect completion from files, not processes.** A live PID does not mean progress; a dead PID does not mean failure, since the worker may have flushed everything and exited cleanly a second before you looked. Workers already write status into their files — read that, and the detection stays consistent with the resume logic.

**Flush harder.** With no notification, the gap between "worker died" and "orchestrator noticed" is your poll interval. Where a push runtime is fine flushing every ten items, flush every three to five here.

**Hermes specifically** has a self-improvement loop that can rewrite its own skills between runs. Pin `PROTOCOL.md` and treat it as read-only input, or a long run ends with different units measured against silently different contracts — which corrupts the aggregate with no error appearing anywhere.

### Any other runtime

Answer three questions and the rest transfers unchanged:

1. **How do I start N things in parallel?** If you cannot, run units in series. You lose throughput and keep every durability property — a legitimate configuration, not a degraded one.
2. **How do I know something finished?** No push signal means you are in the pull family: add the wait loop, shorten flush intervals.
3. **Can a child outlive the parent's turn?** If not, waves must fit inside one turn. Narrow waves, flush often.

---

## What is in the box

```
holdfast/
├── SKILL.md                          the skill itself
├── README.md                         this file
├── scripts/
│   ├── holdfast-init.sh              scaffold a run
│   ├── holdfast-status.sh            state from disk, zero context
│   └── holdfast-collect.py           aggregate, deterministic, re-runnable
├── references/
│   └── runtimes.md                   per-runtime adaptation, in detail
└── assets/
    ├── PROTOCOL.template.md          the shared worker contract
    ├── HANDOFF.template.md           resumable handoff
    ├── dispatch-prompt.template.md   worker prompt shape
    └── resume-prompt.template.md     resume prompt shape
```

---

## Honest limits

**Exercised only on Claude Code.** Everything written about other runtimes is inference from their documented dispatch model — sound reasoning, not evidence.

**No eval suite yet.** The test worth running is blunt: start a wave, kill the session mid-flight, measure what survives. That single experiment is worth more than any amount of reading, and it is the same standard this skill would want applied to anything else claiming resilience.

**It does not make anything faster.** Coordination costs real overhead. What you buy is that the finished part stays finished.

**It does not prevent interruptions.** It changes what they cost.

---

## Three failure modes it will not save you from

**Trusting the report over the disk.** Notifications routinely understate what was saved — a worker reporting that it is "now writing" may already have flushed most of its output. Triaging from notifications redoes completed work. **Always check the disk.**

**A parser that silently drops rows.** Formatting variation in worker output — a bold marker, an extra space — makes a strict regex skip rows without erroring. The rows sit in the file and never reach the aggregate. Have workers emit their own counts so the totals can be cross-checked; `collect.py` does this and warns on mismatch.

**Contaminating workers with unverified context.** Passing your own conclusions as established fact turns independent workers into echoes, and one upstream error propagates into every unit. Pass context as *hypothesis to test* and ask what they refuted. Workers correcting each other — and occasionally retracting their own findings after checking a primary source — is what keeps the aggregate honest.

---

## License

MIT.
