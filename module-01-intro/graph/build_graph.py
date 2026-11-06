"""
Build a relationship graph between vocabulary terms and their usage in the research report.

For every term from ../vocabulary.md the script counts, per report section:
  * explicit mentions - the term itself or its direct forms (plural, abbreviation, full name);
  * implicit mentions - phrases that refer to the same concept without naming it
    (synonyms, descriptions, concrete examples).

Explicit matches are found first and masked, so a phrase is never counted twice.
URLs are removed before counting so that links do not inflate the numbers.

Outputs (written next to this script):
  terms_stats.json       - all counts and the patterns used
  relations_graph.png    - static graph + explicit/implicit bar chart
  relations_graph.html   - self-contained interactive version (open in a browser)
  README.md              - summary table

Usage:
  pip install matplotlib
  python build_graph.py
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent / "research-report.md"
VOCABULARY = HERE.parent / "vocabulary.md"

# term -> (explicit patterns, implicit patterns); all case-insensitive regexes
TERMS = {
    "LLM": (
        [r"\bLLMs?\b", r"\blarge language models?\b", r"\blanguage models?\b"],
        [r"\bmodels?\b"],
    ),
    "Attention mechanism": (
        [r"\battention mechanism\b", r"\battention\b"],
        [r"\bmost relevant\b", r"\brelevant chunks\b"],
    ),
    "Next-token prediction": (
        [r"\bnext-token prediction\b"],
        [r"\bpredict\w*", r"\bstatistically continues\b", r"\bcontinues? a sequence\b"],
    ),
    "Context window": (
        [r"\bcontext windows?\b"],
        [r"\bcontext\b", r"\bshort-term memory\b", r"\bfits? into\b"],
    ),
    "Prompt": (
        [r"\bprompts?\b"],
        [r"\binstructions?\b", r"\bquestions?\b"],
    ),
    "AI agent": (
        [r"\bAI agents?\b", r"\bsub-agents?\b", r"\bagents?\b"],
        [r"\bautonomous(?:ly)?\b", r"\bdelegat\w*"],
    ),
    "Agentic platform": (
        [r"\bagentic platforms?\b"],
        [r"\borchestrat\w*", r"\bmulti-agent\b"],
    ),
    "Copilot": (
        [r"\bcopilots?\b"],
        [r"\bplugin\b", r"\bcompanion\b", r"\bIDE extension\b", r"\binside an IDE\b", r"\bexisting IDE\b"],
    ),
    "AI-native IDE": (
        [r"\bAI-native IDEs?\b", r"\bAI-native\b"],
        [r"\bcode editor\b", r"\bCursor\b", r"\bWindsurf\b", r"\bDevin Desktop\b"],
    ),
    "Vibe coding": (
        [r"\bvibe coding\b"],
        [r"\bnatural[- ]language\b"],
    ),
    "Prompt injection": (
        [r"\bprompt injection\b"],
        [r"\bhidden commands\b", r"\bmalicious instructions\b", r"\buntrusted input\b"],
    ),
    "Hallucination": (
        [r"\bhallucinat\w*"],
        [r"\bconvincing\b", r"\bconfident but wrong\b", r"\bfluent answer\b",
         r"\bwrong conclusions\b", r"\bgarble\w*", r"\bcompiles but breaks\b"],
    ),
}

SECTION_LABELS = {
    "Introduction": "Introduction",
    "1. AI coding assistants": "1 Coding assistants",
    "2. AI-assisted test generation": "2 Test generation",
    "3. Log analysis, debugging and incident investigation": "3 Logs & debugging",
    "4. RAG over internal knowledge and data": "4 RAG",
    "5. Agentic SDLC: from ticket to pull request": "5 Agentic SDLC",
    "6. Small and local LLMs": "6 Small & local LLMs",
    "7. Multimodal document and speech processing": "7 Multimodal",
    "Summary": "Summary",
}

# Palette: categorical slots 1-2 of the validated reference palette (light mode)
EXPLICIT_COLOR = "#2a78d6"
IMPLICIT_COLOR = "#eb6834"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
SURFACE = "#fcfcfb"
GRID = "#e4e3df"


def check_vocabulary_terms():
    """Make sure every configured term really exists in vocabulary.md."""
    headings = re.findall(r"^### (.+)$", VOCABULARY.read_text(encoding="utf-8"), re.M)
    names = {h.split(" (")[0].strip().lower() for h in headings}
    missing = [t for t in TERMS if t.lower() not in names]
    if missing:
        raise SystemExit(f"Terms not found in vocabulary.md: {missing}")


def split_sections(text):
    """Split the report by '## ' headings and keep only the sections we chart."""
    sections = {}
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        if title in SECTION_LABELS:
            body = re.sub(r"\(https?://[^)]*\)", "", parts[i + 1])  # drop link targets
            sections[SECTION_LABELS[title]] = title + "\n" + body
    return sections


def count_and_mask(text, patterns):
    """Count matches of all patterns, longest pattern first, masking each match."""
    total = 0
    for pat in sorted(patterns, key=len, reverse=True):
        regex = re.compile(pat, re.I)
        total += len(regex.findall(text))
        text = regex.sub(lambda m: "█" * len(m.group(0)), text)
    return total, text


def compute_stats():
    sections = split_sections(REPORT.read_text(encoding="utf-8"))
    # longer/more specific terms are matched first (e.g. "prompt injection" before "prompt")
    order = sorted(TERMS, key=lambda t: max(len(p) for p in TERMS[t][0]), reverse=True)

    stats = {t: {s: {"explicit": 0, "implicit": 0} for s in sections} for t in TERMS}
    for section, text in sections.items():
        masked = text
        for term in order:  # pass 1: explicit
            n, masked = count_and_mask(masked, TERMS[term][0])
            stats[term][section]["explicit"] = n
        for term in order:  # pass 2: implicit on what is left
            n, masked = count_and_mask(masked, TERMS[term][1])
            stats[term][section]["implicit"] = n

    terms = []
    for term in TERMS:
        by_section = stats[term]
        terms.append({
            "term": term,
            "explicit_total": sum(v["explicit"] for v in by_section.values()),
            "implicit_total": sum(v["implicit"] for v in by_section.values()),
            "sections_used": sum(1 for v in by_section.values() if v["explicit"] + v["implicit"]),
            "by_section": by_section,
            "explicit_patterns": TERMS[term][0],
            "implicit_patterns": TERMS[term][1],
        })
    return list(sections), terms


def draw_png(sections, terms, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig = plt.figure(figsize=(16, 9), facecolor=SURFACE)
    ax = fig.add_axes([0.02, 0.06, 0.56, 0.84], facecolor=SURFACE)
    bx = fig.add_axes([0.70, 0.08, 0.28, 0.80], facecolor=SURFACE)

    # --- left: bipartite graph (terms -> report sections) ---
    n_t, n_s = len(terms), len(sections)
    ty = {t["term"]: 1 - i / (n_t - 1) for i, t in enumerate(terms)}
    sy = {s: 1 - i / (n_s - 1) for i, s in enumerate(sections)}
    xt, xs = 0.0, 1.0
    max_w = max(max(v["explicit"], v["implicit"]) for t in terms for v in t["by_section"].values())

    for t in terms:
        for s, v in t["by_section"].items():
            for kind, color, style, off in (("explicit", EXPLICIT_COLOR, "-", -0.004),
                                            ("implicit", IMPLICIT_COLOR, "--", 0.004)):
                if v[kind]:
                    ax.plot([xt + 0.02, xs - 0.02], [ty[t["term"]] + off, sy[s] + off],
                            color=color, linestyle=style, alpha=0.55,
                            linewidth=0.6 + 3.4 * v[kind] / max_w, solid_capstyle="round")

    max_total = max(t["explicit_total"] + t["implicit_total"] for t in terms)
    for t in terms:
        total = t["explicit_total"] + t["implicit_total"]
        ax.scatter([xt], [ty[t["term"]]], s=60 + 540 * total / max_total, color=TEXT_PRIMARY,
                   edgecolors=SURFACE, linewidths=2, zorder=3)
        ax.text(xt - 0.09, ty[t["term"]], f'{t["term"]}  ({t["explicit_total"]} / {t["implicit_total"]})',
                ha="right", va="center", color=TEXT_PRIMARY, fontsize=10)
    for s in sections:
        ax.scatter([xs], [sy[s]], s=140, marker="s", color=TEXT_SECONDARY,
                   edgecolors=SURFACE, linewidths=2, zorder=3)
        ax.text(xs + 0.04, sy[s], s, ha="left", va="center", color=TEXT_PRIMARY, fontsize=10)

    ax.text(xt - 0.05, 1.07, "Vocabulary term  (explicit / implicit)", ha="right", color=TEXT_SECONDARY, fontsize=10)
    ax.text(xs, 1.07, "Report section", ha="left", color=TEXT_SECONDARY, fontsize=10)
    ax.plot([], [], color=EXPLICIT_COLOR, linewidth=2.5, label="Explicit mention")
    ax.plot([], [], color=IMPLICIT_COLOR, linewidth=2.5, linestyle="--", label="Implicit mention")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.04), ncol=2, frameon=False,
              labelcolor=TEXT_PRIMARY)
    ax.set_xlim(-0.95, 1.55)
    ax.set_ylim(-0.12, 1.1)
    ax.axis("off")

    # --- right: explicit vs implicit totals per term (sorted by total) ---
    ordered = sorted(terms, key=lambda t: t["explicit_total"] + t["implicit_total"])
    y = range(len(ordered))
    h = 0.38
    bx.barh([i + h / 2 + 0.02 for i in y], [t["explicit_total"] for t in ordered], height=h,
            color=EXPLICIT_COLOR, label="Explicit")
    bx.barh([i - h / 2 - 0.02 for i in y], [t["implicit_total"] for t in ordered], height=h,
            color=IMPLICIT_COLOR, label="Implicit")
    for i, t in enumerate(ordered):
        bx.text(t["explicit_total"] + 0.4, i + h / 2 + 0.02, str(t["explicit_total"]),
                va="center", fontsize=8, color=TEXT_SECONDARY)
        bx.text(t["implicit_total"] + 0.4, i - h / 2 - 0.02, str(t["implicit_total"]),
                va="center", fontsize=8, color=TEXT_SECONDARY)
    bx.set_yticks(list(y), [t["term"] for t in ordered], color=TEXT_PRIMARY)
    bx.tick_params(axis="both", length=0, colors=TEXT_SECONDARY)
    bx.xaxis.grid(True, color=GRID, linewidth=0.8)
    bx.set_axisbelow(True)
    for side in ("top", "right", "left"):
        bx.spines[side].set_visible(False)
    bx.spines["bottom"].set_color(GRID)
    bx.set_xlabel("Mentions in the report", color=TEXT_SECONDARY)
    bx.set_title("Explicit vs implicit usage", loc="left", color=TEXT_PRIMARY, fontsize=12)
    bx.legend(loc="lower right", frameon=False, labelcolor=TEXT_PRIMARY)

    fig.suptitle("Vocabulary terms and their usage in the research report",
                 x=0.02, ha="left", fontsize=15, color=TEXT_PRIMARY)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vocabulary terms and their usage in the report</title>
<style>
.viz-root {
  color-scheme: light;
  --surface-1: #fcfcfb; --text-primary: #0b0b0b; --text-secondary: #52514e;
  --grid: #e4e3df; --explicit: #2a78d6; --implicit: #eb6834; --node: #0b0b0b; --section: #52514e;
}
@media (prefers-color-scheme: dark) {
  .viz-root {
    color-scheme: dark;
    --surface-1: #1a1a19; --text-primary: #f0efec; --text-secondary: #c3c2b7;
    --grid: #3a3936; --explicit: #3987e5; --implicit: #d95926; --node: #f0efec; --section: #c3c2b7;
  }
}
body { margin: 0; }
.viz-root { background: var(--surface-1); color: var(--text-primary);
  font: 14px/1.4 system-ui, -apple-system, "Segoe UI", sans-serif; padding: 24px; min-height: 100vh; box-sizing: border-box; }
h1 { font-size: 20px; margin: 0 0 4px; }
.sub { color: var(--text-secondary); margin: 0 0 16px; }
.controls { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.controls button { font: inherit; padding: 6px 12px; border-radius: 8px; cursor: pointer;
  border: 1px solid var(--grid); background: transparent; color: var(--text-primary); }
.controls button[aria-pressed="true"] { border-color: var(--text-primary); font-weight: 600; }
.legend { display: flex; gap: 16px; color: var(--text-secondary); margin-bottom: 8px; align-items: center; }
.legend i { display: inline-block; width: 22px; height: 0; border-top: 3px solid; vertical-align: middle; margin-right: 6px; }
svg { width: 100%; max-width: 1000px; height: auto; display: block; }
svg text { fill: var(--text-primary); font-size: 13px; }
svg .muted { fill: var(--text-secondary); }
.edge { fill: none; stroke-linecap: round; opacity: .55; transition: opacity .15s; }
.edge.explicit { stroke: var(--explicit); }
.edge.implicit { stroke: var(--implicit); stroke-dasharray: 6 4; }
.dim .edge { opacity: .06; }
.dim .edge.on { opacity: .9; }
.dim .node:not(.on) { opacity: .3; }
.hit { fill: transparent; cursor: pointer; }
#tip { position: fixed; pointer-events: none; background: var(--surface-1); color: var(--text-primary);
  border: 1px solid var(--grid); border-radius: 8px; padding: 8px 10px; font-size: 13px;
  box-shadow: 0 4px 16px rgba(0,0,0,.12); display: none; max-width: 280px; }
#tip b { display: block; margin-bottom: 4px; }
#tip .sw { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px; }
table { border-collapse: collapse; margin-top: 16px; font-size: 13px; }
th, td { padding: 4px 10px; border-bottom: 1px solid var(--grid); text-align: right; }
th:first-child, td:first-child { text-align: left; }
th { color: var(--text-secondary); font-weight: 600; }
details summary { cursor: pointer; color: var(--text-secondary); margin-top: 16px; }
</style>
</head>
<body>
<div class="viz-root">
  <h1>Vocabulary terms and their usage in the research report</h1>
  <p class="sub">Each line links a term to a report section where it is used. Line width shows the number of mentions.
  Hover a term or a section to highlight its links.</p>
  <div class="controls" role="group" aria-label="Mention type">
    <button data-mode="both" aria-pressed="true">Explicit + implicit</button>
    <button data-mode="explicit" aria-pressed="false">Explicit only</button>
    <button data-mode="implicit" aria-pressed="false">Implicit only</button>
  </div>
  <div class="legend">
    <span><i style="border-color: var(--explicit)"></i>Explicit mention</span>
    <span><i style="border-color: var(--implicit); border-top-style: dashed"></i>Implicit mention</span>
    <span>Term label: (explicit / implicit)</span>
  </div>
  <svg id="graph" role="img" aria-label="Relationship graph between vocabulary terms and report sections"></svg>
  <details open>
    <summary>Table view</summary>
    <table id="table"></table>
  </details>
  <div id="tip"></div>
</div>
<script>
(() => {
const DATA = __DATA__;
const svg = document.getElementById('graph');
const NS = 'http://www.w3.org/2000/svg';
const W = 1000, rowT = 44, top = 50;
const H = top + Math.max(DATA.terms.length, DATA.sections.length) * rowT + 10;
svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
const xT = 330, xS = 700;
const yT = i => top + i * (rowT * (Math.max(DATA.terms.length, DATA.sections.length) - 1) / (DATA.terms.length - 1));
const yS = i => top + i * (rowT * (Math.max(DATA.terms.length, DATA.sections.length) - 1) / (DATA.sections.length - 1));
const el = (tag, attrs, parent = svg) => { const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; };
const maxW = Math.max(...DATA.terms.flatMap(t => Object.values(t.by_section).flatMap(v => [v.explicit, v.implicit])));
const maxTot = Math.max(...DATA.terms.map(t => t.explicit_total + t.implicit_total));
const tip = document.getElementById('tip');

el('text', {x: xT, y: 20, 'text-anchor': 'end', class: 'muted'}).textContent = 'Vocabulary term';
el('text', {x: xS, y: 20, class: 'muted'}).textContent = 'Report section';

const edges = el('g', {});
DATA.terms.forEach((t, i) => {
  DATA.sections.forEach((s, j) => {
    const v = t.by_section[s];
    [['explicit', -2], ['implicit', 2]].forEach(([kind, off]) => {
      if (!v[kind]) return;
      const y1 = yT(i) + off, y2 = yS(j) + off, mx = (xT + xS) / 2;
      el('path', {d: `M${xT + 12},${y1} C${mx},${y1} ${mx},${y2} ${xS - 12},${y2}`,
        class: `edge ${kind}`, 'stroke-width': 1 + 4 * v[kind] / maxW,
        'data-term': t.term, 'data-section': s}, edges);
    });
  });
});

function show(evt, html) { tip.innerHTML = html; tip.style.display = 'block';
  tip.style.left = Math.min(evt.clientX + 14, innerWidth - 300) + 'px'; tip.style.top = (evt.clientY + 14) + 'px'; }
function hide() { tip.style.display = 'none'; svg.classList.remove('dim');
  svg.querySelectorAll('.on').forEach(e => e.classList.remove('on')); }
function focus(attr, value) { svg.classList.add('dim');
  svg.querySelectorAll(`.edge[data-${attr}="${CSS.escape(value)}"]`).forEach(e => { e.classList.add('on');
    svg.querySelectorAll(`.node[data-key="${CSS.escape(attr === 'term' ? e.dataset.section : e.dataset.term)}"]`).forEach(n => n.classList.add('on')); });
  svg.querySelectorAll(`.node[data-key="${CSS.escape(value)}"]`).forEach(n => n.classList.add('on')); }
const sw = c => `<span class="sw" style="background:var(--${c})"></span>`;

DATA.terms.forEach((t, i) => {
  const g = el('g', {class: 'node', 'data-key': t.term});
  const r = 5 + 9 * Math.sqrt((t.explicit_total + t.implicit_total) / maxTot);
  el('circle', {cx: xT, cy: yT(i), r, fill: 'var(--node)', stroke: 'var(--surface-1)', 'stroke-width': 2}, g);
  el('text', {x: xT - r - 8, y: yT(i) + 4, 'text-anchor': 'end'}, g).textContent =
    `${t.term}  (${t.explicit_total} / ${t.implicit_total})`;
  const hit = el('rect', {x: 0, y: yT(i) - rowT / 2, width: xT + 20, height: rowT, class: 'hit'}, g);
  hit.addEventListener('mousemove', e => { focus('term', t.term);
    const rows = DATA.sections.filter(s => t.by_section[s].explicit + t.by_section[s].implicit)
      .map(s => `${s}: ${t.by_section[s].explicit} / ${t.by_section[s].implicit}`).join('<br>') || 'not used';
    show(e, `<b>${t.term}</b>${sw('explicit')}Explicit: ${t.explicit_total}<br>${sw('implicit')}Implicit: ${t.implicit_total}<br><br>${rows}`); });
  hit.addEventListener('mouseleave', hide);
});
DATA.sections.forEach((s, j) => {
  const g = el('g', {class: 'node', 'data-key': s});
  el('rect', {x: xS - 6, y: yS(j) - 6, width: 12, height: 12, rx: 2, fill: 'var(--section)'}, g);
  el('text', {x: xS + 14, y: yS(j) + 4}, g).textContent = s;
  const hit = el('rect', {x: xS - 20, y: yS(j) - rowT / 2, width: W - xS + 20, height: rowT, class: 'hit'}, g);
  hit.addEventListener('mousemove', e => { focus('section', s);
    const rows = DATA.terms.filter(t => t.by_section[s].explicit + t.by_section[s].implicit)
      .map(t => `${t.term}: ${t.by_section[s].explicit} / ${t.by_section[s].implicit}`).join('<br>');
    show(e, `<b>${s}</b>term: explicit / implicit<br>${rows}`); });
  hit.addEventListener('mouseleave', hide);
});

document.querySelectorAll('.controls button').forEach(b => b.addEventListener('click', () => {
  document.querySelectorAll('.controls button').forEach(x => x.setAttribute('aria-pressed', x === b));
  const m = b.dataset.mode;
  svg.querySelectorAll('.edge.explicit').forEach(e => e.style.display = m === 'implicit' ? 'none' : '');
  svg.querySelectorAll('.edge.implicit').forEach(e => e.style.display = m === 'explicit' ? 'none' : '');
}));

const table = document.getElementById('table');
table.innerHTML = '<tr><th>Term</th><th>Explicit</th><th>Implicit</th><th>Sections used</th></tr>' +
  DATA.terms.map(t => `<tr><td>${t.term}</td><td>${t.explicit_total}</td><td>${t.implicit_total}</td><td>${t.sections_used} / ${DATA.sections.length}</td></tr>`).join('');
})();
</script>
</body>
</html>
"""


def write_readme(sections, terms, path):
    rows = "\n".join(
        f'| {t["term"]} | {t["explicit_total"]} | {t["implicit_total"]} | {t["sections_used"]} / {len(sections)} |'
        for t in sorted(terms, key=lambda t: -(t["explicit_total"] + t["implicit_total"]))
    )
    path.write_text(f"""# Relationship graph: vocabulary terms vs. report usage

Optional subtask of Module 1. The graph links every term from [vocabulary.md](../vocabulary.md)
to the sections of [research-report.md](../research-report.md) where it is used.

![Relationship graph](relations_graph.png)

Interactive version: download [relations_graph.html](relations_graph.html) and open it in a browser
(hover terms and sections, switch explicit / implicit, table view).

## How mentions are counted

- **Explicit** — the term itself or its direct forms (plural, abbreviation, full name), e.g. `LLM`, `LLMs`, `large language model`.
- **Implicit** — phrases that refer to the concept without naming it: synonyms, descriptions or concrete examples,
  e.g. `model` for *LLM*, `Cursor` for *AI-native IDE*, `natural language` for *vibe coding*.
- Explicit matches are counted first and masked, so one phrase is never counted twice.
  More specific terms are matched first (e.g. *prompt injection* before *prompt*). Link URLs are ignored.
- All patterns are listed in [terms_stats.json](terms_stats.json) and in [build_graph.py](build_graph.py).

## Results

| Term | Explicit | Implicit | Sections used |
|------|---------:|---------:|--------------:|
{rows}

## Rebuild

```bash
pip install matplotlib
python build_graph.py
```
""", encoding="utf-8")


def main():
    check_vocabulary_terms()
    sections, terms = compute_stats()
    payload = {
        "source": {"report": "../research-report.md", "vocabulary": "../vocabulary.md"},
        "method": "Explicit = the term or its direct forms; implicit = synonyms, descriptions or examples "
                  "of the concept. Explicit matches are masked before implicit counting.",
        "sections": sections,
        "terms": terms,
    }
    (HERE / "terms_stats.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    draw_png(sections, terms, HERE / "relations_graph.png")
    (HERE / "relations_graph.html").write_text(
        HTML_TEMPLATE.replace("__DATA__", json.dumps(payload, ensure_ascii=False)), encoding="utf-8")
    write_readme(sections, terms, HERE / "README.md")
    for t in terms:
        print(f'{t["term"]:<24} explicit={t["explicit_total"]:>3}  implicit={t["implicit_total"]:>3}')


if __name__ == "__main__":
    main()
