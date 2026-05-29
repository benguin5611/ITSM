# [Artefact Name] — Decision Record

*This is a template. Replace bracketed placeholders with real content. Italic blocks (like this one) are guidance — delete them once a section is filled in.*

*Companion to [link to the artefact under review — plan, design doc, strategy memo, policy draft, hiring proposal, etc.]. This file is the canonical record of findings raised against the artefact, decisions made, and rationale.*

*The point of this file: when a future review surfaces something that's already been considered, point at this record instead of re-litigating. The skill spawns many agents per pass; their signal-to-noise ratio is typically 1:2 in the first pass, dropping toward 0 false positives by pass 3 if this record is used for anti-noise priming. Maintaining it is what makes that improvement compound.*

---

## 1. Document state

*Metadata for at-a-glance orientation. Keep counts current — they're the quickest health-check of the artefact's review maturity.*

| Field | Value |
|---|---|
| Artefact | `[link or short name]` |
| Last updated | `[YYYY-MM-DD]` |
| Latest pass | `[N]` ([brief descriptor — e.g. "rainbow-team v3, full-artefact-per-agent"]) |
| Applied findings (load-bearing) | `[count]` |
| Standing rejections | `[count]` |
| False positives recorded | `[count]` |
| Accepted residuals | `[count]` |

---

## 2. How to use this file

*Instructions for the two audiences: humans applying the record, and LLMs ingesting it during a fresh review.*

- **Reviewing the artefact?** Read §4 (Applied) and §5 (Standing rejections). If a new finding matches anything in §5, point at this file rather than re-raising. If it matches §4, the change is already in.
- **Running a new adversarial pass?** Read §5 and §7 (Methodology lessons) before kicking off agents. Include §4 and §5 in each agent's context as anti-noise priming ("items confirmed applied / explicitly rejected — do not re-raise without new evidence").
- **Looking up a single finding?** Use the indexes (§4–§6) to find the ID, then read its canonical record in §9. Older IDs are stable — they appear in cross-references and external systems.
- **Adding a new pass?** Append canonical records to §9 with new IDs, update the indexes in §4–§6, and append the pass write-up to §11 (audit trail).
- **For LLM ingestion:** §1–§8 contain the actionable current state. §9 is per-finding detail (read on lookup). §10–§11 are historical (read only for traceability).

---

## 3. ID convention

*Document your ID scheme so future reviewers and LLMs can disambiguate. The convention below is the default that the rainbow-team-review skill produces; adapt as needed.*

| Prefix | Meaning |
|---|---|
| `A1`–`A{n}` | Pass-1 main findings (Critical → Low severity) |
| `N1`–`N{n}` | Pass-1 rejected agent recommendations |
| `Q1`–`Q{n}` | Pass-1 resolved open questions |
| `D1`–`D{n}` | Pass-1 internal consistency / drift fixes |
| `B1`–`B{n}` | Pass-2 applied items |
| `FP1`–`FP{n}` | Pass-2 false positives confirmed |
| `C` / `H*` / `M*` / `L*` | Pass-3 applied (severity-prefixed: Critical / High / Moderate / Low) |
| `P{N}-X*` | Pass-N conflict reconciliations against prior decisions |
| `P{N}-A*` etc. | Pass-N items (prefix for disambiguation when ID schemes collide) |

*If two passes produce IDs that collide (e.g. pass-1 `N1` and pass-3 `N1` referring to different findings), add a pass prefix to disambiguate (`P3-N1`). Do NOT renumber existing IDs — they're cross-referenced from the artefact, commits, tickets, and other records.*

**Status taxonomy:**
- **APPLIED** — change is in the artefact.
- **NO-OP PRESERVE** — finding identified something already in the artefact; no edit needed. Documented as load-bearing.
- **FALSE POSITIVE** — reviewer/agent misread the artefact or supporting evidence. No action.
- **REJECTED (design call)** — considered, decided against. May re-evaluate if context changes.
- **REJECTED (not material)** — considered, deemed not worth the cost. Re-evaluate only on observed need.
- **DEFERRED** — tracked elsewhere; trigger criteria documented in §6.
- **STANDING REJECTION** — explicit "do not re-raise" with reasoning. See §5.

---

## 4. Index — Active applied findings (load-bearing)

*Compact lookup table. Every applied finding gets one row; full detail in §9. Sort by pass then ID.*

| ID | One-line | Severity | Location in artefact |
|---|---|---|---|
| **[ID]** | [brief description of the change made] | [Critical/High/Moderate/Low] | [section/page/component] |
| **[ID]** | [brief description] | [severity] | [location] |

*Example:*

| ID | One-line | Severity | Location in artefact |
|---|---|---|---|
| **A3** | Emergency rollback procedure added to launch plan | High | §4 |
| **B7** | Stakeholder sign-off explicitly required before phase 2 | High | §2 (Approvals) |

---

## 5. Index — Standing rejections (do not re-raise)

*If a future review surfaces any of these, point at this section. Re-raise requires new evidence (new incident, new constraint, new data, observed pattern that wasn't visible before).*

| ID | What NOT to propose | Why rejected |
|---|---|---|
| **[ID]** | [the suggestion that should not be re-raised] | [short rationale — link to evidence or stakeholder decision] |

*Example:*

| ID | What NOT to propose | Why rejected |
|---|---|---|
| **A14** | Pre-draft customer comms templates for every failure mode | Per-incident response is faster than maintaining 12 templates that go stale. Re-evaluate only if a real incident proves the lack of template caused delay. |
| **N3** | Switch from quarterly OKRs to monthly | Leadership team decided cadence based on planning overhead vs. execution velocity in current org. Re-raise only with new data on either side. |

---

## 6. Accepted residuals (re-evaluate on trigger)

*Findings that were surfaced, considered, and accepted as residual risk because the cost of addressing them exceeds the cost of the residual. **Each row needs a trigger** — the specific observable condition that should prompt re-evaluation.*

| ID | Residual | Re-evaluation trigger |
|---|---|---|
| **[ID]** | [the accepted residual risk or limitation] | [the specific observable condition that should re-open this] |

*Example:*

| ID | Residual | Re-evaluation trigger |
|---|---|---|
| **R-VENDOR-LOCK** | Single-vendor dependency on Vendor X for capability Y | Vendor X announces material price increase, OR a competitor matures to feature parity, OR a sourcing audit raises this |
| **R-MANUAL-AUDIT** | Quarterly audit currently relies on operator discipline (no automated check) | Audit finding cites a missed control, OR auditor explicitly flags as concern |

---

## 7. Methodology lessons (load-bearing for future passes)

*Each lesson here was learned the hard way in a prior pass. Apply in future passes. These are reusable across artefacts — they're about HOW to review, not WHAT was reviewed.*

*The rainbow-team-review skill produces several methodology lessons over its passes. Below are the most reusable; add domain-specific ones as you find them.*

### L-FULL-ARTEFACT — every agent gets the full artefact, not a summary

*An orchestrator may be tempted to summarise the artefact to save context tokens for agents. Don't. Agents miss things that the summary glosses over. Examples surface as "agent X claimed the artefact doesn't address Y, but it does on page 14" — Y was in the artefact, just absent from the summary.*

**Apply:** embed the full artefact in every agent prompt. Summaries are for orchestrator narration only.

### L-ANTI-NOISE — prime agents with the standing-rejection list

*By pass 2 or 3, a substantial fraction of agent findings re-raise items already rejected or already applied. This wastes review cycles and creates noise that obscures genuinely new findings.*

**Apply:** include §4 (Applied) and §5 (Standing rejections) of this file in each agent's context, framed as "items confirmed applied / explicitly rejected; do not re-raise without new evidence."

### L-VERIFY-CITATIONS — agents misquote the artefact

*Agents will say "the artefact doesn't address X" or "section 5 says Y" when the artefact does/doesn't. The pattern repeats across passes if not explicitly guarded against. Common failure modes:*

1. **Claimed-missing element** — "the artefact doesn't include rollback steps." Read the cited section verbatim before treating as a finding.
2. **Claimed-broken reference** — "section 5 contradicts section 8." Re-read both before raising.
3. **Claimed-missing data** — "no evidence cited for claim X." Check the evidence registry (§8) and the artefact's footnotes/links.
4. **Claimed-ambiguous statement** — "the artefact is ambiguous on Y." Search the artefact for relevant terms first; agents sometimes miss an entire paragraph that resolves the ambiguity.
5. **Wrong-pattern claim** — "the convention in this org is X, but the artefact uses Y." Check actual practice (other artefacts, documented standards) before raising.

**Apply:** when an agent citation says "X is missing" or "Y is wrong", check the artefact directly before applying the finding. The FP* records in §9 make this easy.

### L-DRIFT-SWEEP — run a post-finding consistency pass

*After the per-finding pass, a second sweep that reads the artefact end-to-end can catch internal inconsistencies (section A says X, section B says Y, they should agree). These are not new findings — they're consistency tails from earlier edits.*

**Apply:** after the per-finding pass, read the artefact looking only for "does this section agree with related sections?" Items found go in §10.

### L-PROCESS-AUTH — "make the accepted changes" excludes questioned items

*When the decision-maker has accepted some findings, rejected others, and questioned a third set, "make the changes" means ONLY the explicitly-accepted set. Questioned items wait for the answer to the question. Orchestrators sometimes apply questioned items because their verification looks solid; this overrides the decision-maker's authority.*

**Apply:** if the decision-maker has questioned an item, don't apply it until they've answered the question. Even if your verification is solid.

### [L-DOMAIN-SPECIFIC] — [add lessons specific to your domain as they emerge]

*Examples:*
- *Code reviews: "verify code citations by re-reading the actual file" — sub-pattern of L-VERIFY-CITATIONS specific to SQL/proto/config misquotes.*
- *Business strategy: "verify financial assumptions against the current model, not last quarter's snapshot".*
- *Policy: "check the current regulatory text, not a paraphrase from a memo".*

---

## 8. Evidence registry

*Source-of-truth pointers that one or more findings cite. Treat as a lookup table; the canonical artefact is whatever the row points to. Generalise from code-fact-registry to whatever evidence your artefact draws on.*

| Source | Fact | Cited by |
|---|---|---|
| `[file:line / document / data source / interview / contract]` | [the specific fact established by this source] | [finding IDs] |

*Examples for different domains:*

| Source | Fact | Cited by |
|---|---|---|
| `pkg/auth/middleware.go:42-58` | Existing auth middleware already enforces tenant isolation | A2, FP1 |
| `Contract: MSA with Vendor X, §7.3` | Termination clause requires 90-day notice | A14 |
| `Customer interview 2026-04-15 (User #42)` | Workflow currently takes 3-4 days end-to-end | A8 |
| `Q1 2026 financial model, sheet "Pricing", row 47` | Margin assumption is 32% on enterprise tier | B5 |
| `Internal RFC-2024-08 (Pricing strategy)` | Decision to bundle SKU A + B was made for retention, not revenue | A21 |

---

## 9. Per-finding canonical records

*The bulk of the document. One block per finding ID. Include: status, severity, location in artefact, what to do if re-raised, history (newest first if multi-pass), source agents/reviewers.*

*Order: group by pass (A1–A{n} first, then B1–B{n}, etc.). Within a pass, sort by severity then numerical order.*

### [ID] — [brief title]
- **Status:** [APPLIED / NO-OP PRESERVE / FALSE POSITIVE / REJECTED / DEFERRED / STANDING REJECTION]
- **Severity:** [Critical / High / Moderate / Low / n/a]
- **Location:** [where in the artefact]
- **If re-raised:** [the specific guidance to apply — what to do, what NOT to do, where to find the evidence]
- **History:** [if multi-pass: newest-first list of changes, with pass IDs]
- **Source:** [which agent / reviewer / stakeholder raised this]
- **Related:** [other finding IDs that touch the same area]

*Example:*

### A3 — Emergency rollback procedure
- **Status:** APPLIED
- **Severity:** High
- **Location:** Artefact §4 (Operational considerations)
- **If re-raised:** Procedure is documented including the specific revert command, the cutoff time for safe rollback, and who has authority to execute. Re-raise only if a real incident exposes a gap.
- **History:** Pass-1 added §4 paragraph; Pass-2 B7 added stakeholder sign-off requirement.
- **Source:** Gold agent (operational lens), pass 1
- **Related:** B7 (stakeholder sign-off)

### A14 — [Standing rejection example]
- **Status:** REJECTED (not material) — see §5
- **Severity:** Moderate
- **If re-raised:** Decision-maker explicitly declined; rationale in §5. Re-raise only with new evidence per §5's trigger.
- **Source:** Yellow agent (UX lens), pass 1

### FP1 — [False positive example]
- **Status:** FALSE POSITIVE
- **Severity:** Critical (claimed)
- **If re-raised:** Agent claimed the artefact lacks rollback procedure; §4 has it. Pattern: agents missed the section. Future agents prone to this should be given §4 line numbers explicitly.
- **Source:** Red agent (failure-mode lens), pass 1

### R-VENDOR-LOCK — [Residual example, named for memorability]
- **Status:** ACCEPTED RESIDUAL — see §6
- **If re-raised:** Cost of mitigation exceeds expected cost of residual at current scale. Trigger criteria in §6.
- **Source:** Black agent (adversarial lens), pass 2

---

## 10. Internal consistency fixes (optional)

*If a drift sweep was conducted, record findings here. These are NOT new design findings — they're places where edits in one section weren't propagated to related sections.*

| ID | Inconsistency | Resolution | Location |
|---|---|---|---|
| **D1** | [Section A said X; section B said Y; they should match] | [What was changed] | [Sections / pages] |

*Example:*

| ID | Inconsistency | Resolution | Location |
|---|---|---|---|
| **D1** | §2 (Approvals) said "VP approval required"; §5 (Process) said "Director approval sufficient" | §5 updated to match §2 — VP approval required for items above threshold | §5 |
| **D2** | Budget number in executive summary didn't match the line-item total | Executive summary corrected to match line items ($2.1M, not $1.8M) | Executive summary |

---

## 11. Audit trail (chronological)

*Brief pass-by-pass record for traceability. Each pass entry references the canonical records in §9; don't duplicate the detail.*

### [YYYY-MM-DD] — Pass 1: [pass type, e.g. "rainbow-team-review + decision-maker verification"]

*Brief narrative (3–5 sentences max). What scope was reviewed, what the headline counts were, what novel lessons emerged.*

*Example:*

> Initial pass against the pre-decision-record artefact. [N] findings raised, [N] applied, [N] false positives, [N] rejected. Signal-to-noise of unverified agent claims was roughly 1:2. Origin of lessons L-VERIFY-CITATIONS and L-DRIFT-SWEEP.

### [YYYY-MM-DD] — Pass 1: drift sweep (optional)

*If a drift sweep was conducted. Record the count of items applied and reference §10.*

### [YYYY-MM-DD] — Pass 2: [pass type]

*Subsequent passes. Note any methodology changes (e.g. "first pass with anti-noise priming"), counts, novel lessons.*

### [YYYY-MM-DD] — [Optional: process correction or restructure entry]

*Record process corrections and structural changes here so a future reader can audit how the record itself evolved.*

---

## Adapting this template

*Notes for the maintainer adapting this template to a non-default context.*

- **Code reviews:** §8 becomes a code-fact registry (file:line). L-VERIFY-CITATIONS specialises to SQL/proto/config-quote verification. Add domain-specific OWASP / dependency / accessibility passes alongside §11.
- **Business strategy:** §8 becomes a source-document registry (contracts, financial models, customer research). L-VERIFY-CITATIONS specialises to "verify financial assumptions against current model". Severity may be money/risk-weighted rather than Critical/High/Moderate/Low.
- **Policy / regulatory:** §8 becomes a regulatory-text registry. Add a compliance pass alongside §11. L-VERIFY-CITATIONS becomes "verify regulatory citations against the current text, not a paraphrase".
- **Hiring / org decisions:** §8 becomes an interview/reference-source registry. Confidentiality matters more — consider redacted IDs in §9 with full detail in a separate access-controlled file.
- **Product launches:** §8 becomes a customer-research + competitive-analysis registry. Add a market-fit pass alongside §11.

*The structure — current-state-first, standing-rejection-second, methodology-lessons-as-first-class, per-finding canonical records, audit-trail-last — is domain-agnostic. Adapt the content; preserve the structure.*
