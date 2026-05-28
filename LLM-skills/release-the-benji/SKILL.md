---
name: release-the-benji
description: >
  Stress-test any plan, decision, or approach using a six-agent adversarial review methodology
  based on cybersecurity team colors (Red, Blue, Purple, White, Yellow) plus a final Judge. Use this skill whenever
  someone asks to "review my plan", "stress-test this", "adversarial review", "red team this",
  "find weaknesses in my approach", "poke holes in this", "challenge this plan", "devil's advocate",
  "what could go wrong", "review this decision", "release the benji", "benji this", or any
  variation of wanting critical, structured feedback on a plan before committing. Also trigger
  when someone pastes a plan, architecture doc, strategy, or proposal and asks for feedback —
  even casually. Works for code architecture, business strategy, hiring decisions, product
  launches, policy changes, process designs, or anything else that benefits from adversarial
  thinking before execution.
---

# Release the Benji

A domain-agnostic methodology for stress-testing plans and decisions using six independent agents
with distinct perspectives: attacker, defender, analyst, referee, builder, and judge. Named after
the team member who was already doing this in every meeting anyway.

## When to use this

Any time someone wants structured critical feedback on a plan before committing to it. The plan
can be about anything — code, business, product, hiring, policy, process, infrastructure. If
someone says "what do you think of this plan?" and it's something with real stakes, this skill
adds rigor that a single-pass review can't match.

## How it works

Six agents review the plan in a specific dependency order. The key insight: Red and Blue never
see each other's output, so their analyses are genuinely independent. Purple then reconciles them.
White and Yellow add proportionality and pragmatism. The Judge then looks at everything
holistically and delivers the single, definitive verdict the user reads first.

```
[Red #1] ──────┐
               ├──▶ [Purple #3] ──┬──▶ [White #4] ─┐
[Blue #2] ─────┘                  └──▶ [Yellow #5]─┴──▶ [Judge #6]
```

For Quick Benji, the Judge fires straight off Purple (no White/Yellow).

## Two modes

- **Full Benji** (all 6 agents) — for high-stakes decisions: major architecture changes,
  business pivots, significant policy decisions, anything expensive to reverse.
- **Quick Benji** (Red + Blue + Purple + Judge) — for moderate decisions where you just want to
  find blind spots fast and get a verdict, without the full proportionality/pragmatism pass.

The Judge runs in both modes — it is the final consolidated recommendation the user reads.

When the user doesn't specify, infer from context. If unsure, ask:
> "Full Benji or Quick Benji? Full runs all six agents including proportionality and
> pragmatism checks. Quick just finds blind spots fast then jumps to the Judge's verdict."

## Orchestration: step by step

### 1. Capture the plan

The plan is the input to every agent. Get it from one of:

1. **Explicit plan text** — the user pastes or describes the plan directly
2. **Plan file** — the user points to a file (markdown, confluence page, etc.)
3. **Conversation context** — the plan is implicit in the discussion so far

If the plan is ambiguous or spread across many messages, write a concise summary (300–800 words)
and confirm with the user before proceeding:
> "Here's my summary of the plan I'll send to the review agents. Does this capture it?"

The summary should include: what's being proposed, key constraints, what's in/out of scope,
and any stated priorities or trade-offs.

### 2. Launch Red and Blue in parallel

Read `references/agent-prompts.md` for the exact prompts.

**Red and Blue must be independent.** Neither sees the other's output. Spawn both subagents in
the same turn, each receiving only the plan summary.

If subagents aren't available, run sequentially — but compose both prompts before running either.
Do not let Red's output bleed into Blue's prompt.

### 3. Launch Purple (after Red + Blue complete)

Purple receives Red's full attack list and Blue's full defense. It also gets the plan summary
for context. Wait for both Red and Blue to finish before launching Purple.

### 4. Launch White and Yellow in parallel (full review only)

Skip this step for **Quick Benji**.

For **Full Benji**, launch both after Purple completes:
- **White** gets Purple's recommendations + original plan summary (scope/constraints)
- **Yellow** gets the original plan summary + Purple's recommendations

### 5. Launch the Judge (always — final agent in both modes)

The Judge is the final agent and produces the user-facing verdict. Wait for all prior agents
to finish before launching.

The Judge receives:
- Plan summary
- Red Team output
- Blue Team output
- Purple Team output
- White Team output (Full Benji only — pass "Not run (Quick Benji)" for Quick)
- Yellow Team output (Full Benji only — pass "Not run (Quick Benji)" for Quick)

The Judge is allowed — and expected — to disagree with prior agents. It is not a mechanical
summarizer; it weighs all the outputs and decides what should actually be done and not done.

### 6. Present the final output

The Judge's verdict IS the final output. Prefix it with a short pipeline summary so the user
can see what work was done, then present the Judge's output verbatim. Do not paraphrase the
Judge or add your own recommendations on top — that would dilute the point of having a single
final arbiter.

**Format:**

```
## Adversarial Review — [Full Benji / Quick Benji]

### Pipeline Summary
- Red Team raised **[N]** attack points
- Blue Team identified **[N]** strengths and rebutted **[N]** criticisms
- Purple Team validated **[N]** of Red's points ([N] critical, [N] high, [N] moderate, [N] low/cosmetic)
[Full Benji only:]
- White Team accepted **[N]** recommendations, rejected **[N]**, modified **[N]**
- Yellow Team rated complexity as **[verdict]** and flagged **[N]** buildability concerns

[Paste the Judge's verdict here verbatim]
```

For Full Benji, you may optionally include a short "Emergent Patterns" section below the
Judge if Green Team (Blue + Yellow) or Orange Team (Red + Yellow) convergence is notable —
but only if it adds signal the Judge didn't already cover.

### 7. Offer to update the plan

Always offer to produce an updated version of the plan with the accepted changes applied.
Include a short plan-diff preview (one line per change, using +/~/- prefixes) so the user
can see exactly what would change before saying yes. Do not apply changes automatically —
wait for confirmation.

## Prompt quality notes

The agent prompts are designed to produce genuinely independent, non-generic analysis:

- Red asks for *specific failure scenarios*, not vague "what could go wrong"
- Blue *predicts criticism and prepares rebuttals* independently of Red
- Purple delivers *verdicts with severity ratings*, not "maybe consider this"
- White *filters for proportionality* — prevents gold-plating
- Yellow *speaks as a builder* — catches paper-reasonable complexity that causes real pain
- The Judge *makes the call* — explicitly names what to do, what not to do, and why,
  rather than averaging the prior agents

If outputs are generic, add one line of domain context to the plan input (e.g., "This is a
cloud infrastructure migration plan" or "This is a hiring process redesign"). Domain context
significantly improves specificity without changing the prompts.
