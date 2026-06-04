# Coverage ROI, build-gated tests & the single findings ledger

Distilled from real test-suite reviews where a ~150-row EARS suite was ~30–50% over-engineered, "what's outstanding?" couldn't be answered in one table, and the suite booked tests for primitives that weren't built. Two disciplines: keep coverage proportionate, and keep findings in one place.

## 0. The final ROI pass — MANDATORY, run last, over EVERY test requirement

This is a **distinct, explicit pass**, not a vibe applied during synthesis. EARS requirements are usually *directionally correct* — each describes a real, sensible behaviour — yet still not worth writing, because the feature doesn't exist yet or the ROI is poor. So once the suite is assembled, walk **every** proposed/surviving test requirement through **two gates, in order**, and record a verdict per row. Do not skip it; "directionally correct" does NOT mean "keep".

- **Gate A — does the feature exist?** Verify the primitive under test is actually built at the grounded HEAD (grep the code; don't trust the spec's status tag). If it is **not** built (a `proposed` rate-limiter, a classification step-up, a planned endpoint, a behaviour decided-against), **DISCARD** it from the suite → either the "Future (build-gated)" appendix (§2), or fold it into the task that builds the feature so the test ships *with* the code. A test for unbuilt code is negative ROI and a false "coverage gap".
- **Gate B — is it worth the effort?** For everything that survives Gate A, apply the ROI gate (§1): **CUT** restatement, cross-layer duplicates, framework/generated-code tests, and trivial cosmetics; **KEEP** behavioural + security-property coverage. When unsure on a marginal row, cut it.

**Required output of the pass:** a keep / cut / appendix verdict for *every* row, the **prune count** ("evaluated N → discarded D (no-feature E, low-ROI F), kept K"), and a one-line reason for any non-obvious cut so the human can audit it. Carry only the survivors into the final artefact, and list them as the actionable test work in the findings ledger (§3). Worked run: 48 candidate rows → 6 discarded (no feature) + 21 discarded (low ROI) + 2 folded into their code tasks → **16 kept**.

The two gates in detail:

## 1. Coverage ROI gate (Gate B) — does this test earn its place?

Apply to every proposed requirement/test. If it trips a REJECT, cut it or collapse it.

**REJECT (cut):**
- **Restatement.** The test just re-types the artefact it's testing — "the migration creates column X" (the migration *is* the spec), "the role grants exactly these procedures", "the allow-list = {this set}". Brittle (breaks on every legitimate change) and adds no behavioural assurance. One "migrations apply + RLS forced" smoke test replaces a dozen DDL-assertion rows.
- **Cross-layer duplication.** The same behaviour asserted at the query layer AND the handler AND the "security" section (e.g. an account-lockout tested 3×). Pick the ONE layer that owns the behaviour; the others reference it.
- **Framework / generated code.** Testing that the request validator validates, that the query layer returns rows, that the ORM maps columns. Not your behaviour.
- **Trivial mappers / cosmetics.** Getter/enum-mapper round-trips; "a UI element was removed"; label/layout/text assertions.

**PREFER (keep):**
- Behavioural assertions (given X, the system does Y) and **security properties** (authz boundaries, masking, row-level *policy* proof under a non-privileged role, concurrency single-winner, crypto cost, output escaping).
- The least-covered, highest-blast-radius surfaces (a new endpoint; a live re-scope path).
- One test per cross-cutting discipline (clock-threading, error-parity) that others reference.

**Smell test:** a ~160-row suite for one feature is over-engineered. Expect to prune 30–50%, and tell the human the number. "Too much polish" / "this is fine" are valid verdicts (do not manufacture coverage).

## 2. Build-gated rule — no tests for unbuilt features

A test for a `proposed` / not-yet-built primitive is a test for code that **may never exist** — negative ROI and a false "coverage gap".

- Do NOT add it as a `TO IMPLEMENT` or `@blocked` suite row.
- Record it in a **"Future (build-gated)" appendix**, outside the suite, naming the feature it gates and its disposition (backlog / proposed / accepted-residual).
- Write the test **only when its feature ships** — then move the row into the relevant section and flip it to `EXISTS`.
- Build-gated ≠ a gap in coverage. The suite's headline counts exclude the appendix.

## 3. The single consolidated findings ledger

Maintain ONE filterable table from the first pass; every finding from every lens lands in it. "What's outstanding?" is then a one-line filter, not a reconstruction across three artefacts. If the human asks twice for "all of it in one table," the ledger failed.

```markdown
| ID | Category | Finding | Severity | Status | Disposition / owner-decision |
|----|----------|---------|----------|--------|------------------------------|
```
- **Category:** security-defect · security-test · spec-correction · complexity · dead-code · coverage · CI/config.
- **Severity:** High / Med / Low / — (for non-severity items).
- **Status:** ✅ done · 🔲 open · ⛔ build-gated · ⏸ dispositioned (backlog/platform/accepted) · — no-action.
- **Disposition:** the owner decision + where it was baked in (commit / req id / addendum entry).

Rules: globally-unique IDs, never reused across passes. Every lens (rainbow, security, dead-code, grudge, simplify) writes into this one table — the per-lens outputs are inputs, not the deliverable. The ledger is what you hand the human and the next agent.
