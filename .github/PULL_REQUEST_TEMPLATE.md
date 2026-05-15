<!-- See CONTRIBUTING.md for what makes a good PR. -->

## Summary

<!-- What this PR changes, and why. One paragraph is fine. Link any related issue. -->

## How I tested it

<!-- Concrete: what you ran, against what, and what happened.
     Examples:
       - Ran devices/sbom/collect.sh on my MacBook; verified the upload landed in the test bucket.
       - `terraform plan` against the prod state showed +1 IAM policy, no destroys.
       - `go test ./...` passed locally.
     "It looked fine" and "the linter passed" don't count as a test plan. -->

## Effect on running systems

<!-- What changes operationally when this merges?
     Examples:
       - On-device script: collect.sh now also captures Homebrew packages.
       - Terraform: adds an S3 lifecycle rule; `terraform apply` will modify the bucket in place.
       - Lambda: handler signature unchanged; no redeploy needed.
       - None (docs-only).
     If the honest answer is "I'm not sure", stop and find out. -->

## Rollback

<!-- One sentence on how to undo this if it breaks.
     Examples:
       - Terraform: `git revert` plus `terraform apply`.
       - Lambda: redeploy the previous artefact.
       - Docs or local scripts: `git revert`.
       - "Trivial" is fine for typo fixes. -->

## Checks

- [ ] PR does one thing
- [ ] Linters and formatters pass for every language this PR touches
- [ ] No secrets in code, state, or this PR description
- [ ] Docs updated in the same PR as the code change
