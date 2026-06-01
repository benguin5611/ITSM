#!/usr/bin/env python3
"""Render matrix.json -> knowledge-matrix-report.md (narrative companion).
Team mode: matrix table, bus-factor, per-engineer profiles, auto succession recs.
Self mode: personal strengths/gaps report.
The orchestrating agent should refine the executive summary + succession actions
with judgement after this runs (see SKILL.md Phase 6).
"""
import json, os
from discmap import load_config, get_disciplines, get_groups

cfg = load_config(); WORK = cfg["workdir"]
M = json.load(open(os.path.join(WORK, "matrix.json")))
matrix = M["matrix"]; busfactor = M["busfactor"]; MODE = M.get("mode","team"); ME = M.get("me","")
selfreport = M.get("selfreport")
REPOS = M.get("repos", []); repo_matrix = M.get("repo_matrix", {}); repo_busfactor = M.get("repo_busfactor", {})
DISCIPLINES = get_disciplines(cfg); DISC_IDS = [d for d, _ in DISCIPLINES]
labels = dict(DISCIPLINES); ROLES_CFG = cfg.get("roles", {})
GROUPS = [(g, [d for d in ds if d in DISC_IDS]) for g, ds in get_groups(cfg)]
GLYPH = {0:"·",1:"🟥",2:"🟧",3:"🟩",4:"🟢"}

def derive_role(p):
    """Generic, taxonomy-agnostic role from where the person is strong. Override via config['roles']."""
    if p in ROLES_CFG: return ROLES_CFG[p]
    c = matrix[p]["cells"]
    strong = sorted([(labels[d], c[d]["level"]) for d in DISC_IDS if c[d]["level"]>=3], key=lambda x:-x[1])
    if not strong: return "Generalist — developing"
    if len(strong) >= max(4, 0.55*len(DISC_IDS)): return "Full-stack / broad authority"
    return "Strength: " + ", ".join(lbl for lbl,_ in strong[:3])

def order_people():
    return sorted(matrix, key=lambda p:(-(sum(1 for d in DISC_IDS if matrix[p]['cells'][d]['level']==4)*2
        + sum(1 for d in DISC_IDS if matrix[p]['cells'][d]['level']>=3)), -matrix[p]['total_prs']))

out=[]; w=out.append
if MODE == "self" and selfreport:
    w(f"# Your Knowledge Profile — {ME}\n")
    w(f"_{cfg.get('owner','')} · generated {cfg.get('today','')} · personal gap analysis from your authored PRs and the reviews on them. "
      "Levels are absolute (0 none · 1 novice · 2 working · 3 strong · 4 SME), not ranked against teammates._\n")
    w("> Open `knowledge-matrix.html` for the visual version.\n")
    c = matrix[ME]["cells"] if ME in matrix else {}
    w("## Proficiency by discipline\n")
    w("| Discipline | Level | |")
    w("|---|---|---|")
    for _, ds in GROUPS:
        for d in ds:
            lv = c.get(d,{}).get("level",0)
            w(f"| {labels[d]} | {lv} | {GLYPH[lv]} {['None','Novice','Working','Strong','SME'][lv]} |")
    w("\n## Your strengths (where you lead or review others)\n")
    if selfreport["strengths"]:
        for s in selfreport["strengths"]:
            ev = "; ".join(s.get("evidence",[])[:2])
            w(f"- **{s['label']}** (L{s['level']})" + (f" — {ev}" if ev else ""))
    else: w("_No clear lead/teaching areas yet — focus on deepening one discipline to reach 'strong'._")
    w("\n## Development areas (lowest level / most corrected)\n")
    for g in selfreport["gaps"]:
        ev = "; ".join(g.get("evidence",[])[:2]); cr = g.get("corrected_received",0)
        w(f"- **{g['label']}** (L{g['level']}" + (f", corrected {cr}×" if cr else "") + ")" + (f" — {ev}" if ev else ""))
    w(f"\n**Untouched disciplines** (no PR footprint): {', '.join(selfreport['untouched']) or '—'} — whitespace to broaden into if relevant to your role.\n")
    w("\n_Next step: pick one development area that matters to your role, pair with the team's SME in it, "
      "and set a 60–90 day goal to move it from where it is to 'strong'._\n")
else:
    n_repos = len({r for p in matrix for r in matrix[p]["repos"]})
    w(f"# {cfg.get('title','Engineering Knowledge Matrix')}\n")
    w(f"_Generated {cfg.get('today','')} · {cfg.get('owner','')} · {len(matrix)} contributors · {n_repos} repos · "
      "**every comment, review and inline thread read** (bots excluded)._\n")
    w("> **Companion:** open `knowledge-matrix.html` for the colour heatmap (hover cells for evidence + PR refs).\n")
    w("## How proficiency was scored\n")
    w("Three evidence streams from the full PR history: **(1) authorship** (volume/size, lightly weighted — broad multi-discipline PRs discounted), "
      "**(2) review authority** (corrective reviews/inline comments *given*, merge authority, design leadership — heavily weighted), and "
      "**(3) who-corrects-whom** (being corrected lowers the level; correcting/teaching others raises it).\n")
    w("**Levels:** `0` none · `1` novice · `2` working · `3` strong · `4` SME (go-to; sets patterns, corrects others, owns the area). "
      "SME is gated to the top authority-holders *within each discipline column* so the matrix differentiates. ⚑ = evidence-based override.\n")
    w("## The matrix\n")
    w("Legend: 🟢 SME (4) · 🟩 Strong (3) · 🟧 Working (2) · 🟥 Novice (1) · · None (0)\n")
    w("| Engineer | Role | " + " | ".join(labels[d] for d in DISC_IDS) + " |")
    w("|" + "---|"*(len(DISC_IDS)+2))
    for p in order_people():
        c = matrix[p]["cells"]
        row = " | ".join(GLYPH[c[d]["level"]] + (" ⚑" if c[d].get("override") else "") for d in DISC_IDS)
        w(f"| **{p}** | {derive_role(p)} | {row} |")
    w("\n## Bus-factor & concentration risk\n")
    w("Ordered by fragility (fewest engineers at Strong+). **CRITICAL** = one strong owner; **WATCH** = two.\n")
    w("| Discipline | # Strong+ | PRs | SME (4) | Other strong (3) | Risk |")
    w("|---|---|---|---|---|---|")
    crit = []
    for d, b in sorted(busfactor.items(), key=lambda kv:(kv[1]["n_strong"], -kv[1]["pr_count"])):
        risk = "🔴 CRITICAL" if b["n_strong"]<=1 else ("🟠 WATCH" if b["n_strong"]==2 else "🟢 OK")
        smes = ", ".join(b["smes"]) or "—"; other = ", ".join([x for x in b["strong_people"] if x not in b["smes"]]) or "—"
        prc = b["pr_count"]
        w(f"| {labels[d]} | {b['n_strong']} | {prc} | {smes} | {other} | {risk} |")
        if b["n_strong"] <= 1 and b["pr_count"] > 10: crit.append((d, b))
    # per-repo slice
    if REPOS and repo_matrix:
        repos_sorted = sorted(REPOS, key=lambda r: -repo_busfactor.get(r,{}).get("pr_count",0))
        w("\n## Proficiency by repository\n")
        w("Who leads vs who is still learning **in each repository** — use this to see who can own or be moved onto a repo. Same 0–4 scale.\n")
        w("Legend: 🟢 SME (4) · 🟩 Strong (3) · 🟧 Working (2) · 🟥 Novice (1) · · None (0)\n")
        w("| Engineer | " + " | ".join(repos_sorted) + " |")
        w("|" + "---|"*(len(repos_sorted)+1))
        for p in order_people():
            row = " | ".join(GLYPH[repo_matrix.get(p,{}).get(r,{}).get("level",0)] for r in repos_sorted)
            w(f"| **{p}** | {row} |")
        w("\n## Repository ownership risk\n")
        w("| Repository | # Strong+ | PRs | Owner(s) — SME | Other strong | Risk |")
        w("|---|---|---|---|---|---|")
        for r in repos_sorted:
            b = repo_busfactor.get(r, {}); ns = b.get("n_strong",0)
            risk = "🔴 CRITICAL" if ns<=1 else ("🟠 WATCH" if ns==2 else "🟢 OK")
            smes = ", ".join(b.get("smes",[])) or "—"
            other = ", ".join([x for x in b.get("strong_people",[]) if x not in b.get("smes",[])]) or "—"
            w(f"| {r} | {ns} | {b.get('pr_count',0)} | {smes} | {other} | {risk} |")
    w("\n## Per-engineer profiles\n")
    for p in order_people():
        c = matrix[p]["cells"]; core = {d for d,_ in sorted(busfactor.items(), key=lambda kv:-kv[1]["pr_count"])[:8]}
        sme = [labels[d] for d in DISC_IDS if c[d]["level"]>=4]; strong=[labels[d] for d in DISC_IDS if c[d]["level"]==3]
        cg = [labels[d] for d in DISC_IDS if d in core and c[d]["level"]<=1]
        w(f"### {p} — {derive_role(p)}")
        w(f"_{matrix[p]['total_prs']} PRs · {len(matrix[p]['repos'])} repos · last active {matrix[p]['last_active']}_\n")
        w(f"- **SME (4):** {', '.join(sme) if sme else '— none —'}")
        w(f"- **Strong (3):** {', '.join(strong) if strong else '—'}")
        gaps_txt = ", ".join(cg) if cg else "none in the busiest disciplines"
        w(f"- **Gaps in high-traffic areas (≤ novice):** {gaps_txt}")
        ev=[]
        for d in DISC_IDS:
            for e in c[d].get("evidence",[])[:1]: ev.append(f"_{labels[d]}_ — {e}")
            if len(ev)>=3: break
        if ev: w(f"- **Evidence:** " + "; ".join(ev[:3]))
        w("")
    w("## Succession & upskilling priorities (auto-derived — refine with judgement)\n")
    if crit:
        for d, b in crit:
            owner = b["smes"][0] if b["smes"] else (b["strong_people"][0] if b["strong_people"] else "nobody")
            # best upskill candidate: highest authority among level<3 with some exposure
            cands = sorted([(p, matrix[p]["cells"][d].get("authority",0)) for p in matrix
                            if matrix[p]["cells"][d]["level"] in (1,2)], key=lambda x:-x[1])
            cand = cands[0][0] if cands else "a mid-level engineer"
            w(f"- **{labels[d]}** rests on **{owner}** alone ({b['pr_count']} PRs). Pair **{cand}** onto it and document the area to break the bus-factor-of-one.")
    else:
        w("- No single-owner CRITICAL disciplines detected. Focus on deepening WATCH (two-owner) areas.")
    # over-concentration
    conc = sorted(matrix, key=lambda p:-sum(1 for d in DISC_IDS if matrix[p]['cells'][d]['level']>=3))
    if conc:
        top = conc[0]; n = sum(1 for d in DISC_IDS if matrix[top]['cells'][d]['level']>=3)
        if n >= 12:
            w(f"- **{top}** is strong/SME in {n} of {len(DISC_IDS)} disciplines — the single biggest knowledge concentration. "
              "Deliberately transfer ownership of a few areas to rising engineers to reduce bus-factor and free senior capacity.")
    # juniors with no specialism
    for p in matrix:
        if matrix[p]["total_prs"] >= 20 and not any(matrix[p]["cells"][d]["level"]>=3 for d in DISC_IDS):
            w(f"- **{p}** has {matrix[p]['total_prs']} PRs but no area of authority yet — assign one specialism with a named mentor and a 90-day depth goal (plateau/retention risk).")
    w("\n## Method notes & limitations\n")
    w("- **Source:** all PRs (open + closed + merged) and their full review/comment/inline bodies, via the GitHub GraphQL API.\n")
    w("- **Disciplines** are assigned from changed-file paths + repo; bulk vendor/codegen PRs (>100 files) truncate file lists at 100 — immaterial to skill signal.\n")
    w("- **Bots excluded:** " + ", ".join(cfg.get("bots", [])[:6]) + ", …\n")
    w("- **Identifiers** are GitHub handles, not display names. This is an *evidence-grounded judgement artefact*, not an appraisal — validate surprising cells against the linked PRs before acting.\n")

open(os.path.join(WORK, "knowledge-matrix-report.md"), "w").write("\n".join(out))
print(f"knowledge-matrix-report.md written ({MODE} mode)")
