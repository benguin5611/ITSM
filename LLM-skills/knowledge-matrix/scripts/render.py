#!/usr/bin/env python3
"""Render matrix.json -> knowledge-matrix.html.
Team mode: colour heatmap (people x disciplines) + per-engineer cards + bus-factor.
Self mode: a focused personal report for the caller (per-discipline strength bars,
strengths, gaps, untouched areas).
Typography: Inter webfont (system fallback), tabular numerals, refined spacing.
"""
import json, os, html
from discmap import load_config, get_disciplines, get_groups

cfg = load_config(); WORK = cfg["workdir"]
M = json.load(open(os.path.join(WORK, "matrix.json")))
matrix = M["matrix"]; busfactor = M["busfactor"]; MODE = M.get("mode", "team")
ME = M.get("me", ""); selfreport = M.get("selfreport")
REPOS = M.get("repos", []); repo_matrix = M.get("repo_matrix", {}); repo_busfactor = M.get("repo_busfactor", {})
DISCIPLINES = get_disciplines(cfg); DISC_IDS = [d for d, _ in DISCIPLINES]
labels = dict(DISCIPLINES)
GROUPS = [(g, [d for d in ds if d in DISC_IDS]) for g, ds in get_groups(cfg)]
ROLES_CFG = cfg.get("roles", {})
LVNAME = {0:"None",1:"Novice",2:"Working",3:"Strong",4:"SME"}
LVCOL  = {0:"#eef0f3",1:"#f0938c",2:"#f6c66b",3:"#9bd17a",4:"#2f9466"}
LVTXT  = {0:"#9aa0a6",1:"#5a1410",2:"#5a3c00",3:"#1f4710",4:"#ffffff"}

def derive_role(p):
    """Generic, taxonomy-agnostic role from where the person is strong. Override via config['roles']."""
    if p in ROLES_CFG: return ROLES_CFG[p]
    c = matrix[p]["cells"]
    strong = sorted([(labels[d], c[d]["level"]) for d in DISC_IDS if c[d]["level"] >= 3], key=lambda x:-x[1])
    if not strong: return "Generalist — developing"
    if len(strong) >= max(4, 0.55*len(DISC_IDS)): return "Full-stack / broad authority"
    # otherwise name the top strengths
    names = ", ".join(lbl for lbl, _ in strong[:3])
    return f"Strength: {names}"

def strengths(p, lvl=4): return [labels[d] for d in DISC_IDS if matrix[p]["cells"][d]["level"] >= lvl]
def cells_at(p, lv): return [labels[d] for d in DISC_IDS if matrix[p]["cells"][d]["level"] == lv]

def order_people():
    def key(p):
        c = matrix[p]["cells"]
        return (-(sum(1 for d in DISC_IDS if c[d]["level"]==4)*2 + sum(1 for d in DISC_IDS if c[d]["level"]>=3)),
                -matrix[p]["total_prs"])
    return sorted(matrix, key=key)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--font:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:#f5f6f8;color:#1a1d21;font-family:var(--font);
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;font-feature-settings:'cv11','ss01';line-height:1.5}
.wrap{max-width:1520px;margin:0 auto;padding:36px 28px 60px}
h1{font-size:27px;font-weight:800;letter-spacing:-.02em;margin:0 0 5px}
.sub{color:#5f6b7a;margin:0 0 20px;font-size:13px;font-weight:450;max-width:1000px}
h2{font-size:19px;font-weight:700;letter-spacing:-.01em;margin:34px 0 12px}
.legend{margin:16px 0 10px;display:flex;gap:7px;flex-wrap:wrap;align-items:center}
.lg{padding:4px 12px;border-radius:14px;font-size:12px;font-weight:600;letter-spacing:.01em}
.matrix-scroll{overflow-x:auto;border-radius:12px;box-shadow:0 1px 4px rgba(20,30,50,.09)}
table{border-collapse:separate;border-spacing:0;font-size:12px;background:#fff;font-variant-numeric:tabular-nums}
th,td{border-bottom:1px solid #eef0f3;border-right:1px solid #eef0f3}
th.rowhdr{background:#fff;position:sticky;left:0;z-index:5;min-width:248px;text-align:left;padding:10px 12px;font-weight:600}
th.grp{background:#222a35;color:#fff;font-size:10.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:7px 8px;text-align:center}
th.disc{background:#f1f3f6;font-weight:600;vertical-align:bottom;height:128px;width:36px;padding:7px 2px}
th.disc div{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;margin:0 auto;font-size:11px;color:#39414d;font-weight:550}
th.person{background:#fff;position:sticky;left:0;z-index:4;text-align:left;padding:9px 12px;min-width:248px}
.pname{font-weight:700;font-size:13.5px;letter-spacing:-.01em}.prole{color:#5f6b7a;font-size:11.5px;font-weight:450}
.pmeta{color:#9aa0a6;font-size:10.5px;margin-top:1px;font-weight:450}
td.lvl{width:36px;height:42px;text-align:center;font-weight:700;font-size:13px;cursor:default}
td.lvl:hover{outline:2.5px solid #1a1d21;outline-offset:-2px;border-radius:3px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(345px,1fr));gap:15px}
.card{background:#fff;border-radius:12px;padding:16px 18px;box-shadow:0 1px 4px rgba(20,30,50,.08)}
.card h3{margin:0 0 1px;font-size:15.5px;font-weight:700;letter-spacing:-.01em}.card .role{color:#5f6b7a;font-size:12px;margin-bottom:9px}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0}
.chip{font-size:11px;padding:3px 9px;border-radius:11px;font-weight:600}
.chip.sme{background:#2f9466;color:#fff}.chip.strong{background:#9bd17a;color:#173a08}.chip.gap{background:#f0938c;color:#5a1410}
.lbl{font-size:10.5px;color:#8a93a0;text-transform:uppercase;letter-spacing:.06em;margin-top:10px;font-weight:700}
.succ{font-size:12px;color:#39414d;margin-top:9px;line-height:1.5}
table.bf{font-size:13px;width:100%;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(20,30,50,.08)}
table.bf td{padding:7px 11px}table.bf th{background:#222a35;color:#fff;padding:8px 11px;text-align:left;font-size:12px;font-weight:600}
.bf td.c{text-align:center}.muted{color:#8a93a0}
.badge{font-size:10px;padding:2px 9px;border-radius:11px;font-weight:700;letter-spacing:.02em}
.badge.critical{background:#e5484d;color:#fff}.badge.watch{background:#f6c66b;color:#5a3c00}.badge.ok{background:#9bd17a;color:#173a08}
tr.bf-critical td{background:#fdf1f1}tr.bf-watch td{background:#fdf9ee}
.note{font-size:12px;color:#4a5462;background:#fff;border-left:3px solid #2f9466;padding:11px 15px;border-radius:8px;margin:13px 0;line-height:1.55;box-shadow:0 1px 3px rgba(20,30,50,.05)}
/* self mode */
.bars{background:#fff;border-radius:12px;padding:8px 20px;box-shadow:0 1px 4px rgba(20,30,50,.08)}
.bar{display:flex;align-items:center;gap:12px;padding:6px 0;border-bottom:1px solid #f1f3f6}
.bar:last-child{border:0}.bar .bl{width:230px;font-size:13px;font-weight:550;flex:none}
.bar .track{flex:1;height:18px;background:#eef0f3;border-radius:9px;overflow:hidden}
.bar .fill{height:100%;border-radius:9px}.bar .lv{width:74px;font-size:11px;font-weight:700;flex:none;text-align:right}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:760px){.two{grid-template-columns:1fr}.bar .bl{width:150px}}
"""

def tooltip(p, d):
    c = matrix[p]["cells"][d]; raw = c.get("raw", {})
    bits = [f"{p} — {labels[d]}: {LVNAME[c['level']]} ({c['level']})"]
    if raw: bits.append(f"authored={int(raw.get('authored_n',0))} reviews_given={int(raw.get('subst_review_given',0))} "
                        f"corrected_others={int(raw.get('corrected_others',0))} was_corrected={int(raw.get('was_corrected',0))} "
                        f"led_design={int(raw.get('led_design',0))}")
    if c.get("override"): bits.append("OVERRIDE: " + c["override"])
    for e in c.get("evidence", [])[:4]: bits.append("• " + e)
    return html.escape(" \n".join(bits))

legend = "".join(f'<span class="lg" style="background:{LVCOL[l]};color:{LVTXT[l]}">{l} {LVNAME[l]}</span>' for l in range(5))
today = cfg.get("today", "")
n_repos = len({r for p in matrix for r in matrix[p]["repos"]})

def build_team():
    rows = []
    gh = ['<th class="rowhdr"></th>'] + [f'<th class="grp" colspan="{len(ds)}">{html.escape(g)}</th>' for g, ds in GROUPS]
    rows.append("<tr>" + "".join(gh) + "</tr>")
    dh = ['<th class="rowhdr">Engineer / Discipline →</th>']
    for _, ds in GROUPS:
        for d in ds: dh.append(f'<th class="disc"><div>{html.escape(labels[d])}</div></th>')
    rows.append("<tr>" + "".join(dh) + "</tr>")
    for p in order_people():
        tds = [f'<th class="person"><div class="pname">{html.escape(p)}</div>'
               f'<div class="prole">{html.escape(derive_role(p))}</div>'
               f'<div class="pmeta">{matrix[p]["total_prs"]} PRs · last {matrix[p]["last_active"]}</div></th>']
        for _, ds in GROUPS:
            for d in ds:
                c = matrix[p]["cells"][d]; lv = c["level"]; star = "<sup>*</sup>" if c.get("override") else ""
                tds.append(f'<td class="lvl" style="background:{LVCOL[lv]};color:{LVTXT[lv]}" '
                           f'title="{tooltip(p,d)}">{lv if lv>0 else ""}{star}</td>')
        rows.append("<tr>" + "".join(tds) + "</tr>")
    bf_rows = []
    for d, b in sorted(busfactor.items(), key=lambda kv: (kv[1]["n_strong"], -kv[1]["pr_count"])):
        risk = "critical" if b["n_strong"] <= 1 else ("watch" if b["n_strong"] == 2 else "ok")
        smes = ", ".join(b["smes"]) or "—"
        other = ", ".join([x for x in b["strong_people"] if x not in b["smes"]]) or "—"
        prc = b["pr_count"]
        bf_rows.append(f"<tr class='bf-{risk}'><td>{html.escape(labels[d])}</td><td class='c'>{b['n_strong']}</td>"
                       f"<td class='c'>{prc}</td><td>{html.escape(smes)}</td><td class='muted'>{html.escape(other)}</td>"
                       f"<td class='c'><span class='badge {risk}'>{risk.upper()}</span></td></tr>")
    cards = []
    for p in order_people():
        c = matrix[p]["cells"]
        core = {d for d, _ in sorted(busfactor.items(), key=lambda kv:-kv[1]["pr_count"])[:8]}
        core_gaps = [labels[d] for d in DISC_IDS if d in core and c[d]["level"] <= 1]
        cs = "".join(f'<span class="chip sme">{html.escape(x)}</span>' for x in strengths(p,4)) or '<span class="muted" style="font-size:11px">— none —</span>'
        cst = "".join(f'<span class="chip strong">{html.escape(x)}</span>' for x in cells_at(p,3)) or '<span class="muted" style="font-size:11px">—</span>'
        cg = "".join(f'<span class="chip gap">{html.escape(x)}</span>' for x in core_gaps[:6]) or '<span class="muted" style="font-size:11px">no core gaps</span>'
        cards.append(f"""<div class="card"><h3>{html.escape(p)}</h3><div class="role">{html.escape(derive_role(p))} ·
          {matrix[p]['total_prs']} PRs · {len(matrix[p]['repos'])} repos · last active {matrix[p]['last_active']}</div>
          <div class="lbl">SME (4)</div><div class="chips">{cs}</div>
          <div class="lbl">Strong (3)</div><div class="chips">{cst}</div>
          <div class="lbl">Gaps in high-traffic areas (≤ novice)</div><div class="chips">{cg}</div></div>""")
    return f"""<h1>{html.escape(cfg.get('title','Engineering Knowledge Matrix'))}</h1>
    <p class="sub">{html.escape(cfg.get('owner',''))} · {len(matrix)} contributors · {n_repos} repos · generated {today} ·
    proficiency from authorship volume, review authority &amp; who-corrects-whom in PR discussion (every comment read)</p>
    <div class="legend"><b style="font-size:12px">Proficiency:</b>{legend}
      <span class="muted" style="font-size:11px">· hover any cell for evidence &amp; PR refs · <sup>*</sup>=evidence override</span></div>
    <div class="matrix-scroll"><table>{''.join(rows)}</table></div>
    <div class="note"><b>How to read this:</b> rows are engineers (ordered by depth + breadth of authority), columns are disciplines.
    Green = teaches/sets patterns here (authority); amber = competent but still guided; red = little/no exposure.
    <b>4 (SME)</b> is the go-to who corrects others and owns the area; <b>1–2</b> marks a development opportunity.</div>
    <h2>Bus-factor &amp; concentration risk</h2>
    <table class="bf"><tr><th>Discipline</th><th>#&nbsp;Strong+</th><th>PRs</th><th>SME (4)</th><th>Other strong (3)</th><th>Risk</th></tr>{''.join(bf_rows)}</table>
    <div class="note"><b>CRITICAL</b>=single strong owner (bus-factor-of-one); <b>WATCH</b>=only two. Some cross-cutting
    disciplines may show a low PR count if they are scored mainly from review/comment authority rather than file paths.</div>
    {build_repo_heatmap()}
    <h2>Per-engineer profiles</h2><div class="cards">{''.join(cards)}</div>"""

def build_repo_heatmap():
    if not REPOS or not repo_matrix: return ""
    repos = sorted(REPOS, key=lambda r: -repo_busfactor.get(r, {}).get("pr_count", 0))
    ordered = order_people()
    head = ['<th class="rowhdr">Engineer / Repository →</th>'] + \
           [f'<th class="disc"><div>{html.escape(r)}</div></th>' for r in repos]
    rows = ["<tr>" + "".join(head) + "</tr>"]
    for p in ordered:
        tds = [f'<th class="person"><div class="pname">{html.escape(p)}</div>'
               f'<div class="pmeta">{matrix[p]["total_prs"]} PRs · {len(matrix[p]["repos"])} repos</div></th>']
        for r in repos:
            c = repo_matrix.get(p, {}).get(r, {"level": 0}); lv = c["level"]
            raw = c.get("raw", {})
            tip = html.escape(f"{p} — {r}: {LVNAME[lv]} ({lv}) | authored={int(raw.get('authored_n',0))} "
                              f"reviews_given={int(raw.get('subst_review_given',0))} corrected_given={int(raw.get('corrected_given',0))} "
                              f"corrected_received={int(raw.get('corrected_received',0))}")
            tds.append(f'<td class="lvl" style="background:{LVCOL[lv]};color:{LVTXT[lv]}" title="{tip}">{lv if lv>0 else ""}</td>')
        rows.append("<tr>" + "".join(tds) + "</tr>")
    bf = []
    for r in repos:
        b = repo_busfactor.get(r, {}); risk = "critical" if b.get("n_strong",0) <= 1 else ("watch" if b.get("n_strong",0)==2 else "ok")
        smes = ", ".join(b.get("smes",[])) or "—"
        other = ", ".join([x for x in b.get("strong_people",[]) if x not in b.get("smes",[])]) or "—"
        bf.append(f"<tr class='bf-{risk}'><td>{html.escape(r)}</td><td class='c'>{b.get('n_strong',0)}</td>"
                  f"<td class='c'>{b.get('pr_count',0)}</td><td>{html.escape(smes)}</td><td class='muted'>{html.escape(other)}</td>"
                  f"<td class='c'><span class='badge {risk}'>{risk.upper()}</span></td></tr>")
    return (f"""<h2>Proficiency by repository</h2>
    <div class="note">Who leads vs who is still learning <b>in each repository</b> — use this to see who can safely
    own or be moved onto a repo. Same 0–4 scale, scored per repo. Hover for the signals.</div>
    <div class="matrix-scroll"><table>{''.join(rows)}</table></div>
    <h2>Repository ownership risk</h2>
    <table class="bf"><tr><th>Repository</th><th>#&nbsp;Strong+</th><th>PRs</th><th>Owner(s) — SME</th><th>Other strong</th><th>Risk</th></tr>{''.join(bf)}</table>""")

def build_self():
    c = matrix[ME]["cells"]
    bars = []
    for _, ds in GROUPS:
        for d in ds:
            lv = c[d]["level"]; pct = int(lv/4*100)
            bars.append(f'<div class="bar"><div class="bl">{html.escape(labels[d])}</div>'
                        f'<div class="track"><div class="fill" style="width:{max(pct,3)}%;background:{LVCOL[lv]}"></div></div>'
                        f'<div class="lv" style="color:{LVTXT[lv] if lv>=3 else "#39414d"}">{LVNAME[lv]} ({lv})</div></div>')
    def panel(items, kind):
        if not items: return '<span class="muted" style="font-size:12px">— none —</span>'
        out = []
        for it in items:
            ev = (it.get("evidence") or [""])[0]
            extra = f" · corrected {it['corrected_received']}×" if kind=="gap" and it.get("corrected_received") else ""
            out.append(f'<div style="margin:7px 0"><span class="chip {"strong" if kind=="str" else "gap"}">{html.escape(it["label"])} '
                       f'(L{it["level"]}){extra}</span>'
                       + (f'<div style="font-size:11.5px;color:#5f6b7a;margin-top:2px">{html.escape(ev)}</div>' if ev else "") + '</div>')
        return "".join(out)
    # per-repo bars for the caller
    rbars = []
    rm = repo_matrix.get(ME, {})
    for r in sorted(REPOS, key=lambda r: -rm.get(r, {}).get("authority", 0)):
        c2 = rm.get(r, {"level": 0}); lv = c2["level"]
        if lv == 0 and not c2.get("raw"): continue
        rbars.append(f'<div class="bar"><div class="bl">{html.escape(r)}</div>'
                     f'<div class="track"><div class="fill" style="width:{max(int(lv/4*100),3)}%;background:{LVCOL[lv]}"></div></div>'
                     f'<div class="lv" style="color:{LVTXT[lv] if lv>=3 else "#39414d"}">{LVNAME[lv]} ({lv})</div></div>')
    repo_section = (f'<h2>Proficiency by repository</h2><div class="bars">{"".join(rbars)}</div>' if rbars else "")
    sr = selfreport or {"strengths":[],"gaps":[],"untouched":[]}
    untouched = ", ".join(sr["untouched"]) or "—"
    return f"""<h1>Your Knowledge Profile — {html.escape(ME)}</h1>
    <p class="sub">{html.escape(cfg.get('owner',''))} · personal gap analysis from your authored PRs and the reviews on them ·
    generated {today}. Levels are absolute (not ranked against teammates).</p>
    <div class="legend"><b style="font-size:12px">Proficiency:</b>{legend}</div>
    <h2>Proficiency by discipline</h2><div class="bars">{''.join(bars)}</div>
    {repo_section}
    <h2>Strengths &amp; development areas</h2>
    <div class="two">
      <div class="card"><div class="lbl">Your strengths (where you lead / review others)</div>{panel(sr["strengths"],"str")}</div>
      <div class="card"><div class="lbl">Development areas (low level / most corrected)</div>{panel(sr["gaps"],"gap")}</div>
    </div>
    <div class="note"><b>Untouched disciplines</b> (no PR footprint): {html.escape(untouched)}.
    These are whitespace — opportunities to broaden if they matter to your role.</div>"""

body = build_self() if (MODE == "self" and ME in matrix) else build_team()
doc = f"""<!doctype html><html lang="en-AU"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(cfg.get('title','Knowledge Matrix'))}</title><style>{CSS}</style></head>
<body><div class="wrap">{body}</div></body></html>"""
open(os.path.join(WORK, "knowledge-matrix.html"), "w").write(doc)
print("knowledge-matrix.html written ("+("self" if (MODE=='self' and ME in matrix) else "team")+" mode)")
