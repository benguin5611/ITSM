# Project binding — the concrete environment + worked instances

This is the quarantine file. Everything project-, stack- and company-specific lives here and **nowhere else** in the skill: the generic `SKILL.md` and the other references stay project-agnostic and point back here. This is the one file to fill in for your project — and the one file to scrub or drop before any public or derived port. Read it once at the start of a real run to bind the generic method to the actual project.

Keep internal identifiers (card numbers, tickets, customer names) out of this file. Refer to any running example by a neutral name.

## The stack the method binds to

Record the concrete stack so the generic phases bind to something real:

- **Backend.** `<your backend language + framework>`, `<your datastore>`, `<how queries are built>`. Note any cross-cutting invariants the method must respect — e.g. how multi-tenant isolation (row-level tenancy, scoping context) is enforced on every request path, and where request/contract validation happens.
- **Frontend.** `<your frontend framework>` across `<your app/packages>`; `<your unit-test runner>`.
- **New vs existing services.** State the rule for new work vs existing — e.g. greenfield prefers `<your preferred contract approach>`, existing services match the pattern they already use. Match the service you are in; don't change a transport on a whim.

## The CI/CD pipeline to mirror locally

List the CI jobs and exactly how to reproduce each one locally. Phase 0 mirrors them so a failure surfaces on your machine, not in the pipeline; Phase 2's loop reruns the relevant ones every increment.

| CI job | What it runs | Mirror locally with |
|---|---|---|
| `<your CI job>` | `<your linter@version>`, `<your test command>` | run the same commands at the **same versions** |
| `<your web job>` | `<install / lint / build>` | the same |
| `<your contract job>` | `<schema lint + breaking-change check>` | the same |
| `<your infra job>` | `<fmt / lint / security scan>` | install the tools, or flag the gap |

- **Match versions, not just commands.** A pinned linter at a different local version gives different findings and a false-green — pin the same version locally.
- **Prefer commands over a CI emulator.** When CI uses bespoke runners or secrets, replicate the **exact commands + versions** rather than reaching for a generic CI emulator; it won't reproduce the bespoke-runner / secret surface and gives misleading results.
- **Record the gaps.** List any job whose tools are **not installed locally** (e.g. an infra security scanner). For changes touching those areas, either install the tools or flag the gap explicitly to the human — don't quietly skip a gate and call CI mirrored.

## The local production-replica

The replica is the truth-teller for Phase 0's environmental pre-mortem and Phase 2's frequent prod-replica testing.

- **Bring it up with `<your command to stand up the replica>`.** Note any process that must be started separately, and any readiness quirk (a probe that's too tight, a service that flaps before it settles).
- **Local test-env gotchas** (these are **environment, not code** — fix the env, never "fix" the code to make them pass): list each one, e.g. an env var that must be **unset** for a subsystem's tests to pass, an API key that must be **present** for full-stack tests, or a feature-flag gate that must be disabled locally.

## Org / policy reminders (non-negotiable in this environment)

Restate the local policies the run must obey, e.g.:

- **Never bypass commit hooks** unless the human explicitly asks.
- **Recoverable deletes only** — use the platform trash, never an unrecoverable delete; matters in Phase 5 archival.
- **No `cd` in automation** — use absolute paths and per-repo git invocation; chained `cd && …` silently bypass deny rules.
- **Secrets files need approval to read and are never committed.** No secret is ever written to a file or committed.
- **House language/style** in everything produced (spelling conventions, terminology).

## Worked instances — each generic lesson, as it actually bit

This is the concrete companion to `references/anti-patterns.md` (A1–A22) and to the lifecycle phases. Leave it empty until the method bites your project — then record each lesson **as it actually happened here**, one short entry per anti-pattern, so the next run on this project inherits the hard-won specifics.

For each entry, capture: which anti-pattern it instances, what you assumed, how the real environment differed, and the fix. A worked instance is worth more than the generic rule because it names the exact coupling, command, or contract that bit *on this project*.

## Review delegation

Phase 3 does **not** review here. It delegates the review to a dedicated multi-lens review pass — a review orchestrator (if your toolkit has one) that grounds, sequences and composes the individual lenses (`rainbow-team-review`, a security-audit skill / `owasp-top-10`, a simplification / dead-code pass) against the real code and arbitrates into one human-in-the-loop verdict. Feed its findings back into the Phase 2 build loop; never re-implement reviewing in this skill.
