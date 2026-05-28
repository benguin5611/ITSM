# Orchestration reference

This file covers two things the orchestrator needs to know:

1. **Prompt substitutions** — what each per-agent prompt expects to receive.
2. **Output assembly** — how to present the Judge's verdict, offer changes, and remind about open questions.

Per-agent prompts live in `references/agents/` (one file per agent, numbered in run order).

## Prompt substitutions

Each per-agent file under `references/agents/` contains a self-contained prompt with placeholder variables. Replace them as follows before invoking the agent:

- **All agents** receive `{{PLAN_TEXT}}` — the **full verbatim plan**, never a summary (see SKILL.md §1).
- **All agents except Gray** receive `{{GRAY_TEAM_OUTPUT}}` — Gray Team's ground-truth output.
- **Gray** additionally receives `{{AVAILABLE_SKILLS}}` — the list of agent skills available in the current runtime (the orchestrator enumerates these from its own context before launching Gray; see SKILL.md §2). Gray uses this list to recommend specific matching skills by name in its Specialist Review Recommendations section.
- **Purple** additionally receives `{{RED_TEAM_OUTPUT}}`, `{{BLUE_TEAM_OUTPUT}}`, `{{BLACK_TEAM_OUTPUT}}`.
- **White, Yellow, Gold** additionally receive `{{PURPLE_TEAM_OUTPUT}}`.
- **Green** additionally receives `{{BLUE_TEAM_OUTPUT}}` and `{{YELLOW_TEAM_OUTPUT}}`.
- **Orange** additionally receives `{{RED_TEAM_OUTPUT}}` and `{{YELLOW_TEAM_OUTPUT}}`.
- **The Judge** receives every upstream output. Pass `"Not run (Quick Review)"` for White, Yellow, Gold, Green, Orange when in Quick mode.

**Critical: `{{PLAN_TEXT}}` must always be the full verbatim plan, never a summary.** Summaries silently drop details — including the bugs the summary glosses over. If the plan is long, the agent still gets it in full.

The prompts are domain-agnostic by design. They use "plan," "approach," and "decision" — never domain-specific terms like "code," "deploy," or "revenue."

## Output assembly — ask depth, present, offer changes, remind about open questions

After the Judge completes, the orchestrator presents the user-facing output in stages. The Judge's verdict is the authoritative content; do not paraphrase or layer additional recommendations on top.

### Step 1 — Ask the user how deep they want to go (before showing anything)

Before presenting any output, ask:

> Two ways to see this review:
> - **Full breakdown** — what every team surfaced individually (lots of content)
> - **Summary** — the Judge's verdict only (compact)
>
> Which would you prefer?

If the user chooses **Full breakdown**, present the per-team breakdown (template below) FIRST, then the Summary. If they choose **Summary** (or don't specify clearly), present only the Summary.

### Step 2 — Present the Summary (verbatim from the Judge)

Paste the Judge's output verbatim, in this order. Add nothing else.

```
## Rainbow Team Review — [Full Review / Quick Review]

[For "Pause and reconsider" or "Do not proceed" verdicts only, include a single bold line
above the Key. For the common "proceed with changes" case, start directly with the Key.]

### Key
[Judge's Key table — ✅ ❌ ❓ ⚠️ explanations.]

### Summary Table
[Judge's table — clean ID column, Adopt? column has ✅/❌/❓ with `⚠️` to the right of the
glyph on override rows (e.g. `✅ ⚠️` or `❌ ⚠️`), plain-text priority (Critical / High /
Moderate / Low / —), source column with full team names. No separate source-codes legend.]

### Open Questions
[Judge's Q items in Decide:/Validate: format. If no open questions, the Judge writes "None."]
```

DO NOT paste "Actions to take — detail" or "Actions to NOT take — detail" here.

[Quick Review only, append an italic line after Open Questions:]
> _This was a Quick Review. Proportionality (White), buildability (Yellow), disaster tabletop (Gold), defense-buildability (Green), and attack-plausibility (Orange) were not assessed. Run a Full Review if you want those lenses applied._

### Per-team breakdown template (used only if the user chose Full breakdown in Step 1)

```
### Per-team breakdown
- Gray Team verified **[N]** factual claims (**[N]** confirmed, **[N]** wrong/regressions,
  **[N]** unverifiable), mapped **[N]** concepts, flagged **[N]** rationales
- Red Team raised **[N]** attack points
- Blue Team identified **[N]** strengths
- Black Team surfaced **[N]** out-of-band vectors
- Purple Team validated **[N]** combined concerns ([N] critical, [N] high, [N] moderate, [N] low)
[Full Review only:]
- White Team accepted **[N]**, rejected **[N]**, modified **[N]**
- Yellow Team rated complexity as **[verdict]**; **[N]** buildability concerns
- Gold Team tabletop verdict: **[verdict]**; **[N]** pre-mortem recommendations
- Green Team identified **[N]** high-confidence defenses; flagged **[N]** low-confidence
- Orange Team identified **[N]** high-confidence attacks; downgraded **[N]** theoretical
```

### Step 3 — Offer the changes (with detail-on-request option)

Each ✅ accepted action gets one line with an intuitive emoji prefix:

- ✅ — adds new content (new section, new runbook)
- ✏️ — modifies existing content (changes a value, swaps a variable, edits a step)
- 🗑️ — removes existing content

Combine the changes list with the detail-on-request option in a single message:

```
Here are the changes I'd apply:
✅ [addition — e.g. "Adds rollback procedure after step X"]
✏️ [modification — e.g. "Revises assumption Y to require stakeholder sign-off"]
🗑️ [removal — e.g. "Removes step Z (Judge rejected as unnecessary overhead)"]

Reply **apply** to apply all, list IDs to apply a subset (e.g. `apply A1, A2`), say
**detail on [IDs]** to see the Judge's reasoning first, or **skip** to cancel.
```

If the user requests detail, paste the Judge's "Actions to take — detail" and "Actions to NOT take — detail" sections verbatim, filtered to the requested IDs. Then re-offer the changes message. Loop until they apply or skip.

### Step 4 — After applying, remind about Open Questions

When the user applies (all or subset), apply the changes to the plan, then surface the Open Questions the review left for human decision:

```
Changes applied.

Before you ship, the review left these for you to resolve:
- **Q1 · Decide:** [question]
- **Q2 · Validate:** [question]
```

If the Judge produced no Open Questions, omit this reminder.
