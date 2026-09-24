# Phase 2 — build loop

## Before each unit

Four checks, seconds each: is this the right change in the right place; does it already exist in the
repo; which pattern is current — the decision log's, not the nearest file's; and is anything the gate
left open now due. An open decision (`TBD`, `undecided`, "X or Y" in any doc) is a fork: stop, put it
to the human with a recommendation against the whole roadmap, write the answer into the doc, then
code. New information that contradicts a Phase 0 artefact goes back to the gate the same way.

## The loop

Small unit → the binding's gate commands → `driftguard check --staged` → breaking-change oracle if set
→ commit → push only when the human says and everything is green.

A unit is one coherent change you can describe in a line. Hooks are never bypassed; a hook that seems
hung is usually the harness's own tool timeout — raise the timeout, do not diagnose the hooks. After
any interrupted commit, verify the restored tree before trusting it. Run against the replica from the
binding often; tests against your own stubs prove only that the code matches your assumptions.

## The two-tier gate

Tier 1 runs every unit and is entirely mechanical: lint, format, types, tests at pinned versions,
`driftguard`, the breaking-change oracle, adoption census, secret scan. Green is exit 0. Its evidence
is the command output; nothing is written about it.

Tier 2 is scheduled, one build step each with its own `verify_test`: a security review (delegate to
the review skill in the binding), compatibility on the pinned target, regression against named past
findings, interoperability across a live seam on a stated cadence. Each phase in `build_plan.json`
names the step or decision that carries each dimension; an empty key fails `driftguard`. Never invent a
log file to record that a dimension was checked — the step's computed status is the record.

## Three states

A step is open (on the critical path), parked (blocked purely on something outside this project —
needs a `decision_ref`, a ticket in the other team's tracker, and it shows in the index count), or
closed (settled forever). Parked is never conflated with closed; the index surfaces the parked count
so revisiting does not rely on memory.

## Commits and PRs

One logical change per commit; codegen and formatting churn in their own commits, verbatim, never
hand-edited; tests land with the code they cover; never commit secrets, artefacts, debug output or
editor cruft — review `git status` and stage intentionally. Subject: `type(scope): KEY-NNN summary`,
imperative, no full stop; the tracker key from the binding rides every commit and the PR title. The PR
body is a thesis paragraph — what the reviewer should expect and why, proportional to complexity, never
a restated diff or a log. A body that admits a stopgap opens the tracked ID for the real fix in the
same change. Confirm repo visibility before adding any AI attribution trailer; public means none.

Integrate by merging trunk into a shared branch and rebasing only an unpushed one; never rewrite
pushed history. Resolve conflicts by reading both sides; regenerate generated files and diff the
result before staging — content that vanished is the source losing a row, not the generator working.
On a CI failure, pull every job's log and fix everything locally in one pass.

## Scope

Fix what you find when it is small; offer everything larger as a list the human can accept in one
line. A narrow instruction returns exactly the narrow change plus that list. Keep a live TODO list of
units and tick each as it lands; state unprompted what is pending the human's call.
