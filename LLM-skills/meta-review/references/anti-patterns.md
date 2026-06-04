# meta-review — process anti-patterns → pre-build checks

Methodology lessons distilled from running real grounded meta-reviews. Each is a failure mode plus the check that prevents it. (Process only — no project specifics.)

## A1. Silent hang on a single-point-of-failure step (LOAD-BEARING)
**Failure:** a sequential agent with no deadline (typically the final synthesis or a judge) stalls; the run dies with no completion signal and no output, and only a human happening to look notices. Blindly resuming re-runs the same unguarded step and hangs again.
**Worked anti-pattern:** a synthesis step once hung repeatedly; each resume re-wedged the same step. It was only contained once the step was deadline-bounded — at which point the failure became a *loud* abort, and it emerged the work had actually completed (the guard had tripped on a slow *return* after the output was already written).
**Worked anti-pattern (the OVERLOADED agent):** a single `grudge` agent doing a deep adversarial code review *and* adjudicating a large dead-code candidate list blew its 8-min deadline **twice** — but the transcript showed it was *genuinely working* (mid-read, events still growing), not hung. It was simply ~15–20 min of work crammed into one bounded step. Lengthening the deadline treats the symptom; the fix was to **split it into two bounded halves (`grudge-code-review` + `deadcode-adjudicate`) run in parallel** — each lighter, overlapping in wall-clock — then resume from cache so only the two halves + synthesis re-ran. (The bundled `scripts/meta-review.workflow.js` `grudge()` was refactored to this split form for the same reason.)
**Checks:** (1) every fan-out `agent()` is wrapped in `withDeadline()` (degrade-to-null in a barrier); (2) every sequential single-point-of-failure step is wrapped in `critical()` (deadline → retry once → loud abort with a resume hint); an unbounded `await agent(...)` is a defect. (3) On launch, pre-arm an artefact/deadline watchdog that distinguishes *slow-but-alive* (transcripts still being written) from *idle/hung*; use a harness wake-up, not a bash loop (loops get reaped). (4) On a **repeat** stall of the same step, stop resuming — **fix the step**: bound it; split a one-shot synthesis into sectioned writes; or split an *overloaded* agent that bundles two heavy jobs (e.g. code-review + dead-code adjudication) into **bounded parallel halves**. Prefer splitting over merely lengthening the deadline — more time cannot save a step doing 20 min of work, and parallel halves also cut wall-clock. Distinguish *overloaded-but-alive* (transcript still growing → split) from *truly idle* (no events → unbound/wedged). (5) On a loud `FAIL-FAST`, check whether the output was already produced before re-running.

## A2. Relaying a sub-agent's numbers without re-deriving them
**Failure:** the synthesis reports a headline count (requirements, findings, coverage) that does not match the actual artefact; sub-agents miscount and over-claim.
**Check:** independently recount against the finished artefact — requirement bullets **==** coverage rows, zero duplicate IDs, per-section sums **==** headline — before the artefact is called final. Counts are a directive-4 ("verify, don't trust") item, not a formatting detail.

## A3. Grounding too early against a moving target
**Failure:** the code map is regenerated, then the branch moves (new commits, new migrations), and the whole fan-out runs against stale ground truth.
**Check:** regenerate at the *last responsible moment* (right before fan-out) and record the exact commit. If the branch is in flux, get it frozen first, or re-confirm `HEAD` immediately before launch and abort if it moved.

## A4. Re-litigating settled decisions
**Failure:** each pass re-raises decisions the owner already made (masking choices, deliberate residuals), burning effort and eroding trust.
**Check:** maintain ONE canonical decision record; prime every pass with it; a finding that contradicts a settled decision needs new evidence or it is dropped. "This is fine" is a valid outcome — no manufactured findings.

## A5. Open questions left in a "final" deliverable
**Failure:** the definitive doc ships with an open-questions section, so it is not actually decidable.
**Check:** the synthesis returns open items *separately*; put each to the human (recommended option first), bake the answers in as definitive requirements, and record them as resolved decisions. The doc itself carries none.

## A6. Manufactured findings / polish-for-its-own-sake
**Failure:** the review invents issues to look thorough, or recommends churn that changes working code for no behaviour/control gain.
**Check:** apply the engineering-evaluation precedence — secure/privacy-by-design → match existing conventions → no new tools/deps → simplicity. "Does this match existing conventions?" (cite a precedent) and "too much polish" are valid rejections.

## A7. Duplicating the lenses instead of composing them
**Failure:** meta-review re-implements what a sub-skill already does, so its content overlaps and drifts from the source skill.
**Check:** delegate the actual reviewing to the existing skills via the Skill tool / the bundled workflow; meta-review only grounds, sequences, composes, verifies, arbitrates, and carries the record.

## A8. Expensive fan-out before discovery sign-off
**Failure:** a large agent swarm runs before assumptions are surfaced and the human has approved scope and cost.
**Check:** the discovery gate is BLOCKING — surface assumptions, map shared/generic-component coupling, present a cost estimate (agents, tokens), and stop for explicit sign-off before any heavy pass.

## A9. Over-engineered coverage (the EARS-inflation trap)
**Failure:** a requirements/test spec balloons — one feature yields ~160 numbered `shall`s, many re-typing the schema/config they "test", asserting the same behaviour at the query AND handler AND security layer, or testing framework/generated code. Reads thorough; mostly ceremony with poor ROI, and nobody wants to write 130 low-value tests.
**Worked anti-pattern:** a large EARS suite for a single feature was ~30–50% restatement / cross-layer duplication / cosmetics; pruned to the subset carrying behavioural or security signal.
**Check:** run the coverage-ROI gate (`coverage-and-findings.md` §1) — cut restatement, collapse duplicated behaviour to one owning layer, drop framework/getter/UI-removal tests; prefer behavioural + security-property coverage. A big suite for a small feature is a smell; state the prune %.

## A10. Writing tests for features that don't exist
**Failure:** the spec books `TO IMPLEMENT`/`@blocked` requirements for `proposed`/unbuilt primitives (rate-limit, classification, a planned endpoint). They can only be skip-stubs, inflate the "gap" count, and may test code that is never built.
**Check:** never spec/write a test for an unbuilt feature. Put it in a "Future (build-gated)" appendix outside the suite; write it only when the feature ships, then move it in. Build-gated ≠ a coverage gap (`coverage-and-findings.md` §2).

## A11. Scattered findings — no single answer to "what's left?"
**Failure:** findings live across the changeset, the security-findings file, and the decision addendum, so "everything outstanding in one table" takes a painful reconstruction (the human had to ask repeatedly).
**Check:** maintain ONE consolidated findings ledger (`id · category · severity · status · disposition`) from the first pass; every lens writes into it; outstanding work is a one-line filter (`coverage-and-findings.md` §3).

## A12. Dead code by judgement instead of a deterministic emitter census
**Failure:** dead code is left to review agents to *eyeball*, so it survives repeated audits — because "is this ever emitted?" is a **reachability** question you cannot answer by reading. Reading samples; proving a negative ("nothing constructs this") needs an *exhaustive* reference count, not a judgement. Two compounding blind spots: (a) **API-surface dead code** — a proto `oneof` variant or `enum` value is referenced by the *generated* marshalling code, so generic reachability tools (Go's `deadcode`, staticcheck `U1000`) report it **used** and stay silent, and a human reads "wire-contract symbol → public API → load-bearing, leave it"; (b) **migration leftovers** — when a capability moves path A→B, A's types/enum values are orphaned but still *defined* and still *shipped* (into the published contract / OpenAPI), and every point-in-time audit after the move sees a codebase that *looks* coherent.
**Worked anti-pattern (generic):** a feature branch defined two audit-event `oneof` variants — call them `EventTypeA` and `EventTypeB` (the next two wire fields on the event message) — that shipped into the published API contract. After the feature's lifecycle moved those two events onto a dedicated per-entity event timeline, both old variants had **0 non-generated emitters** (nothing in hand-written code ever constructed or set them; only the generated marshalling referenced them). Multiple grounded audits — including a judgement-based dead-code swarm — missed them; the reachability tool reported the enclosing package **clean**, because the generated references made them look used. A deterministic emitter census — enumerate every `oneof` variant + `enum` value, count non-generated/non-test constructors — found them in seconds (0 emitters = dead), and confirmed the new event variants introduced for the replacement timeline were all live (non-zero emitters). The lesson: reachability tools are *fooled* by generated references; an emitter census is not.
**Check:** the dead-code swarm runs a **deterministic emitter census as a mechanical pre-pass** over the API-surface catalogue — enumerate every proto `oneof` variant, `enum` value, and audit-event constant; count **non-generated, non-test** emitters; **zero = dead candidate** for adjudication. Do NOT rely on `deadcode`/staticcheck for API-surface deadness (generated references hide it; those tools cover unexported funcs only — run them too, for that tier). Trigger the census hardest when the changeset **moves a capability between paths**: census the *old* path's types explicitly. It is exhaustive and scriptable — keep it a *counted* step, never an eyeballed slice.
