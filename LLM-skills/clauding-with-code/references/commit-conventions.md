# Commit conventions

Rules for committing when coding with an AI agent — agent-facing, but human-readable. This is the
**ecosystem-wide** source of truth; it **cross-links to existing rules rather than restating them**.
Where a repo already has its own `AGENTS.md` (or equivalent), keep that file to the lean subset
relevant to that repo and let the rest live here.

---

## 0. Already governed elsewhere — do not restate, just obey

- **Verification gates** — never `--no-verify`, `--no-gpg-sign`, or skip pre-commit hooks unless
  explicitly told to. Commit only when the unit is **green**: formatted, linted, local CI-mirror
  passing (Phase 2 build loop).
- **Signing** — follow whatever the repo's branch protection actually requires; check before
  assuming. If a repo enables required/verified-signature protection, set up the key properly
  rather than working around it with `--no-gpg-sign`.
- **Secrets** — never write secrets to files or commit them; treat any `.env`-style file as
  sensitive and never commit it.
- **PR split** — git is the completeness oracle; partition by file; `main + all PRs ≡ feature
  branch` ([`pr-split-method.md`](pr-split-method.md)).
- **Push discipline** — push only when the human explicitly asks; fast-forward only, never
  force-push a shared branch; delete the local branch once the PR is raised. **Note the deliberate
  override:** an autonomous build loop may treat "green" as its own push gate — but a
  human-in-the-loop run keeps push **human-gated**, green or not.
- **House language/style** everywhere, including commit messages and PR text.
- **No `cd` in automation** — use absolute paths and per-repo git invocation (`git -C <path>`).

---

## 1. What to commit — atomicity & hygiene

- **One logical change per commit.** Never mix a refactor with a behaviour change.
- **Codegen and formatting churn get their own commit** — `chore(codegen): ...` for
  generated-code/schema/OpenAPI output, `style: ...` for bulk formatting. Never fold generated or
  reformatted lines into a logic commit. Commit generated output **verbatim**; never hand-edit it.
- **Generated & co-located docs** — treat generated docs/API specs exactly like other codegen (own
  commit, verbatim, never hand-edit). If a downstream repo publishes specs sourced from this one,
  check whether the change needs a coupled PR there too, and in which order.
- **Tests land with the code they cover** — same commit or the adjacent one, not a trailing batch.
- **Large & binary files** — no new binary blob without explicit approval; flag any single added
  file over ~1 MB for a human check. Vendored dependencies enter **only** via the toolchain's own
  vendoring command, in a dedicated `chore(deps)`/`build(vendor)` commit, never hand-placed. If the
  repo has no large-file storage configured, treat that as a reason to be stricter about binaries,
  not looser — they bloat history permanently. **Build artefacts and cache directories** (compiled
  bytecode, `__pycache__`, `node_modules`, etc.) should never be tracked at all — if one is found
  already committed, remove it with `git rm --cached` and add it to `.gitignore` in its own `chore`
  commit rather than letting it ride along in an unrelated one.
- **Never commit:** secrets / `.env` / credentials, build artefacts, stray result/output files,
  debug logging, commented-out code, editor/OS cruft (`.DS_Store`, etc.).
- **Pre-commit hygiene** — always review `git status` and the staged diff before committing, and
  **stage intentionally** (avoid blanket `git add -A`). This is the cheap mechanical guard that
  catches stray files, debug logs, `.env`, and OS cruft. If gitignored cruft is already tracked,
  remove it with `git rm --cached` in a `chore` commit.

## 2. When to commit

- **Only when the unit is green** — a broken commit is never acceptable on a branch you intend to PR.
- **Commit only when the human asks**, and **never push** until the human explicitly says so.
- **Branch first** — never commit to `main`. If the working tree is on `main`, branch off before
  the first commit.

## 3. How often to commit — cadence

- **One commit per completed logical unit** — small and frequent on the working branch, never one
  giant end-of-session commit. The unit is "the smallest coherent change that leaves the tree
  green," matching the `small unit → lint → CI-mirror → commit` loop.
- **WIP/checkpoint commits are fine on a working branch** (harmless if `main` squash-merges), but
  tidy them with rebase / `--fixup` + autosquash before the PR so the branch reads as deliberate
  units.
- **Don't hoard unrelated changes** waiting for a "perfect" moment — that produces unsplittable
  commits and defeats the PR-split invariant.

## 4. Where to commit — branch, repo & identity

- **Branch off `main`; never commit directly to `main`.**
- **Branch name carries the tracker id** — `TICKET-1234-short-desc` (or `type/short-desc` where
  there genuinely is no card). The id ties branch → commits → PR.
- **Right repo, right identity** — if you work across more than one account or identity (a work
  account and a personal one, say), commit under the `git user.email` that actually owns the repo.
  A wrong-identity commit is a silent failure that's awkward to unwind later.
- **Multi-repo pushes** — when a change spans repos under different identities, push each repo
  under its own identity in turn rather than mixing them, and honour each repo's own commit style
  (re-derive it from that repo's own `git log`, never assume it from another repo).
- **Bot-authored commits** — leave dependabot/bot commit authorship and style intact; when
  hand-applying a dependency bump, follow the repo's existing `chore(deps)` convention, and never
  bolt an unrelated trailer onto a mechanical dependency commit.
- **Stale merged branches** — once a branch's content has landed on `main` (via merge or squash),
  delete it, both locally and on the remote. A branch that lingers after merge invites a stray
  commit to land on it later instead of on a fresh branch off current `main` — confirm with
  `git branch --merged main` before deleting, and never delete a branch carrying commits `main`
  doesn't have yet.

## 5. Commit message structure

**Two tiers if `main` is squash-merged** — confirm from the repo's own history
(`git log --merges`) rather than assuming; adapt the shape below if it isn't:

**(a) Working-branch commits** — granular, Conventional Commits, **carrying the tracker id from
commit one**:

```
type(scope): TICKET-1234 short imperative description
```

- The id rides on **every** commit (subject prefix as above, or a `Refs: TICKET-1234` trailer) so
  each commit surfaces on the issue's development panel — not just the squash title
  ([`work-tracking.md`](work-tracking.md)). Solo tooling repos with no card use plain
  `type(scope): desc`.
- `type` ∈ `feat | fix | chore | refactor | docs | test | ci | style | perf | build`
- `scope` = the area: a domain or a path; in single-purpose repos, the unit (`<skill-name>`,
  `<schema-name>`).
- description: imperative mood, lower-case start, no trailing full stop, ≤ ~72 chars.

**(b) The PR title = the permanent squash commit** — same form, repeats the tracker id; most hosts
append a PR number automatically:

```
type(scope): TICKET-1234 short imperative description
```

- This is the record that survives on `main` — make it self-explanatory.
- **Never let a raw branch name become the PR title.**

**Body** (when the change isn't self-evident): wrap ~72 cols; explain **why**, not the **what** the
diff already shows.

**Repo-specific conventions** — some repos bake extra state into every commit message (a version
bump, a changelog line, a manifest field). Check [`project-binding.md`](project-binding.md) and the
repo's recent `git log` for anything like this before committing, and follow it.

## 6. Integrating, rewriting & resolving

- **Update a branch against `main`** — **merge** `main` in when the branch is shared/pushed
  (preserves others' commits, no force-push); **rebase** onto `main` only when the branch is
  unpushed and yours alone. Rebasing a shared/pushed branch is a history rewrite (forbidden below)
  and can clobber a collaborator's or a concurrent agent's commits if more than one session is
  working the same branch.
- **History rewriting** — amend / rebase / `--fixup` + autosquash are **allowed** on an unpushed (or
  yours-alone) working branch to clean WIP into deliberate units; **forbidden** after push on a
  shared branch, and any force-push to `main` is forbidden.
- **Conflict resolution** — never discard the other side blindly; verify the post-resolution diff
  against **both** parents (corollary of the PR-split "git is the checksum" invariant). Re-generate
  codegen and re-vendor dependencies on conflict — never hand-merge generated/vendored files. If a
  conflict is non-trivial, **stop and surface it to the human**.
- **Shipped regressions** — fix forward with a `revert` commit, not history surgery.
