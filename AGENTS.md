# ITSM

IT Service Management tooling for a one-person IT department running a macOS developer fleet. Four independent subsystems — read the relevant section before making changes.

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

Bash scripts (everything except `devices/twingate-mdm/`):

```
bash -n <script.sh>
shellcheck <script.sh>
```

Bash scripts must remain **bash 3.2 compatible** (macOS ships bash 3.2, not GNU bash 5). Do not use bash 4+ features: associative arrays (`declare -A`), `mapfile`, or `${var^^}`/`${var,,}` case conversion.

`devices/twingate-mdm/` scripts are zsh by design (see the subsystem table). Verify them with `zsh -n <script.sh>`; shellcheck does not support zsh, so skip it for those.

### Terraform (devices/sbom/terraform)

```
terraform -chdir=devices/sbom/terraform init
terraform -chdir=devices/sbom/terraform plan
terraform -chdir=devices/sbom/terraform apply
```

Terraform state stays local and gitignored (see `devices/sbom/terraform/.gitignore`). Never commit it: state can hold secret values in plaintext. There is no remote backend (solo operator), so protect and back up the state file as you would a credential.

### LLM-skills

No build step. Copy skill directories to `~/.claude/skills/<skill-name>/` to activate in Claude Code. No compilation or validation command required.

## CI

CodeQL runs on push/PR to `main` and builds the Go code. Failing CI blocks merge.

## Deploy

Distribute the on-device scripts via your MDM (Kandji, Jamf, or whatever you run). Lambda is deployed via Terraform. Assume no staging environment: test script changes on a single machine before pushing them fleet-wide.

## Key Rules

- **Bash scripts stay bash 3.2 compatible** — verify with `bash -n` + `shellcheck` before committing. The `devices/twingate-mdm/` scripts are zsh: verify those with `zsh -n` and skip shellcheck.
- The Go SBOM validator embeds `spdx-2.3-schema.json` as the validation source of truth — do not delete or replace it.
- Terraform state is local and gitignored. Never commit it to this repo.
- `twingate-mdm/` uses `launchctl bootstrap` which may emit warnings on first run — the `|| true` pattern is intentional.
- LLM-skills must follow the Agent Skills format: `SKILL.md` with valid YAML frontmatter is required in each skill directory.

## Commit Conventions

Write commit messages as commands: "Add X", "Fix Y" (see [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)). One logical change per commit.
