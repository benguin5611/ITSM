# Contributing

Thanks for taking a look. Before opening anything, a quick note on scope.

This repository is built primarily for one person's use and shared publicly in case any of it is useful to others running IT for a small team. It is not a community-maintained project. Issues and pull requests are welcome, but responses are best-effort, and changes that don't fit the maintainer's environment may be declined even when they're objectively good ideas. If that's not what you're after, fork freely; the MIT licence is permissive on purpose.

The principles in the [README](../README.md) apply here too:

- Short scripts you can read in one sitting, not frameworks.
- Lean on vendor APIs and existing tools rather than reinvent them.
- Keep a human in the loop where automation can plausibly get things wrong.

If your change fights any of those, it's probably the wrong repository.

## Reporting issues

Good issues are specific and reproducible. Please include:

- What you ran, and what you ran it on (macOS version, shell, Go version, Terraform version, whichever apply).
- What you expected to happen.
- What actually happened, including the full error output.
- A minimal way to reproduce it, if you have one.

Vague reports like "the script doesn't work" are hard to act on and will likely sit. If you've already worked around the problem, mentioning the workaround helps too.

For feature requests, describe the underlying problem first and the proposed change second. The problem is more useful than the solution; sometimes there's a simpler fix.

## Security issues

Don't open a public issue for anything that looks like a vulnerability. See [SECURITY.md](SECURITY.md) for how to report it privately.

## Proposing changes

Before you spend real time on a non-trivial change, open an issue to sketch the idea. That avoids both of us discovering, at PR review, that it doesn't fit.

For small fixes (typos, broken links, obvious bugs, tighter error handling), a PR straight to `main` is fine.

When you open a PR:

- Keep it focused on one thing. Multiple unrelated changes get split or declined.
- The description should say what changed and why.
- Include reproduction or test notes if behaviour changed.
- Update the relevant README or in-tree docs in the same PR.

By submitting a contribution you agree it can be released under the project's [MIT licence](../LICENSE).

## Style and quality

The repo is mostly Bash, Go, and Terraform. Match the style of what's already there.

**Bash**

- `#!/usr/bin/env bash` and `set -euo pipefail` at the top.
- Quote variables (`"$var"`, not `$var`) unless you have a reason not to.
- ShellCheck-clean. If you must suppress a warning, comment why.
- Prefer a few well-named functions over one long script body.
- Print clear error messages to stderr (`>&2`) and exit non-zero on failure.

**Go**

- `gofmt`, `go vet`, and `go build ./...` should pass.
- Return errors with context (`fmt.Errorf("doing X: %w", err)`); don't swallow them.
- Standard library first. New dependencies need a real reason.
- Keep handlers small and testable.

**Terraform**

- `terraform fmt` and `terraform validate` should pass.
- Variables documented with `description` and sensible defaults where they make sense.
- No secrets in code or state. Use the existing patterns (Secrets Manager, KMS, etc.).
- If you add a resource that costs money or creates IAM permissions, call it out in the PR description.

## Commits and branches

- Write commit messages as commands: "Add X", "Fix Y".
- One logical change per commit where practical. Squash noise before opening the PR.
- Branch from `main`. Feature branches named however you like; they'll be deleted on merge.

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Questions

If you're not sure whether something belongs here, open an issue and ask before writing code. That's nearly always faster than guessing.
