# LLM-skills

Reusable Claude skills for engineering, security, and decision-making work. Each skill is a self-contained folder that Claude (or any compatible agent runtime) can load and invoke.

## What's a skill?

A skill is a directory containing a `SKILL.md` (instructions, triggers, workflow) plus optional `references/` files (style guides, schemas, prompts). When the user's request matches the skill's trigger phrases, the agent loads the skill and follows its instructions instead of relying on general defaults.

Skills here are deliberately domain-agnostic — no company names, internal tools, or proprietary references. Drop a folder into your skills directory and it works.

## Contents

### [rainbow-team-review/](rainbow-team-review/)

Structured multi-agent adversarial review for any plan, decision, or approach. Ten independent agents modelled on the cybersecurity rainbow-team taxonomy — Gray (ground-truth verification), Red (attacker), Blue (defender), Black (out-of-band adversary), Purple (analyst), White (referee), Yellow (builder), Gold (crisis tabletop), Green (defense + buildability), Orange (attack + buildability) — plus a final Judge that consolidates findings into a single actionable verdict. Works for code architecture, business strategy, hiring, product launches, policy changes, anything that benefits from "what could go wrong" before execution. Also activates via "release the benji" / "benji this".

### [owasp-top-10/](owasp-top-10/)

Structured OWASP Top 10 2025 security analysis against a file, directory, or diff. Produces a severity-rated report with CWE references and remediation guidance. Supports scoping to a single category (`A01`–`A10`) or scanning only changed files.

### [write-like-a-human/](write-like-a-human/)

Detects and removes signs of AI-generated writing. Catches em-dashes, negation pivots, participle-phrase tails, and the vocabulary clusters that survive normal editing. Applies a generic style reference (sentence-case headings, consistent locale, no trailing punctuation on short bullets) on the way out.

### [business-case/](business-case/)

Structured workflow for building defensible business cases — SaaS tools, infrastructure, vendors, services, processes, strategies. Prevents the common failures: discovering requirements too late, comparing options at the wrong level of detail, presenting more options than necessary.

### [custom-json-schema/](custom-json-schema/)

Build, edit, and audit JSON schemas in any format. Domain knowledge is plugged in via two companion files (`docs-reference.md` for rules, `skeleton-schema.md` for a seed example) — replace those and the skill adapts to whatever schema format you're working with.

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
