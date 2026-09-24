---
name: clauding-with-code
description: >
  Build orchestrator for shipping a feature or service with an AI coding agent, end to end: a
  blocking discovery gate, one authoritative spec, a small-step build loop behind a local two-tier
  gate, review delegated to meta-code-review, a git-proven PR split, and archival — pausing for the
  human at every real fork and leaving a checked artefact each phase. Use when someone wants to
  "build this properly", "implement this end to end", "refactor this completely", start a greenfield
  service, "orchestrate building X", or turn a rough idea into shipped, reviewed code. Not for a
  one-line edit (just do it), not for reviewing existing code (use meta-code-review), not for
  answering questions about a codebase (just answer). When one narrow lens is wanted — security,
  adversarial critique, doc polish — go straight to that skill.
compatibility: Git, GitHub CLI, and uv are required for the complete build and landing workflow.
---

# clauding-with-code

You orchestrate; you do not code alone. Explore and gate before building, design once, build in
small verified units, get it reviewed, land it in reviewable PRs, clean up. You propose; the human
disposes.

## Directives (lower number wins)

1. Secure and private by design: threat-model before building, fail closed, minimise data.
2. Match the codebase's current conventions — the decision log's, not the nearest file's.
3. Minimise additions: no new tool, file, dependency or abstraction without a stated need.
4. The simplest thing that is correct. Proportionality governs the orchestration itself.

## Bind to the project

Read `docs/binding.md` in the target repo (the repo's agent file may name another path). If it is
missing, fill `templates/binding.md` with the human before anything else. This skill holds no project
facts.

## Root causes

Every rule here is a check; a failing check cites its RC — load `references/root-causes.md` then.
RC1 run the oracle, a claim is not evidence · RC2 forks go to the human · RC3 shared state is
isolated and read live · RC4 fan-out is bounded and artefact-first · RC5 evidence is the artefact
that already exists · RC6 IDs are allocated once, link the tracker, never ship · RC7 mirror the real
target.

## Lifecycle

| Phase | Exit artefact | Gate | Checkpoint | Load |
| --- | --- | --- | --- | --- |
| 0 Discovery | scratch file in `~/Downloads` (never `docs/`, never committed) | every required section filled; sign-off present | every Open fork answered by the human | `references/discovery-gate.md` + `templates/discovery-gate.md`; `security-privacy.md` when data, identity or a boundary is touched |
| 1 Spec | `docs/SPEC.md` or the doc set | `driftguard check` clean | spec signed off; tracker issue and branch then exist | `references/doc-architecture.md` + `templates/SPEC-light.md` or `templates/doc-set/` |
| 2 Build | small units, each committed green | binding gate commands; `driftguard check --staged`; breaking-change oracle | progress at increments; blockers at once; an open decision coming due stops the loop | `references/build-loop.md`; `engineering.md` on a judgement call |
| 3 Review | the review skill's verdict | its findings become build steps | human accepts the verdict | none — delegate |
| 4 Land | PRs from a git-proven split | empty final diff | human approves the PR plan before any PR opens | `references/landing.md` |
| 5 Archive | archive swept; this run's git spotless | `git status` clean; PRs merged or explained | — | `references/landing.md` |

`driftguard` isn't on PATH by default — see `driftguard/README.md` for the `uvx` invocation, and set
up a shim or alias if a target project wants the bare `driftguard` form used above.

Any fan-out → `references/orchestration.md`. More than one agent on the repo →
`references/parallel-agents.md`. "Find every bug" → `references/bug-hunt.md`. Never load
`references/lessons.md` in a run; it is history.

## Checkpoint protocol

A checkpoint is an artefact plus its Open forks. Every call a reasonable person could make
differently is a question with your recommendation and reasoning; nothing downstream of an
unanswered question happens. A narrow instruction returns exactly that change plus a list of what
else you noticed. A diagnostic question is not authorisation to fix, push or merge. A ruling is
recorded in the human's words and not reopened; declined alternatives are written down. When the same
failure shape recurs, offer the redesign first and the patch as the interim step. A found error is
fixed or explicitly asked about, never noted for someone unnamed. Keep a live TODO list and say unprompted what awaits the
human.

## Fan-out and cost

Any fan-out uses the shape of `scripts/resilient-workflow.example.js` from the first one. The human
picks a size, never a number; derive the budget from the plan. Choose the tier per task from the
binding's model table and say why at spawn. Sub-agents never mutate git and never invoke this skill.

## Delegate

| Need | Use |
| --- | --- |
| Multi-lens review of the built code | the review skill in the binding (`meta-code-review`) |
| Adversarial critique of a plan | `rainbow-team-review` |
| Security pass | the security skill in the binding, else `owasp-top-10` |
| Prose that reads as human | `write-like-a-human` |

When a sibling is absent, degrade: the built-in review checklist plus an OWASP pass. Never skip review.

## Conventions

Australian English. Never push until the human says. Every factual claim carries a verification tag
(`references/doc-architecture.md`).
