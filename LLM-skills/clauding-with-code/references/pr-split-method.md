# PR split — git as the completeness oracle, not your memory

Splitting a long-lived feature branch into reviewable PRs is where code silently disappears. The thing that fails is exactly the thing people lean on: recall of a large change-set. A human (or an LLM) reconstructing "what changed" from memory will drop files, miss a helper, forget a migration — and the loss is invisible until production. So memory is never the oracle. **Git is the oracle.** Every "is this complete?" question is answered by a diff that is empty or not, never by judgement.

## The invariant
`(main + all PRs)` must be byte-identical to the feature branch. The feature branch therefore *is* the checksum. Keep it pushed and untouched until the invariant provably holds **and** the PRs have merged — it is the only thing that can prove nothing was dropped. Delete it earlier and you have thrown away the answer key.

## Method
1. **Freeze a SHA `F`.** A concurrent agent or process moves `HEAD` while you work; pin the split to one commit and never chase the tip. Record `F` explicitly (`git -C <repo> rev-parse HEAD`) and treat it as immutable for the whole split.

2. **Derive the checklist from git.** The changed-file list is the work, not your notes:
   ```
   git -C <repo> diff --name-only $(git -C <repo> merge-base main F) F | sort
   ```
   Use the merge-base, not raw `main..F`, so unrelated main commits don't pollute the list. This sorted list is the universe every later step must account for.

3. **Partition, then PROVE the partition — before building anything.** Assign every changed file to **exactly one** PR. Split at **file granularity, never hunk**: hunk-splitting drops code, and the exhaustive-partition proof only holds at file level. A file genuinely shared by two PRs goes *wholesale* into one of them (the earlier/foundational PR), never carved up. Prove the partition mechanically:
   - **Nothing unassigned, nothing extra** — the union of the per-PR file lists, sorted, must `diff` clean against the step-2 list (empty diff).
   - **Nothing duplicated** — concatenate all per-PR lists and run `sort | uniq -d`; output must be empty.
   Both empty = exhaustive and disjoint. Do not write a single PR branch until both checks pass.

4. **Build each PR from the exact bytes of `F`.** Branch off `main`, then transfer real content — never re-derive, never re-type from memory:
   ```
   git -C <repo> checkout F -- <paths-for-this-PR>
   ```
   The commit *message* is descriptive prose you write; the commit *content* is bytes git copied from `F`. Re-typing code by hand reintroduces exactly the drift this method exists to prevent.

5. **FINAL GATE — prove completeness with an empty diff.** Merge every PR branch onto a throwaway verify branch cut from `main`, then diff it against `F`:
   ```
   git -C <repo> checkout -b verify-complete main
   # merge each PR branch in
   git -C <repo> diff F..verify-complete            # must be empty
   ```
   If `main` has drifted since `F`, scope the diff to the changed paths (`-- <paths>`) so unrelated drift doesn't mask the result. **Empty = provably complete.** Non-empty is not a setback — git has just printed the exact list of what was dropped or mistyped; fold it into the right PR and re-run the gate until empty.

## Guardrails
- **Keep the feature branch (pushed) until the invariant passes and the PRs merge.** It is the checksum; discarding it forfeits the only proof of completeness.
- **Squash-merge collapses intermediate commits** — fine for history, but it means the *post-merge* state on `main` is what the gate must reconcile against. Verify against merged content, not against your local PR branches' commit graph.
- **Commit or remove working-tree WIP before you split.** The diff oracle only sees committed content; uncommitted changes are invisible to `git diff` and will silently fail to make it into any PR. Either commit WIP to a real SHA (and include it in `F`'s lineage) or stash/discard it deliberately.
- **Mind main drift.** `main` moves under you during review. Re-cut the verify branch from current `main` and re-run the gate before declaring done; scope diffs to changed paths when drift is unrelated.

## Concrete instance
For the worked N-PR example with real branch names, file counts, and the exact commands used, see `references/project-binding.md`.
