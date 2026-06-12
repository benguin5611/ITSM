# Orchestration reference

This file covers two things the orchestrator needs to know:

1. **Prompt substitutions** — what each per-agent prompt expects to receive.
2. **Output assembly** — how to present the Judge's verdict, offer changes, and remind about open questions.

Per-agent prompts live in `references/agents/` (one file per agent, numbered in run order).

## Prompt substitutions

Each per-agent file under `references/agents/` contains a self-contained prompt with placeholder variables. Replace them as follows before invoking the agent:

- **All agents** receive `{{PLAN_TEXT}}` — the **full verbatim plan**, never a summary (see SKILL.md §1).
- **All agents** receive `{{PRIOR_DECISIONS}}` — the anti-noise priming extract from the project's decision record (§4 + §5 + §6 + §7 of the decision-record template). If this is the first review, pass the literal string `"No prior decisions on this project — this is the first review."` See the "Decision record workflow" section below for how to detect, load, and update the record.
- **All agents except Gray** receive `{{GRAY_TEAM_OUTPUT}}` — Gray Team's ground-truth output.
- **Gray** additionally receives `{{AVAILABLE_SKILLS}}` — the list of agent skills available in the current runtime (the orchestrator enumerates these from its own context before launching Gray; see SKILL.md §2). Gray uses this list to recommend specific matching skills by name in its Specialist Review Recommendations section.
- **Purple** additionally receives `{{RED_TEAM_OUTPUT}}`, `{{BLUE_TEAM_OUTPUT}}`, `{{BLACK_TEAM_OUTPUT}}`.
- **White, Yellow, Gold** additionally receive `{{PURPLE_TEAM_OUTPUT}}`.
- **Green** additionally receives `{{BLUE_TEAM_OUTPUT}}` and `{{YELLOW_TEAM_OUTPUT}}`.
- **Orange** additionally receives `{{RED_TEAM_OUTPUT}}` and `{{YELLOW_TEAM_OUTPUT}}`.
- **The Judge** receives every upstream output. Pass `"Not run (Quick Review)"` for White, Yellow, Gold, Green, Orange when in Quick mode.

**Critical: `{{PLAN_TEXT}}` must always be the full verbatim plan, never a summary.** Summaries silently drop details — including the bugs the summary glosses over. If the plan is long, the agent still gets it in full.

The prompts are domain-agnostic by design. They use "plan," "approach," and "decision" — never domain-specific terms like "code," "deploy," or "revenue."

## Failure handling — fail fast and loud, never hang

Agents can fail (tool errors, timeouts, a dead subagent). The pipeline must degrade explicitly, never stall waiting and never silently drop a lens.

- **One retry per agent.** If an agent errors or returns nothing usable, relaunch it once with the same prompt. If the retry also fails, mark that agent's output as `"Not run (failed)"` and move on. Never retry more than once and never block the pipeline indefinitely on a single agent.
- **Gray is the only hard dependency.** If Gray fails twice, stop and tell the user — every downstream agent is anchored to Gray's ground truth, so proceeding without it undermines the whole review. Offer to retry or to run a degraded review with `{{GRAY_TEAM_OUTPUT}}` set to `"Not run (failed) — claims in the plan are UNVERIFIED"`, but make the user choose.
- **Phase-1/3/4 agents degrade individually.** If Red, Blue, Black, White, Yellow, Gold, Green, or Orange fails twice, substitute `"Not run (failed)"` for its output in every downstream prompt and continue. Special case: if Yellow fails, skip Green and Orange entirely (both depend on Yellow) and pass `"Not run (Yellow failed)"` for all three.
- **The Judge must always run.** It already knows how to handle `"Not run (...)"` inputs from Quick mode; failed agents look the same to it. If the Judge itself fails twice, present Purple's validated concerns directly with an explicit warning that no final arbitration was performed.
- **Surface every degradation to the user.** The presented verdict must name any lens that didn't run, e.g.: *"⚠️ Black Team failed twice and was skipped — out-of-band risks were not assessed in this review."* Never present a degraded review as a complete one.

## Decision record workflow

The decision record is what stops agents re-litigating already-decided findings on every pass. The template is at [`references/decision-record-template.md`](decision-record-template.md). This section is the operational detail for SKILL.md's "Decision record — persistence across runs" — the orchestrator does these things at the times specified there.

### Step 0a — Detect the runtime

Local runtimes have `Read`/`Write`/`Bash`/`Edit` tool access. Web runtimes (Claude.ai, ChatGPT) do not. If you can call `Read` against the user's filesystem, you're local.

### Step 0b — Determine the artefact stem

The file is named `<artefact-stem>-decisions.md`. The stem identifies the project so subsequent runs find the same file. Derive it from:

1. The plan file path if one was provided (`workspace-sharing-otp-plan.md` → stem `workspace-sharing-otp-plan`).
2. An explicit identifier the user provided (e.g. "this is the Q4 pricing plan" → stem `q4-pricing-plan`).
3. Otherwise ask: *"What's a short identifier for this project? I'll use it to name the decision record (e.g. `q4-pricing-plan` → `q4-pricing-plan-decisions.md`)."*

Use kebab-case. Avoid spaces. Stems are persistent — once set on first run, all subsequent runs use the same stem.

### Step 0c — Detect or initialise

**Local:**

1. Check `~/Downloads/<stem>-decisions.md`. If found, read it.
2. If not found, check `~/Downloads/<stem>-decisions-active.md` (the file may have been split — see splitting rules). If found, read it.
3. If neither exists, this is the first review — set `{{PRIOR_DECISIONS}}` to `"No prior decisions on this project — this is the first review."` and plan to create the file in step 9.

**Web:**

Ask the user: *"Do you have a decision record from a prior review of this artefact? If so, paste it now — I'll use it to prime the agents. If not, I'll create one at the end and you can save it for next time."* If they paste one, treat it the same as the local case. If not, treat as first review.

### Step 0d — Extract priming content

From the loaded decision record, extract sections 4 (Applied), 5 (Standing rejections), 6 (Accepted residuals), and 7 (Methodology lessons). Concatenate with section headers preserved. This is `{{PRIOR_DECISIONS}}` for every agent.

**Do NOT pass §9 (per-finding canonical records) as part of the priming context** — it's the detail-on-lookup layer, and including it would bloat agent context. Agents reference §9 only when an agent's own output cites a prior-finding ID and the orchestrator wants to verify the prior detail.

### Step 9a — Build the per-finding records from the Judge output

After the user has applied/rejected the Judge's recommendations, build one canonical-record entry per Judge action ID:

```
### [ID] — [Judge's one-line title for the finding]
- **Status:** [APPLIED / NO-OP PRESERVE / FALSE POSITIVE / REJECTED (design call) / REJECTED (not material) / DEFERRED / STANDING REJECTION]
- **Severity:** [from Judge's table]
- **Location:** [where the change went, or where the rejected suggestion would have gone]
- **If re-raised:** [short guidance — "Do not re-raise: [reason]" for rejections; "Already in §X" for applied items; "Re-evaluate when [trigger]" for residuals]
- **Rationale:** [user's reasoning if given; otherwise "Accepted per Judge's recommendation." for applied items; ask for one-line rationale on rejections that have none]
- **Source:** [agent(s) that raised this — Judge's source column]
```

**Status derivation from user action:**

- User applied → **APPLIED**
- User skipped + Judge had recommended ❌ → **REJECTED** (sub-type from rationale: "not worth the cost" → not material; "decided against" → design call; "do not re-flag" → STANDING REJECTION)
- User skipped + Judge had recommended ✅ → ask the user: *"You skipped [ID] which the Judge recommended — rejecting (and why) or deferring?"*
- User said "track for later" → **DEFERRED** (capture trigger criteria as a §6 row)
- Judge marked ⚠️ override and user accepted → **APPLIED** with a note explaining the override
- Finding turned out to misread the plan → **FALSE POSITIVE** (record so future passes don't repeat)

### Step 9b — Update the indexes and audit trail

For each new canonical record:

- **APPLIED** → row in §4 (Applied findings index), row in §9 (per-finding canonical records)
- **STANDING REJECTION** → row in §5 (Standing rejections), row in §9
- **DEFERRED** → row in §6 (Accepted residuals) with trigger criteria, row in §9
- **REJECTED (design call / not material) without standing-rejection language** → row in §9 only (compact); promote to §5 if a future pass re-raises and you reject again
- **FALSE POSITIVE** → row in §9 only

Append a new entry to §11 (audit trail) summarising the pass: date, mode (Full/Quick), counts (applied / rejected / false positive / deferred), any novel methodology lesson learned.

If you discovered a methodology lesson during the pass (e.g. "agents keep misreading section X"), add it to §7 with an `L-` prefix.

### Step 9c — Write the file

**Local:**

- First run: `Write` the new file to `~/Downloads/<stem>-decisions.md`. Use the template at [`decision-record-template.md`](decision-record-template.md) as the starting structure — replace the italic guidance blocks with actual content; delete the unused example tables.
- Subsequent runs: `Edit` the existing file. Add new rows to indexes (§4/§5/§6), append new canonical records to §9, append the audit-trail entry to §11. Do NOT rewrite the whole file — preserve every existing record verbatim.

**Web:**

- Present the full updated file content as a fenced markdown code block in the conversation.
- Add this footer message: *"Save this as `<stem>-decisions.md` somewhere you can paste back next time you review this artefact — a Claude.ai project's project knowledge, a ChatGPT custom GPT's knowledge file, a shared note in your team's wiki, or a local file you upload at the start of each session. The next review of this project will be much more efficient if the agents can read this."*

### Step 9d — Splitting check

After writing, estimate the file size. A rough heuristic: **~40,000 characters ≈ ~10,000 tokens**. If the file exceeds this threshold, split it into two:

- **`<stem>-decisions-active.md`** — sections 1–9 (document state, how-to-use, ID convention, indexes, residuals, methodology lessons, evidence registry, per-finding canonical records). This is the file loaded into agent context on subsequent runs.
- **`<stem>-decisions-audit.md`** — sections 10–11 (internal consistency fixes, chronological audit trail). Historical; consulted only when a reviewer wants to audit decision history.

Update §1 of `-active.md` to add a pointer row:
```
| Audit file | `<stem>-decisions-audit.md` (historical sections 10–11) |
```

After a split, subsequent runs read only `-active.md` for priming.

**If the active file itself approaches 10k tokens after a split:** that's the signal to archive resolved per-finding records. Move records whose status hasn't changed in three consecutive passes (e.g. STANDING REJECTION confirmed in passes N, N+1, N+2) from `-active.md` §9 into `-audit.md` as an "Archived per-finding records" section. Keep a compact index entry in `-active.md` §5 (one row, no full record). The status hasn't changed → the detail doesn't need to be hot.

### Step 9e — Confirm with the user

After writing/presenting:

- **Local:** *"Decision record updated at `~/Downloads/<stem>-decisions.md`. The next review of this project will read it automatically."* If a split happened, mention both file paths.
- **Web:** *"Decision record content above. Save it to wherever you'll paste it back next time."*

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
> _This was a Quick Review. Proportionality (White), buildability (Yellow), disaster tabletop (Gold), defence-buildability (Green), and attack-plausibility (Orange) were not assessed. Run a Full Review if you want those lenses applied._

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
- Green Team identified **[N]** high-confidence defences; flagged **[N]** low-confidence
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
