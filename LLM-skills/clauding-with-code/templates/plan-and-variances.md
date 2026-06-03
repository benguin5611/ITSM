<!--
  plan-and-variances.md — the paired working document for building <feature name>
  (clauding-with-code Phase 2: the build loop).

  Two halves that live together:
    - THE PLAN: how you intend to build it — objective, approach, the small-unit build sequence,
      and the discovery-gate outputs the plan rests on.
    - THE VARIANCES / DEVIATION LOG: filled in AS YOU BUILD. Every time reality diverged from the
      plan, record it. This log is the backtrack catalogue — later it feeds the lessons distilled at
      end of run. Do not "tidy away" a deviation by editing the plan to match what happened; the
      whole value is the honest record of what changed and why.

  Keep the plan stable; let the variances log absorb the churn. Australian English. Descriptive
  headings, no numbers — except the variances, which are the numbered entries.
-->

# <feature name> — plan and variances

**Baseline SHA at plan time:** `<HEAD SHA>` · **Branch:** `<branch name>`

## The plan

### Objective

<!-- One or two sentences: what shipping this achieves and what "done" means. -->

`<objective and definition of done>`

### Approach

<!-- The shape of the solution at a glance — the strategy, the key components, the order of attack.
     Not a re-spec; the SPEC.md holds the detail. Just enough that the build sequence below makes
     sense. -->

`<approach>`

### Build sequence (small units)

<!-- The ordered list of small, independently verifiable units. Each obeys the build loop:
       small unit -> lint -> local CI-mirror (fail-fast) -> commit -> push only when green.
     Keep each unit small enough to lint, test, and commit on its own. Tick them off as you go. -->

- [ ] `<unit 1 — smallest sensible slice>`
- [ ] `<unit 2>`
- [ ] `<unit 3>`

### Discovery-gate outputs this plan rests on

<!-- Pointers to the Phase 0 artefacts the plan assumes. If any of these turns out wrong mid-build,
     that is a variance (and may mean looping back to the gate). Reference, do not duplicate. -->

- *Dependency-coupling map:* `<path / summary>`
- *Assumptions register:* `<path / summary>`
- *Environmental / CI pre-mortem:* `<path / summary>`

## Variances / deviation log

<!-- Fill this in continuously as you build. One numbered row PER deviation, at the moment it
     happens. "Planned" = what the plan said; "Actual" = what really happened; "Why" = root cause
     (a wrong assumption? a coupling the gate missed? an environment fact? a better design seen
     mid-build?); "Decision" = what you did about it and who approved if it was a real fork.
     Honesty here is the point — this is the backtrack catalogue that the end-of-run lessons mine. -->

| # | Date | Planned | Actual | Why it diverged | Decision taken (and who approved) |
|---|---|---|---|---|---|
| 1 | `<date>` | `<what the plan said>` | `<what actually happened>` | `<root cause>` | `<decision / approver>` |
| 2 | `<date>` | `<…>` | `<…>` | `<…>` | `<…>` |
