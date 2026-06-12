# Business Case Document Template

This is the target output structure. Not every section is mandatory — scale to the complexity of the decision. A comparison between 2 SaaS tools might skip the risk table. A major infrastructure decision might need every section.

---

## Structure

### 1. Executive Summary
Write this LAST. It should:
- State the problem in one sentence
- State what was evaluated
- State who won the head-to-head comparison (be honest — this may not be the recommended option if cost or other criteria override capability)
- State the recommendation as primary / secondary / tertiary with costs
- State the immediate next step

The executive summary must stand alone — a reader who only reads this section should understand the recommendation, why it's the recommendation, and what the stronger alternative is if circumstances change.

### 2. Problem Statement
**Narrative prose** — not a table with bullet points. Tell the story:
- How did the current setup come to be? (usually: organically, without formal evaluation)
- What tools are in place, on what plans, at what cost?
- What depends on them? What breaks if they fail?
- What are the specific problems? (fragility, compliance gaps, scalability limits)
- Why act now?

Support the narrative with a current-state table (tool / plan / status), but the table supports the story — it doesn't replace it.

### 3. Risks
Place risks early — before the analysis — to establish urgency. The reader should understand what's at stake before committing to reading the full evaluation.

| **Risk** | **Impact** | **Mitigation** |
|---|---|---|
| [Risk] | HIGH/MED/LOW | [Specific mitigation action] |

Only include risks that could change the recommendation or block implementation.

### 4. Requirements
Two bullet-point lists:
- **Must-have (R1, R2, ...):** Each with a brief, specific definition
- **Nice-to-have (N1, N2, ...):** Each clearly labelled as non-blocking

End with the decision criteria: what the user identified as the most important factors when choosing between options that all meet the must-haves.

### 5. Suitable Options (Qualification Matrix)
A table showing **all evaluated options** against **all must-have requirements**. Include requirements that every option passes — the table should be self-contained.

Below the table, a brief paragraph stating how many options qualify and what the key disqualifying factor is.

### 6. Investment Level
Frame options across four tiers of ambition:

| **Tier** | **Option** | **Annual Cost** | **R1–Rn?** | **Key trade-off** |
|---|---|---|---|---|
| Do Nothing | [Status quo] | [current cost] | ❌ | [primary risk] |
| Do Something | [Minimum change] | [cost] | ❌ | [what it fixes and what it misses] |
| **Do Many Things** | **[Recommended]** | **[cost]** | **✅** | **[one-line trade-off]** |
| Do Everything | [Maximum option] | [cost] | ✅ | [why it's more than needed] |

The tiers justify the recommended level of investment: "we're not under-investing (Do Something won't meet compliance) and not over-investing (Do Everything is disproportionate for our scale)."

### 7. Head-to-Head Comparison
A single consolidated table with bold dimension headers. All viable options as columns. Covers every requirement, operational dimensions, and nice-to-have coverage. See `references/comparison-guide.md`.

### 8. Recommendation
Three components:

**Head-to-head summary:** 1–2 sentences stating which option won the comparison and on what dimensions. Be honest — if the recommended option lost the head-to-head, say so and explain what overrides it.

**Decision criteria reference:** Restate the criteria from Section 4 and show how they apply.

**Primary / Secondary / Tertiary:**

Each recommendation tier should name the option, state the cost, explain why it's at this priority level, and state the **condition** that would shift the decision to the next tier. Conditions should be dynamic — tied to whatever uncertainties exist:

- Pricing confirmation ("contingent on reconfirming the sales offer")
- Quote competitiveness ("if the quote comes in at or below $X")
- Migration feasibility ("if the prototype validates the migration path")
- Trial outcomes ("if the trial confirms operational fit")
- Timeline pressure ("if the vendor can't deliver within the required timeframe")
- Stakeholder approval ("if leadership approves the migration effort")

The conditions connect the tiers into a decision tree, not a static ranked list.

### 9. Next Steps
A table of specific actions. Owners and timelines are optional — they may belong in a project plan or Jira tickets rather than the business case itself.

| # | Action |
|---|---|
| 1 | [Specific action] |
| 2 | [Specific action] |

### 10. Sources
A single flat table. Fold everything into one place — Slack thread context, sales email evidence, vendor documentation links, pricing pages.

| **Topic** | **Links / Notes** |
|---|---|
| [Topic] | [URL or description] |

---

## Formatting Guidelines

- **Tables over prose** for structured data
- **Prose over tables** for the problem statement and recommendation narrative
- **Bullet points for requirements** — not tables, not paragraphs
- **Bold the recommended option** in summary tables
- **Link every source** — vendor docs, pricing pages, community posts
- **Date the document** — include "Prepared by" and date at the top
- **Use the vendor's official product name** — check their website

---

## Scaling Guidelines

| Decision size | Expected length | Sections to include |
|---|---|---|
| Quick comparison (2 tools, known requirements) | 1–2 pages | Exec summary, comparison table, recommendation |
| Standard business case (3+ options, formal approval) | 3–6 pages | All sections except risks (if risks are low) |
| Major infrastructure decision (high cost, many stakeholders) | 6–10 pages | All sections, detailed risks, full sources |

The document should be as short as it can be while remaining defensible. If a section doesn't add information that would change the decision, cut it.
