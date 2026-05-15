# Schema Documentation Reference

> **This file is one of two pluggable inputs for the JSON Schema skill.**
> Replace the content below with documentation for your schema format.
> The skill reads this file before every build, edit, and audit — it is
> the single source of truth for what makes a schema valid.
>
> Structure this however makes sense for your format. Include only the
> sections that apply. At minimum, cover:
>
> - **What is this format and what consumes it?**
> - **What are the structural rules?** (required shape, node types, nesting)
> - **What are the known failure modes?** (this is the most valuable section — each failure mode becomes an audit check)
>
> Optional but useful: naming conventions, type/value constraints,
> expression syntax, styling rules, plugin behaviour, external doc links.
>
> **Tip:** The Known Failure Modes section drives the audit checklist.
> Write each failure as: what breaks, why, and how to fix it. The more
> specific you are, the more useful the audit becomes.

---

*Replace everything below this line.*

---

## Format Overview

Describe what this schema format is, what application or system consumes it, and what happens when a schema is invalid.

## Structural Rules

Document the required structure: top-level shape, required properties on every node, valid node types, nesting constraints, composition patterns.

## Naming Conventions

Document naming style (camelCase, snake_case, etc.), reserved names, uniqueness constraints.

## Type and Value Constraints

Document valid values for each property, enum restrictions, string formats, date/time conventions, locale rules.

## Known Failure Modes

Document every failure mode you've hit. The skill generates its audit checklist from this table — the more entries, the better the audit.

| Failure | Cause | Fix |
|---------|-------|-----|
| *Example: App crashes on load* | *Computed value on input node creates infinite loop* | *Use display-only nodes for computed values* |
| *Example: Field missing from submitted data* | *Node missing required `name` property* | *Add `name` to every field node* |

## External Documentation

List URLs to official documentation, guides, and API references. The skill can fetch these during builds when deeper reference is needed.
