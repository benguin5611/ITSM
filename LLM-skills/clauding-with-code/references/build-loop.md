# Build loop — small unit → lint → CI-mirror → commit → push when green

Build discipline for the implementation phase. Code is shipped in **small, verifiable units**, each
run through the same tight loop. The loop is not bureaucracy — it serves the prime directives:
linting and static analysis enforce **secure-by-design** and **match-conventions** for free, every
iteration, without you having to remember to. Concrete toolchain, commands, and versions →
[`project-binding.md`](project-binding.md).

## The loop (every unit, no exceptions)

1. **Write a small unit.** One coherent, verifiable change — a function, a handler, a migration, a
   component. Small enough to reason about, test, and revert in one piece. If you can't describe it
   in one line, it's too big — split it.
2. **Lint / format / static-analyse.** Run the full linter, formatter, and static-analysis suite
   **every loop**. Never bypassed, never deferred to "later". They catch convention drift and a
   whole class of security defects before they ever reach a commit.
3. **Test in a production-replica environment.** Run against an environment that mirrors production —
   same services, same auth, same data shape. **Self-referential local tests prove nothing**: a unit
   test against stubs you wrote passes by construction. A production replica surfaces the real
   failures — auth, mail, tenancy, concurrency, network — that the happy path hides. Run it
   **frequently**, not just at the end.
4. **Run the local CI mirror, scoped to changed files.** Reproduce the CI pipeline locally — same
   commands, same tool versions — but scope it to what you touched so the loop stays fast. CI must
   fail **locally first**, never on push. The mirror is **fail-fast**: stop on the first failure,
   fix it, re-run.
5. **Commit small, with a descriptive message.** One unit, one commit, a message that says what
   changed and why. Small commits keep the history bisectable and the eventual PR split clean.
6. **Push only when green.** Lint clean, production-replica tests passing, local CI mirror green.
   A red push is a defect — it burns shared CI and breaks others.

## Non-negotiables

- **Linters/formatters/static-analysis run every loop and are never bypassed.** They are the
  cheapest enforcement of directives 1 (secure by design) and 2 (match conventions) available —
  free, automatic, every iteration. Suppressing a warning to "move on" is moving the defect
  downstream, not removing it.
- **Never bypass commit hooks.** No `--no-verify`, no skipping pre-commit, no disabling the gate.
  The hooks exist because something was once shipped without them. The only exception is an explicit
  human instruction, recorded.
- **Production-replica over self-reference.** Frequent runs against a real-shaped environment beat a
  large suite of tests that only exercise your own mocks. Prove the unit works where it will
  actually run.
- **Mirror the CI pipeline locally before you need it.** If CI can fail, it should be able to fail
  on your machine first. Scope to changed files for speed; widen before the PR.
- **Small units, small commits.** Big-bang changes hide defects and make review and PR-splitting
  painful. Keep the increment reviewable.

## Why the loop serves the directives

The discipline is not for its own sake. **Lint = secure-by-design + match-conventions**, enforced
automatically. The CI mirror = the environmental pre-mortem made continuous — the real failures
caught locally, every loop, instead of on push or in production. Small units + small commits = a
clean, bisectable history that makes the later review and git-proven PR split cheap. Keep the loop
tight and the expensive phases downstream get cheaper.
