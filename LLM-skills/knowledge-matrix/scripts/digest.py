#!/usr/bin/env python3
"""Build slim per-PR digests for agent reading: discipline tags + FULL discussion
text (every comment/review/inline body verbatim), dropping per-file size bulk.
Team mode: splits the corpus into balanced chunks for parallel agents.
Self mode: one digest file for the caller's corpus.
Output: <workdir>/digest/*.jsonl
"""
import json, glob, os
from discmap import load_config, build_mapper

cfg = load_config(); WORK = cfg["workdir"]
_, discs_for = build_mapper(cfg)
NCHUNKS = int(cfg.get("chunks", 6))
os.makedirs(os.path.join(WORK, "digest"), exist_ok=True)

def digest_pr(repo, pr):
    disc = []
    author = (pr.get("author") or {}).get("login")
    for c in (pr.get("comments", {}) or {}).get("nodes", []):
        b = (c.get("bodyText") or "").strip()
        if b: disc.append({"by": (c.get("author") or {}).get("login"), "kind": "comment", "text": b})
    for rv in (pr.get("reviews", {}) or {}).get("nodes", []):
        b = (rv.get("bodyText") or "").strip(); st = rv.get("state")
        if b or st in ("APPROVED", "CHANGES_REQUESTED"):
            disc.append({"by": (rv.get("author") or {}).get("login"), "kind": f"review:{st}", "text": b})
    for th in (pr.get("reviewThreads", {}) or {}).get("nodes", []):
        for c in (th.get("comments", {}) or {}).get("nodes", []):
            b = (c.get("bodyText") or "").strip()
            if b: disc.append({"by": (c.get("author") or {}).get("login"), "kind": "inline",
                               "path": c.get("path"), "text": b})
    return {"repo": repo, "number": pr.get("number"), "title": pr.get("title"), "author": author,
            "state": pr.get("state"), "merged": bool(pr.get("mergedAt")),
            "mergedBy": (pr.get("mergedBy") or {}).get("login"),
            "createdAt": (pr.get("createdAt") or "")[:10],
            "additions": pr.get("additions"), "changedFiles": pr.get("changedFiles"),
            "labels": [l["name"] for l in (pr.get("labels", {}) or {}).get("nodes", [])],
            "disciplines": sorted(discs_for(repo, pr)), "discussion": disc}

allpr = []
for f in sorted(glob.glob(os.path.join(WORK, "raw", "*.ndjson"))):
    repo = os.path.basename(f)[:-len(".ndjson")].replace(".me", "").replace(".rev", "")
    for line in open(f):
        line = line.strip()
        if line: allpr.append(digest_pr(repo, json.loads(line)))
# de-dupe (self mode harvests author+reviewer separately)
seen = {}
for dg in allpr: seen[(dg["repo"], dg["number"])] = dg
allpr = list(seen.values())
allpr.sort(key=lambda x: (x["repo"], x["number"]))

def weight(dg): return 200 + sum(len(d["text"]) for d in dg["discussion"])

if cfg.get("mode") == "self" or len(allpr) <= 250:
    with open(os.path.join(WORK, "digest", "corpus.jsonl"), "w") as fh:
        for dg in allpr: fh.write(json.dumps(dg) + "\n")
    print(f"digest/corpus.jsonl: {len(allpr)} PRs, {sum(weight(d) for d in allpr)//1000}k chars")
else:
    total = sum(weight(d) for d in allpr); target = total / NCHUNKS
    chunks = [[] for _ in range(NCHUNKS)]; ci = acc = 0
    for dg in allpr:
        chunks[ci].append(dg); acc += weight(dg)
        if acc >= target and ci < NCHUNKS - 1: ci += 1; acc = 0
    for i, ch in enumerate(chunks):
        with open(os.path.join(WORK, "digest", f"chunk{i+1:02d}.jsonl"), "w") as fh:
            for dg in ch: fh.write(json.dumps(dg) + "\n")
        print(f"digest/chunk{i+1:02d}.jsonl: {len(ch)} PRs, {sum(weight(d) for d in ch)//1000}k chars")
