# Orchestration and cost

`scripts/resilient-workflow.example.js` encodes the mechanics — deadlines that cover only a worker's
own run, waves at the concurrency cap, a budget counter, progress-based liveness, artefact-first
receipts, tail retry with triage, git pre- and post-flight probes, `doneWhen` prerequisites. Use that
shape for any fan-out, from the first one; an unbounded `await agent(...)` is a defect, and guards
retrofitted mid-run never reach the agents already in flight. This file covers what the script cannot
decide for you.

## Whether to fan out

Fan-out earns its keep on independent slices. Dependency-stacked work — each unit needs the previous
unit's shipped result — runs sequentially in the main agent; that is the correct shape, not a
fallback. State which you picked and why before launching either.

## Budget and tier

The human picks a size intent, never a number. Derive the agent count from the plan (slices ×
attempts + overhead), cap it at the preset, log the cost frame before spending and the spend per
wave, log what was dropped. Route the tier per task and say why at spawn: mechanical work
(applying a known edit, reconciling a listing) to the cheap tier in the binding; judgement, security,
concurrency and anything touching a destructive gate to the strong tier. Verification and application
of the same finding often sit on opposite sides.

## Every sub-agent's preamble

Terse output. No state-changing git; writes only under the run's output directory, or a per-agent
worktree when repo edits are the job (`parallel-agents.md`). Absolute paths, no `cd`, no shell
expansions — nobody is present to answer a permission prompt. Hand down the doctrine files it needs;
never let it invoke this skill, because checkpoints need the human and orchestration does not nest.
Give it explicit licence to contradict your brief.

## The brief

Your ground-truth brief is the one claim-bearing artefact nobody else verifies, and an error in it
is systematic. Re-derive every number in it by a command whose output you paste. When a worker
contradicts the brief, re-verify before dismissing it.

## Human-gated steps

Position in the dependency graph decides, never the clock. A predictable prerequisite runs live in
the foreground before the fan-out, gated by a probe; every unmet one fails in a single batch before
the planner spends a token. A prerequisite discovered mid-run aborts with the exact command and a
resume hint. Only a step nothing reads may defer to the end-of-run list, and a deferred verification is
reported as unverified.

## Liveness, aborts, resume

Silence is not death and a moving transcript is not life: judge by disk and git evidence — files
changing, commits landing — against a sane expectation for that step. For ad hoc delegation without a
heartbeat file, ask at spawn for interim progress messages. Before discarding an agent, check its
worktree for salvageable commits or diff and adopt them. A loud abort is not proof the work was not
done: check the artefact on disk, read the run journal, then decide. Resume with config baked into
the script and the arguments re-passed; confirm the prior run is dead by recent writes, not the
in-flight count; never resume twice into the same failure — diagnose, bound or split, then resume.

## Context and cost hygiene

Load only the files the phase needs. Sub-agents return summaries and paths, never bodies. Prompt-cache
the invariant context, batch non-interactive bulk, measure tokens per run against a baseline — a run
that balloons is a signal. The largest saving is not doing the work twice: the gate catches a defect
at the unit that introduced it.

## End of run

The journal and transcripts are the flight recorder. Read them before diagnosing an odd result; sweep
them into the archive with the other working artefacts (`landing.md`).
