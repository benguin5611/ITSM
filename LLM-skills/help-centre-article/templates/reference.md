# Reference template

**Diátaxis quadrant:** Reference (information-oriented).

**When to use:** the reader needs to look up a fact — a field, a code, a default, a permission, a value, a rule. Reference articles describe what is, in the most concise way that still answers the lookup. The reader has come for one cell of a table; the article's job is to make sure that cell is easy to find and correct.

**What earns a reference:** a reference earns its shape when the reader has come to **look up one fact** — a field, value, code, default, permission, or rule — and the article's job is to make that fact findable and correct. If the article carries procedural instructions, it's not reference; Diátaxis treats this as the firmest rule in the framework: reference *describes and only describes*. If the reader needs the model behind the values, link to an [explanation](explanation.md) — using the Explanation article specialisation within when the model is about a single named product object.

**Voice and tone:** neutral, factual, present tense. Avoid the warm second person of a tutorial and the conditional imperatives of a how-to guide — reference *describes and only describes*. Diátaxis explicitly endorses warnings where the facts demand them (deprecations, breaking changes, dangerous defaults); include those, but not encouragement, narrative, or rationale.

**Structural elements:**

- **Opening:** one sentence stating the scope of the article — what is and isn't covered. No history, no rationale, no walkthrough.
- **The reference body itself:** a table, a definition list, a structured list, or a few of these in sequence. Tables for comparisons across consistent attributes; definition lists for term-by-term lookups; structured lists when ordering matters.
- **See also:** sideways links to how-to guides that use this reference and to the explanation article that gives the model behind the values.

**What to avoid:**

- Procedural instructions. If readers need to do something with a value, link to the how-to guide. Don't fold steps into the reference. This is the firmest of Diátaxis's rules for reference — "describe and only describe".
- "Why we built it this way" paragraphs. That belongs in the explanation article. A one-sentence scope statement is fine; a rationale section is not.
- Tutorial framing. Reference is not a journey; readers arrive at the article already knowing what they're looking for.
- Hidden values. Every value the reader might come looking for should be in the table. If something is intentionally not listed, say so.

---

## Worked example — *Permission roles*

> This article lists every permission role available, the surfaces each role can access, and the actions each role can take. It does not cover how to assign a role — see the [how-to guide for adding a team member](#) for that.
>
> ### Roles at a glance
>
> | Role | Intended for | Scope |
> |---|---|---|
> | administrator | Workspace owner, team lead | Single workspace |
> | manager | Project lead, shift supervisor | Single workspace |
> | member | Day-to-day contributors | Single workspace or team |
> | viewer | Stakeholders who need read access | Single workspace |
> | organisation administrator | Account-level staff managing multiple workspaces | All workspaces in the organisation |
>
> ### What each role can do
>
> - **administrator** — Manage members and roles in the workspace. Create and delete projects. Configure workspace settings. Read all reports.
> - **manager** — Create and edit projects. Assign and reassign tasks. Read all reports. Cannot manage members or change workspace settings.
> - **member** — Work projects and tasks assigned to them or to their team. Read related history. Cannot create projects or change settings.
> - **viewer** — Read access only to the surfaces shared with them. Cannot edit anything.
> - **organisation administrator** — All administrator actions, across every workspace in the organisation. Manage which members belong to which workspace. Read consolidated reporting.
>
> ### See also
>
> - [How to add a team member](#)
> - [How to change a team member's role](#)
> - [Understanding the role model](#) — the design decisions behind why roles are scoped to workspaces and organisations rather than to features.
