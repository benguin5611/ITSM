#!/usr/bin/env python3
"""Merge deterministic metrics.json + (optional) qualitative findings/*.json into a
scored matrix (level 0-4 per person x discipline) with evidence and risk flags.
Output: <workdir>/matrix.json

Scoring rubric: see references/scoring-rubric.md. Levels:
 0 none · 1 novice · 2 working · 3 strong · 4 SME.
Team mode promotes strong->SME relative to each discipline column (so columns
differentiate). Self mode uses absolute levels (no relative promotion) and adds a
gaps/strengths breakdown for the caller.
Overrides (evidence-based level corrections) come from config.json["overrides"]:
  [["login","disc-id",level,"cited reason"], ...]
"""
import json, glob, os, sys, collections
from discmap import load_config, get_disciplines

cfg = load_config(); WORK = cfg["workdir"]; MODE = cfg.get("mode", "team")
ME = cfg.get("me", "")
metrics = json.load(open(os.path.join(WORK, "metrics.json")))
DISCIPLINES = get_disciplines(cfg); DISC_IDS = [d for d, _ in DISCIPLINES]
labels = dict(DISCIPLINES)

# sum qualitative findings across all finding files (optional — pipeline works without)
qual = collections.defaultdict(lambda: collections.defaultdict(lambda: {
    "review_authority": 0, "corrected_others": 0, "was_corrected": 0, "led_design": 0, "evidence": []}))
for f in sorted(glob.glob(os.path.join(WORK, "findings", "*.json"))):
    try: data = json.load(open(f))
    except Exception: continue
    for person, discs in data.items():
        for d, v in (discs or {}).items():
            if d not in DISC_IDS: continue
            q = qual[person][d]
            for k in ("review_authority", "corrected_others", "was_corrected", "led_design"):
                q[k] += int(v.get(k, 0) or 0)
            for e in (v.get("evidence") or [])[:5]:
                if len(q["evidence"]) < 8: q["evidence"].append(e)

cap = lambda x, c: min(x, c)

def score_cell(m, q):
    g = lambda k: m.get(k, 0)
    an, srg, cg = g("authored_n"), g("subst_review_given"), g("corrected_given")
    cr, mo, ig, ls = g("corrected_received"), g("merged_others"), g("inline_given"), g("learning_signal")
    ra, co, wc, ld = q["review_authority"], q["corrected_others"], q["was_corrected"], q["led_design"]
    authority = (0.22*cap(an,12) + 0.9*cap(srg,8) + 1.3*cap(cg,8) + 0.35*cap(ig,10)
                 + 0.9*cap(mo,8) + 1.6*cap(ra,8) + 2.2*cap(co,6) + 3.0*cap(ld,3))
    learner = 1.1*cap(cr,12) + 1.8*cap(wc,8) + 0.7*cap(ls,8)
    exposure = an + srg + ig + ra
    raw = dict(authored_n=an, authored_recent=g("authored_recent"), subst_review_given=srg,
               corrected_given=cg, corrected_received=cr, merged_others=mo, review_authority=ra,
               corrected_others=co, was_corrected=wc, led_design=ld)
    return authority, learner, exposure, raw

def base_level(authority, learner, exposure, raw):
    if exposure == 0 and learner == 0: return 0, 0.0
    net = authority - 0.6*learner
    co, ld, wc, srg, cr = (raw["corrected_others"], raw["led_design"], raw["was_corrected"],
                           raw["subst_review_given"], raw["corrected_received"])
    lvl = 0
    if net >= 6 and authority >= 6 and (srg >= 3 or co >= 1 or raw["review_authority"] >= 2 or ld >= 1) and learner < authority:
        lvl = 3
    elif net >= 2 and exposure >= 4: lvl = 2
    elif exposure >= 4 and raw["authored_n"] >= 4: lvl = 2
    elif exposure >= 1 or learner > 0: lvl = 1
    if (wc >= 2 or cr >= 7) and co == 0 and ld == 0 and srg < 3: lvl = min(lvl, 2)
    if learner > authority * 1.4 and co == 0 and ld == 0: lvl = min(lvl, 2)
    return lvl, net

matrix = {}
for person, pdata in metrics["people"].items():
    cells = {}; dm = pdata.get("disc", {})
    for d in DISC_IDS:
        m = dm.get(d, {}); q = qual[person].get(d, {"review_authority":0,"corrected_others":0,"was_corrected":0,"led_design":0,"evidence":[]})
        if not m and not any(q[k] for k in ("review_authority","corrected_others","was_corrected","led_design")):
            cells[d] = {"level": 0, "authority": 0.0}; continue
        authority, learner, exposure, raw = score_cell(m, q)
        lvl, net = base_level(authority, learner, exposure, raw)
        cells[d] = {"level": lvl, "authority": round(authority,1), "learner": round(learner,1),
                    "net": round(net,1), "raw": raw, "evidence": q["evidence"][:5]}
    matrix[person] = {"total_prs": pdata["total_prs"], "repos": pdata["repos"],
                      "last_active": pdata["last_active"], "active_recent": pdata["active_recent"], "cells": cells}

# TEAM MODE: promote strong(3) -> SME(4) relative to each discipline column
if MODE != "self":
    for d in DISC_IDS:
        ranked = sorted(matrix, key=lambda p: -matrix[p]["cells"][d].get("authority", 0))
        amax = matrix[ranked[0]]["cells"][d].get("authority", 0) if ranked else 0
        if amax <= 0: continue
        promoted = 0
        for rank, p in enumerate(ranked):
            c = matrix[p]["cells"][d]
            if c["level"] < 3: break
            raw = c.get("raw", {}); a = c.get("authority", 0); net = c.get("net", 0)
            if (a >= max(7.0, 0.55*amax) and net >= 6
                and (raw.get("led_design",0) >= 1 or raw.get("corrected_others",0) >= 2)
                and c.get("learner",0) < a and promoted < 3 and rank < 4):
                c["level"] = 4; promoted += 1
else:
    # SELF MODE: allow absolute SME only on very strong evidence (no relative inflation)
    for p in matrix:
        for d in DISC_IDS:
            c = matrix[p]["cells"][d]; raw = c.get("raw", {})
            if c["level"] == 3 and raw.get("led_design",0) >= 2 and raw.get("corrected_others",0) >= 3 \
               and c.get("net",0) >= 10:
                c["level"] = 4

# evidence-based overrides from config
for ov in cfg.get("overrides", []):
    try: p, d, lvl, reason = ov
    except Exception:
        print(f"WARNING: malformed override {ov!r} — skipping. Expected [login, disc-id, level, reason].", file=sys.stderr)
        continue
    if p in matrix and d in matrix[p]["cells"]:
        matrix[p]["cells"][d]["level"] = lvl; matrix[p]["cells"][d]["override"] = reason
    else:
        print(f"WARNING: override {ov!r} matches no person/discipline cell — check the login and disc-id.", file=sys.stderr)

# bus-factor (team) and gaps/strengths (self)
busfactor = {}
for d in DISC_IDS:
    strong = sorted([(p, matrix[p]["cells"][d]["level"]) for p in matrix if matrix[p]["cells"][d]["level"] >= 3], key=lambda x:-x[1])
    busfactor[d] = {"n_strong": len(strong), "smes": [p for p,l in strong if l==4],
                    "strong_people": [p for p,_ in strong], "pr_count": metrics["disc_pr_count"].get(d,0)}

# ---- per-REPO slice: same scoring, scoped to each repository (deterministic signal only) ----
REPOS = metrics.get("repos", [])
Q0 = {"review_authority":0,"corrected_others":0,"was_corrected":0,"led_design":0}
repo_matrix = {}
for p in matrix:
    rcells = {}
    rd = metrics["people"][p].get("repo", {})
    for r in REPOS:
        m = rd.get(r, {})
        if not m: rcells[r] = {"level": 0, "authority": 0.0}; continue
        authority, learner, exposure, raw = score_cell(m, Q0)
        lvl, net = base_level(authority, learner, exposure, raw)
        rcells[r] = {"level": lvl, "authority": round(authority,1), "net": round(net,1), "raw": raw}
    repo_matrix[p] = rcells
if MODE != "self":
    for r in REPOS:                       # relative SME promotion within each repo column
        ranked = sorted(matrix, key=lambda p: -repo_matrix[p][r].get("authority",0))
        amax = repo_matrix[ranked[0]][r].get("authority",0) if ranked else 0
        if amax <= 0: continue
        promoted = 0
        for rank, p in enumerate(ranked):
            c = repo_matrix[p][r]
            if c["level"] < 3: break
            if c.get("authority",0) >= max(7.0, 0.55*amax) and c.get("net",0) >= 6 and promoted < 3 and rank < 4:
                c["level"] = 4; promoted += 1
repo_busfactor = {}
for r in REPOS:
    strong = sorted([(p, repo_matrix[p][r]["level"]) for p in matrix if repo_matrix[p][r]["level"] >= 3], key=lambda x:-x[1])
    repo_busfactor[r] = {"n_strong": len(strong), "smes": [p for p,l in strong if l==4],
                         "strong_people": [p for p,_ in strong], "pr_count": metrics.get("repo_pr_count",{}).get(r,0)}

selfreport = None
if MODE == "self" and ME in matrix:
    c = matrix[ME]["cells"]
    touched = [(d, c[d]) for d in DISC_IDS if c[d]["level"] > 0 or c[d].get("raw",{}).get("corrected_received",0)]
    gaps = sorted(touched, key=lambda kv: (kv[1]["level"], -(kv[1].get("raw",{}).get("corrected_received",0))))
    strengths = sorted(touched, key=lambda kv: -kv[1]["level"])
    selfreport = {
        "me": ME,
        "strengths": [{"disc": d, "label": labels[d], "level": v["level"], "evidence": v.get("evidence",[])} for d,v in strengths if v["level"] >= 3][:8],
        "gaps": [{"disc": d, "label": labels[d], "level": v["level"],
                  "corrected_received": v.get("raw",{}).get("corrected_received",0),
                  "evidence": v.get("evidence",[])} for d,v in gaps if v["level"] <= 2][:10],
        "untouched": [labels[d] for d in DISC_IDS if c[d]["level"] == 0 and not c[d].get("raw")],
    }

out = {"disciplines": DISCIPLINES, "matrix": matrix, "busfactor": busfactor,
       "repos": REPOS, "repo_matrix": repo_matrix, "repo_busfactor": repo_busfactor,
       "edges": metrics.get("edges", {}), "recent_cutoff": metrics["recent_cutoff"],
       "mode": MODE, "me": ME, "selfreport": selfreport}
json.dump(out, open(os.path.join(WORK, "matrix.json"), "w"), indent=2)
print(f"matrix.json written — mode={MODE}, {len(matrix)} people"
      + (f", self-report for {ME}" if selfreport else ""))
