# Work tracking — issue first, then project the plan onto it

The tracking issue comes **before the code, not after it**. Create the parent record at the gate, so
its ID exists before the first branch is cut and the first commit is written — then every branch,
commit, and PR carries it natively, and the host↔tracker integration links the work from commit one.
Retrofitting an ID onto commits that already exist means rewriting history; creating it first costs
nothing. Concrete tracker, project key and the real card breakdown live in [`project-binding.md`](project-binding.md).

## Two moments, in order

**1. At the discovery gate, before any code — create the parent tracking issue.**
Size it to the work: a single issue for a small change, an **epic** for a feature, a parent story for
something in between. You do not need the full breakdown yet — you need the **ID**. With it you:

- cut the branch with the ID in its name (`TICKET-1234/short-slug`),
- write **every commit** with the ID (prefix or trailer) from the first one, and
- open PRs whose titles carry the ID.

Because the ID predates the first commit, the link is native — no history rewrite, no force-push, no
gap where early work is invisible on the board.

**2. After the spec + PR plan are signed off — flesh out the hierarchy under that parent.**
Now project the signed-off artefacts onto the tracker as children of the issue you already created.
This is a **projection** of artefacts that exist and have been reviewed — not a fresh decomposition
invented in the tracker.

## Principles for the hierarchy

- **Decompose from the spec/PR-plan, never from memory.** The epic *is* the feature; its children are
  the capabilities and build units the spec already names. If tracker and spec disagree, the spec wins.
- **Proportionate scoping.** Match the hierarchy to the work. Resist both over-decomposition (a card
  per file) and under-decomposition (one card for everything). When the tracker offers task *vs*
  sub-task (or story *vs* task), pick the grain the team actually uses; don't agonise over the label.
- **Three levels is usually enough:** **Epic** (the feature) → **Feature/Story** (each user-facing
  capability or workstream) → **Task/Sub-task** (each build unit).
- **Map a review-and-merge workstream 1:1 to the PR plan.** One child workstream "code review and
  merge" whose tasks correspond exactly to the planned PRs, each carrying the PR's scope and merge-order
  note — so the tracker and the git-proven PR split ([`pr-split-method.md`](pr-split-method.md)) stay in
  lockstep.
- **Capture the non-code workstreams too.** Pre-production readiness — provisioning, feature flags,
  secrets, templates, legacy cleanup — is real work. Give it its own feature, or it falls through the
  cracks between "code done" and "shipped".
- **Keep cards lean.** A clear summary and a short prose description beat a ceremony of empty fields.
  Use story points / labels / components / acceptance-criteria fields **only if the team uses them**.
  Convey ordering in prose ("merge after PR3") unless the tracker's blocks/relates links are part of the
  workflow.

## The linking convention (decide it at the gate)

The host↔tracker integration keys off the ID in branch names, commit messages, and PR titles:

- **Branch** name carries the parent ID in the prefix — `TICKET-1234/short-slug`.
- **Commits** carry the ID (prefix or trailer) so individual commits surface on the issue's
  development panel — this is the half that *only* works cheaply if the ID exists before you commit.
- **PR/MR titles** carry the ID so the change auto-links. Use the **parent/epic key** in branch and
  title prefixes; per-PR child keys can go in the PR body for finer linkage.

## Anti-pattern this prevents

See [`anti-patterns.md`](anti-patterns.md) **A20** (tracker created late / reinvented / mis-scoped /
skipped — including the special case where the issue is made *after* code, so early commits carry no ID
and can only be linked by rewriting history).
