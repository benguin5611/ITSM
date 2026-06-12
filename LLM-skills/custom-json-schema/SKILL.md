---
name: custom-json-schema
description: Build, edit, and audit JSON schemas. Adapts to any schema format via pluggable documentation and seed templates. Use when asked to build, edit, validate, or audit a JSON schema for any format once its two companion files (docs-reference.md and skeleton-schema.md) are populated — the skill refuses to run until they contain real content.
argument-hint: "[file-path] [--audit]"
---

# JSON Schema Builder

This skill derives **all domain knowledge** from two companion files:

- **[docs-reference.md](docs-reference.md)** — Rules, constraints, valid patterns, anti-patterns, and known failure modes for the schema format
- **[skeleton-schema.md](skeleton-schema.md)** — Annotated seed example of a well-formed schema

Update those two files to adapt this skill to any JSON schema format. Everything below is format-agnostic. The skeleton is a starting point, not a structural constraint — Build mode uses it as a seed and may deviate when the user's requirements demand it.

---

## 1. Load and Validate Context

Before doing any work, read both companion files and verify they contain real content.

1. **Read [docs-reference.md](docs-reference.md)** — extract every rule, constraint, and convention. Catalogue every known failure mode. Note any external documentation URLs to fetch later if needed.
2. **Read [skeleton-schema.md](skeleton-schema.md)** — understand the canonical structure, which parts are fixed boilerplate vs. which adapt per schema, and the naming conventions demonstrated.

**Validate before proceeding:**

- If either file is empty or contains unreplaced placeholder tokens (e.g. `{{...}}`, `[INSERT...]`, `TODO`, `Replace this with`), **stop and tell the user.** Explain which file needs to be populated and what it should contain. Do not attempt to build, edit, or audit without both files providing real content.
- If docs-reference.md and skeleton-schema.md contradict each other (e.g. the skeleton demonstrates a pattern the docs call an anti-pattern), **flag the contradiction to the user** and ask which takes precedence. Resolution order if unresolved: explicit user instruction overrides docs-reference.md, which overrides skeleton-schema.md. Surface which source was followed.

---

## 2. Parse Arguments and Determine Mode

Interpret `$ARGUMENTS`:

| Input | Mode | Action |
|---|---|---|
| File path (e.g. `schemas/intake.json`) | **Edit** | Read the file, apply changes per user request |
| `--audit` (with optional file path) | **Audit** | Validate schema against all documented rules |
| No arguments / description only | **Build** | Generate a new schema from a natural language description |
| Pasted JSON in conversation | **Edit** | Treat inline JSON as the schema to modify |

If a file path is given, read it immediately. If the read fails, say so and ask the user to paste the file contents directly.

If the input is not valid JSON, identify the apparent format (YAML, JavaScript object, plain text description, etc.) and ask whether to convert it to JSON or treat it as reference material before proceeding.

If the input matches more than one mode trigger (e.g. a file path AND a description), ask which mode applies before proceeding.

---

## 3. Planning Phase (all modes)

Before writing any JSON:

- Confirm the schema's purpose, structure, and scope with the user
- If requirements are ambiguous, **ask clarifying questions** — do not guess
- Cross-reference requirements against docs-reference.md to verify feasibility and identify which rules apply
- If editing, read the existing schema in full and identify exactly what needs to change
- If the schema involves scoring, computed values, or complex conditional logic, confirm the specifics upfront — changing these later typically means rewriting dependent expressions

---

## 4. Build Mode

Build mode is natural-language-driven. The user describes what they want and you produce a complete, valid schema.

### First pass

1. **Interpret the description.** Extract intent: what data is being collected or configured, what sections or groupings exist, what conditional logic is implied, what validation is needed.

2. **Ask before assuming.** If the description is vague or underspecified, ask targeted questions before building:
   - What are the distinct sections or logical groups?
   - Which fields are required vs. optional?
   - Are there conditional fields (show X only when Y)?
   - Are there computed or derived values?
   - What data types are involved?

3. **Start from the skeleton.** Copy the structure from skeleton-schema.md. Never start from a blank file — the seed template encodes structural decisions that are easy to miss.

4. **Flesh out the skeleton.** Replace placeholder content with real fields, sections, and logic. For each structural decision, verify it against docs-reference.md.

5. **Verify against the documentation.** Before outputting, walk the completed schema against every applicable rule and every known failure mode in docs-reference.md. If any violations are found, report them explicitly — list what was wrong and what was corrected. Do not silently self-correct and return the schema without disclosure.

### Iterative refinement

Build mode is rarely one-shot. After the first pass, the user will typically request changes: "add a section for X," "make Y conditional on Z," "this field should be a dropdown not a text input." Handle each refinement as a targeted edit — apply the change, re-verify the affected area against the documentation, and output the updated schema. Do not rebuild from scratch on each iteration.

---

## 5. Edit Mode

1. Read the existing schema in full
2. Identify the minimal set of changes needed
3. Apply changes while preserving existing valid structure
4. Verify edits don't introduce any violations of documented rules
5. Do not refactor, reformat, or "improve" parts the user didn't ask to change

---

## 6. Audit Mode

The audit checklist is generated dynamically from docs-reference.md on every run. Updating the documentation automatically updates what the audit checks for.

### Step 1: Generate the checklist

Read docs-reference.md end to end. Every rule, constraint, convention, and known failure mode becomes one audit check. Assign severity using this framework:

| Severity | Criteria |
|---|---|
| **Critical** | The documentation describes this as causing crashes, data loss, broken rendering, infinite loops, or the consuming application becoming non-functional |
| **Bug** | The documentation describes this as causing silent data issues, incorrect behaviour, values being lost or ignored, features not triggering, or output that doesn't match intent |
| **Cosmetic** | The documentation describes this as a convention, naming style, structural preference, or consistency expectation |

If the documentation doesn't clearly indicate severity, classify based on impact: could a user lose data or see broken behaviour? → Bug or Critical. Is it about how the schema looks or reads? → Cosmetic.

**Output a summary before running:** total check count and count per severity. Do not print every individual check upfront — only violations will be reported in detail.

```
Audit checklist generated: N checks (X critical, Y bug, Z cosmetic)
Running...
```

### Step 2: Run every check

Walk the schema and evaluate every check. Do not skip checks — the value of an audit is exhaustiveness.

### Step 3: Report findings

For each violation:

| Field | Description |
|---|---|
| **Rule** | Which documented rule is violated (reference the docs section) |
| **Location** | JSON path (e.g. `$.steps[0].fields[2].name`) |
| **Severity** | **Critical**, **Bug**, or **Cosmetic** |
| **Fix** | Exactly what to change — not "fix it" but the specific remediation |

Group findings critical-first:

1. **Critical** — functionality will break
2. **Bug** — behaviour is silently wrong
3. **Cosmetic** — convention violations

End with a summary: total checks run, pass count, violation count, breakdown by severity.

---

## 7. Output

| Mode | Format |
|---|---|
| **Build** | Complete JSON schema. Pretty-printed with 2-space indentation. For schemas under ~200 lines, output in a fenced `json` code block. For larger schemas, write directly to a file. |
| **Edit** | Apply edits using the Edit tool. For pasted content, output the modified JSON in a code block. |
| **Audit** | Findings report grouped by severity, with summary. |

---

## Principles

These are the skill's invariants — they override any ambiguity in the workflow above.

**Documentation is the authority.** Every rule you enforce must trace back to docs-reference.md or skeleton-schema.md. If the documentation is silent on a topic, flag it to the user rather than guessing. Do not invent rules.

**Consistency over cleverness.** Match the patterns in the skeleton and documentation. If the docs show one way to do something, use that way — even if you know an alternative.

**Minimal touch in edit mode.** Change what the user asked to change. Nothing more. Every unnecessary change is a potential regression.

**Valid JSON always.** Output must be parseable. No trailing commas, missing quotes, unescaped characters, or mismatched brackets.
