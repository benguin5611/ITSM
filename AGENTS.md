# ITSM

IT Service Management tooling for a one-person IT department running a macOS developer fleet. Three independent subsystems — read the relevant section before making changes.

## Subsystems

| Directory | Purpose | Tech |
|-----------|---------|------|
| `devices/sbom/` | Monthly SBOM collection from managed devices | Go 1.24, Bash, AWS Lambda, Terraform |
| `devices/twingate-mdm/` | MDM audit and remediation for Twingate | zsh |
| `devices/macos-network-diag/` | User-facing network diagnostic scripts | Bash |
| `LLM-skills/` | Reusable Claude Code / Agent SDK skills | Markdown |

## Build & Verify

### Go (devices/sbom)

```
go -C devices/sbom build ./...
go -C devices/sbom vet ./...
```

### Shell scripts

```
bash -n <script.sh>
shellcheck <script.sh>
```

All scripts must remain **bash 3.2 compatible** — macOS ships bash 3.2, not GNU bash 5. Do not use `[[ ]]`, associative arrays (`declare -A`), `local -r`, or other bash 4+ features.

### Terraform (devices/sbom/terraform)

```
terraform -chdir=devices/sbom/terraform init
terraform -chdir=devices/sbom/terraform plan
terraform -chdir=devices/sbom/terraform apply
```

Terraform state is versioned in the repo by design (solo operator). Do not add it to `.gitignore`.

### LLM-skills

No build step. Copy skill directories to `~/.claude/skills/<skill-name>/` to activate in Claude Code. No compilation or validation command required.

## CI

CodeQL runs on push/PR to `main` and builds the Go code. Failing CI blocks merge.

## Deploy

Scripts are distributed to devices via **Kandji MDM**. Lambda is deployed via Terraform. No staging environment — changes go directly to production devices.

## Key Rules

- **bash 3.2 only** — verify all shell scripts with `bash -n` + `shellcheck` before committing.
- The Go SBOM validator embeds `spdx-2.3-schema.json` as the validation source of truth — do not delete or replace it.
- Terraform state is intentionally committed.
- `twingate-mdm/` uses `launchctl bootstrap` which may emit warnings on first run — the `|| true` pattern is intentional.
- LLM-skills must follow the Agent Skills format: `SKILL.md` with valid YAML frontmatter is required in each skill directory.

## Commit Conventions

Conventional commits.
