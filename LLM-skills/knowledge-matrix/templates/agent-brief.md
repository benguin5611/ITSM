# Analysis agent brief — team mode (one per digest chunk)

Copy this brief for each `digest/chunk*.jsonl`, substituting `<CHUNK_FILE>` and the
absolute `<WORKDIR>`. Spawn the agents in parallel (one per chunk). Do NOT put any
person's name in this brief — the agent learns identities only from the data it reads.

---

You are extracting per-engineer authority signals from a GitHub PR corpus to build a
knowledge matrix. Work entirely from files on disk; do not use the network.

STEP 1 — Read the discipline taxonomy (canonical IDs + proficiency definitions):
`<WORKDIR>/taxonomy.md`

STEP 2 — Read your assigned digest file IN FULL — every line and every discussion entry:
`<WORKDIR>/digest/<CHUNK_FILE>`

Each line is one PR: `{repo, number, title, author, state, merged, mergedBy, createdAt,
additions, changedFiles, labels, disciplines:[...], discussion:[{by, kind, text, path?}]}`.
`kind` ∈ {comment, review:APPROVED, review:CHANGES_REQUESTED, review:COMMENTED, inline}.
Read the FULL text of every discussion entry — this is where authority signal lives.

YOUR JOB — for each human engineer, per discipline, judge authority vs learning:
- `review_authority` — gave a substantive/corrective/teaching review or inline comment showing
  command of the area (not just "LGTM").
- `corrected_others` — explicitly corrected, redirected, or taught another person on a technical point.
- `was_corrected` — was corrected, told they were wrong, or asked a basic/learning question.
- `led_design` — introduced, architected, or set the pattern for a subsystem (from title/body/their comments).
Primary discipline = the PR's `disciplines` array; refine using an inline comment's `path` or the
discussion text. Use ONLY the exact discipline IDs from `taxonomy.md`.

EXCLUDE bots entirely (any login containing: dependabot, copilot, github-advanced-security,
blacksmith, github-actions, renovate). Use logins EXACTLY as they appear in the data — never
invent, normalise, or guess a real name.

OUTPUT — write JSON to `<WORKDIR>/findings/<CHUNK_FILE>.json`:
```json
{ "<login>": { "<discipline_id>": {
    "review_authority": <int>, "corrected_others": <int>, "was_corrected": <int>, "led_design": <int>,
    "evidence": ["PR#<n>: <terse note>", ...]
} } }
```
Only include disciplines with real signal. Evidence: up to 5 per cell, ≤140 chars each, cite PR
numbers, prefer concrete "X told Y to…" notes. After writing, reply with ONLY a 3–4 line summary
(PRs read, who showed most authority and in what, notable teach/correct dynamics). The file is the
deliverable. Australian English.
