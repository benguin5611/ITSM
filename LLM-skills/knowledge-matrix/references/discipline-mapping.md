# Discipline mapping & runtime discovery

`scripts/discmap.py` turns a changed-file path (plus its repo) into a set of discipline
IDs. The rules are **generic by default** and **fully overridable per run** via `config.json`
— so a project-specific mapping is discovered from the target repos at runtime, never shipped.

## How a PR is classified
1. `build_mapper(cfg)` returns `map_path(repo, path)`, which unions:
   - **language rules** — file extension → discipline (`lang_rules`, default `DEFAULT_LANG_RULES`);
   - **path rules** — path-substring → discipline (`path_rules`, default `DEFAULT_PATH_RULES`);
   - **repo base** — whole-repo disciplines for single-purpose repos (`repo_base`, default `{}`).
2. `discs_for(repo, pr)` unions disciplines across all the PR's files; if nothing matches it
   falls back to `fallback_discipline` (default `backend`).
3. A path may map to several disciplines (e.g. a UI file under a forms area → `frontend` and a
   forms discipline). That is fine — the scorer down-weights raw volume precisely because broad
   tagging inflates it, and relies on review-authority/teaching signal to separate SMEs from
   high-volume generalists.

## The generic defaults (applied when config omits a key)
- Languages: `.ts/.tsx/.js/.jsx/.vue/.svelte/.css/.scss/.html` → `frontend`;
  `.go/.py/.java/.rb/.rs/.cs/.kt/.php/.scala/.ex/.clj` → `backend`.
- Path keywords (illustrative): `/web//ui//client/`→frontend; `/services//api//internal//pkg/`→backend;
  `.sql//migrations/`→database; `.proto/openapi/graphql/buf.`→api-contracts; `.tf/terraform/helm/k8s`→infra-iac;
  `.github/workflows/circleci`→ci-cd; `dockerfile/compose/deploy`→containers-deploy;
  `makefile/.nix/scripts//tools/`→local-devx; `auth/oauth/jwt/crypto/rbac`→auth-security;
  `log/metric/trace/otel`→observability; `test/spec/e2e/cypress`→testing; `.md//docs/readme`→docs.

## Discovering a project-specific mapping (what the orchestrator does)
1. List the repos and their languages: `gh api repos/<owner>/<repo>/languages`.
2. Sample the structure: top-level directories, `services/*`, `apps/*`, `packages/*`, proto/
   schema dirs, infra dirs. Service/package directory names are the strongest source of
   product-domain disciplines (e.g. a directory per bounded context → one discipline each).
3. Propose a tailored `disciplines` + `groups` + `path_rules` (+ `repo_base` for single-purpose
   repos) and confirm with the user. Write them into `config.json`.
4. Keep IDs short, lowercase, hyphenated; 12–22 columns.

## Known limitation
Files are captured up to 100 per PR (GraphQL connection cap). A few bulk vendor/codegen PRs
(>100 files) truncate — immaterial, since those are mass regenerations, not individual skill.
