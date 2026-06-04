# Versioned artefact — changeset + requirements-coverage map (templates)

The synthesis produces a NEW version of the artefact (preserving correct content verbatim with its IDs) plus these two companion outputs. The artefact itself carries NO open-questions section.

## Changeset memo
```markdown
# <Artefact> — V<n-1> → V<n> Changeset

**Artefact:** <path> (grounded at HEAD <hash>)   **Prior baseline:** <hash>

## What changed, at a glance
- <re-grounding / renames / CODE-WINS corrections, each one line>

## Counts
| | V<n-1> | V<n> |
|---|---|---|
| Requirements | <a> | <b> |
| Coverage rows | <a> | <b> |
Change classes: FIX-STALE <x>, ADD <y> (covering <z> new reqs), RECLASSIFY <p>, STRENGTHEN <q>. Net +<b−a>.
> Verified by direct recount: <b> distinct IDs, 0 duplicates, bullets == rows. (Do NOT relay the synth's self-tally — re-derive it.)

## Findings considered but not adopted
- <finding> — <why not> (cite precedent / mitigation / "too much polish")

## Dead code (adjudicated)
- REMOVE: <item> — <receipts>   |   KEEP: <item> — <reason>
```

## Requirements-coverage map
Map every external requirement (spike / principle / spec clause) to the artefact requirement(s) that cover it, or mark it deferred-with-reason. This is what makes the suite *traceable*.
```markdown
| External requirement | Artefact coverage | Status |
|---|---|---|
| <REQ-id> | <req ids> | covered / TO IMPLEMENT / deferred-with-reason (<why>) |
```

## QC gate (run before "final")
- Requirement bullets **==** coverage rows; per-section sums **==** headline count.
- Zero duplicate IDs; IDs globally unique and not reused from a prior pass.
- No residual open-question / "TBD" / "❓" language in the artefact.
- Change-class tally reconciles with the count delta.
- Every owner decision is baked in and recorded in the decision record.
