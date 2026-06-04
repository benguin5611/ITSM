# Decision record — template (one canonical record, carried across passes)

One file per review thread. Prime every pass with it; never re-litigate a settled item without new evidence. Discrete, single-theme; convert relative dates to absolute.

```markdown
# <Artefact> — Decision Record

**Artefact:** <path>   **Ground truth:** <code map> @ commit <hash>   **Updated:** <YYYY-MM-DD>

## Settled — do NOT re-raise (with rationale)
- D<n> — <decision> — <why> — <date> — <who signed off>

## Resolved this pass (owner decisions, baked into the artefact)
- D-V<n>-<m> — <question> → <answer chosen> — <how applied: which requirement(s)/ids> — <date>

## Accepted residual risks (carry forward; not findings)
- <risk> — <why accepted> — <date>

## Standing rejections (considered, deliberately not done)
- <proposal> — <why rejected (cite the precedent / "too much polish")>

## Open — awaiting the owner (NEVER left in the final deliverable)
- <item> — <recommended option first> — <what it gates>

## Counts (this version)
- <N> requirements / <N> coverage rows — verified: bullets == rows, 0 duplicate IDs.
```

**Rules:** globally-unique IDs, never reused across passes. Every "Resolved" entry names where it was baked into the artefact. The "Open" section is emptied (resolved with the owner) before the deliverable is called final.
