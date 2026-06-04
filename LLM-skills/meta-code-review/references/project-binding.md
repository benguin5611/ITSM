# Project binding — the concrete environment the lenses ground against

This is the quarantine file. Everything project-, stack- and company-specific lives here and **nowhere else** in the skill: the generic `SKILL.md` and the other references stay project-agnostic and point back here. This is the one file to fill in for your project — and the one file to scrub or drop before any public or derived port. Read it once at the start of a real run to bind the generic method to the actual project.

Keep internal identifiers (card numbers, tickets, customer names, file:line, exploit detail) out of this file. Refer to any running example by a neutral name; record methodology, not sensitive specifics.

## The stack the lenses assume

Record the concrete stack so the generic lenses and the code-grounding map bind to something real:

- **Backend.** `<your backend language + framework>`, `<your datastore>`, `<how queries are built>`. Note the cross-cutting invariants the review must respect — e.g. how multi-tenant isolation is enforced on every request path (a row-level policy, a scoping context), where request/contract validation happens, and how error codes are preserved across boundaries. The security and dead-code lenses lean on these.
- **Frontend.** `<your frontend framework>` across `<your app/packages>`; `<your unit-test runner>`. Frontend/generated consumers count as blast radius for the discovery gate.
- **Contract surface.** `<how your wire/RPC contract is defined and generated>` — name the generated-marshalling layer, because the API-surface emitter census (A12) keys off it (generated references don't count as live emitters).

## Security lens references

Point the security lens at the concrete reference files for your stack — the stack-specific security-audit skill (e.g. `owasp-top-10`) carries them: the OWASP API/Web lists, the applicable CWE catalogue, and your project's sinks/trust-boundaries catalogue. Record where those live so the workflow's `secRefs` arg can be set. Adversarial role specs live in `rainbow-team-review/references/agents/`.

## Output location and house rules

- **Output artefacts default to `<your working output location>`** (the human chooses; e.g. a repo docs/working folder or a downloads dir).
- **House language/style** in everything produced (spelling conventions, terminology).
- **Never `git push` / publish without explicit permission.**
- **Recoverable deletes only** — use the platform trash, never an unrecoverable delete.
- **Secrets files need approval to read and are never committed.**

## Worked instance — the method working (methodology only)

Leave this empty until the method runs on your project — then record one neutral, sanitised account of a healthy pass, with **no requirement text, IDs, identifiers, or defect specifics** (those live only in the project's own artefacts). The shape of a healthy pass:

1. **Ground.** The code map is regenerated at the current commit and the load-bearing claims spot-checked by hand. Spec claims that turn out stale become corrections (CODE-WINS), not code changes.
2. **Discovery gate.** Assumptions and the new surface are surfaced; a cost estimate is shown; the owner signs off before the heavy fan-out.
3. **Compose.** The adversarial panel, the security sweep, and the dead-code + grudge passes run (the heavy ones via the bundled workflow, every agent deadline-bounded). Findings are de-duplicated and verified against the code.
4. **Resilience pays off.** A stalled synthesis step fails *loud* (bounded) instead of hanging silently — and on inspection the output had often already been written (the guard tripped on a slow return). The lesson is encoded as anti-pattern A1.
5. **Verify.** A headline count reported by a sub-agent is contradicted by a direct recount; the recount (distinct IDs, bullets == rows) is authoritative and the count corrected.
6. **Resolve + finalise.** Open items are put to the owner (recommended option first), the answers baked in as definitive requirements, and the decision record updated so the next pass starts primed.

## Review delegation

The composition layer delegates the actual reviewing to existing skills — `rainbow-team-review`, a stack-specific security-audit skill / `owasp-top-10`, a simplification / dead-code pass — grounds them against the real code, and arbitrates into one human-in-the-loop verdict. Never re-implement reviewing here; meta-code-review is connective tissue only.
