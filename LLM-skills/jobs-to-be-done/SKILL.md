---
name: jobs-to-be-done
description: Write compact, human-readable Jobs-to-be-Done analyses in the Klement/Christensen Job Story school — the struggle and circumstance, the core job framed as progress, job stories (When [situation], I want to [motivation], so I can [outcome]), forces of progress, emotional and social jobs, and a good/better/best tiering of how fully the job gets served. Use whenever someone says "JTBD", "jobs to be done", "job story", "job stories", "job to be done", or asks what job a feature does for its users — including when they paste a spec, PRD, PR, card, or feature description and want it framed around customer jobs rather than functionality. Also trigger when someone asks to condense, tidy, or humanise an existing JTBD write-up. Handles both greenfield mode (pre-build, driving requirements) and retrospective mode (post-build, documenting as-built behaviour and flagging gaps). Output is Australian English, prose-first, with a strict example budget.
---

# Jobs-to-be-Done write-ups

This skill produces a JTBD analysis of a feature, product, or process: the progress someone is trying to make, the circumstance that triggers it, and how well the current (or proposed) solution helps them make it. The school is Klement's Job Story format sitting on Christensen's theory — a job is *the progress a person is trying to make in a particular circumstance*, and people "hire" a solution to make it. Jobs are stable; solutions are not. A good write-up would still be true if the feature were rebuilt on entirely different technology tomorrow. **The rebuild test:** if a sentence wouldn't survive that rebuild, it's describing the solution, not the job. Rewrite it.

The output is deliberately compact. The structural skeleton and the job-story grammar are non-negotiable; examples are ornamental. Most of this skill exists to stop you decorating every line.

## Workflow

1. **Gather context.** Feature spec, PRD, PR, a product-discovery card, a use-case doc, or the conversation itself. For retrospective write-ups you also need as-built behaviour — the good/better/best section compares what's shipped against what fully serving the job would take.
2. **Translate the raw input, don't copy it.** Real input arrives loose — a "Customer Feedback / Job to be Done" card, a batch of "I'd like to…" lines, a field note. Tighten each into the job-story grammar; a raw wish is not a job story until its situation, motivation, and outcome are all present and solution-free.
3. **Pick a mode.** Retrospective (the thing exists or is built): the good/better/best section documents what's shipped as *Good* and holds the known gaps in *Better/Best*. Greenfield (pre-build): good/better/best is the build ambition, flagging the outcomes most at risk of being underserved. Everything else is identical. If it's genuinely unclear which applies, ask.
4. **Draft long, then condense.** Write every situation, job story, force, and emotional/social job first without worrying about length. Then apply the condensation contract. Don't try to write short in one pass — you'll drop job stories without noticing.
5. **Voice pass.** Apply the language rules below, then if the `write-like-a-human` skill is available in your environment, read it and run its checks before shipping.

If someone hands you an existing JTBD write-up to condense or humanise, skip to steps 4–5: apply the condensation contract, run the lossless check, and report the job-story count before and after.

Before your first write-up with this skill, read `references/exemplar.md` — a full bare → bloated → condensed progression of a worked example, annotated with why each move works.

## The six sections

Fixed order:

1. The struggle (context)
2. Core job to be done
3. Job stories
4. Emotional and social jobs
5. Forces of progress
6. Good, better, best

### 1. The struggle (context)

The circumstance and the struggling moment — what's happening when the job arises, and why it's hard right now. Name what people "hire" today (a spreadsheet, an email chain, a rival product) and why that solution is getting "fired".

The school leads with the *situation*, not the persona. Klement's point is that "As a [role]" bakes in an imaginary actor and hides causality — the situation is what determines behaviour. Name a role only where the situation genuinely differs by who's in it (a frontline worker's situation is not a manager's). Ground each in a person the reader can picture, but the situation, not the job title, is the subject of the sentence. Usually one to three distinct situations.

### 2. Core job to be done

One high-level job, written as progress: what the person is ultimately trying to accomplish, solution-free. This is the spine every job story hangs off.

Write it either as a progress statement ("Get a document to an outside party without them needing an account") or as a headline job story. Apply the rebuild test. One core job; add a second only if another situation's core job is genuinely distinct and the write-up suffers without it.

### 3. Job stories

**Grammar: When [situation], I want to [motivation], so I can [outcome].**

The situation is the trigger and context. The motivation is the first-order goal — solution-free, and it can carry an anxiety ("…I want to be sure the old link no longer works, so I can…"). The outcome is the progress made. The rebuild test applies to the motivation and the outcome: "When I open the file, I want to click Share, so I can send a link" fails — that's the implementation talking. "When I need to get a file to an outsider, I want to share just that file for just as long as needed, so I can hand it over without exposing anything else" passes.

These are the constituent stories that make up the core job (Klement's high-level job → supporting stories). Two to four per situation, merged into one prose block per situation, each story's grammar intact inside the prose. You may compress "When [situation]" once per group and let the shared situation govern the stories under it — but every story must still parse as situation + motivation + outcome.

### 4. Emotional and social jobs

Every job has functional, social, and emotional dimensions (Christensen). The job stories above carry the functional dimension; this section carries the other two. Emotional = how the person wants to feel (or avoid feeling) while making progress. Social = how they want to be perceived.

**The cardigan test:** strip the feeling verb. If what remains is just a functional job, it's a functional job wearing a cardigan — bin it. "Feel confident a share doesn't expose more than intended" survives, because the confidence is the point. "Feel happy using the export button" does not.

One or two per situation, one line each. If a situation has no genuine emotional stake, write nothing — an empty subsection beats an invented feeling.

### 5. Forces of progress

Why they switch, and why they don't (the four forces of progress, developed by Bob Moesta and Chris Spiek and popularised in Christensen's *Competing Against Luck*). Keep it tight — a line each, only the forces that are real:

- **Push** — the pain of the current situation that drives them off the status quo.
- **Pull** — the appeal of a better way.
- **Anxiety** — what worries them about the new way (will it be secure? will it lose my data?).
- **Habit** — the inertia of today's workaround, however bad.

Change happens when push + pull outweigh anxiety + habit. This is where a write-up earns its keep: the anxieties and habits are what a solution has to overcome — the "why now, and what's in the way" that a good discovery card captures.

### 6. Good, better, best

Tier how fully the job gets served — the good (enough) / better / best framing, or equivalently MVP / MLP (minimum *lovable* product) / complete.

- **Good (enough)** — the smallest thing that gets the core job done: resolves the biggest push and the top anxiety.
- **Better** — also serves the emotional and social jobs and the secondary situations. The version people would *choose*, not merely tolerate.
- **Best** — serves the job across edge situations and removes the residual anxieties and habits.

**The discipline that keeps this JTBD, not a backlog:** phrase each tier as the job it newly serves — the progress newly made — never a list of features. If you catch yourself listing features, you've fallen back into solution-space; restate as "at this tier the person can now…". This is the wrinkle the philosophy tolerates: the tiers are about *how completely the job is served*, so the jobs above stay solution-free.

**Retrospective mode:** *Good* describes what's shipped and already serving the core; *Better* and *Best* hold the known gaps — what the job still needs. A reader should be able to lift each gap straight into a ticket, but keep the job attached: never a bare bug report ("no backend clamp on scope widening") — the job half is what makes the gap matter.

**Greenfield mode:** the tiers are the build ambition. Flag under *Good* the outcomes most at risk of being underserved by the obvious minimum build, plus genuine unknowns about the situation or the job that need validating against users, support tickets, whatever evidence exists.

## The style contract

### Example budget

- One parenthetical example per situation in section 1.
- One worked scenario ("example thread") for the core job — a single concrete run through it, in a sentence or two. That's the core job's entire example allowance.
- Inside job-story prose, an example only where a reader who hasn't seen the feature would misparse the statement. That's the test — not "would an example be nice here". If the statement is clear bare, leave it bare.
- Parentheticals under ~15 words. Needing more usually means the statement is too abstract — fix the statement, not the example.
- Never one example per job story. That's the bloat failure this skill exists to prevent.

### Condensation contract

- Merge job stories into flowing prose within each situation group.
- **Lossless on job stories:** count job-story statements before and after condensing. Stories in = stories out. If you deliberately cut one, say so and why — never drop silently.
- Cut ornaments, not substance: per-line examples, table scaffolding, restated context, label-style headers.
- A full write-up for a mid-sized feature lands around one to two pages.

### Voice and language

Australian English throughout: minimise, authorise, organise, analyse, behaviour, licence (noun) / license (verb). *Program* for software; *programme* only for schedules of events. "Minimise" with a z is the single most common slip.

Human voice, inline rules:

- Vary sentence length. Let short ones land.
- Banned: "it's worth noting", "delve", "in today's landscape", "leverage" as a verb, "utilise" (just write use), "robust" unless it's genuinely about failure tolerance, "seamless".
- No rule-of-three padding. No bold-label bullet spam in the write-up itself.
- Plain verbs over nominalisations: "track", not "conduct tracking of".
- Contractions are fine. Write like you're explaining the feature to a colleague at their desk.

Final pass: if the `write-like-a-human` skill is available, read it and apply its checks. If not, the rules above stand alone.

## Failure modes

- **Solution language in the motivation or outcome** — "I want to click the share button" is the mechanism; "control what an outside party can see, for exactly as long as needed" is the job. Apply the rebuild test.
- **Persona padding** — "As a user, when…". The school drops the persona and leads with the situation. Name a role only where the situation truly differs by who's in it.
- **Job stories that are acceptance criteria** — "When I click submit, I want a spinner" is a UI spec, not a job. A job story survives a rebuild.
- **Forces that just restate the job** — forces are about the switch decision (what pushes, pulls, and holds back), not a re-list of motivations.
- **Good/better/best as a feature backlog** — each tier names the job it newly serves, not a pile of features.
- **Emotional/social jobs wearing cardigans** — a functional job with "feel" bolted on.
- **Silent job-story loss during condensation** — run the count, every time.
- **"Minimize" with a z** — and its friends: organize, behavior, license as a noun.
- **Tables where a sentence would do.**
- **Padding emotional/social because the section "looks empty"** — empty beats invented.

## Out of scope

This skill is the Job Story school (Klement) on Christensen's theory. It deliberately excludes Ulwick/Strategyn ODI's quantitative machinery — outcome-scoring, importance/satisfaction surveys, opportunity algorithms, outcome-based segmentation, and the eight-stage universal job map. If someone asks to rank or score outcomes, that's a prioritisation question: reach for a value/effort or RICE-style method, or a possible / viable / desirable / valuable lens, rather than improvising numbers here. The good/better/best section handles ambition tiering — how fully to serve the job — not numeric scoring.
