#!/usr/bin/env python3
"""Shared config + discipline taxonomy/mapping for the knowledge-matrix pipeline.

The taxonomy is NOT hardcoded to any company or product. There is a GENERIC default
set of universal engineering disciplines, and everything is overridable per-run via
config.json — the orchestrator discovers a project-specific taxonomy from the target
repos (languages, top-level dirs, service names) and writes it to
taxonomy.discovered.json, which load_config auto-merges (see SKILL.md Phase 2.5).
All identity and all project-specific structure come from the
repos at runtime; nothing here names a person, company, product, or internal repo.

config.json keys this module reads (all optional — generic defaults apply):
  disciplines : [["id","Label"], ...]               # matrix columns for this run
  groups      : [["Group name", ["id", ...]], ...]   # column groupings for rendering
  path_rules  : [{"any": ["substr", ...], "disc": "id"}, ...]  # path-substring -> discipline
  lang_rules  : {".ext": "id", ...}                  # file extension -> discipline
  repo_base   : {"repo-name": ["id", ...]}           # whole-repo base disciplines
  bots        : ["login-substring", ...]             # excluded contributors
"""
import json, os, sys

# ---- GENERIC default taxonomy (universal to most software teams) ----
DEFAULT_DISCIPLINES = [
    ("frontend", "Frontend / UI"),
    ("backend", "Backend / services"),
    ("database", "Database / migrations"),
    ("api-contracts", "API contracts / schemas"),
    ("infra-iac", "Infrastructure / IaC"),
    ("ci-cd", "CI/CD & release"),
    ("containers-deploy", "Containers / deployment"),
    ("local-devx", "Build / local dev tooling"),
    ("auth-security", "Auth & application security"),
    ("observability", "Observability / logging"),
    ("testing", "Testing / QA"),
    ("docs", "Docs / API docs"),
]
DEFAULT_GROUPS = [
    ("Application code", ["frontend", "backend", "database", "api-contracts"]),
    ("Platform / infra / DevEx", ["infra-iac", "ci-cd", "containers-deploy", "local-devx"]),
    ("Cross-cutting", ["auth-security", "observability", "testing", "docs"]),
]
# path-substring -> discipline (checked against the lowercased path)
DEFAULT_PATH_RULES = [
    {"any": ["/web/", "/frontend/", "/ui/", "/client/", "component", "/pages/", "/views/"], "disc": "frontend"},
    {"any": ["/server/", "/services/", "/service/", "/api/", "/internal/", "/pkg/", "/backend/", "/cmd/", "/app/"], "disc": "backend"},
    {"any": [".sql", "/migrations/", "/migrate", "/db/", "schema.", "sqlc", "prisma", "goose", "flyway", "alembic", "/models/"], "disc": "database"},
    {"any": [".proto", "openapi", "swagger", ".graphql", "/graphql", "/proto/", "buf.", "/schema/", "jsonschema", "avro"], "disc": "api-contracts"},
    {"any": [".tf", "terraform", "pulumi", "cloudformation", "/ansible", "helm", "/k8s", "kubernetes", "/infra"], "disc": "infra-iac"},
    {"any": [".github/workflows", ".gitlab-ci", "jenkinsfile", "circleci", "/.circleci", "/ci/", "azure-pipelines", "release.", "/release/"], "disc": "ci-cd"},
    {"any": ["dockerfile", "docker-compose", "compose.yml", "compose.yaml", "/deploy", "kustom", ".helm", "/charts/"], "disc": "containers-deploy"},
    {"any": ["makefile", "justfile", ".nix", "devenv", "flake.", "/scripts/", "/tools/", ".editorconfig", "package.json", "go.mod", "pyproject", "/build"], "disc": "local-devx"},
    {"any": ["auth", "oauth", "oidc", "/jwt", "login", "session", "crypto", "encrypt", "/security", "secret", "rbac", "permission", "iam", "saml"], "disc": "auth-security"},
    {"any": ["/log", "logger", "metric", "/trace", "telemetry", "otel", "opentelemetry", "prometheus", "sentry", "monitor", "grafana"], "disc": "observability"},
    {"any": ["test", "/spec", ".spec.", "_test.", "__tests__", "/e2e", "cypress", "playwright", "vitest", "jest", ".feature"], "disc": "testing"},
    {"any": [".md", "/docs/", "readme", "changelog", "/adr", ".rst", "mkdocs", "docusaurus"], "disc": "docs"},
]
# file-extension -> discipline (language-level fallback)
DEFAULT_LANG_RULES = {
    ".ts": "frontend", ".tsx": "frontend", ".js": "frontend", ".jsx": "frontend",
    ".vue": "frontend", ".svelte": "frontend", ".css": "frontend", ".scss": "frontend", ".html": "frontend",
    ".go": "backend", ".py": "backend", ".java": "backend", ".rb": "backend", ".rs": "backend",
    ".cs": "backend", ".kt": "backend", ".php": "backend", ".scala": "backend", ".ex": "backend", ".clj": "backend",
}
DEFAULT_BOTS = ["dependabot", "copilot", "github-advanced-security", "github-actions",
                "blacksmith", "renovate", "[bot]", "snyk-bot", "imgbot", "allcontributors"]

def load_config(workdir=None):
    workdir = workdir or os.environ.get("KM_WORKDIR") or os.getcwd()
    cfg_path = os.path.join(workdir, "config.json")
    if not os.path.exists(cfg_path):
        sys.exit(f"config.json not found in {workdir} — write it first (see SKILL.md Phase 1).")
    cfg = json.load(open(cfg_path))
    cfg["workdir"] = workdir
    # Merge a discovered taxonomy if present (written by the discovery step). Keys already
    # set explicitly in config.json win; otherwise the data-derived taxonomy is used.
    disc_path = os.path.join(workdir, "taxonomy.discovered.json")
    if os.path.exists(disc_path):
        try:
            td = json.load(open(disc_path))
            for k in ("disciplines", "groups", "path_rules", "lang_rules", "repo_base", "fallback_discipline"):
                if k in td and k not in cfg:
                    cfg[k] = td[k]
        except Exception:
            pass
    cfg.setdefault("mode", "team")
    cfg.setdefault("recent_cutoff", "")
    cfg.setdefault("today", "")
    cfg.setdefault("bots", DEFAULT_BOTS)
    return cfg

def get_disciplines(cfg):
    return [tuple(x) for x in cfg.get("disciplines", DEFAULT_DISCIPLINES)]

def get_groups(cfg):
    return [tuple(x) for x in cfg.get("groups", DEFAULT_GROUPS)]

def is_bot(login, cfg):
    if not login: return True
    lo = login.lower()
    return any(b.lower() in lo for b in cfg.get("bots", DEFAULT_BOTS))

def build_mapper(cfg):
    """Return map_path(repo, path) -> set(discipline_ids) using cfg rules or generic defaults."""
    disc_ids = {d[0] for d in get_disciplines(cfg)}
    path_rules = cfg.get("path_rules", DEFAULT_PATH_RULES)
    lang_rules = cfg.get("lang_rules", DEFAULT_LANG_RULES)
    repo_base = cfg.get("repo_base", {})
    fallback = cfg.get("fallback_discipline", "backend")

    def map_path(repo, p):
        p = p.lower()
        d = set()
        for ext, disc in lang_rules.items():
            if p.endswith(ext) and disc in disc_ids:
                d.add(disc)
        for rule in path_rules:
            disc = rule.get("disc")
            if disc in disc_ids and any(k in p for k in rule.get("any", [])):
                d.add(disc)
        for b in repo_base.get(repo, []):
            if b in disc_ids: d.add(b)
        return d

    def discs_for(repo, pr):
        d = set()
        for n in (pr.get("files", {}) or {}).get("nodes", []):
            d |= map_path(repo, n["path"])
        if not d and fallback in disc_ids:
            d = {fallback}
        return d
    return map_path, discs_for
