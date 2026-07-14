# Business Case Anti-Patterns

Read this before starting AND check it again before publishing. Each pattern below caused real rework in business cases. The "wrong" examples are drawn from actual mistakes.

---

## 1. Late-Discovered Requirements

**Wrong:** Complete the analysis, then discover a must-have requirement that eliminates 3 of 4 options.

**Right:** Run the full requirements interview (Phase 1) before any research. Specifically probe for hidden requirements: static IP needs, data residency, compliance frameworks, integration dependencies.

**Test:** Before starting Phase 2, ask yourself: "Is there any question the decision-maker might ask about a requirement that I haven't captured?" If yes, go back.

---

## 2. Binary Comparison (Checkmarks)

**Wrong:**
| | Option A | Option B |
|---|---|---|
| Audit logging | ✅ | ✅ |

**Right:**
| | Option A | Option B |
|---|---|---|
| Audit retention | 90 days, JSON via API | 18 months, CSV + API. Logpush Enterprise only. |

**Test:** For every ✅ in a comparison table, ask: "Could two options both have ✅ here but differ meaningfully?" If yes, replace with specifics.

---

## 3. "Do Nothing" Costs $0

**Wrong:** "Option 1: Do Nothing — $0/yr"

**Right:** "Option 1: Do Nothing — ~$216/yr (3 users × $6/mo on current plan)" — plus the risk cost of the expired trial, compliance gaps, etc.

**Test:** If something is already in place and being paid for, "Do Nothing" has a cost. Always ask what the current spend is.

---

## 4. Missing Option Tiers

**Wrong:** Only presenting the 2–3 options that meet all requirements, with no context for what was considered at other levels of investment.

**Right:** Frame across four tiers of ambition: Do Nothing (baseline), Do Something (minimum viable change), Do Many Things (comprehensive, usually the recommendation), Do Everything (maximum investment). The tiers justify the recommended level — "we're not under-investing and not over-investing." Eliminated tiers get one line each with the reason.

**Test:** Could a stakeholder ask "why can't we just do the minimum?" or "why aren't we going all-in?" If any tier is missing, the recommendation isn't anchored.

---

## 5. Prose Contradicts Tables

**Wrong:** Writing "No vendor provides everything in a single plan" while the requirements matrix shows 3 plans meeting all requirements.

**Right:** Cross-check every prose statement against the data tables. If the tables show something, the prose must match.

**Test:** After writing the recommendation section, re-read the qualification matrix. Does the prose align?

---

## 6. Too Many Options

**Wrong:** Presenting 7 options when only 2 meet all requirements. The extra 5 create noise.

**Right:** Build the qualification matrix first. Only detail options that pass ALL must-have requirements. Mention eliminated options briefly with the reason they were dropped.

**Test:** For each option in the document, ask: "Does this meet every must-have?" If not, it shouldn't have its own section.

---

## 7. Mislabelled Options

**Wrong:** Calling an option "Standalone" when it actually requires 2 tools.

**Right:** "Standalone" = one vendor, one tool. "Hybrid" = 2+ tools. Label accurately.

**Test:** For each option, count the number of vendors/tools involved. If it's more than one, it's a hybrid.

---

## 8. Stale Pricing Without Caveat

**Wrong:** "Hybrid pricing is $12/user/mo blended" based on a 2-year-old sales email, presented as fact.

**Right:** "Hybrid pricing was $12/user/mo blended per a Feb 2024 sales email — needs reconfirmation. If unavailable, standard pricing is $18/user/mo."

**Test:** Is any pricing data older than 6 months? If so, flag it explicitly and note the date.

---

## 9. Vendor Marketing Names vs Official Names

**Wrong:** Calling the whole platform "Cloudflare Zero Trust" when the vendor's docs and dashboard brand the umbrella platform "Cloudflare One" (Zero Trust survives as a sub-brand and in plan names).

**Right:** Check the vendor's current website and use their official product name.

**Test:** Visit the vendor's pricing or product page. What do they call it today?

---

## 10. Duplicate Analysis

**Wrong:** Comparing options in a head-to-head table AND restating the same information as bullet-point pros/cons for each option.

**Right:** The comparison table IS the analysis. The options section is a one-line summary with cost and key trade-off. Don't say it twice.

**Test:** If you deleted the pros/cons section, would any information be lost that isn't in the comparison tables? If not, delete it.

---

## 11. Recommendation Without Criteria

**Wrong:** "We recommend Option B because it's the best fit."

**Right:** "The user identified cost and single-vendor consolidation as the highest priorities. Option B is the lowest-cost option that meets all requirements and is the only single-vendor solution. Therefore, we recommend Option B."

**Test:** Can you trace the recommendation directly to the decision criteria established in Phase 1? If not, the recommendation is opinion, not analysis.

---

## 12. Inventing Options the User Didn't Ask For

**Wrong:** Adding a "Starter plan as a stopgap" option that the user doesn't need and that doesn't meet requirements.

**Right:** Only present options that meet requirements or that fit into the investment spectrum (Do Nothing / Do Something / Do Many Things / Do Everything). Don't pad the document with options that serve no analytical purpose.

**Test:** For each option, ask: "Does this meet requirements, or does it serve a clear role in the investment spectrum?" If neither, remove it.

---

## 13. Not Asking Who Accesses What

**Wrong:** Assuming an internal tool is only used by employees, then discovering external partners also need access — changing the architecture options.

**Right:** For every tool/service in scope, ask: "Who accesses this? Employees only, or external users too?" The answer determines which solutions are viable.

**Test:** Can you state, for every service mentioned, exactly who accesses it and how?

---

## 14. Hiding Requirements From the Qualification Matrix

**Wrong:** Only showing R4, R5, R6, R8 in the qualification matrix because R1, R2, R3, R7 are met by all options, with a prose note saying "R1–R3 and R7 are met by all tiers."

**Right:** Show ALL requirements in the matrix. The table should be self-contained — a reader who only looks at the matrix should see every requirement without cross-referencing a paragraph.

**Test:** Could a reader understand the full qualification picture from the table alone? If they need to read surrounding prose to know which requirements were evaluated, the table is incomplete.

---

## 15. Executive Summary Hides the Head-to-Head Winner

**Wrong:** The executive summary only states the recommendation, not which option actually won the comparison.

**Right:** State who won the head-to-head AND what the recommendation is. If they differ (e.g., the stronger platform isn't recommended because of cost), say so explicitly. The reader deserves to know the full picture.

**Test:** Does the executive summary explain both which option is strongest and which is recommended? If they're different, is the reason stated?

---

## Pre-Publication Checklist

Run through these before sharing the document:

- [ ] No contradictions between prose and tables
- [ ] No binary ✅/❌ in head-to-head comparison (specifics only)
- [ ] No options that fail must-have requirements listed as viable
- [ ] No duplicate analysis across sections
- [ ] "Do Nothing" has a realistic cost
- [ ] All four investment tiers represented (even if some are one-liners)
- [ ] Vendor names match current official branding
- [ ] Every factual claim has a source link
- [ ] Recommendation references the decision criteria from Phase 1
- [ ] Recommendation uses primary/secondary/tertiary with conditions for shifting between them
- [ ] All option labels are accurate (standalone vs hybrid)
- [ ] Pricing data is dated, and stale data is flagged
- [ ] Every service/tool has a confirmed user base (employees, contractors, external)
- [ ] Qualification matrix includes ALL must-have requirements
- [ ] Head-to-head table covers ALL requirements plus nice-to-haves
- [ ] Executive summary states both the head-to-head winner and the recommendation
- [ ] Next steps include specific actions
