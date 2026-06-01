# Taxonomy-discovery brief — derive this codebase's disciplines from its own data

The orchestrator can do this inline, or delegate it to one agent. The point: the discipline
categories must be **discovered from the actual code**, not taken from a generic list.
Substitute `<WORKDIR>`.

---

You are designing the discipline taxonomy for a knowledge matrix, from evidence about a
specific codebase. Do NOT use a generic boilerplate list — derive categories that reflect
what THIS codebase actually contains.

STEP 1 — Read the inventory: `<WORKDIR>/inventory.json`. It contains, PR-weighted across the
real change history: file **extensions** (languages present), **top-level** and **second-level**
directories, and **service/domain directory names** (e.g. entries under `services/`, `apps/`,
`packages/`, `pkg/`, `proto/`, `cmd/`). Optionally also consult `gh api repos/<owner>/<repo>/languages`.

STEP 2 — Derive the taxonomy. Combine two kinds of column:
- **Technical/layer disciplines** from the languages and structural dirs actually present —
  e.g. a backend language → a backend discipline; a frontend framework → a frontend discipline;
  SQL/migrations → a database discipline; proto/openapi/graphql → an API-contracts discipline;
  IaC/CI/containers/test/docs dirs → those cross-cutting disciplines. Only include what's evidenced.
- **Product-domain disciplines** from the service/domain directory names. Cluster related
  service names into meaningful domains and NAME them from the evidence (e.g. several
  `*-billing`/`*-invoicing` services → one billing domain; `*-notification`/`*-email` → a
  messaging domain). One discipline per genuine bounded context; merge tiny or near-duplicate ones.

Guidance: 12–22 columns total. Short, lowercase, hyphenated IDs. Don't invent categories with
no evidence; don't lump everything into "backend". Every domain name must trace to directory/
language evidence in the inventory — never to outside knowledge of the company or product.

STEP 3 — For each discipline, write `path_rules`: the path substrings that map a changed file
to it (lowercased; use the real directory/service names and extensions from the inventory). Add
`repo_base` for single-purpose repos (whole repo → one or two disciplines). Pick a `fallback_discipline`.

OUTPUT — write JSON to `<WORKDIR>/taxonomy.discovered.json` (this is merged into config.json):
```json
{
  "disciplines": [["<id>","<Human Label>"], "..."],
  "groups": [["<Group name>", ["<id>", "..."]], "..."],
  "path_rules": [{"any": ["<substr>", "..."], "disc": "<id>"}, "..."],
  "repo_base": {"<repo-name>": ["<id>", "..."]},
  "fallback_discipline": "<id>"
}
```
After writing, reply with ONLY the discipline IDs you created and one line each on the evidence
that justified it (cite the dir/extension). Australian English. Never put a person, company, or
product name in the output — only structural/technical category names traceable to the inventory.
