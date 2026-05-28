---
name: rainbow-team-review
description: >
  Stress-test any plan, decision, or approach using a structured multi-agent adversarial review
  methodology based on cybersecurity team colors — Gray (ground-truth verification), Red (attacker),
  Blue (defender), Black (out-of-band adversary), Purple (analyst), White (referee), Yellow
  (builder), Gold (crisis strategist) — plus a final Judge that delivers a single consolidated
  verdict. Use this skill whenever someone asks to "review my plan", "stress-test this",
  "adversarial review", "red team this", "rainbow team this", "find weaknesses in my approach",
  "poke holes in this", "challenge this plan", "devil's advocate", "what could go wrong",
  "review this decision", "release the benji", "benji this", or any variation of wanting critical,
  structured feedback on a plan before committing. Also trigger when someone pastes a plan,
  architecture doc, strategy, or proposal and asks for feedback — even casually. Works for code
  architecture, business strategy, hiring decisions, product launches, policy changes, process
  designs, or anything else that benefits from adversarial thinking before execution.
---

# Rainbow Team Review

A domain-agnostic methodology for stress-testing plans and decisions using ten independent
agents with distinct perspectives — fact-checker, attacker, defender, out-of-band adversary,
analyst, referee, builder, crisis strategist, defense-buildability filter, and attack-plausibility
filter — plus a final Judge that consolidates their findings into a single verdict. Modelled on
cybersecurity rainbow teaming (the named team colors are real industry terminology) but framed
domain-agnostically so it applies equally to code architecture, business strategy, hiring,
product launches, policy changes, and anything else where a careful adversarial pass before
commitment is valuable.

Also known as "Release the Benji" — the activation phrase the skill was originally named after,
honouring the team member who was already doing this in every meeting anyway.

## Color quick reference

| Color  | Role                          | What it asks                                                         | When it runs                |
|--------|-------------------------------|-----------------------------------------------------------------------|-----------------------------|
| Gray   | Fact-checker / intel          | What's actually true vs. what the plan claims is true?                | Phase 0 (always)            |
| Red    | Attacker (design-internal)    | What's wrong with the design as written?                              | Phase 1 (always)            |
| Blue   | Defender                      | Why is the design correct given its constraints?                      | Phase 1 (always)            |
| Black  | Attacker (out-of-band)        | What's outside the plan's frame that could destroy it?                | Phase 1 (always)            |
| Purple | Analyst / reconciler          | Which attacks survive the defenses? Severity?                         | Phase 2 (always)            |
| White  | Referee / proportionality     | Which validated concerns are worth implementing?                      | Phase 3 (Full Review only)  |
| Yellow | Builder                       | Will this actually work when someone sits down to do it?              | Phase 3 (Full Review only)  |
| Gold   | Crisis strategist (tabletop)  | If the worst plausible case happens mid-execution, what's recovery?   | Phase 3 (Full Review only)  |
| Green  | Defense + buildability filter | Which Blue defenses are both effective AND actually buildable?         | Phase 4 (Full Review only)  |
| Orange | Attack + buildability filter  | Which Red attacks survive Yellow's build-reality check?                | Phase 4 (Full Review only)  |
| —      | The Judge                     | Given everything: what gets done, what doesn't, why?                  | Final (always)              |

The taxonomy follows April C. Wright's 2017 "Orange Is the New Purple" extended cybersecurity
color-wheel model (primaries Red/Blue/Yellow + secondaries Purple/Green/Orange + governance
White), with Black (physical/out-of-band adversary) and Gold (crisis tabletop) added from
broader rainbow-teaming practice. Gray's intelligence-gathering role is adapted from the
threat-research framing used in extended models.

## When to use this

Any time someone wants structured critical feedback on a plan before committing to it. The plan
can be about anything — code, business, product, hiring, policy, process, infrastructure. If
someone says "what do you think of this plan?" and it's something with real stakes, this skill
adds rigor that a single-pass review can't match.

## How it works

Ten agents review the plan in a specific dependency order. Gray Team runs first and establishes
ground truth — verifying factual claims, mapping concepts, flagging unjustified rationales, and
identifying domains that need specialist review. Every subsequent agent receives Gray's output
so their arguments are anchored to verified facts rather than the plan's framing of itself.

Then Red (attacker), Blue (defender), and Black (out-of-band adversary) run in parallel, all
blind to each other — Red attacks the design as written, Blue defends it, Black attacks the
plan from outside its frame (supply-chain, social engineering, external dependencies,
competitor reaction, etc., adapted to the plan's domain). Purple reconciles all three. For
Full Review, White (proportionality), Yellow (buildability), and Gold (disaster tabletop) then
run in parallel against Purple's validated concerns. Once Yellow has completed, Green
(defense-buildability filter) and Orange (attack-plausibility filter) run in parallel, each
extracting the high-signal subset of Blue and Red findings through Yellow's lens. Finally,
the Judge looks at everything holistically and delivers the single, definitive verdict the
user reads first.

```
              ┌──▶ [Red #1] ─────┐                  ┌──▶ [White #5]  ─┐    ┌──▶ [Green #8] ──┐
[Gray #0] ────┼──▶ [Blue #2] ────┼──▶ [Purple #4] ──┼──▶ [Yellow #6] ─┼────┤                 ├──▶ [Judge #10]
              └──▶ [Black #3] ───┘                  └──▶ [Gold #7]   ─┘    └──▶ [Orange #9] ─┘
```

For Quick Review, the Judge fires straight off Purple (no Phase 3 or Phase 4 teams). Gray,
Red, Blue, Black, Purple, and the Judge always run.

## Two modes

- **Full Review** (all 10 agents + Judge) — for high-stakes decisions: major architecture
  changes, business pivots, significant policy decisions, anything expensive to reverse.
  Includes White (proportionality), Yellow (buildability), Gold (tabletop survivability),
  Green (high-confidence defenses), and Orange (high-confidence attacks).
- **Quick Review** (Gray + Red + Blue + Black + Purple + Judge) — for moderate decisions where
  you just want to find blind spots fast and get a verdict, without the full
  proportionality / pragmatism / tabletop / convergence-filter pass.

Gray Team and the Judge run in both modes. Gray runs first so factual errors and conceptual
conflations are surfaced before adversarial debate begins; the Judge runs last as the final
consolidated recommendation the user reads.

When the user doesn't specify, infer from context. If unsure, ask:
> "Full or Quick review? Full runs all ten agents including proportionality, buildability,
> disaster-tabletop, and the Green/Orange convergence filters. Quick runs Gray + Red + Blue +
> Black + Purple then jumps straight to the Judge's verdict."

## Orchestration: step by step

### 1. Capture the plan — full text, never a summary

**Every agent always receives the full plan text. No summaries.** Summaries silently drop details
— including the bugs the summary glosses over. This is a hard rule: if you are tempted to
summarise to save tokens, stop. The whole point of the skill is to catch what an inattentive
reader misses; pre-summarising hands the inattentive read to every agent.

Get the plan text from one of:

1. **Explicit plan text** — the user pastes or describes the plan directly. Use it verbatim.
2. **Plan file** — the user points to a file (markdown, Confluence page, etc.). Read the
   complete file. If the file is too large to read in one call, read it in chunks and concatenate
   — do NOT excerpt.
3. **Conversation context** — the plan is implicit in the discussion so far. Reconstruct the
   full plan text by concatenating the relevant user messages verbatim. If consolidation is
   genuinely needed (multiple iterations, contradictory drafts), produce a **consolidated full
   text** (not a summary) and confirm with the user:
   > "Here's the consolidated plan text I'll send verbatim to every agent. Anything missing or
   > superseded?"

The consolidated text must contain every constraint, every numbered step, every code block,
every section heading, and every rationale paragraph the original plan contains. If you find
yourself dropping detail to make it shorter, you are summarising — don't.

Pass the full plan text as `{{PLAN_TEXT}}` to every agent's prompt. Never substitute a summary.

### 2. Launch Gray Team (Phase 0 — runs first, alone)

Gray Team establishes ground truth. It runs before Red and Blue so its output anchors every
subsequent agent. Read `references/agent-prompts.md` for the exact Gray prompt.

Gray produces four outputs:
- **Fact Check** — verifies every factual claim in the plan against current behaviour
- **Concept Map** — enumerates every distinct concept, flags conflations
- **Self-Justifying Rationale Watch** — flags premises that cite no baseline
- **Specialist Review Recommendations** — flags domains where a specialist's view is needed,
  cross-referenced against the available-skills list so specific matching skills are
  recommended by name when they exist

**Before launching Gray, enumerate the available skills in your current runtime context** and
pass them as `{{AVAILABLE_SKILLS}}` in Gray's prompt. In Claude Code, the available-skills
list appears in system-reminder messages — each skill has a name and a description of what
failure modes it catches. Pass the full list (name + one-line description per skill) so Gray
can match domains to specific skills. If the runtime exposes no skill list, pass
`"No skills enumerated for this runtime — use generic specialist recommendations only"` and
Gray will fall back to describing the domain generically.

Gray's output is passed to every downstream agent as `{{GRAY_TEAM_OUTPUT}}`. Wait for Gray to
complete before launching Red and Blue.

### 3. Launch Red, Blue, and Black in parallel

Read `references/agent-prompts.md` for the exact prompts.

**Red, Blue, and Black must be independent.** None sees the others' output. Spawn all three
subagents in the same turn, each receiving the full plan text + Gray's output.

- **Red** attacks the design as written.
- **Blue** defends the design as written.
- **Black** attacks the plan from OUTSIDE its frame — supply-chain risks, social engineering,
  external dependencies, competitor reaction, regulatory shifts, the operator-error class of
  failure. Black's value comes from finding the attack vector the plan didn't think to model.

If subagents aren't available, run sequentially — but compose all three prompts before running
any. Do not let one team's output bleed into another's prompt.

### 4. Launch Purple (after Red + Blue + Black complete)

Purple receives the full plan text, Gray's output, Red's full attack list, Blue's full defense,
and Black's full out-of-band vector list. Wait for all three Phase-1 teams to finish before
launching Purple.

### 5. Launch White, Yellow, and Gold in parallel (full review only)

Skip this step for **Quick Review**.

For **Full Review**, launch all three after Purple completes. Each gets the full plan text +
Gray's output + Purple's validated concerns:

- **White** assesses proportionality — which of Purple's recommendations are worth implementing
  given the plan's scope and constraints.
- **Yellow** assesses buildability — what's harder to execute than the plan implies, what's
  over-engineered, what practical details are missing.
- **Gold** runs the tabletop / war-room exercise — assumes the worst plausible combination of
  validated concerns materializes mid-execution and walks through detection, triage,
  containment, communication, and recovery. Produces a survivability verdict and pre-mortem
  recommendations.

### 6. Launch Green and Orange in parallel (full review only — Phase 4)

Skip this step for **Quick Review**. Also skip if Yellow did not run (it shouldn't run without
Yellow, since both filters depend on Yellow's output).

For **Full Review**, after Yellow completes (alongside or after White and Gold), launch Green
and Orange in parallel. Each gets the full plan text + Gray's output + one primary team's
output + Yellow's output:

- **Green** receives Blue + Yellow. Extracts the high-confidence defensive recommendations
  (defenses Blue articulated that survive Yellow's buildability test) and flags low-confidence
  defenses the plan should not lean on.
- **Orange** receives Red + Yellow. Extracts the high-confidence attack vectors (Red findings
  whose preconditions Yellow's analysis confirms exist in the buildable plan) and downgrades
  theoretical attacks that don't survive the build-reality filter.

Green and Orange are independent of each other; spawn both in the same turn.

### 7. Launch the Judge (always — final agent in both modes)

The Judge is the final agent and produces the user-facing verdict. Wait for all prior agents
to finish before launching.

The Judge receives:
- Full plan text
- Gray Team output
- Red Team output
- Blue Team output
- Black Team output
- Purple Team output
- White Team output (Full Review only — pass "Not run (Quick Review)" for Quick)
- Yellow Team output (Full Review only — pass "Not run (Quick Review)" for Quick)
- Gold Team output (Full Review only — pass "Not run (Quick Review)" for Quick)
- Green Team output (Full Review only — pass "Not run (Quick Review)" for Quick)
- Orange Team output (Full Review only — pass "Not run (Quick Review)" for Quick)

The Judge is allowed — and expected — to disagree with prior agents. It is not a mechanical
summarizer; it weighs all the outputs and decides what should actually be done and not done.
The Judge's output leads with a summary table (✅ to take, ❌ to NOT take, ❓ for open question)
so the user can see the recommendations at a glance, then provides detailed reasoning below.

### 8. Ask the user how much they want to see, then present

The Judge generates everything in one pass (reasoning is preserved internally), but you
present it in stages so the first message stays scannable. Do not paraphrase the Judge or
add your own recommendations on top — that would dilute the point of having a single final
arbiter.

**Before showing anything, ask the user how deep they want to go.** The full per-team
breakdown is a lot of content; many users only want the Judge's summary. Make the
trade-off explicit:

> Two ways to see this review:
> - **Full breakdown** — what every team surfaced individually (lots of content)
> - **Summary** — the Judge's verdict only (compact)
>
> Which would you prefer?

If the user chooses **Full breakdown**, present the per-team breakdown FIRST (template
below), then the Summary. If they choose **Summary** (or don't specify clearly), present
only the Summary.

**The Summary** — paste the Judge's output verbatim, in this order. Add nothing else:

```
## Rainbow Team Review — [Full Review / Quick Review]

[Only include a verdict line for "Pause and reconsider" or "Do not proceed" cases.
For the common "proceed with changes" case, start directly with the Key table.]

### Key
[Judge's Key table explaining every glyph (✅ ❌ ❓ ⚠️). Priority words are not in the Key —
"Critical / High / Moderate / Low" is descriptive enough on its own.]

### Summary Table
[Judge's table — clean ID column, action titles, Adopt? column showing ✅/❌/❓ with `⚠️`
to the right on override rows (e.g. `✅ ⚠️` or `❌ ⚠️`), plain-text priority
(Critical / High / Moderate / Low / —), source column with full team names.]

### Open Questions
[Judge's Q items — Decide / Validate format.]
```

[Quick Review only, append a single italic line after the Open Questions:]
> _This was a Quick Review. Proportionality (White), buildability (Yellow), disaster
> tabletop (Gold), defense-buildability (Green), and attack-plausibility (Orange) were not
> assessed. Run a Full Review if you want those lenses applied._

**The per-team breakdown template** (only shown when the user chose Full breakdown):

```
### Per-team breakdown
- Gray Team verified **[N]** factual claims (**[N]** confirmed, **[N]** wrong/regressions,
  **[N]** unverifiable), mapped **[N]** concepts, flagged **[N]** rationales
- Red Team raised **[N]** attack points (design-internal)
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

### 9. Offer the changes (with optional detail, then remind about Open Questions)

After the Summary is presented, offer the changes the Judge accepts. Each ✅ accepted
action becomes a single line with an intuitive emoji prefix:

- ✅ — adds new content (new section, new runbook)
- ✏️ — modifies existing content (changes a value, swaps a variable, edits a step)
- 🗑️ — removes existing content

Combine the changes list with the detail-on-request option in a single message so the user
can drill into reasoning before deciding what to apply:

> Here are the changes I'd apply:
> ✅ [addition]
> ✏️ [modification]
> 🗑️ [removal]
>
> Reply **apply** to apply all, list IDs to apply a subset (e.g. `apply A1, A2`), say
> **detail on [IDs]** to see the Judge's reasoning first, or **skip** to cancel.

If the user requests detail, paste the Judge's "Actions to take — detail" and "Actions to
NOT take — detail" sections verbatim, filtered to the requested IDs (or "all"). Then
re-offer the changes message. Loop until they apply or skip.

**After applying** the changes (whether all or a subset), remind the user about the Open
Questions the review left for human decision. They are not changes to the plan but they
must be resolved before shipping:

> Changes applied.
>
> Before you ship, the review left these for you to resolve:
> - **Q1 · Decide:** [question]
> - **Q2 · Validate:** [question]

If the Judge produced no Open Questions, omit the reminder entirely.

## Prompt quality notes

The agent prompts are designed to produce genuinely independent, non-generic analysis:

- Gray *verifies factual claims* against external sources and *maps concepts* — establishes the
  baseline every other agent argues from
- Red asks for *specific failure scenarios*, not vague "what could go wrong"
- Blue *predicts criticism and prepares rebuttals* independently of Red
- Black *attacks the plan's frame* — finds what the plan didn't think to model
- Purple delivers *verdicts with severity ratings*, not "maybe consider this"
- White *filters for proportionality* — prevents gold-plating
- Yellow *speaks as a builder* — catches paper-reasonable complexity that causes real pain
- Gold *runs the tabletop* — assumes the worst plausible failure mode and walks recovery
- Green *filters Blue's defenses through Yellow's reality check* — extracts high-confidence
  defensive recommendations
- Orange *filters Red's attacks through Yellow's reality check* — extracts high-confidence
  attack vectors
- The Judge *makes the call* — explicitly names what to do, what not to do, and why,
  rather than averaging the prior agents

If outputs are generic, add one line of domain context to the plan input (e.g., "This is a
cloud infrastructure migration plan" or "This is a hiring process redesign"). Domain context
significantly improves specificity without changing the prompts.
