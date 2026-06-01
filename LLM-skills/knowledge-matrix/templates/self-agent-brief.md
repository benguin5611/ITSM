# Analysis agent brief — self mode (single agent, the caller's corpus)

Optional enrichment for self mode. One agent reads the caller's whole corpus
(`digest/corpus.jsonl`) and produces the same findings shape, focused on `<ME>` but
also recording where `<ME>` gave authority on others' PRs. Substitute `<WORKDIR>` and `<ME>`.

---

You are building a personal engineering gap-analysis for the GitHub user `<ME>` from their
PR history. Work entirely from files on disk; do not use the network.

STEP 1 — Read the taxonomy: `<WORKDIR>/taxonomy.md`
STEP 2 — Read the corpus IN FULL: `<WORKDIR>/digest/corpus.jsonl` (PRs `<ME>` authored, plus
PRs where `<ME>` reviewed or commented). Same per-line shape as the team brief.

For `<ME>` specifically, per discipline, judge:
- `review_authority` / `corrected_others` / `led_design` — where `<ME>` demonstrates command
  (teaches others, sets patterns, reviews authoritatively). These become **strengths**.
- `was_corrected` — where `<ME>` was corrected or asked learning questions. These become
  **development areas**. Capture WHO corrected them and on WHAT (the value is the specific lesson).
Use ONLY exact discipline IDs from `taxonomy.md`. Exclude bot logins. Never invent real names.

OUTPUT — write JSON to `<WORKDIR>/findings/self.json` keyed by login (include `<ME>` and, briefly,
anyone who corrected `<ME>` so the reviewer can see who the mentors are):
```json
{ "<login>": { "<discipline_id>": {
    "review_authority": <int>, "corrected_others": <int>, "was_corrected": <int>, "led_design": <int>,
    "evidence": ["PR#<n>: <terse note — who corrected/taught what>", ...]
} } }
```
After writing, reply with ONLY a 3–4 line summary of `<ME>`'s clearest strength and clearest
development area with one PR example each. Australian English.
