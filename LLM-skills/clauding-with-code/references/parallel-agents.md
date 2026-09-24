# Parallel agents — several builds on one repo at once

Distinct from a fan-out inside one run (`orchestration.md`) and from a same-lineage handover
(`templates/session-handover.md`). Stand this up only when a second concurrent build is real.

## Two layers that never track the same fact

Fast local layer: each agent in its own worktree and branch, coordinating through a small git-tracked
ledger that answers one question — is another agent building this now. Shipping layer: finished work
reaches trunk through the same reviewed PR path a solo run uses (`landing.md`). The ledger never grows
a PR or merged column; the forge owns merge state (`gh pr view --json state`, never `git branch
--merged`). Decide before dispatch whether the agents' work is disjoint (independent PRs, ideally via a
merge queue), dependent (stacked PRs off each other, merged bottom-up) or overlapping on the same
files (integrate, then split with the git-proven method).

## Identity

Pick your own one-word identifier from a diceware-style list, check existing branch prefixes and
ledger rows for a collision, and record it with your session ID in the ledger row and your first
status message — the word alone repeats across time. On resume, identity is live state: read the
ledger against the forge's branch list, or ask; never take it from a memory file or a handover. Two
artefacts disagreeing about who is live is a stop-and-ask, not a coin toss. Name files for the work,
not the worker; a handover addresses its reader as a new agent who claims their own identifier.

## The ledger

`AGENT_CLAIMS.md` at the repo root, header intact:

```markdown
<!-- Live-claims ledger. Tracks one thing: who is building what, now. Never a PR or merge column. -->
# Agent claims
Before claiming: self-assign an identifier; read the latest committed copy AND open PRs touching this
file. Merge rule: this file may push direct to trunk only where the ruleset allows (verify by pushing);
every other file goes through a reviewed PR, no exceptions. After claiming, re-read; the earlier
landed claim wins. Remove your row when your PR opens or you abandon the unit.

| Work-unit ID | Task | Agent (session) | Branch |
|---|---|---|---|
```

Any ledger edit spanning more than a couple of minutes (a rescue rebase, a hand-resolved conflict)
re-reads the committed file as the literal last step before committing and reconciles against that
fresh copy — a snapshot taken at the start of the operation is expired.

## Worktrees and what they share

Branch `<agent>/<work-unit>-<slug>`, one worktree each. Worktrees share the common git directory: the
stash stack is global (never stash to move work; commit to your branch), `FETCH_HEAD` is shared (pin
fetch targets by SHA), and a shared checkout is nobody's workspace. Before any git-mutating edit to a
shared tip, even one ledger line, cut a detached throwaway worktree from `origin/main`, edit, push,
remove it. Before touching any checkout that is not your own, `git status` and `git log -3`: unfamiliar
branch, staged changes or a commit minutes old means another agent is there — this applies to the
orchestrator's own interactive work, not only sub-agents. Recover your uncommitted work by copying
file contents into a fresh worktree; never disturb the other agent's branch. A shared runtime (one
database, one identity provider) is a separate hazard a worktree does nothing about; use a per-agent
environment where it matters.

## Sequential IDs

Numbers on trunk are not the free ones: an open PR already holds the next few, and a merged PR's
title is a permanent record of a number spent even after its doc row moved. `DG-HWM` is the gate.
Discipline on top: reserve the bare ID in a small PR, confirm it landed uncontested, then write content
that cites it; when launching a wave that allocates, release agents one at a time so claims land in
turn. A single line every agent appends to (a running "reconfirmed" note) is a sequential space in
disguise — resolve its conflicts by keeping both sides.

## Dead or hung agents

Judge by disagreement between signals, not silence: a transcript still ticking with no new commits,
pushes or file writes over a sane window for that step is the red flag; a long quiet full test run is
not. Check `git log`/`status` in its worktree, `gh pr list --search head:<branch>`, and a process
listing against the path. Before discarding: adopt real commits or diff, finish the remaining steps or
cherry-pick into a fresh worktree, and clear its stale ledger row. Discard only when nothing usable
exists.

## Talking to peers

When your work touches theirs, send a status message:

```markdown
# Status: <your unit> → <recipient>
What landed (commit/PR, how verified) · Relevant to you (the shared dependency, file or blocker) ·
Shared state you should know (environment you changed, from/to) · Coordination facts (a corrected
rule, a row to update) · Not touched (so they know what is safe to assume).
```

On handover, reconcile your task list against the other agent's own message, item by item: adopted
comes off, declined stays unclaimed, unnamed needs a human. Ownership is not monotonic — a stood-down
agent can return, so write who owns what as at when. Never clean up a peer's worktrees, branches or
rows. A peer's claim or correction is evidence to check against the primary source, in both
directions; then fix the artefact and tell them.

## Shared mutable environment

Wrap every shared-state mutation in try/finally with an explicit revert. Only stop what you started.
Check state before mutating; it may have moved. Announce mutations in a status message. A git hook is
shared environment via inherited variables: any nested `git` call from a hook strips
`GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES`
first, or it can land in a sibling worktree.

## Spawning an agent

The launch prompt is self-contained: repo, backlog location, ledger path, and "land per the ledger's
own merge rule". It asks the agent to claim (reserving a bare ID first if the space is sequential),
cut `<agent>/<unit>-<slug>` in its own worktree, report its identifier before building, build with
this skill's normal lifecycle, ship per the repo's disjoint/dependent/overlapping decision, drop its
ledger row when the PR opens, and delete branches only after the forge confirms the merge.

## Docs under concurrency

Each agent updates only the docs its own change touches, and a linter verifies structure, not truth.
Ship the doc-sentence flip in the same PR as the feature it describes; run a periodic code-wins audit
— read-only agents per doc cluster checking claims against live code — with the brief itself verified
first. Put a pointer to the ledger and this protocol in the repo's agent file; never a copy.
