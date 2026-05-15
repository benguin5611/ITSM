---
name: business-case
description: >
  Write structured business cases that compare options, evaluate trade-offs, and recommend a path forward for decision-makers. Use this skill whenever someone asks to "write a business case", "evaluate options", "compare vendors", "compare tools", "justify a purchase", "vendor comparison", "cost comparison", "should we buy X or Y", "make a recommendation", "options analysis", "help me choose between", "I need to present options to [CIO/CEO/CFO/board]", or needs to formalise any decision for leadership approval — whether SaaS tools, infrastructure, services, vendors, processes, or strategies.
---

# Business Case Writer

A structured workflow for building defensible business cases. Works for any domain: SaaS tools, infrastructure, vendors, services, processes, or strategic decisions.

The skill prevents the most common business case failures: discovering requirements too late, comparing options at the wrong level of detail, and presenting more options than necessary.

---

## Before You Start

Read `references/anti-patterns.md` — it's a short list of mistakes that waste iterations. Knowing them upfront saves hours of rework.

---

## Phase 1: Requirements Interview

**Do this before any research.** The single biggest cause of business case rework is discovering a requirement after the analysis is complete.

The reference file `references/requirements-interview.md` has the complete question set including domain-specific probes for SaaS, network security, infrastructure, and process decisions. The questions below are the minimum — always ask at least these, and consult the reference file for deeper coverage.

### Current State (what exists today)
- What tools/services/processes are in place for this?
- What plan/tier/version? What does it cost today?
- Who uses each tool? Employees only, or external users too?
- What depends on it? (other systems, integrations, workflows)
- What's working? What isn't?

### Decision Context
- What's the single most important factor: cost, simplicity, compliance, capability, single vendor, zero migration, or something else?
- Who is the audience for this document? (CIO, CFO, board, team lead)
- Is there a budget ceiling?
- What's the timeline — urgent, weeks, months?
- Is there an existing vendor relationship? (sales contacts, quotes, trials, contracts)

### Hard Requirements
- Walk through each requirement and ask: "Is this a must-have or a nice-to-have?"
- For each must-have, ask: "What specifically would satisfy this?" (not just "audit logging" — what retention, what format, what types?)
- Probe for hidden requirements by asking about:
  - Integration needs (IdP, MDM, SIEM, APIs, specific SaaS tools)
  - Compliance frameworks (ISO 27001, SOC 2, HIPAA, PCI-DSS, GDPR)
  - Access patterns (static IPs, egress requirements, geo-restrictions)
  - User types (technical vs non-technical, contractors, partners)
  - Data residency or sovereignty
  - Migration effort tolerance

### Decision Criteria
Before proceeding, confirm: **"Of all these requirements, what would you weigh most heavily when choosing between options that all meet the must-haves?"** This becomes the tiebreaker in the recommendation.

### Output
Document requirements as two lists:
- **Must-have (R1, R2, ...):** Each with a specific, testable definition
- **Nice-to-have (N1, N2, ...):** Each clearly labeled as non-blocking

---

## Phase 2: Research

Only start research after Phase 1 is complete.

### For vendor/tool comparisons:
1. Use `web_search` to find each option's **pricing page** and **documentation site** (not marketing pages)
2. For every capability claim, find the specific documentation page and note the URL
3. Use the vendor's **current official product name** — verify on their website
4. Record per-plan/tier: name, price, feature matrix
5. Flag anything that needs reconfirmation (stale quotes, trial pricing, "contact sales" features)

### For process/strategy comparisons:
1. Research industry benchmarks, case studies, and best practices
2. Quantify costs where possible (labour hours, tool costs, opportunity cost)
3. Identify precedents — has a similar organisation made this decision publicly?

### Source discipline:
- Every factual claim should have a source URL — this makes the document defensible when challenged
- Distinguish between vendor documentation (reliable) and marketing copy (verify)
- Note the date of any pricing information
- Flag "contact sales" pricing as unknown, not estimated

---

## Phase 3: Qualify, Then Compare

### Step 1: Build the qualification matrix

Create a table with every option as a column and **every must-have requirement as a row** — including requirements that all options meet. The table should be self-contained so a reader doesn't need to cross-reference prose to understand the full picture.

Mark each cell:
- ✅ Confirmed (with source)
- ❌ Does not meet
- ⚠️ Partially meets (explain)

Only options that pass every must-have requirement proceed to the head-to-head. If an option fails a single must-have, it appears in the qualification matrix but doesn't get detailed analysis.

### Step 2: Frame the investment level

Separately from the qualification matrix, frame options across four tiers of ambition. These represent how much change the organisation is willing to accept — not specific products. Specific options slot into the appropriate tier.

- **Do Nothing** — accept the status quo. Document the current cost and the risks of inaction. This is the baseline.
- **Do Something** — the minimum viable change that addresses the most urgent problem, even if it doesn't solve everything. Buys time or removes the biggest risk.
- **Do Many Things** — a comprehensive solution that meets all or most must-have requirements. Typically where the recommendation lands.
- **Do Everything** — the maximum investment option. Meets all requirements plus nice-to-haves. Anchors the recommended tier as proportionate.

The qualification matrix and the investment spectrum are separate sections in the document because they answer different questions — one is analytical (which plans pass), the other is strategic (what level of commitment).

### Step 3: Head-to-head comparison

Read `references/comparison-guide.md` for the methodology.

Build **a single consolidated table** with bold dimension headers grouping the rows. All viable options as columns. Cover **every requirement** — including ones where options are equivalent, so the reader doesn't have to wonder whether you forgot something or it genuinely didn't matter.

The core rule: **specifics, not checkmarks.** Every cell should contain concrete details (retention periods, protocols, mechanisms, effort estimates) rather than ✅/❌ markers.

The table should include:
- One dimension group per must-have requirement (R1, R2, ... Rn)
- An "Operational" group (setup effort, migration, support, pricing)
- A "Nice-to-Have Coverage" group (N1, N2, ... Nn)

### Step 4: Cross-check

Before proceeding, verify:
- Does every prose claim match the comparison table?
- Is every option label accurate? ("Standalone" = one vendor. "Hybrid" = 2+ tools.)
- Does the "Do Nothing" option have a cost? (It's never $0 if something is already in place.)

---

## Phase 4: Assemble the Document

Phase 3 covered how to build each component. This phase covers how to assemble them into the final document.

Read `references/document-template.md` for the full structure. The target table of contents:

```
1. Executive summary
2. Problem statement
3. Risks
4. Requirements
5. Suitable options
6. Investment level
7. Head-to-head comparison
8. Recommendation
   8.1 Primary
   8.2 Secondary
   8.3 Tertiary
9. Next steps
Appendix A - Sources
```

Key principles:

- **Executive summary written last** — it summarises the analysis, not the other way around
- **Executive summary states who won the head-to-head** — even if the recommendation differs due to cost or other criteria. The reader deserves to know the full picture, not just the conclusion.
- **Problem statement is narrative prose** — tell the story of how the current state came to be, what's at stake, and why action is needed now. A table supports the narrative but doesn't replace it.
- **Risks before requirements** — establishes urgency before the reader commits to the analysis
- **Qualification and investment are separate sections** — they answer different questions
- **No duplicate analysis** — if it's in the comparison table, don't restate it in prose
- **Recommendation uses conditional sequencing** — primary/secondary/tertiary, with the conditions for shifting between them stated explicitly. The conditions should be dynamic — tied to whatever uncertainties exist in the analysis (pricing confirmation, migration feasibility, quote competitiveness, trial outcomes, stakeholder approval, timeline constraints, etc.), not hardcoded to any single factor.

### Anti-patterns to check before sharing

Run through `references/anti-patterns.md` as a final checklist.

---

## Phase 5: Deliver

Once the user confirms the business case content is final, ask where they want it delivered. Do not assume a destination — ask.

**Prompt the user:**
> "The business case is ready. Where would you like it published?"

Offer the following options based on available tools:
- **Confluence** — create a page using the Atlassian tools (if available)
- **Google Docs** — create via Google Drive tools (if available), or offer the content for copy-paste
- **Word document (.docx)** — generate using the docx skill
- **Markdown file (.md)** — save to outputs and present
- **PDF** — generate using the pdf skill
- **Slack** — post a summary with a link to the full document (if published elsewhere first)

If the user names a destination not listed, accommodate it. The content is format-agnostic — it's structured markdown that converts to any output.

For any destination, offer to also post a summary to Slack linking to the full document.

---

## Modes of Operation

Not every request needs the full 5-phase workflow. Match the user's intent:

| User says | Mode |
|---|---|
| "Write a business case for X" / "Help me decide between X and Y" | Full workflow (Phases 1–5) |
| "Compare X vs Y" / "What are the differences between X and Y" | Phases 1–3 only (comparison, no formal document) |
| "Update the business case with new information" | Phase 4 only (revise existing document) |
| "Publish / export the business case" | Phase 5 only (ask for format) |
| "I already know the requirements, just compare these options" | Skip Phase 1, confirm requirements, then Phases 2–5 |

---

## Sub-Agent Validation (Optional)

If the user wants vendor-specific validation, offer to spawn sub-agents acting as each vendor's Solution Architect and Sales Executive. Each reviews the business case for accuracy of claims about their product. This catches errors in capability descriptions, pricing, and plan-tier attribution.

After sub-agent review, incorporate corrections before publishing. Flag any claim that a vendor disputes with both perspectives.

---

## Style reference

Business cases are formal documents read by executives. The style guide is in `references/style-reference.md` — sentence-case headings, minimal punctuation, banned filler phrases, no contractions in formal documents. **Read it before drafting**, and apply it to the final document regardless of how the user phrased their input.

Business-case-specific notes that build on the reference:

- Treat business cases as "formal documents" per the reference — no contractions (`do not`, not `don't`).
- Table cells and constrained columns can use the short date format; body text uses the long form.
- Recommendations use active voice and name the decision-maker.

---

## Key Principles

1. **Requirements before research.** Never start evaluating options before you know what "good" looks like.
2. **Qualify before comparing.** Don't waste pages on options that fail a must-have.
3. **Specifics, not checkmarks.** The head-to-head comparison is the centrepiece of the document.
4. **Cite everything.** Every factual claim needs a source URL.
5. **Fewer options is better.** 2–3 well-analysed options beats 7 under-analysed ones.
6. **The recommendation follows the criteria.** If the user said cost matters most, recommend the cheapest option that meets all requirements.
7. **"Do Nothing" always has a cost.** If something is already in place, document what it costs and what risks it carries.
8. **State who won the head-to-head.** The executive summary should be honest about which option is strongest, even if other factors override capability in the final recommendation.
