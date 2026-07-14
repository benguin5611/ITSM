# Fresh-write SPEC.md, PR-PLAN.md, and architecture-c4.md from current codebase state

This is the gold-standard methodology for writing (or re-writing) the three canonical feature
artefacts. It was distilled from a long-running feature whose three canonical docs had been
patched through dozens of commits and had drifted from the code. The methodology applies to any feature.

## Why fresh write, not patch

"Rewriting" means starting from the existing file and editing — still anchored to old prose,
prone to carrying forward stale phrasing. **Fresh write**: ignore the existing file content
entirely. Use the current section headings as a skeleton only. Write new prose for each section
verified directly against the running code. Existing docs become a content checklist (these topics
must all be covered), not a starting draft.

The git log is the authoritative record of how we got here. These docs describe where we are.

Signs a doc needs a fresh write (not a patch):
- Inline changelog at the top (commit hashes, "(landed `xxxxx`)" annotations)
- Conflicting HEAD claims in the same document
- Sidebar boxes explaining historical renames or migration squashes
- "Living document / concurrent agent can move HEAD fast" framing
- RPC counts, enum value counts, or file lists known to be stale
- Any section framing an event in terms of "what changed" rather than "what is"

---

## Heading structures (validate before writing)

### SPEC.md

Keep the existing section structure. Fresh content only.

```
# <Feature name> — Specification

[Big-feature framing paragraph + single HEAD reference — nothing else before Overview]

## Overview
## What was built
## Terminology
## How it works end to end
  ### <key flow>
  ### <key flow>
## Why it was built this way
  ### <settled decision>
  ### <settled decision>
  ### Standing rejections register
  ### PR-ordering rationale
## Architecture and as-built code map
  ### <layer>
  ### <layer>
## Security posture
  ### Threat model
  ### Outstanding findings
  ### Accepted residuals
  ### Standing rejections
## Pre-production readiness
```

### PR-PLAN.md

```
# <Feature name> — PR Decomposition Plan (PR1–PRN)

[Intro paragraph — git as the completeness oracle, present tense, no history narrative]

## Frozen anchors
[table: F, BASE, main tip, total changed files — no history narrative]

## Partition at a glance
[table: PR1–PRN, files, depends-on]

## PR1 — <tracker-id> <title>
[scope N files; merge first; how to review]

## PR2 — ...
...

## Partition proof
[exhaustive + disjoint shell commands against current F]

## Final verification gate
[the invariant: main+all PRs ≡ F; the git checkout transfer commands; empty-diff check]
```

Each PR section has: **Scope (N files)**, file list, **Summary**, **What changed and why**,
**Dependencies / merge order**, **How to review / blast radius**, **Test notes**.

### architecture-c4.md

Standard C4 structure — keep it. Fresh intro paragraph and updated diagram content only.

```
# <Feature name> — Architecture Diagrams

## System Context
## Containers
  ### Data tables and their access roles
## Components — inside the API
## Dynamic view — <key end-to-end flow>
```

---

## Phase 0 — Transcript survey (before writing anything)

The transcripts from the feature's development contain the full reasoning behind every design
decision that ended up compressed into a one-liner in the current spec. Reading them gives the
agent the "why this, not that" context it needs to write authoritative dispositions — especially
for ACCEPTED-RESIDUAL calls, standing rejections, and OUTSTANDING findings.

Claude Code transcripts live in `~/.claude/projects/<project-slug>/`. Before writing any of the
three docs:

1. Find all JSONL transcript files modified since the feature work started:
   ```bash
   touch -t <YYYYMMDD>0000 /tmp/feature-start-marker
   find ~/.claude/projects/<project-slug>/ \
     -name "*.jsonl" -newer /tmp/feature-start-marker | sort
   ```

2. Read through the relevant sessions, extracting for each design decision:
   - The full reasoning given at the time
   - Any alternative that was explicitly rejected and why
   - Any correction to earlier thinking (if a decision reversed, capture the reversal reason)

3. Use this context to write the ACCEPTED-RESIDUAL dispositions and standing rejections
   accurately — verify against the actual reasoning, not just carrying forward one-liners.

The transcript survey also covers the finding ledger: confirm every OUTSTANDING finding is still
open (hasn't been closed in a recent commit), and every ACCEPTED-RESIDUAL still reflects the
current posture.

---

## Phase 1 — Finding ledger decision

Keep: OUTSTANDING, ACCEPTED-RESIDUAL, standing rejections.
Drop: FIXED entries (they are changelogs; the fix is in the code).

The restructured security posture section:
1. Threat model (current controls — written as "what IS there", not "what was wrong")
2. OUTSTANDING findings (open work, brief table with what's needed)
3. ACCEPTED-RESIDUAL findings (brief table — fold related residuals into a single heading; no
   per-decision H3 headings needed)
4. Standing rejections (table — prevents re-raising)

---

## Writing instructions

### SPEC.md

**Opening** (required structure):

First paragraph: stake the feature's significance — compliance surface, audit trail, IAM
decoupling, lifecycle model — whatever is load-bearing. The spec exists at this level of detail
because the work earned it: every subsystem traces to a requirement.

Second line: ground the document with a single HEAD reference and branch name. Nothing before
Overview except these two elements.

Example:
> <Feature name> is a big feature. The security surface, the audit trail, the access-control
> model, the lifecycle model — all of it is load-bearing. This spec exists at this
> level of detail because the work earned it: every subsystem traces to a requirement, the PR split
> is described in PR-PLAN.md, and a reviewing engineer should finish this knowing exactly how the
> feature works, satisfied it works without breaking its own workflow, adjacent code, or its security
> properties, and knowing what must be true in production before it ships.
>
> All load-bearing claims are grounded in the code at HEAD `<SHA>` on `<branch>`.

**What NOT to carry forward from a patched doc**:
- Any inline changelog (commit hashes, landing annotations)
- Sidebar boxes narrating historical renames or schema changes
- All "(landed `xxxxx`)" inline annotations — keep the claim, drop the attribution
- "Living document" / "concurrent agent" framing
- Framing a resolved finding as "was X, now Y" — it's Y; state as fact
- Any card/ticket ID that was scrubbed from the feature artefacts

### PR-PLAN.md

**Before writing**, derive the file list from git — do NOT copy from the old PR-PLAN:

```bash
git -C <repo> rev-parse HEAD                                        # current F
git -C <repo> merge-base main HEAD                                  # current BASE
git -C <repo> diff --name-only main HEAD | grep -v '^vendor/' | sort   # authoritative file list
git -C <repo> diff --name-only main HEAD | grep -v '^vendor/' | wc -l  # total count
```

**Partition methodology** (the only safe approach — see also `pr-split-method.md`):

1. Run the git commands above → `full.txt`
2. For each PR, assemble its file list as a text file (`pr1.txt`…`prN.txt`) by assigning
   every file from `full.txt` to exactly one PR based on path patterns and concern
3. Before writing a word in the PR-PLAN, **run the proof**:
   ```bash
   # Disjoint: must be empty (no file in two PRs)
   cat pr1.txt pr2.txt ... prN.txt | sort | uniq -d

   # Exhaustive: must be empty diff (union = full list)
   cat pr1.txt pr2.txt ... prN.txt | sort > union.txt
   diff union.txt full.txt
   ```
4. **Sanity-check pass** — after the proof returns empty, read each file assignment and verify
   the file's actual content matches its assigned PR concern. Flag any that look wrong and move
   them before writing.
5. Only write the PR-PLAN once both proof checks return empty AND the sanity pass is done.

This is non-negotiable. A missing file means reconstruction produces a different tree from the
feature branch, which means something won't compile or a test will be missing.

**What NOT to carry forward from a patched doc**:
- Any "Note on F" section narrating commits since the prior anchor — pure history
- "What changed" prose that explains intermediate rename/retype artefacts — state current API only
- Checklist commands or partition proofs that reference an old F hash
- File lists assembled from memory (they will be missing files)

### architecture-c4.md

Fresh intro paragraph (same stale-hash and rename-history problems as SPEC opening). The diagrams
are largely structural but need verification:
- Data tables: confirm every table's column list against the current migration files
- Components diagram: confirm every handler appears, including newer ones added late in the branch
- Sequence diagram: confirm the full lifecycle (including state-change paths) is represented

---

## Verification after all three files are written

After writing, run these sanity checks for any identifiers that were renamed, squashed, or
superseded during the feature work. Adapt the patterns to the specific feature:

```bash
# Old RPC/type names must not appear (except legitimate retained HTTP bindings)
grep -n "<old-rpc-name>\|<old-type-name>" SPEC.md PR-PLAN.md

# Squashed/superseded migration numbers must not appear
grep -n "<old-migration-num>" SPEC.md PR-PLAN.md architecture-c4.md

# Stale RPC counts
grep -n "<old-count> RPC\|<old-count> new.*RPC" SPEC.md PR-PLAN.md

# Stale enum value counts
grep -n "(0–<old-max>)\|values.*0–<old-max>" SPEC.md
```

Spot-checks:
- Every RPC in the final inventory appears in PR-PLAN's file list for the proto PR
- The PR-PLAN's F hash matches `git rev-parse HEAD` at execution time
- Partition proof re-runs clean against the live repo
- Every "outstanding" finding in the security posture is still actually open in the code
