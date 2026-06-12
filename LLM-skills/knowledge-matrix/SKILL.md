---
name: knowledge-matrix
description: >-
  Build an engineering knowledge matrix from a team's GitHub pull-request history — a
  colour-coded people×discipline heatmap (red→green) plus a narrative report showing who
  is an SME vs a novice in each discipline, for succession and upskilling planning. Reads
  every PR (open + closed + merged) and every review/comment/inline thread to score
  proficiency from authorship volume, review authority, and who-corrects-whom. Two modes:
  TEAM (everyone — full matrix, bus-factor and succession risk) and SELF (only the caller's
  PRs — a private personal gap analysis). Use whenever someone asks to "build a knowledge
  matrix", "skills matrix", "who knows what", "who are our SMEs", "succession planning",
  "find knowledge gaps / bus-factor risks", "analyse our PRs to see who's strong/weak in X",
  or "show me my own engineering gaps". Identity comes ONLY from the chosen Git repositories
  at runtime — the skill never hardcodes names or usernames.
argument-hint: "[--team | --self] [owner] [repo ...]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, TodoWrite
---

# Engineering Knowledge Matrix

This skill profiles an engineering team's strengths and weaknesses across disciplines by
mining their GitHub PR history, and renders a **colour heatmap** (`knowledge-matrix.html`)
plus a **narrative report** (`knowledge-matrix-report.md`).

It runs a pipeline of bundled scripts in `scripts/`:
`harvest.sh` → `analyze.py` → `digest.py` (+ parallel agents) → `score.py` → `render.py` → `report.py`.
Each reads a single `config.json` in the working directory, so runs are reproducible and resumable.

## Privacy — read first
- **Identity is pulled ONLY from the chosen Git repos at runtime.** Never hardcode, guess, or
  invent a person's name or handle anywhere — not in scripts, config, narrative, or chat.
- The matrix uses **GitHub login handles**, not real/display names. Do not map handles to real
  names or add PII unless the user explicitly asks.
- **Exclude bots** (dependabot, copilot, github-advanced-security, github-actions, renovate, etc.).
- This is an **evidence-grounded judgement artefact, not a performance appraisal.** Say so in the
  output, and treat low cells as development opportunities.

## The two modes
- **TEAM** (`--team`, default): harvests *everyone's* PRs across the chosen repos and builds the
  full matrix with relative-SME gating, bus-factor and succession recommendations.
- **SELF** (`--self`): harvests only the *caller's* PRs (authored) plus the PRs they reviewed/
  commented on, and produces a private personal gap analysis (absolute levels, strengths, weak
  spots, untouched areas). Lighter and faster — no team comparison.

## Phase 0 — Prerequisites & resolve target
1. Require `gh` (authenticated) and `python3`/`jq`. `gh auth status` must show a logged-in account.
   **This makes the skill local-only:** on claude.ai the sandbox has no authenticated `gh` and no
   repo access — stop and tell the user to run it in Claude Code (or another local runtime) instead
   of attempting a degraded run.
2. **Mode:** `--self` → self; otherwise team. If ambiguous, ask.
3. **Owner:** from the argument, else infer from the repos' git remotes (`git -C <repo> remote get-url origin`),
   else ask. (e.g. a GitHub org like `your-org`.)
4. **Caller login (self mode):** `gh api user --jq .login`. This is `me`. Confirm with the user.
5. **Working dir:** `~/Downloads/knowledge-matrix/` (override if the user names another).
   Create `raw/`, `digest/`, `findings/` under it.
6. **Recency cutoff & today:** set `recent_cutoff` to ~12 months before today, and `today` to the
   current date (pass these in — do not call date functions inside scripts).

## Phase 1 — Choose repositories & write the base config
- If the user named repos, use those. Otherwise list candidates: `gh repo list <owner> --limit 200 --json name`
  (or enumerate local clones' remotes). Get PR volume per candidate:
  `gh pr list -R <owner>/<repo> --state all --limit 2000 --json number --jq 'length'`.
- **Scope deliberately** and tell the user the plan: include repos that reflect current skills; consider
  excluding legacy/archived repos or weighting them down. Confirm scope before a very large harvest.
- Write a **base** `config.json` (the discipline taxonomy is NOT set here — it is discovered from the data in Phase 2.5):
```json
{ "mode": "team", "owner": "<owner>", "title": "<Team> Engineering Knowledge Matrix",
  "repos": ["<repo>", "..."], "recent_cutoff": "<YYYY-MM-DD>", "today": "<YYYY-MM-DD>",
  "chunks": 6, "overrides": [] }
```
For self mode set `"mode":"self"` and `"me":"<login>"`. All identity (`me`, contributors) and all project
structure come from the repos — never hardcode a name, handle, product, or repo into the skill.

## Phase 2 — Harvest the PR corpus
For each repo, harvest the full corpus (authors, changed-file paths, labels, reviews, **every**
comment/review/inline body) into `raw/<repo>.ndjson`:
- **Team:** `scripts/harvest.sh all <owner> <repo> raw/<repo>.ndjson`
- **Self:** `scripts/harvest.sh search <owner> <repo> raw/<repo>.me.ndjson "author:<login>"` and
  again with `"reviewed-by:<login>"` and `"commenter:<login>"` (the harvester de-dupes by number).
- Run the big repo in the background; the small ones in the foreground.
- **Verify completeness:** compare `wc -l raw/<repo>.ndjson` against the `gh pr list … --jq length`
  count. If a paged harvest stopped early (GraphQL complexity/timeout), backfill the missing numbers
  with `scripts/fetch_pr.sh <owner> <repo> <number> raw/<repo>.ndjson` (it retries per PR).
- Comments/reviews are captured up to 100/50 per PR (no observed truncation in practice); only a few
  bulk PRs truncate the *file* list at 100 — immaterial. Note this, don't chase it.

## Phase 2.5 — DISCOVER the discipline taxonomy from the data (do not assume generic categories)
The matrix columns must reflect what *this* codebase actually contains — derived from the data, the
way a human analyst would by reading the repo structure. Do not ship the generic defaults as the answer.
1. `python3 inventory.py` — aggregates, PR-weighted across every changed file: languages (extensions),
   top-level and second-level directories, and service/domain directory names. Writes `inventory.json`.
   (Optionally also `gh api repos/<owner>/<repo>/languages`.)
2. **Derive the taxonomy** from `inventory.json` — inline yourself, or delegate to one agent — using
   [templates/taxonomy-discovery-brief.md](templates/taxonomy-discovery-brief.md). Combine layer/
   language disciplines (only those evidenced) with product-domain disciplines clustered and named
   from the service/domain directory names. 12–22 short hyphenated IDs, each traceable to inventory
   evidence — never to outside knowledge of the company/product. Write `taxonomy.discovered.json`.
3. `discmap.py` auto-merges `taxonomy.discovered.json` into the config for every later step. Show the
   user the discovered disciplines (with the one-line evidence per column) and let them tweak before continuing.

The generic taxonomy in `scripts/discmap.py` is a **last-resort fallback only** (e.g. discovery
infeasible) — say so explicitly if you ever fall back to it.

## Phase 3 — Deterministic analysis (reads every comment)
From `scripts/`, with `KM_WORKDIR=<workdir>`: `python3 analyze.py`.
This reads every comment/review/inline body and writes `metrics.json` — per-person × per-discipline
authorship, substantive/corrective reviews given, corrections received, merge authority, and a
directional who-corrects-whom graph. **The pipeline is fully functional after this step alone.**

## Phase 4 — Qualitative enrichment (recommended, optional)
Adds human-readable evidence and sharpens `led_design`/`corrected_others`. If sub-agents are
unavailable, **skip this phase** — `score.py` degrades gracefully to deterministic signal.
1. `python3 digest.py` — builds slim digests with full discussion text. Team mode splits into
   `digest/chunk*.jsonl` (balanced by discussion volume); self mode writes `digest/corpus.jsonl`.
2. Spawn analysis agents **in parallel** (Agent tool), one per chunk, using
   [templates/agent-brief.md](templates/agent-brief.md) (self mode: a single agent with
   [templates/self-agent-brief.md](templates/self-agent-brief.md)). Substitute the absolute
   `<WORKDIR>` and chunk filename. Each agent writes `findings/<chunk>.json`.
3. If the agents hit a usage/rate limit, do the same reading yourself over the digest files (it is
   the same task), or skip to Phase 5 with deterministic-only scoring.

## Phase 5 — Score
`python3 score.py` → `matrix.json`. See [references/scoring-rubric.md](references/scoring-rubric.md).
- Levels 0–4; team mode promotes strong→SME *relative to each discipline column* so columns
  differentiate; self mode uses absolute levels.
- **Review the result.** Where the qualitative reading clearly contradicts the volume-driven level
  (e.g. a high-volume author repeatedly corrected on a sub-skill), add an evidence-cited override to
  `config.json["overrides"]` as `["<login>","<disc-id>",<level>,"<cited reason>"]` and re-run
  `score.py`. Keep overrides few and justified; they are marked ⚑.

## Phase 6 — Render & report
- `python3 render.py` → `knowledge-matrix.html` (team: discipline heatmap + a **proficiency-by-repository**
  heatmap with repo-ownership risk + per-engineer cards + bus-factor; self: per-discipline and per-repo bars
  + strengths/gaps). The per-repo slice answers "who can own / be moved onto repo X".
- `python3 report.py` → `knowledge-matrix-report.md` (matrix table, bus-factor, profiles,
  auto-derived succession priorities).
- **Then refine the narrative with judgement:** the auto-derived succession actions are a starting
  point. Add a short executive summary, sanity-check surprising cells against the linked PRs, and
  tighten role labels. Roles are heuristic — override per person via `config.json["roles"]`
  (`{"<login>":"<role>"}`) if needed, sourced from the repo activity, not assumed.

## Phase 7 — Deliver
Surface both files (they live in `~/Downloads/knowledge-matrix/`). Summarise the headline findings:
the pillars, the bus-factor-of-one disciplines, the over-concentration risk, and the clearest
upskilling targets. Offer to re-run periodically to track movement.

## Operational rules
- **Read-only on the source repos** — the skill only reads PR metadata via `gh`; it never writes to
  any target repo.
- **All artefacts live in the working dir** (default `~/Downloads/`), never inside a target repo.
- **Never echo more identity than necessary.** When demonstrating progress, prefer counts/levels over
  pasting handle lists; never reproduce a full name×discipline grid in chat unless asked.
- **Australian English** throughout (chat, code comments, reports).
- **Scale to the ask:** a quick personal check (self mode) is cheap; a full multi-repo team matrix can
  be thousands of PRs — confirm scope and run the heavy harvest in the background.

## Updating this skill
The discipline set defaults to a generic, language-agnostic taxonomy and is normally tailored per run
via `config.json` (Phase 1). To change the built-in defaults for a different kind of codebase, retarget
codebase, edit `scripts/discmap.py` (`DISCIPLINES`, `REPO_BASE`, `map_path`) and
[references/discipline-mapping.md](references/discipline-mapping.md) together, and adjust the column
groups in `render.py`/`report.py`. After any change, follow the skill-sync convention: push to the
canonical repo, sync to `~/.claude/skills/`, regenerate the Downloads ZIP. Keep the skill
identity-free — verify with a grep against any real handle list before committing.
