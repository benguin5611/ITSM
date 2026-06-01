# Scoring rubric

How `scripts/score.py` turns raw signals into a 0–4 level per person × discipline.
The aim is **contrast**: most cells should land 0–2, with 3–4 reserved for genuine
authority — otherwise every senior looks like an expert at everything and the matrix
is useless for succession planning.

## Inputs per cell
Deterministic (from `analyze.py`, which reads every comment):
- `authored_n`, `authored_w` (size-weighted), `authored_recent`
- `subst_review_given` — substantive reviews (>40 chars) this person gave others here
- `corrected_given` — corrective reviews/inline comments given (CHANGES_REQUESTED or corrective language)
- `corrected_received` — times this person was corrected here
- `inline_given`, `merged_others`, `learning_signal`

Qualitative (optional, from `findings/*.json` written by analysis agents):
- `review_authority`, `corrected_others`, `was_corrected`, `led_design`, `evidence[]`

> The pipeline works **without** the qualitative layer — it degrades to deterministic
> signal only. Agents enrich accuracy (especially `led_design` and `corrected_others`)
> and supply human-readable evidence. If sub-agents are unavailable, skip Phase 4; the
> matrix is still defensible.

## Authority vs learner
```
authority = 0.22·min(authored_n,12) + 0.9·min(subst_review_given,8) + 1.3·min(corrected_given,8)
          + 0.35·min(inline_given,10) + 0.9·min(merged_others,8)
          + 1.6·min(review_authority,8) + 2.2·min(corrected_others,6) + 3.0·min(led_design,3)
learner   = 1.1·min(corrected_received,12) + 1.8·min(was_corrected,8) + 0.7·min(learning_signal,8)
net       = authority − 0.6·learner
```
Volume is deliberately weak (it is noisy — one PR often touches 4–8 disciplines). Real
authority comes from **giving** corrective review, **leading** design, and **teaching** others.

## Base level (absolute)
- `3` strong: `net≥6 and authority≥6 and (subst_review_given≥3 or corrected_others≥1 or review_authority≥2 or led_design≥1) and learner<authority`
- `2` working: `net≥2 and exposure≥4`, or `exposure≥4 and authored_n≥4`
- `1` novice: any exposure or any learner signal
- `0` none

**Caps (pull learners down in their weak areas):**
- If `was_corrected≥2 or corrected_received≥7`, and no teaching/design here (`corrected_others=0, led_design=0, subst_review_given<3`) → cap at `2`.
- If `learner > 1.4·authority` with no teaching/design → cap at `2`.

## SME (4)
- **Team mode:** promote `3 → 4` only for the top authority-holders *within each discipline
  column* — `authority ≥ max(7, 0.55·column_max)`, `net≥6`, `(led_design≥1 or corrected_others≥2)`,
  `learner<authority`, and ranked in the column's top 4, max 3 SMEs per discipline. This is what
  makes columns differentiate instead of saturating.
- **Self mode:** no relative promotion (a team of one would self-promote). `4` only on very
  strong absolute evidence (`led_design≥2 and corrected_others≥3 and net≥10`).

## Overrides
`config.json["overrides"]` is a list of `["login","disc-id",level,"cited reason"]`. Use these
**sparingly** where the qualitative PR reading clearly contradicts the volume signal (e.g. a
high-volume author who is repeatedly corrected on a sub-skill). Each override must carry a cited
reason and is marked ⚑ in outputs. Overrides come from the **runtime config** — never hardcode
identities into the skill.

## Bus-factor
Per discipline, count engineers at level ≥ 3. `n_strong ≤ 1` = **CRITICAL** (bus-factor-of-one);
`= 2` = **WATCH**. `report.py` auto-derives upskilling candidates (highest-authority person at
level 1–2 in a critical discipline) — refine these with human judgement.
