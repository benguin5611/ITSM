<!--
  SPEC.md — the sceptical-engineer specification for <feature name>.

  This is the ONE authoritative, self-contained spec for the feature (clauding-with-code Phase 1).
  A reviewing engineer should be able to read it top to bottom and finish KNOWING:
    - exactly how the feature works, end to end;
    - that it is correct, secure, and does not break adjacent code;
    - how to verify it (run the tests, locally, including the gotchas);
    - what must be true in production before it ships.

  Fill every section. Delete a section only if you can justify why it does not apply — do not leave
  it blank. Keep it grounded in the real code: every behavioural claim must be checkable against a
  file:line anchor at the baseline SHA below. If prose and code ever disagree, CODE WINS — fix the
  prose. Australian English throughout. Headings are descriptive, never numbered; numbered lists
  are reserved for the end-to-end walkthrough steps and the security finding ledger.
-->

# <feature name> — specification

*One line: what this feature is and the problem it solves.* `<one-sentence purpose>`

**Grounding baseline:** every claim in this document is verified against `<HEAD SHA>` on branch
`<branch name>`. *Code wins:* if this spec and the code at that SHA disagree, the code is the source
of truth and this document is the bug — update it.

## Overview

<!-- The 3–5 sentence orientation for a reader who knows the codebase but not this feature.
     What it does, who/what uses it, where it sits in the system. No implementation detail yet. -->

`<overview>`

## What was built

<!-- The concrete inventory of the change: new/modified endpoints, schema/migrations, jobs,
     config/flags, UI surfaces. Bullet list, each item with its file:line anchor. This is the
     "deliverables" list — a reviewer uses it to scope the diff. -->

- `<thing built>` — `<file:line>`
- `<thing built>` — `<file:line>`

## How it works end to end

<!-- The narrative walkthrough of a request/operation from entry to persistence and back.
     Follow ONE happy-path flow step by step, then the important variants/error paths.
     Anchor each step to code. A reader should be able to trace it in the source as they read. -->

1. `<step>` — `<file:line>`
2. `<step>` — `<file:line>`

*Key variants / error paths:* `<what happens on failure, edge inputs, retries>`

## Why it was built this way

<!-- Design rationale. For each significant decision: state the choice, the trade-off accepted, and
     the alternatives REJECTED and why. This is where you defend the design to a sceptic. Tie back
     to the prime directives (secure-by-design, match conventions, minimise additions, simplest
     thing that works) where relevant. -->

| Decision | Chosen approach | Trade-off accepted | Rejected alternative(s) and why |
|---|---|---|---|
| `<decision>` | `<choice>` | `<cost we accepted>` | `<alternative>` — `<why not>` |

## Architecture and code map

<!-- The map from concept to code. List the components/layers the feature touches and the exact
     files (with line anchors) that implement each. A reviewer uses this to navigate. Include a
     small diagram reference if one exists (e.g. ./architecture.md or an image). -->

| Component / layer | Responsibility | Where it lives |
|---|---|---|
| `<component>` | `<what it does>` | `<file:line>` |

*Diagram:* `<path to architecture diagram, if any>`

## Security posture

<!-- Secure-by-design is prime directive #1. Make the threat model explicit, then the controls,
     then the residual risk you are knowingly accepting. The finding ledger below is ONE continuous,
     numbered list — every security finding raised during design/build/review lands here with its
     status, so there is a single place to see the security story. Do not scatter findings. -->

**Threat model.** *Trust boundaries, who/what can reach this, what an attacker would target.*
`<threat model summary>`

**Controls.** *Authn/authz, tenancy isolation, input validation, secrets handling, rate limiting,
fail-closed behaviour, audit logging — each mapped to where it is enforced.*

| Threat | Control | Enforced at |
|---|---|---|
| `<threat>` | `<control>` | `<file:line>` |

**Accepted residual risks.** *Risks knowingly left in scope, with the reasoning and any sign-off.*

- `<residual risk>` — `<why accepted, by whom>`

**Security finding ledger** *(single continuous list — every finding, any source, with status):*

1. `<finding>` — severity `<…>` — status `<open / fixed @ file:line / accepted>` — `<note>`
2. `<finding>` — severity `<…>` — status `<…>` — `<note>`

## Testing guide

<!-- MANDATORY. Do not ship without this section, and ground it in the REAL test files — not tests
     you wish existed. A reviewer must be able to run the tests from here and trust the coverage.
     If a behaviour is untested, say so in the gap list below rather than implying coverage. -->

**Testing strategy.** *What is covered at each level (unit / integration / production-replica /
e2e) and why that split. What deliberately is and is not tested at each level.*
`<strategy>`

**Requirement → test coverage map.** *Each requirement/behaviour mapped to the test(s) that prove
it. Mark anything unverified honestly.*

| Requirement / behaviour | Test(s) | Where | Status |
|---|---|---|---|
| `<requirement>` | `<test name>` | `<file:line>` | `<covered / partial / NOT covered>` |

**How to run the tests locally.** *The exact commands, in order, plus the environment gotchas a
fresh machine will hit (env vars to set/unset, services that must be up, secrets/keys required,
flags to disable). Be specific enough that someone can copy-paste.*

```
<command to run the suite>
```

*Environment gotchas:* `<e.g. unset VAR X; service Y must be running; key Z required; flag W off>`

**Build-gated / deferred coverage.** *Tests intentionally not yet written because the feature they
cover is not built. Keep these separate from real gaps — they are a forward plan, not a hole.*

- `<deferred test>` — gated on `<unbuilt feature>`

## Pre-production readiness

<!-- Everything that was worked around, stubbed, faked, or assumed in dev/test and MUST be solved
     before this ships. The dev shortcut on one side, the production requirement on the other, and
     who owns closing it. This is the "do not ship until" list. -->

| Worked around in dev/test | Must be true in production | Owner / how to close |
|---|---|---|
| `<dev shortcut>` | `<prod requirement>` | `<owner / action>` |

## How it does not break adjacent code

<!-- Blast radius. What existing behaviour shares code, data, or contracts with this change, and the
     evidence it is unaffected — e.g. unchanged callers, preserved schema/contract, regression tests
     that still pass, breaking-change checks run. A reviewer worried about collateral damage reads
     this. -->

| Adjacent surface | How it could have been affected | Why it is safe (evidence) |
|---|---|---|
| `<adjacent code/data/contract>` | `<risk>` | `<evidence — unchanged caller / passing test / contract check @ file:line>` |

## Landing mechanics

<!-- One line. Landing/PR-split detail lives in its own plan, not here. -->

*PR / landing plan:* `<path to PR plan>`.

## Open concerns a reviewer should still check

<!-- Honest list of things you could not fully close, want a second pair of eyes on, or that depend
     on a human decision. Per house rules, a DEFINITIVE deliverable carries no open questions —
     resolve these with the human and bake the answers in before final sign-off; until then, list
     them plainly here so nothing is hidden. -->

- `<open concern>` — `<what to check, why it is unresolved>`
