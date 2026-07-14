# Orchestration economy — running a multi-agent fan-out cheaply AND reliably

Multi-agent orchestration is powerful and expensive. Every rule below was paid for in a real failure: a run that timed out, hung silently, burned hours of wall-clock, or re-ran a finished job. The two failure axes are **cost** (wall-clock + tokens) and **reliability** (does it finish, and do you know when it has?). Treat them together — a "comprehensive" run that stalls at hour three is the worst of both. (Process only — record your worked instance with real numbers in `references/project-binding.md`.)

## 1. Budget up front — cost is a first-class constraint
**Why:** an unbounded "be thorough" instinct produced a ~178-agent, ~5-hour run for one feature. It was not 178 agents' worth of signal; it was an order of magnitude past the point of diminishing returns, and most of the cost was queue tail and duplicated reads.
**Rule:** agree an agent budget with the human *before* launch, and right-size every fan-out to it. Default an order of magnitude **cheaper** than a notional "comprehensive" run — a high-signal subset, inputs batched per agent, one worker per unit of work. Reserve the heavy modes — mine-everything finders, multi-vote verification, large finder pools — for **explicit opt-in** with a cost estimate shown. "Mine the whole journey" governs what you READ, not how many agents you spawn: a few agents reading widely beats many agents each reading a sliver.

## 2. Never let a deadline timer count queue time
**Why:** the runtime caps true concurrency. Submitting 100+ agents at once runs ~10 and queues the rest — the queueing itself is harmless (the harness schedules them as slots free up and every call completes). The failure is **self-inflicted**: a hand-rolled deadline timer wrapped around the call starts ticking at *submission*, so the queued tail burns its whole deadline *waiting for a slot*, which presents as a mass timeout that looks like the agents hung. They never started.
**Rule:** the deadline clock on a worker should only ever cover *its own execution*, never time spent queued behind other workers. Achieve that one of two ways: make the deadline generous enough to absorb worst-case queue time, or feed work in **waves** of roughly the concurrency cap (~10) so every agent in a wave starts executing immediately and its timer covers only its own run. If you bound nothing by hand, just submit the fan-out whole and let the harness schedule it.

## 3. Decompose read-all / write-all MONOLITHS
**Why:** one agent told to read everything *and* write everything will blow any deadline — not because it hung, but because it is genuinely doing 20+ minutes of work in a single bounded step. Lengthening its deadline does not help; the work is simply too big for one agent and one turn.
**Rule:** split the monolith into a bounded **PLANNER** plus fanned-out **WRITERS**:
- The planner reads only *compact summaries* and decides the structure / the change-list / the partition of work. It is small, fast, and a single point of failure (guard it — see §4).
- The writers are fanned out **in waves** (§2); each reads only **its own slice** and produces one unit of output.
- A cheap downstream **reassembly** step stitches the units into the manifest the rest of the pipeline expects.
The same split rescues an *overloaded* agent that bundles two heavy jobs (e.g. a deep review AND a large adjudication): break it into bounded halves run in parallel — each lighter, overlapping in wall-clock — rather than serialising both into one step.

## 4. Deadlines are coarse backstops, NOT the stall detector
**Why:** a fixed elapsed-time timer cannot tell *slow-but-alive* from *hung*. It false-alarms on a legitimately long step, and on a fan-out it wrongly counts **queue time** against a worker that has not started. A deadline that is tight enough to catch a real hang quickly will also kill healthy long-running work; a deadline loose enough to never false-alarm cannot catch a hang promptly. You cannot win this with a timer alone.
**Rule:** make the deadline a **generous backstop** — long enough that tripping it genuinely means *something is wrong*, used only to convert a true hang into a loud abort. The real stall detector is a separate **liveness watchdog** that judges by **progress**, not elapsed time: are output artefacts still growing? are agent transcripts still gaining events? It classifies each step as *complete* / *slow-but-alive* (artefacts or transcripts still changing — leave it) / *genuinely idle* (no writes, no events — intervene).
**Crucial:** the watchdog must be a **harness-managed scheduled wake-up** (a deferred re-invocation), **NOT** a long-lived background shell loop. Background loops get reaped mid-watch — a host/IDE restart or session churn kills them silently, and then nothing is watching at the moment it matters.

## 5. A loud abort is NOT proof the work wasn't done
**Why:** an agent can finish writing its entire output and then overrun only on its **return** — the artefact is already on disk when the deadline trips. A real synthesis step did exactly this: it aborted loudly, looked like a failure, and the complete output was sitting in the output directory the whole time. Blindly re-running re-did finished work (cost) and risked clobbering a good artefact (reliability).
**Rule:** on any `FAIL-FAST` / deadline abort, **inspect the artefact on disk first**. If the expected output exists and is complete, the step succeeded — record it and move on. Only re-run once you have confirmed the output is missing or partial.

## 6. Resume mechanics — confirm DEATH, re-pass inputs, diagnose first
**Why:** several distinct foot-guns, each seen live:
- A resume **re-evaluates the whole script top-to-bottom**. If inputs/args lived only in the launching call, the resumed run loses them and fails differently.
- An IDE/host restart kills background tasks, and a killed task's *started* events **linger as phantom "in-flight" entries**. Reading the in-flight count says "still running" when nothing is. Judging liveness by that count resumes on top of a run that is actually dead — or refuses to resume one that is.
- Blindly resuming into the **same unguarded failure** just re-hangs the same step, twice over, burning the budget again.
**Rule:**
1. Workflow scripts have **no filesystem access** — a script cannot read its inputs back from a file. **Bake config into the script file itself** (the harness persists every invocation's script under the session directory — edit that copy and relaunch via `scriptPath`), and **re-pass `args` verbatim alongside `resumeFromRunId`**.
2. Before resuming, confirm the prior run is **genuinely dead** — judge by *recent file writes / transcript events*, never by the in-flight count (which lies after a host restart).
3. **Never resume blindly into the same failure twice.** Diagnose first: bound the unbounded step, split the monolith (§3), or fix the input — *then* resume. A resume from cache replays completed agents and re-runs only the failed step, so the fix is cheap once you know what it is.

## 7. Finish the tail cheap
**Why:** a heavy run that has already delivered ~95% with a small tail still failing (a couple of slices that flaked, one writer that timed out) tempts a full re-run "to be safe". The re-run pays the entire monolith cost to recover a few percent.
**Rule:** complete the tail with **one or two targeted agents** scoped to exactly the missing units — or finish it **by hand** if it is trivial. Reassemble against the existing 95%. Never re-run the whole monolith to recover a small tail.

## Quick checklist before you launch a fan-out
- [ ] Agent budget agreed with the human; default an order of magnitude below "comprehensive"; heavy modes opt-in only.
- [ ] Inputs batched per agent (one worker per unit), not one agent per artefact.
- [ ] No deadline timer can count queue time — generous backstops, or waves (~10) so a timer covers only its own run.
- [ ] No read-all/write-all monolith — split into planner + waved writers + reassembly.
- [ ] Every fan-out `agent()` deadline-bounded (degrade-to-null in a barrier); every sequential single-point-of-failure step guarded (deadline → retry once → loud abort with a resume hint).
- [ ] Deadlines are generous backstops; a **progress** watchdog (harness wake-up, not a bash loop) is the real stall detector.
- [ ] Resume plan: config baked into the script; `args` re-passed verbatim with `resumeFromRunId`; confirm death by recent writes (not in-flight count); diagnose before any second resume.
- [ ] On a loud abort, inspect the artefact on disk before re-running.
