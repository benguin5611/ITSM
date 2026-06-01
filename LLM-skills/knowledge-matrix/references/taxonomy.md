# Discipline taxonomy

The matrix columns are **disciplines**. This skill does **not** ship any company's or
product's disciplines. It works in two layers:

1. **Generic default** — a universal engineering taxonomy that applies to almost any
   software team, defined in `scripts/discmap.py` (`DEFAULT_DISCIPLINES`).
2. **Project-specific (discovered at runtime)** — the orchestrator inspects the target
   repositories (languages via the GitHub API, top-level directories, service/package
   names) and proposes a tailored discipline set, which the user confirms. That tailored
   taxonomy is written into the per-run `config.json` (keys `disciplines`, `groups`,
   `path_rules`, `lang_rules`, `repo_base`) and overrides the defaults for that run.

All project-specific structure therefore comes from the repos at runtime. Nothing here
names a person, company, product, or internal repository.

## Generic default disciplines
Application code: `frontend`, `backend`, `database`, `api-contracts`.
Platform / infra / DevEx: `infra-iac`, `ci-cd`, `containers-deploy`, `local-devx`.
Cross-cutting: `auth-security`, `observability`, `testing`, `docs`.

These are deliberately broad. For a real run you will usually refine them — e.g. split
`backend` into the languages actually present, or add the team's product domains as
columns (derived from service/package directory names, never assumed).

## Proficiency levels (per person × discipline)
- `0` none — no evidence of activity
- `1` novice / exposure — a few small/dependent PRs, asks questions, gets corrected, no review authority
- `2` working — authors real changes here, reviewed by others, occasional minor review comments
- `3` proficient / strong — authors substantial changes independently, reviews others' work substantively, trusted
- `4` SME / authority — the go-to: sets patterns, corrects others authoritatively, others defer, owns the area

## Authority signals to weigh
**RAISES level:** volume & size of authored PRs in the area; substantive approving/change-request
reviews on OTHERS' PRs; correcting others and being deferred to; merging others' PRs (merge
authority); designing/introducing the subsystem; recency (last ~12 months weighted higher).

**LOWERS level:** being corrected repeatedly; asking basic questions; only dependabot-style or
trivial edits; no activity in >12 months (mark inactive/former rather than expert).

## Designing a project-specific taxonomy (runtime)
- Keep IDs short, lowercase, hyphenated — they are dict keys everywhere.
- Aim for 12–22 columns. Too few and the heatmap can't differentiate; too many and thin
  columns add noise.
- Group related disciplines (`groups` in config) for the rendered column bands.
- Some cross-cutting disciplines (e.g. application security) may be scored mainly from
  review/comment authority rather than file paths, so their PR-count column can read low —
  that is expected, not a bug.
