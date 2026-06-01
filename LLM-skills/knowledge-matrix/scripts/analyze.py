#!/usr/bin/env python3
"""Deterministic authority analysis over the whole corpus — reads EVERY comment,
review and inline thread. Produces per-person x per-discipline metrics, the same
signals sliced per-repository, and a directional 'who-corrects-whom' graph.
Output: <workdir>/metrics.json. Reads config.json + raw/*.ndjson.
"""
import json, glob, os, re, collections
from discmap import load_config, build_mapper, get_disciplines, is_bot

cfg = load_config()
WORK = cfg["workdir"]
RECENT = cfg.get("recent_cutoff", "")
map_path, discs_for = build_mapper(cfg)
DISC_IDS = [d for d, _ in get_disciplines(cfg)]
def bot(login): return is_bot(login, cfg)

CORRECT_RE = re.compile(r"\b(should(n't| not)?|don't|do not|instead|actually|incorrect|wrong|"
    r"the issue is|this won't|this will (break|fail)|need to|must|prefer|avoid|"
    r"not how|that's not|this is not|revert|please (use|change|remove|fix)|"
    r"why (are|is|do|don't)|nit:|suggestion:|consider |we (use|don't use)|"
    r"this should be|missing|you('| a)re (using|missing)|let's not)\b", re.I)
LEARN_RE = re.compile(r"\b(good (catch|point)|you('| a)re right|my (bad|mistake)|"
    r"i('ll| will) (fix|change|update|revert)|done(\.|,| -)|fixed|TIL|"
    r"i (didn't|did not) (know|realise|realize)|thanks for (the )?(catch|pointer|explaining)|"
    r"how (do|should) i|not sure (how|if|what|why)|is (this|that) (right|correct|ok)|"
    r"can you (explain|clarify)|makes sense, (changed|updated|fixed))\b", re.I)

# per (person, discipline) and per (person, repo)
metrics = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(float)))
rmetrics = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(float)))
edges = collections.defaultdict(lambda: collections.Counter())
people, last_active = set(), {}
total_prs = collections.Counter()
repos_active = collections.defaultdict(set)
disc_pr_count = collections.Counter()
repo_pr_count = collections.Counter()
all_repos = set()

def add(p, d, k, v=1):
    if not p or bot(p): return
    metrics[p][d][k] += v; people.add(p)

def radd(p, repo, k, v=1):
    if not p or bot(p): return
    rmetrics[p][repo][k] += v

for f in glob.glob(os.path.join(WORK, "raw", "*.ndjson")):
    repo = os.path.basename(f)[:-len(".ndjson")].replace(".me", "").replace(".rev", "")
    all_repos.add(repo)
    for line in open(f):
        line = line.strip()
        if not line: continue
        pr = json.loads(line)
        author = (pr.get("author") or {}).get("login")
        discs = discs_for(repo, pr)
        for d in discs: disc_pr_count[d] += 1
        repo_pr_count[repo] += 1
        created = pr.get("createdAt") or ""
        recent = (not RECENT) or created >= RECENT
        adds = pr.get("additions", 0) or 0
        size_w = 1.0 + min(adds, 3000) / 1000.0
        if author and not bot(author):
            total_prs[author] += 1; repos_active[author].add(repo)
            last_active[author] = max(last_active.get(author, ""), created)
            for d in discs:
                add(author, d, "authored_n", 1); add(author, d, "authored_w", size_w)
                if recent: add(author, d, "authored_recent", 1)
            radd(author, repo, "authored_n", 1); radd(author, repo, "authored_w", size_w)
            if recent: radd(author, repo, "authored_recent", 1)
        for rv in (pr.get("reviews", {}) or {}).get("nodes", []):
            who = (rv.get("author") or {}).get("login")
            if bot(who) or who == author: continue
            body = (rv.get("bodyText") or "").strip(); state = rv.get("state")
            corrective = (state == "CHANGES_REQUESTED") or (len(body) > 60 and CORRECT_RE.search(body))
            for d in discs:
                add(who, d, "reviews_given", 1)
                if len(body) > 40: add(who, d, "subst_review_given", 1)
                if corrective:
                    add(who, d, "corrected_given", 1)
                    if author and not bot(author): add(author, d, "corrected_received", 1); edges[d][(who, author)] += 1
            radd(who, repo, "reviews_given", 1)
            if len(body) > 40: radd(who, repo, "subst_review_given", 1)
            if corrective:
                radd(who, repo, "corrected_given", 1)
                if author and not bot(author): radd(author, repo, "corrected_received", 1)
        for th in (pr.get("reviewThreads", {}) or {}).get("nodes", []):
            for c in (th.get("comments", {}) or {}).get("nodes", []):
                who = (c.get("author") or {}).get("login")
                if bot(who): continue
                body = (c.get("bodyText") or "").strip(); cpath = c.get("path") or ""
                cd = (map_path(repo, cpath) if cpath else discs) or discs
                if who != author:
                    corrective = len(body) > 50 and CORRECT_RE.search(body)
                    for d in cd:
                        add(who, d, "inline_given", 1)
                        if corrective:
                            add(who, d, "corrected_given", 1)
                            if author and not bot(author): add(author, d, "corrected_received", 1); edges[d][(who, author)] += 1
                    radd(who, repo, "inline_given", 1)
                    if corrective:
                        radd(who, repo, "corrected_given", 1)
                        if author and not bot(author): radd(author, repo, "corrected_received", 1)
                elif LEARN_RE.search(body):
                    for d in cd: add(who, d, "learning_signal", 1)
                    radd(who, repo, "learning_signal", 1)
        for c in (pr.get("comments", {}) or {}).get("nodes", []):
            who = (c.get("author") or {}).get("login")
            if bot(who): continue
            body = (c.get("bodyText") or "").strip()
            if len(body) < 25: continue
            if who == author:
                if LEARN_RE.search(body):
                    for d in discs: add(who, d, "learning_signal", 1)
                    radd(who, repo, "learning_signal", 1)
            elif CORRECT_RE.search(body):
                for d in discs: add(who, d, "corrected_given", 0.5)
                radd(who, repo, "corrected_given", 0.5)
        mb = (pr.get("mergedBy") or {}).get("login")
        if mb and not bot(mb) and mb != author:
            for d in discs: add(mb, d, "merged_others", 1)
            radd(mb, repo, "merged_others", 1)

people = sorted(p for p in people if not bot(p))
repos = sorted(all_repos)
out = {"people": {p: {
        "total_prs": total_prs.get(p, 0), "repos": sorted(repos_active.get(p, [])),
        "last_active": last_active.get(p, "")[:10],
        "active_recent": (not RECENT) or last_active.get(p, "") >= RECENT,
        "disc": {d: {k: round(v, 1) for k, v in dd.items()} for d, dd in metrics[p].items()},
        "repo": {r: {k: round(v, 1) for k, v in rr.items()} for r, rr in rmetrics[p].items()},
    } for p in people},
    "disc_pr_count": dict(disc_pr_count),
    "repo_pr_count": dict(repo_pr_count),
    "repos": repos,
    "edges": {d: [{"from": a, "to": b, "n": n} for (a, b), n in c.most_common(8)] for d, c in edges.items()},
    "recent_cutoff": RECENT}
json.dump(out, open(os.path.join(WORK, "metrics.json"), "w"), indent=2)
print(f"metrics.json written — {len(people)} people, {len(disc_pr_count)} disciplines, {len(repos)} repos")
