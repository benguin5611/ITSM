# Head-to-Head Comparison Guide

The comparison is the centrepiece of the business case. It must be specific enough that a decision-maker can see the real trade-offs — not just that both options "support" something, but HOW they support it differently.

---

## The Core Rule

**Compare the same dimension across all viable options with specifics, not checkmarks.**

| ❌ Wrong | ✅ Right |
|---|---|
| ✅ Audit logging | 90 days retention, JSON export via API |
| ✅ SSO | OIDC only, one IdP per account |
| ✅ Support | Email only, no published SLA, 25+ user minimum |

A checkmark hides the difference. A specific reveals it.

---

## Single Consolidated Table

Build **one table** with all viable options as columns. Group rows by dimension using **bold header rows**. This gives the reader the full comparison in a single pass.

```markdown
| **Dimension** | **Option A** | **Option B** |
|---|---|---|
| **Requirement 1 (R1)** | | |
| [Specific attribute] | [Specific detail] | [Specific detail] |
| [Specific attribute] | [Specific detail] | [Specific detail] |
| **Requirement 2 (R2)** | | |
| [Specific attribute] | [Specific detail] | [Specific detail] |
| **Operational** | | |
| Setup effort | [Quantified] | [Quantified] |
| Migration | [Specific] | [Specific] |
| **Nice-to-Have Coverage** | | |
| N1: [Name] | [How it's handled] | [How it's handled] |
| N2: [Name] | [How it's handled] | [How it's handled] |
```

---

## Cover Every Requirement

Include **all** must-have requirements in the table — even ones where all options are equivalent. The table should be self-contained. A reader who only looks at the comparison table should see the full picture without cross-referencing other sections.

If two options handle a requirement identically, showing that is still valuable — it tells the reader "this isn't a differentiator" without them having to guess.

---

## What to Include

### One dimension group per must-have requirement (R1–Rn)
For each requirement, include 2–4 rows that answer: "How specifically does each option satisfy this?"

Example for audit logging:
| **Audit Logging (R6)** | **Option A** | **Option B** |
|---|---|---|
| Admin audit retention | 90 days, JSON export via API | 18 months, API + Logpush to any destination |
| Traffic logs | Network flow logs (device-to-device). Destination logging requires Enterprise. | Gateway logs: DNS, HTTP, network sessions. Extended retention. |
| SIEM streaming | Config logs to Splunk/Datadog/S3. Flow logs: Enterprise only. | Logpush to any destination. |

### Operational group
- Setup/migration effort (quantified in hours where possible)
- Migration from current state
- Support (channel, SLA, response times)
- Pricing (at the user's scale, with caveats for unknowns)

### Nice-to-Have Coverage group (N1–Nn)
One row per nice-to-have. For each, state how the option handles it or "Not available." This lives inside the same table — not as a separate section.

---

## Handling Edge Cases

### When a feature doesn't apply
Use "N/A" — not "❌". "❌" means the option was supposed to do this and can't. "N/A" means the dimension isn't relevant to this option's architecture.

### When information is unavailable
Write "Unknown — requires [vendor quote / trial / documentation review]" rather than leaving the cell empty or guessing.

### When options are equivalent on a dimension
Still include the dimension. Showing equivalence is informative — the reader knows it's not a differentiator. Use similar specifics for both options so the reader can confirm they're equivalent rather than taking your word for it.

---

## Cross-Check Before Finalising

- [ ] Every cell contains a specific (number, format, mechanism) — not a checkmark
- [ ] Every claim cites a source URL (in the Sources table)
- [ ] Bold header rows clearly separate dimension groups
- [ ] All must-have requirements are represented (not just differentiators)
- [ ] Nice-to-have coverage is included as the final group
- [ ] Prose sections don't contradict table contents
