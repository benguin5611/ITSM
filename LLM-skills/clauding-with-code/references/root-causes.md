# Root causes

Seven reasons a build goes wrong. Each names the checks that make the failure mechanical rather
than remembered. Load this when a check fails and its output cites an RC. The incidents behind
each are in `lessons.md`.

## RC1 — Run the oracle; a claim is not evidence

A status, a tag, a count, a supersession note or a peer's assertion is a claim until a command
reproduces it. Grep proves only that text is absent; the compiler, the breaking-change linter, the
live test, the third party's own docs are the oracles. Write the tag after the oracle runs.

Enforced by: `DG-DANGLING`, `DG-DUPLICATE`, `DG-TOMBSTONE`; computed build-plan status (merged PR
plus a passing `verify_test`); `DG-CURRENCY`; `DG-REGISTRY-STALE`; the PR-split empty-diff invariant
(`landing.md`); the ADR `Verification` section and the spec `Verification ledger` (`DG-SECTION`).
Absorbs A3 A9 A13 A18 A26 A29 A30 A31 A36 A37 A41 A43 A44 A45 A46 A48 A58 A60 A61 A62 A63 A67 A68.

## RC2 — Forks go to the human

A decision a reasonable person could make differently is a question, not a recommendation to
rubber-stamp. A narrow instruction is itself a decision; a diagnostic question is not authorisation;
a repeated failure shape gets the redesign offered before the patch; a found error is fixed or
explicitly asked about, never noted for someone unnamed.

Enforced by: `Open forks` and `Declined alternatives` required (`DG-SECTION`); `DG-ASSUMPTION`; a
step body saying TBD or undecided with no `decision_ref` (`DG-REGISTRY-ROW`); the checkpoint
protocol in `SKILL.md`; `doneWhen` prerequisites in the resilient workflow.
Absorbs A24 A39 A53 A56 A57 A59.

## RC3 — Shared state is isolated and read live

Two agents on one repo collide on the checkout, the stash, fetched refs, sequential IDs and any
file both append to. Identity, ownership and "is this merged" are live facts from the forge, never a
persisted note.

Enforced by: `DG-HWM` over open and merged PR titles; `DG-REGISTRY-ORPHAN`; `Merge policy` required
in the binding; the worktree, ledger and identity checklist in `parallel-agents.md`; git pre- and
post-flight probes in the resilient workflow.
Absorbs A23 A35 A38 A40 A42 A54 A64.

## RC4 — Fan-out is bounded and artefact-first

Every fanned-out agent has a deadline that covers only its own run, writes its output to disk and
returns a receipt, and is watched for progress, not elapsed time. A missing verdict is reported as
missing, never folded in as a pass.

Enforced by: `scripts/resilient-workflow.example.js` and its test; `driftguard`'s `SKIPPED`
reporting.
Absorbs A5 A6 A7 A8 A14 A47 A52.

## RC5 — Evidence is the artefact that already exists

The merged PR, the command's exit code, the passing test are the evidence. A second file whose only
job is recording that a check happened is checked for its own shape and becomes the rubber stamp it
was built to prevent.

Enforced by: no hand-typed status anywhere (`build_plan.json` → computed `Status`); phase `tier2`
keys required; `Known Gaps` headings and Do/Verify bullets outside the plan banned (`DG-BANNED`);
`Testing guide` required.
Absorbs A11 A28 A32 A33 A49 A50 A66.

## RC6 — IDs are allocated once, link the tracker, and never ship

Every requirement, decision and step has one stable ID with one home. The tracker key exists before
the first commit and rides every branch, commit and PR. IDs are authoring scaffolding: never in
code, comments, runtime strings or commit bodies. Outstanding work is an ID, never a list or a
sentence in a commit.

Enforced by: `DG-LEAK`; `DG-DANGLING`, `DG-DUPLICATE`; `Tracker` required in the binding; `parked`
requires a `decision_ref`; stopgap wording in a PR body without a tracked ID fails the checkpoint.
Absorbs A15 A20 A22 A38 A49 A51 A55 A69.

## RC7 — Mirror the real target

The environment that matters is the one the code will run in: the runner's OS, the pinned tool
versions, real mail and auth, the actual consumers of a contract, the pattern the decision log
currently blesses rather than the nearest file. Name and rename at the gate, because retrofitting a
name cascades through every layer.

Enforced by: `Gate commands` with pins and target OS, and `Breaking-change oracle` required in the
binding; gate `Prior art` (two candidates, builds and tests), `Coupling map`, `Names`, `Contract`
(`DG-SECTION`, `DG-ROW-INCOMPLETE`); `DG-ADOPTION`; `--staged` scoping so a gate judges the diff.
Absorbs A1 A2 A4 A16 A17 A19 A25 A27 A34 A65 A70.
