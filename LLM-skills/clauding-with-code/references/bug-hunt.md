# Bug hunt — find every bug, then fix through the normal loop

For "find every bug in this codebase", not for reviewing a diff (delegate that). Two phases, both
fan-outs under `orchestration.md`'s rules.

## Hunt

Start with the bug registry if the project has one: run every row's `detection_check` first — a known
class is re-found in seconds, not by an agent spending a pass. Cluster the codebase by module into
slices one agent can read closely; note which clusters share files, you need that in the fix phase.
Run it as a loop-until-dry workflow from round one (per-cluster dry-streak tracking, watchdog),
paired with a hard round or wall-clock cap agreed up front — a large surface keeps yielding a fresh
file long after the easy bugs are gone. Findings live in one ledger file on disk that every agent
reads before hunting and appends to; it survives compaction where conversation does not.

Size hunt/verify deadlines PER CLUSTER from the planner's estimate — reuse
`resilient-workflow.example.js`'s `msFor` (2x estimate, floored, capped), never a flat deadline for
every cluster. A worked example of the loop's control flow (per-cluster dry-streak, timeout never
counted as dry, adversarial verification batched per cluster) lives at
`scripts/workflow-loop-until-dry.example.js` — add the watchdog/`msFor` sizing on top of it for a run
large enough to need one. The harness can't kill an in-flight agent: a deadline only stops the script waiting, the
real call keeps running and holds a concurrency slot — an abandoned call becomes a zombie the next
round queues behind. Hit live: flat 6-minute deadlines against 15-40-file clusters silently zeroed an
entire run's findings and its report call, no error surfaced. Don't skip the watchdog just because
deadlines look generous — check the planner's estimates first; watchdog catches a genuinely dead
worker early, deadline is only the last-resort backstop for a misestimated one.

Verify inside the loop. Feeding recurring shapes back as a checklist speeds the hunt and breeds
confirmation bias; verify a taxonomy-guided round before compounding another on it. Verification is
its own adversarial fan-out: one agent per cluster gives every finding CONFIRMED / INVALID / PARTIAL,
defaulting to sceptical. Report the hit rate plainly; a low rate says narrow the taxonomy, not hunt
harder. A confirmed finding that recurs graduates into `bug_registry.json` (class, locations,
`detection_check`, later the `regression_test`); a genuine one-off stays in the ledger.

Any dedup or collision check against the forge pulls full history; a page-limited query reads as
clear when the match is older than the window.

## Fix

Each fix is normal build-loop work: one agent per cluster in its own worktree, IDs reserved before
anyone writes, the same gate every unit runs, landed through the git-proven split. Decide disjoint /
dependent / overlapping from the shared-file note before dispatch. Use the multi-signal liveness check
and salvage before restarting. Closing a registry row is part of the fix's own PR: cite the passing
regression test and `driftguard write bugs` flips its status; a class the team will not fix gets a
`decision_ref` instead — a row with neither fails the gate. A finding that needs a design call becomes
its own tracked step with the question stated, never a silent drop or an arbitrary answer.
