#!/usr/bin/env python3
"""Build a code inventory from the harvested PR corpus — the evidence the skill uses to
DISCOVER its own discipline taxonomy (instead of assuming generic categories).

Aggregates, across every changed file in raw/*.ndjson: file extensions (languages),
top-level and second-level directories, and service/package/domain-style directory names
(services/*, apps/*, packages/*, pkg/*, cmd/*, proto/*, modules/*, libs/*). Frequencies
are PR-weighted, so they reflect where the team actually works.

Output: <workdir>/inventory.json — a compact, identity-free map of the codebase that the
discovery step (see templates/taxonomy-discovery-brief.md) turns into disciplines + rules.
"""
import json, glob, os, collections
from discmap import load_config

cfg = load_config(); WORK = cfg["workdir"]
SERVICE_PARENTS = {"services", "service", "apps", "app", "packages", "pkg", "cmd",
                   "proto", "modules", "libs", "lib", "internal", "domains", "workers"}

ext = collections.Counter()
dir1 = collections.Counter()
dir2 = collections.Counter()
domain_dirs = collections.Counter()   # e.g. services/<name> -> "<name>"
repo_info = {}

for f in glob.glob(os.path.join(WORK, "raw", "*.ndjson")):
    repo = os.path.basename(f)[:-len(".ndjson")].replace(".me", "").replace(".rev", "")
    r = repo_info.setdefault(repo, {"prs": 0, "exts": collections.Counter(), "dirs": collections.Counter()})
    for line in open(f):
        line = line.strip()
        if not line: continue
        pr = json.loads(line)
        r["prs"] += 1
        seen_d1, seen_d2, seen_dom = set(), set(), set()
        for n in (pr.get("files", {}) or {}).get("nodes", []):
            p = (n.get("path") or "").lower()
            if not p: continue
            if "." in os.path.basename(p):
                e = "." + p.rsplit(".", 1)[-1]
                if len(e) <= 8: ext[e] += 1; r["exts"][e] += 1
            segs = p.split("/")
            if segs:
                seen_d1.add(segs[0])
                r["dirs"][segs[0]] += 1
            if len(segs) >= 2:
                seen_d2.add(segs[0] + "/" + segs[1])
                if segs[0] in SERVICE_PARENTS:
                    seen_dom.add(segs[1])
        for d in seen_d1: dir1[d] += 1
        for d in seen_d2: dir2[d] += 1
        for d in seen_dom: domain_dirs[d] += 1

def top(counter, n): return [[k, v] for k, v in counter.most_common(n)]

inv = {
    "note": "Evidence for discovering this codebase's discipline taxonomy. Frequencies are PR-weighted.",
    "global": {
        "extensions": top(ext, 30),
        "top_level_dirs": top(dir1, 30),
        "second_level_dirs": top(dir2, 50),
        "service_or_domain_dirs": top(domain_dirs, 60),
    },
    "repos": {repo: {"prs": ri["prs"], "top_dirs": top(ri["dirs"], 12), "exts": top(ri["exts"], 10)}
              for repo, ri in sorted(repo_info.items())},
}
json.dump(inv, open(os.path.join(WORK, "inventory.json"), "w"), indent=2)
print(f"inventory.json written — {len(repo_info)} repos, {len(ext)} extensions, "
      f"{len(domain_dirs)} service/domain dirs")
print("top languages:", ", ".join(f"{e}({c})" for e, c in ext.most_common(8)))
print("top service/domain dirs:", ", ".join(f"{d}" for d, _ in domain_dirs.most_common(12)) or "(none)")
