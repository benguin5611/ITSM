# Phases 4 and 5 — land it, then leave it clean

## PR split with git as the oracle

Memory of what changed is never the checklist. The invariant: trunk plus every PR is byte-identical
to the feature branch, which stays pushed until the PRs merge — it is the checksum.

1. Freeze a SHA `F` (`git rev-parse HEAD`) and never chase the tip.
2. Derive the file list: `git diff --name-only $(git merge-base main F) F | sort`. Commit or discard
   any working-tree change first; the oracle sees only commits.
3. Partition every file into exactly one PR, at file granularity — a file two PRs need goes whole into
   the earlier one. Prove it before building: the union of the lists diffs clean against step 2, and
   `sort | uniq -d` over the concatenation is empty.
4. Build each PR from `F`'s bytes: branch from trunk, `git checkout F -- <paths>`, commit with your
   prose. Never retype content.
5. Final gate: merge every PR branch onto a throwaway branch from trunk and `git diff F..verify`
   must be empty, scoped to the changed paths if trunk moved. Non-empty prints exactly what was
   dropped; fold it in and re-run.

Squash-merge means the post-merge trunk is what you reconcile against, not your local branches.

Before reshaping or removing anything with a stable parseable shape — a table, a register, a fixed
heading — grep the whole codebase, not other docs: production code parses documentation more often
than anyone expects.

## Merging

Verify the merge regime by attempting a normal merge, not by reading settings; a ruleset can reject
what the classic API calls unprotected, and can make one required check un-bypassable while others
stay bypassable. Know which checks are required before treating green as sufficient. A standing bypass
permission is scoped to the blast radius it was granted for — a change touching production
credentials, a safety gate or a double-digit file count gets its own confirmation. Rebase onto trunk
immediately before opening a PR; prefer one final rebase over incremental force-pushes (a stuck
mergeability calculation after a force-push is unrecoverable for that PR). `gh pr create` reads the
shell's cwd: pass `--head` and `--base` explicitly. Confirm `MERGED` with `gh pr view --json state`,
never the merge command's exit code, and delete branches only after that — `git branch --merged` lies
under squash-merge. Stacked PRs merge bottom-up.

## Archival

Sweep every working artefact — intermediate docs, transcript digests, scripts, handovers, prior
versions, run journals and agent transcripts — into the project's archive. Confirm each copy exists
before removing the original; use a recoverable delete. Then: `git status` shows nothing from this run
uncommitted or unpushed; `gh pr list` shows this run's PRs merged or each explained; this run's own
worktrees and branches are gone. Touch nothing you did not create — an unfamiliar branch, worktree or
recent commit belongs to someone else and stays exactly as found.
