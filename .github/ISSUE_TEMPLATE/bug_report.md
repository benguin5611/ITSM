---
name: Bug report
about: Something here doesn't work the way it should
title: ''
labels: bug
assignees: ''

---

> Before filing: please confirm you're running against the latest commit on `main` (see [SECURITY.md](../SECURITY.md) for why). For anything that looks like a security issue, **don't open a public issue** — report it privately per [SECURITY.md](../SECURITY.md).

## What you ran

The script, command, or Terraform action that triggered the bug. Include flags and arguments.

```
# e.g.
sbom-audit-spdx --force
terraform apply
```

## What you ran it on

Only the bits that apply:

- macOS version (e.g. `Sonoma 14.5`):
- Shell (e.g. `bash 3.2` / `zsh 5.9`):
- Go version (`go version`):
- Terraform version (`terraform version`):
- AWS region:
- Anything else relevant (MDM, Nix version, Homebrew vs Workbrew):

## What you expected to happen

A short, specific description.

## What actually happened

Include the **full error output**, not a paraphrase. Use a code block. Redact tokens, account IDs, and anything sensitive.

```
<paste output here>
```

## Minimal reproduction

The shortest sequence of commands that reliably triggers the bug. If you've already worked around the problem, describe the workaround too — it often points at the root cause.

## Additional context

Anything else that might matter: recent changes to your environment, related logs, links to relevant lines in the repo.
