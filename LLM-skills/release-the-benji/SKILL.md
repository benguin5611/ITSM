---
name: release-the-benji
description: >
  Stress-test any plan, decision, or approach using a five-agent adversarial review methodology
  based on cybersecurity team colors (Red, Blue, Purple, White, Yellow). Use this skill whenever
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

A domain-agnostic methodology for stress-testing plans and decisions using five independent agents
with distinct perspectives: attacker, defender, analyst, referee, and builder. Named after the
team member who was already doing this in every meeting anyway.

## When to use this

Any time someone wants structured critical feedback on a plan before committing to it. The plan
can be about anything — code, business, product, hiring, policy, process, infrastructure. If
someone says "what do you think of this plan?" and it's something with real stakes, this skill
adds rigor that a single-pass review can't match.

## How it works

Five agents with cybersecurity-inspired roles review the plan in a specific dependency order.
The key insight: Red and Blue never see each other's output, so their analyses are genuinely
independent. Purple then reconciles them. White and Yellow add proportionality and pragmatism.

```
[Red #1] ──────┐
               ├──▶ [Purple #3] ──┬──▶ [White #4]
[Blue #2] ─────┘                  └──▶ [Yellow #5]
```

## Two modes

- **Full Benji** (all 5 agents) — for high-stakes decisions: major architecture changes,
  business pivots, significant policy decisions, anything expensive to reverse.
- **Quick Benji** (Red + Blue + Purple only) — for moderate decisions where you just want to
  find blind spots fast without the full proportionality/pragmatism pass.

When the user doesn't specify, infer from context. If unsure, ask:
> "Full Benji or Quick Benji? Full runs all five agents including proportionality and
> pragmatism checks. Quick just finds blind spots fast."

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

### 5. Synthesize

After all agents complete, produce the final output using the synthesis template in
`references/agent-prompts.md`.

**Quick Benji synthesis:**
- Pipeline stats (e.g., "Red raised 15 points, Purple validated 6")
- Purple's validated recommendations as the output
- Note that proportionality and pragmatism weren't assessed

**Full Benji synthesis:**
- Pipeline stats across all five agents
- White's accepted recommendations as the primary output
- Yellow's simplification flags and buildability concerns
- Emergent patterns:
  - **Green Team** (Blue + Yellow convergence) — where defenses become more buildable
  - **Orange Team** (Red + Yellow convergence) — where hardening becomes more pragmatic

### 6. Offer to update the plan

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

If outputs are generic, add one line of domain context to the plan input (e.g., "This is a
cloud infrastructure migration plan" or "This is a hiring process redesign"). Domain context
significantly improves specificity without changing the prompts.
