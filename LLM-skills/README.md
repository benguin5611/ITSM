# LLM-skills

Reusable Claude skills for engineering, security, and decision-making work. Each skill is a self-contained folder that Claude (or any compatible agent runtime) can load and invoke.

## What's a skill?

A skill is a directory containing a `SKILL.md` (instructions, triggers, workflow) plus optional `references/` files (style guides, schemas, prompts). When the user's request matches the skill's trigger phrases, the agent loads the skill and follows its instructions instead of relying on general defaults.

Skills here are deliberately domain-agnostic — no company names, internal tools, or proprietary references. Drop a folder into your skills directory and it works.

## Contents

### [rainbow-team-review/](rainbow-team-review/)

Structured multi-agent adversarial review for any plan, decision, or approach. Ten independent agents modelled on the cybersecurity rainbow-team taxonomy — Gray (ground-truth verification), Red (attacker), Blue (defender), Black (out-of-band adversary), Purple (analyst), White (referee), Yellow (builder), Gold (crisis tabletop), Green (defense + buildability), Orange (attack + buildability) — plus a final Judge that consolidates findings into a single actionable verdict. Works for code architecture, business strategy, hiring, product launches, policy changes, anything that benefits from "what could go wrong" before execution. Also activates via "release the benji" / "benji this".

### [help-centre-article/](help-centre-article/)

Write, edit, or audit help centre articles end to end — classifies the article type (tutorial / how-to / reference / explanation), drafts with the right voice and structure for that type, and produces Zendesk-compliant HTML ready for Guide. Covers Australian English conventions, label and content-tag suggestions, supported HTML elements, allowed inline styles, table layout, dark-mode-safe callouts, and known Zendesk rendering failure modes.

### [owasp-top-10/](owasp-top-10/)

Structured security analysis against three OWASP Top 10 lists: Web 2025 (A01–A10), API Security 2023 (API1–API10), and LLM AI 2025 (LLM01–LLM10). Auto-detects which lists apply based on the codebase (API routes present → API list; LLM SDK detected → LLM list; Web always). Produces a severity-rated report with CWE references and remediation guidance. Supports scoping by category code, directory, or changed files only.

### [knowledge-matrix/](knowledge-matrix/)

Builds an engineering knowledge matrix from a team's GitHub pull-request history — a colour-coded heatmap of who is an SME versus a novice in each discipline and each repository, for succession and upskilling planning. Reads every PR and its reviews/comments to score proficiency from authorship, review authority, and who-corrects-whom. Discovers the discipline categories from the repos themselves (languages, services, directories) rather than assuming a fixed list. Two modes: team (the whole picture, with bus-factor and concentration risk) and self (just your own PRs — a private read on your own gaps).

### [write-like-a-human/](write-like-a-human/)

Detects and removes signs of AI-generated writing. Catches em-dashes, negation pivots, participle-phrase tails, and the vocabulary clusters that survive normal editing. Applies a generic style reference (sentence-case headings, consistent locale, no trailing punctuation on short bullets) on the way out.

### [business-case/](business-case/)

Structured workflow for building defensible business cases — SaaS tools, infrastructure, vendors, services, processes, strategies. Prevents the common failures: discovering requirements too late, comparing options at the wrong level of detail, presenting more options than necessary.

### [custom-json-schema/](custom-json-schema/)

Build, edit, and audit JSON schemas in any format. Domain knowledge is plugged in via two companion files (`docs-reference.md` for rules, `skeleton-schema.md` for a seed example) — replace those and the skill adapts to whatever schema format you're working with.

### [clauding-with-code/](clauding-with-code/)

Build orchestrator for shipping a feature or service with an AI coding agent, end to end. Drives the lifecycle in phases — a blocking discovery gate, a single authoritative spec, a small-step build loop, a delegated multi-lens review, a git-proven PR split, and end-of-run archival — pausing for the human at every real fork. Project-agnostic: the concrete stack, CI pipeline, and local replica are bound in one quarantine file (`references/project-binding.md`) you fill in for your own project.

### [meta-review/](meta-review/)

The connective layer above the individual review skills. It doesn't re-implement reviewing — it grounds, sequences, composes, de-duplicates, and arbitrates multiple lenses (adversarial, security, simplification, dead-code, grudge passes) against the real code into one human-in-the-loop verdict, evolving a versioned artefact across passes. Includes a deterministic emitter-census pre-pass that catches API-surface dead code (`oneof` variants / `enum` values) the generic reachability tools miss. Project-agnostic via a `references/project-binding.md` quarantine file.

## Using these skills

The exact loading mechanism depends on your runtime:

- **Claude Code** — drop the folder into `~/.claude/skills/` or your project's skills directory. The skill name comes from the frontmatter `name:` field.
- **Other agent harnesses** — most support Anthropic's skills format directly. Check your harness docs.

To invoke a skill manually, type `/<skill-name>` (e.g. `/rainbow-team-review`). For automatic invocation, the agent picks the skill when the user's request matches the description and trigger phrases in `SKILL.md`.

## Conventions

- One skill per folder.
- `SKILL.md` is the entry point; it must have YAML frontmatter with `name:` and `description:`.
- Supporting material lives under `references/`.
- No company-specific names, internal tools, or proprietary content.

## Licence

MIT — see [../LICENSE](../LICENSE).
