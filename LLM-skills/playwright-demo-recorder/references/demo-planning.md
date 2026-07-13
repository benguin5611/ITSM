# Phase 1 — Planning the beat plan

The beat plan is the demo's single source of truth: an ordered list of beats, each with a narration line, an action, and a duration. It is written **before any recorder code**, approved by the user, and Phase 4 later diffs the recording against it. ("Beat plan" always means this artefact; "script" means code.)

## 1. Enumerate what's demoable — from the actual work, never from memory

Ground every beat in what the branch/feature really contains:

```bash
git -C <repo> log --oneline origin/main..HEAD
git -C <repo> diff origin/main...HEAD --stat
```

Plus the branch README (if any) and the user's feature description. If the diff and the description disagree, ask — don't guess.

**Sanity-check the merge base.** Compare against `origin/main`, not local `main` (a stale local main pollutes the list with unrelated merged commits). Eyeball the commit list: if it contains work that clearly isn't this feature, re-anchor at the feature's first commit (`git log --oneline <first-feature-commit>^..HEAD`) and say you did so.

**Only the branch's story.** Cut any beat that showcases a pre-existing feature, however good it looks — a beat demoing a feature the branch didn't build dilutes the story and adds runtime for no reason. Demo *tooling* in the diff (recorder scripts, DEV hooks, probes) is never part of the story either — exclude it even when it dominates the commit count.

## 2. Order the beats in a narrative arc

Each beat sets up the next; the viewer never wonders "why am I seeing this?":

1. **Frame the problem** — title card / one-line setup (talk, no clicks).
2. **Admin/config primes what follows** — show the configuration whose effect the viewer is about to see.
3. **Core flow** — the main table/list/screen doing its job.
4. **Close the loop** — the step-2 config visibly reappearing in use (e.g. the adaptive form showing the admin-defined fields).
5. **Payoff view** — the visualisation/graph/wow moment.
6. **Generality** — "same pattern everywhere" (a second record type, a second context).
7. **Summary caption** — the one-line takeaway.
8. **End card** — full-screen "Demo complete" with a spoken outro.

**Beat granularity:** one narration line + one action (or one tightly coupled action group) per beat, ~4–12 s each. An arc stage above usually decomposes into 2–3 beats; a 60-second "step" in a human-presented flow is too coarse for a recorded beat.

## 3. Write the narration lines

Each beat gets exactly one narration line. It is simultaneously the on-screen caption and the voiceover, so:

- **≤ ~12 words.** With speech-length pacing, every extra word directly stretches the video.
- **Match your organisation's copy policy** (a preferred English variant, tone rules, whatever applies), and if you have a writing-polish or AI-tell-detection skill, **actually run it on the full set of lines** — AI-prose tells are far louder read aloud than they look on the page.
- **No em-dashes in narration lines** — commas/full stops give the TTS its pauses anyway (the `SPEECH_MAP` converts any that slip through). This rule wins over any em-dash you see in this file's own formats or example.
- **Never name specific sample-data parties in narration.** Sample data varies per machine and per reload — narration that names a specific person or record breaks silently when the data changes. Describe roles, not names.
- Words the voice mispronounces go in the recorder's `SPEECH_MAP`, not in the caption text (see voiceover.md).

## 4. Estimate the runtime — and get it approved with the beats

Runtime ≈ Σ per beat (narration duration + 450 ms tail + action time). Rule of thumb: **~3 s per short narration line (tail included), plus 2–5 s per beat of actions/settling; force-layout graphs need ~3.5–5 s of settle before you narrate over them.** Each beat's "Est" column includes its tail. State the estimated total in the beat plan. After recording, Phase 4 compares actual vs estimate: >20 % over means re-cut narration or beats, not silent delivery.

## 5. Flag the undemoable up front

For each beat, note anything that can't be reliably scripted, with the chosen workaround:

- **Canvas hit-targets** (graph nodes/edges) → DEV-only coordinate hook (see recorder-patterns.md), or narrate instead of click.
- **Hover-only affordances** → make them always-visible for the demo (often better UX anyway), or narrate.
- **Non-deterministic layouts** → settle time + hooks; never guess pixels.

## 6. Approval — and re-approval

Present the beat plan (beats, narration lines, per-beat durations, total runtime, workarounds) and get explicit approval before writing the recorder. **If Phase 2 forces a beat change (e.g. a click downgraded to narration), re-present that beat before recording** — the shipped video must match what was approved.

## Beat plan format

```markdown
# <demo-name> beat plan (est. total M:SS)
| # | Beat | Narration (caption = voiceover) | Action | Est |
|---|------|----------------------------------|--------|-----|
| 1 | Title | "<Product>: <feature>" | title card, centre | 4s |
| 2 | Admin primes | "Admins define X per Y" | open Settings → X | 8s |
| … | | | | |
Workarounds: <undemoable items + chosen approach>
```

## Worked example (illustrative — a fictional support-ticketing app)

A worked demo-sequencing answer for a fictional feature: tags on a support ticket, where each tag type carries its own metadata. **It illustrates the method, not a real product** — invented for this reference so the arc is concrete without describing any real application. Where an example like this ever disagrees with your actual code or README, **the code and README win** — take the arc, the each-step-sets-up-the-next ordering, and the honest mock-store framing note; not the selectors:

> Here's the tightest sequential flow — it's ordered so each step sets up the next and lands the core argument (tag data belongs on the *tag*, one ticket can carry many, and you need both table and graph). ~5 minutes.
>
> **Before you start (10 sec)** — Log in as a standard support user. Pick **one ticket** as your hero and keep it open in a tab. The sample loader builds the story around whichever ticket you're viewing. It's front-end-only (localStorage) — click freely, nothing hits the backend. To start clean between runs, clear site data for localhost.
>
> **1. Frame the problem (talk, no clicks) — 20s** — "This ticket is tagged Billing, Urgent, *and* Escalated. That's three tags on the same ticket, each with its own data — and that data belongs to the tag, not to the ticket as a whole."
>
> **2. Admin defines the fields first — Settings → Tag Types — 60s** — Switch the type selector: **Billing** vs **Urgent** vs **Escalated** — show each captures *different* fields. Point: "An admin controls what's captured per tag type — same mechanism as ticket custom fields." This primes the next step.
>
> **3. Tags tab → Table view — 60s** — Open your hero ticket → **Tags** tab → **Load sample tags**. **Table** shows every tag on this ticket. Highlight: the **same tag type appears across multiple tickets** — the reuse point. Click the **eye icon** → drawer shows the full captured metadata.
>
> **4. Add a tag — closes the loop with step 2 — 45s** — **Add tag** → choose **Escalated** → the metadata form *adapts* to the fields you saw in admin → save → it appears in the table instantly.
>
> **5. Graph view — the payoff — 60s** — Toggle **Graph**. Show your hero ticket and **another ticket** connected *through* a shared tag — the indirect view a flat list can't give.
>
> **6. It's everywhere — 20s** — Open a different record type (e.g. a **Task**) → same Tags tab, sensible types. "One pattern across every record type."
>
> **One thing to say out loud** — The graph/table read the **prototype's mock store** (by design — not wired to the backend). So frame it as "here's the *experience* we'd build," not "this is writing to the database."

(A recorded version of a flow like this might later **cut** a step-2 aside comparing the simple type selector against an advanced editor — pre-existing feature, not this branch's story — and turn step 1's spoken framing into a title-card beat. Both are the §1–§2 rules in action.)
