"""
NIVEDH — THE SERIES · GitHub profile artwork generator.

Static art (title sequence, original posters, end credits) is written to assets/.
Live art (contribution reel, "continue watching" card) is written to dist/ and is
regenerated every day by .github/workflows/series.yml.

Usage:
  python scripts/generate.py static                 # rebuild assets/
  python scripts/generate.py live                   # needs GITHUB_TOKEN, writes dist/
  python scripts/generate.py live --sample          # offline preview with fake data
Only the Python standard library is used.
"""

import base64
import json
import os
import random
import re
import sys
import urllib.request
from datetime import date, timedelta
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGIN = "NivedhReddy2048"
PROGRESS_URL = "https://raw.githubusercontent.com/NivedhReddy2048/CodeSage/main/docs/PROGRESS.md"

INK = "#07070a"
BONE = "#f4f1ec"
MIST = "#a7a6ad"
SMOKE = "#6d6c74"
RED = "#ff3d5a"
CRIMSON = "#e5132b"


# ---------------------------------------------------------------- helpers
def font_css(*names):
    faces = {
        "bebas": ("Bebas", "bebas.woff2", 400),
        "inter": ("InterX", "inter.woff2", 500),
        "inter-bold": ("InterX", "inter-bold.woff2", 700),
    }
    out = []
    for n in names:
        fam, file, weight = faces[n]
        b64 = base64.b64encode((ROOT / "fonts" / file).read_bytes()).decode()
        out.append(
            f"@font-face{{font-family:'{fam}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    out.append(".d{font-family:'Bebas',Impact,'Arial Narrow',sans-serif;}")
    out.append(".s{font-family:'InterX','Segoe UI',Helvetica,Arial,sans-serif;}")
    return "".join(out)


def mark(cx, cy, r, color=None):
    """Nivedh's own studio mark: a ring with a play triangle (deliberately not a letter logo)."""
    c = color or RED
    h = r * .55
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c}" stroke-width="{max(1.5, r / 9):.1f}"/>'
            f'<path d="M{cx - h * .55:.1f} {cy - h:.1f} L{cx + h:.1f} {cy} L{cx - h * .55:.1f} {cy + h:.1f} Z" fill="{c}"/>')


def t(s):
    return escape(s, quote=False)


def write(path, svg):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}  ({len(svg) // 1024} KB)")


# ---------------------------------------------------------------- title sequence
def title_sequence():
    W, H = 1000, 380
    particles = []
    rnd = random.Random(7)
    for i in range(26):
        x = rnd.randint(40, W - 40)
        y = rnd.randint(120, H - 30)
        r = rnd.choice([1, 1.2, 1.6, 2])
        dur = rnd.uniform(6, 11)
        delay = -rnd.uniform(0, 10)
        particles.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{RED}" class="p" '
            f'style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"/>'
        )
    css = f"""
{font_css('bebas', 'inter', 'inter-bold')}
.seq{{animation:seq 14s infinite;}}
.studio{{animation:studio 14s infinite;opacity:0}}
.name{{animation:name 14s infinite cubic-bezier(.2,.7,.2,1);opacity:0;transform-box:fill-box;transform-origin:center}}
.series{{animation:series 14s infinite;opacity:0}}
.tag{{animation:tag 14s infinite;opacity:0}}
.play{{animation:play 14s infinite;opacity:0}}
.ring{{animation:ring 1.8s infinite;transform-box:fill-box;transform-origin:center}}
.p{{animation-name:rise;animation-iteration-count:infinite;animation-timing-function:linear;opacity:0}}
.streak{{animation:streak 7s infinite linear}}
.streak2{{animation:streak 9s infinite linear;animation-delay:-4s}}
.glow{{animation:glow 14s infinite}}
@keyframes seq{{0%,94%{{opacity:1}}99%{{opacity:0}}100%{{opacity:1}}}}
@keyframes studio{{0%{{opacity:0;letter-spacing:6px}}6%,13%{{opacity:1}}18%,100%{{opacity:0;letter-spacing:14px}}}}
@keyframes name{{0%,17%{{opacity:0;transform:scale(1.35);filter:blur(14px)}}26%{{opacity:1;transform:scale(1);filter:blur(0)}}90%{{opacity:1;transform:scale(.98)}}96%,100%{{opacity:0;transform:scale(.96)}}}}
@keyframes series{{0%,27%{{opacity:0;letter-spacing:4px}}33%,90%{{opacity:1;letter-spacing:18px}}96%,100%{{opacity:0}}}}
@keyframes tag{{0%,35%{{opacity:0;transform:translateY(10px)}}41%,90%{{opacity:1;transform:translateY(0)}}96%,100%{{opacity:0}}}}
@keyframes play{{0%,42%{{opacity:0}}48%,90%{{opacity:1}}96%,100%{{opacity:0}}}}
@keyframes ring{{0%{{transform:scale(1);opacity:.7}}100%{{transform:scale(1.45);opacity:0}}}}
@keyframes rise{{0%{{opacity:0;transform:translateY(0)}}20%{{opacity:.7}}100%{{opacity:0;transform:translateY(-120px)}}}}
@keyframes streak{{0%{{transform:translateX(-700px)}}100%{{transform:translateX(1300px)}}}}
@keyframes glow{{0%,17%{{opacity:.15}}30%,90%{{opacity:.9}}100%{{opacity:.15}}}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Nivedh — The Series">
<title>Nivedh — The Series</title>
<style>{css}</style>
<defs>
  <radialGradient id="rg" cx="50%" cy="48%" r="55%"><stop offset="0" stop-color="{CRIMSON}" stop-opacity=".55"/><stop offset=".55" stop-color="#6e0d1d" stop-opacity=".25"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>
  <linearGradient id="st" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="shine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <clipPath id="nameclip"><text x="500" y="235" text-anchor="middle" class="d" font-size="168" letter-spacing="6">NIVEDH</text></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  <ellipse cx="500" cy="190" rx="520" ry="230" fill="url(#rg)" class="glow"/>
  <g transform="rotate(-18 500 190)" opacity=".8">
    <rect class="streak" x="0" y="120" width="420" height="2" fill="url(#st)"/>
    <rect class="streak2" x="0" y="260" width="560" height="1.5" fill="url(#st)"/>
  </g>
  {''.join(particles)}
  <g class="seq">
    <g class="studio">
      {mark(500, 146, 24)}
      <text x="500" y="208" text-anchor="middle" class="s" font-weight="700" font-size="15" fill="{MIST}" letter-spacing="10">A PINGILI ORIGINAL</text>
    </g>
    <g class="name">
      <text x="500" y="235" text-anchor="middle" class="d" font-size="168" letter-spacing="6" fill="{BONE}">NIVEDH</text>
      <g clip-path="url(#nameclip)"><rect x="-300" y="80" width="220" height="200" fill="url(#shine)" transform="skewX(-20)">
        <animateTransform attributeName="transform" type="translate" values="0 0;0 0;1500 0;1500 0" keyTimes="0;.3;.45;1" dur="14s" repeatCount="indefinite" additive="sum"/>
      </rect></g>
    </g>
    <text class="series s" x="500" y="275" text-anchor="middle" font-weight="700" font-size="17" fill="{RED}" letter-spacing="18">THE SERIES</text>
    <text class="tag s" x="500" y="312" text-anchor="middle" font-size="15" fill="{MIST}" letter-spacing="4">PYTHON &amp; DJANGO  •  GENAI / RAG  •  DATA ENGINEERING</text>
    <g class="play">
      <circle cx="500" cy="345" r="15" fill="none" stroke="{RED}" stroke-width="2" class="ring"/>
      <circle cx="500" cy="345" r="15" fill="{BONE}"/>
      <path d="M495 337 L507 345 L495 353 Z" fill="{INK}"/>
    </g>
  </g>
  <rect width="{W}" height="14" fill="#000"/><rect y="{H - 14}" width="{W}" height="14" fill="#000"/>
</g>
</svg>"""


# ---------------------------------------------------------------- posters
PALETTES = {
    "violet": ("#120822", "#3d1a6e", "#07060c", "#b98bff"),
    "jade": ("#03150f", "#0d5a40", "#050a08", "#46e3a8"),
    "crimson": ("#24060b", "#6e0d1d", "#09070a", "#ff3d5a"),
    "amber": ("#1c1003", "#6b3c06", "#0a0806", "#ffb547"),
    "ocean": ("#04121f", "#0f4c6e", "#05080d", "#4cc9ff"),
    "rust": ("#1a0d02", "#8a4a07", "#0a0806", "#ffb547"),
}

POSTERS = [
    dict(id="ekip", title=["EKIP"], genre="GENAI • MULTI-AGENT • RAG", year="2026", pal="violet", motif="flow",
         line=["12-node LangGraph pipeline,", "9 agents, cited answers."], live=True),
    dict(id="carebridge", title=["CAREBRIDGE"], genre="FULL-STACK • HEALTHTECH", year="2026", pal="jade", motif="shield",
         line=["Telemedicine, records, billing", "and AI insights — on Django."], live=True),
    dict(id="doc-intel", title=["DOCUMENT", "INTELLIGENCE"], genre="GENAI • HYBRID RAG", year="2026", pal="crimson", motif="shield",
         line=["BM25 + dense retrieval,", "re-ranked and cited."], live=True),
    dict(id="fraud", title=["REAL-TIME", "FRAUD DETECTION"], genre="DATA ENG • STREAMING • AZURE", year="2026", pal="ocean", motif="flow",
         line=["10.28M transactions through", "a streaming lakehouse."], live=False),
    dict(id="placement", title=["SMART", "PLACEMENT"], genre="FULL-STACK • AI • CAREERS", year="2026", pal="amber", motif="grid",
         line=["Resume analysis and job", "matching — Django + Next.js."], live=True),
    dict(id="traffic", title=["TRAFFIC", "ENFORCEMENT"], genre="COMPUTER VISION • OCR", year="2026", pal="rust", motif="flow",
         line=["YOLOv8 + ByteTrack catch", "red-light runners."], live=True),
]


def motif(kind, a):
    if kind == "shield":
        lines = "".join(
            f'<line x1="196" x2="{238 if i % 2 else 252}" y1="{110 + i * 14}" y2="{110 + i * 14}" stroke-width="3" stroke-linecap="round" stroke-opacity="{.35 + i * .1:.2f}"/>'
            for i in range(5)
        )
        return f"""<g fill="none" stroke="{a}" stroke-opacity=".85">
<path d="M224 54 L282 76 V132 C282 174 256 200 224 214 C192 200 166 174 166 132 V76 Z" stroke-width="2"/>
<path d="M224 70 L268 87 V132 C268 165 248 186 224 198 C200 186 180 165 180 132 V87 Z" stroke-opacity=".4"/>{lines}
<path d="M206 178 l12 12 l26 -28" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>"""
    if kind == "grid":
        cells = "".join(
            f'<rect x="{166 + c * 40}" y="{56 + r * 40}" width="30" height="30" rx="7" stroke-width="1.6" stroke-opacity="{.25 + ((r + c) % 3) * .25:.2f}"/>'
            for r in range(4) for c in range(3)
        )
        return f'<g fill="none" stroke="{a}">{cells}</g>'
    return f"""<g fill="none" stroke="{a}" stroke-width="2">
<circle cx="180" cy="90" r="18" stroke-opacity=".9"/><path d="M198 90 h40" stroke-opacity=".7"/>
<circle cx="256" cy="90" r="18" stroke-opacity=".8"/><path d="M272 80 l20 -24 M272 100 l20 24" stroke-opacity=".6"/>
<circle cx="300" cy="50" r="10" fill="{a}" fill-opacity=".85" stroke="none"/><circle cx="300" cy="130" r="10" stroke-opacity=".5"/>
<path d="M180 108 v40 h120" stroke-opacity=".35" stroke-dasharray="10 7"/>
<circle cx="214" cy="190" r="26" stroke-opacity=".25"/></g>"""


def poster(p, idx):
    W, H = 320, 460
    f, v, to, a = PALETTES[p["pal"]]
    n = len(p["title"])
    size = 64 if n == 1 and len(p["title"][0]) <= 6 else (52 if n == 1 else 46)
    y0 = 330 - (n - 1) * size * .86
    title = "".join(
        f'<text x="24" y="{y0 + i * size * .86:.0f}" class="d" font-size="{size}" fill="{BONE}" letter-spacing="1">{t(s)}</text>'
        for i, s in enumerate(p["title"])
    )
    lines = "".join(
        f'<text x="24" y="{372 + i * 18}" class="s" font-size="12.5" fill="{BONE}" fill-opacity=".82">{t(s)}</text>'
        for i, s in enumerate(p["line"])
    )
    cta = "▶ LIVE DEMO" if p["live"] else "◆ VIEW CODE"
    cta = cta.replace("◆", "→")
    delay = idx * 1.3
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{t(' '.join(p['title']))}">
<title>{t(' '.join(p['title']))}</title>
<style>{font_css('bebas', 'inter', 'inter-bold')}
.sh{{animation:sh 8s infinite;animation-delay:{delay:.1f}s}}
.pulse{{animation:pulse 3s infinite;animation-delay:{delay:.1f}s}}
@keyframes sh{{0%,60%{{transform:translateX(-260px) skewX(-18deg)}}85%,100%{{transform:translateX(560px) skewX(-18deg)}}}}
@keyframes pulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
</style>
<defs>
  <linearGradient id="bg{idx}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{f}"/><stop offset=".55" stop-color="{v}"/><stop offset="1" stop-color="{to}"/></linearGradient>
  <radialGradient id="gl{idx}" cx="72%" cy="22%" r="60%"><stop offset="0" stop-color="{a}" stop-opacity=".45"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
  <linearGradient id="fade{idx}" x1="0" y1="0" x2="0" y2="1"><stop offset=".35" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".88"/></linearGradient>
  <linearGradient id="sh{idx}" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <clipPath id="c{idx}"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#c{idx})">
  <rect width="{W}" height="{H}" fill="url(#bg{idx})"/>
  <rect width="{W}" height="{H}" fill="url(#gl{idx})" class="pulse"/>
  {motif(p['motif'], a)}
  <rect width="{W}" height="{H}" fill="url(#fade{idx})"/>
  {mark(33, 32, 9)}
  <text x="48" y="36" class="s" font-weight="700" font-size="9.5" fill="{BONE}" fill-opacity=".85" letter-spacing="3.5">ORIGINAL</text>
  <rect x="{W - 62}" y="20" width="40" height="20" rx="4" fill="none" stroke="#fff" stroke-opacity=".35"/>
  <text x="{W - 42}" y="34" text-anchor="middle" class="s" font-weight="700" font-size="10" fill="{BONE}">{p['year']}</text>
  <text x="24" y="{y0 - size * .86 + 4:.0f}" class="s" font-weight="700" font-size="10" fill="{a}" letter-spacing="2.5">{t(p['genre'])}</text>
  {title}{lines}
  <rect x="24" y="{H - 52}" width="{118 if p['live'] else 120}" height="32" rx="6" fill="{BONE}"/>
  <text x="{24 + (118 if p['live'] else 120) / 2}" y="{H - 31}" text-anchor="middle" class="s" font-weight="700" font-size="12" fill="{INK}">{t(cta)}</text>
  <rect class="sh" x="0" y="-20" width="140" height="{H + 40}" fill="url(#sh{idx})"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="#fff" stroke-opacity=".08"/>
</svg>"""


# ---------------------------------------------------------------- end credits
CREDITS = [
    ("WRITTEN, BUILT & DEPLOYED BY", "Nivedh Reddy"),
    ("STARRING", "Python  ·  Django  ·  Django REST Framework"),
    ("BACKEND CREW", "Celery  ·  Redis  ·  Django Channels  ·  PostgreSQL"),
    ("GENAI & AGENTS", "LangGraph  ·  LangChain  ·  RAG  ·  Gemini  ·  ChromaDB  ·  Qdrant"),
    ("COMPUTER VISION", "YOLOv8  ·  ByteTrack  ·  OpenCV  ·  CLIP  ·  EasyOCR"),
    ("FRONTEND", "Next.js  ·  React  ·  TypeScript  ·  Tailwind CSS  ·  Streamlit"),
    ("DATA ENGINEERING", "PySpark  ·  Databricks  ·  Data Factory  ·  Delta Lake  ·  Event Hubs"),
    ("FILMED ON LOCATION IN", "Microsoft Azure  ·  AWS  ·  Vercel  ·  Render  ·  Hugging Face"),
    ("CERTIFIED BY", "Microsoft (AZ-900)  ·  AWS Academy"),
    ("SHIPPED WITH", "Docker  ·  GitHub Actions  ·  pytest"),
]


def end_credits():
    W, H = 1000, 300
    y = 0
    rows = []
    for role, names in CREDITS:
        rows.append(f'<text x="500" y="{y}" text-anchor="middle" class="s" font-weight="700" font-size="11" fill="{RED}" letter-spacing="4">{t(role)}</text>')
        big = role.startswith("WRITTEN")
        cls, size, ls = ("d", 44, 3) if big else ("s", 17, 0)
        rows.append(
            f'<text x="500" y="{y + (40 if big else 28)}" text-anchor="middle" class="{cls}" '
            f'font-size="{size}" fill="{BONE}" letter-spacing="{ls}">{t(names)}</text>'
        )
        y += 92 if big else 72
    y += 20
    rows.append(f'<text x="500" y="{y}" text-anchor="middle" class="s" font-size="11" fill="{SMOKE}" letter-spacing="3">NO BUGS WERE HARMED IN THE MAKING OF THIS SERIES. SOME WERE FIXED.</text>')
    total = y + 90  # one full loop of the roll, including the gap before it repeats
    dur = total / 22  # ~22 px per second
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="End credits — tech stack">
<title>End credits — tech stack</title>
<style>{font_css('bebas', 'inter', 'inter-bold')}
.roll{{animation:roll {dur:.1f}s linear infinite}}
@keyframes roll{{0%{{transform:translateY(40px)}}100%{{transform:translateY({40 - total}px)}}}}
</style>
<defs>
  <linearGradient id="fv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}"/><stop offset=".22" stop-color="{INK}" stop-opacity="0"/><stop offset=".78" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}"/></linearGradient>
  <radialGradient id="cg" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="{CRIMSON}" stop-opacity=".14"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>
  <clipPath id="cf"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#cf)">
  <rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#cg)"/>
  <g class="roll"><g>{''.join(rows)}</g><g transform="translate(0 {total})">{''.join(rows)}</g><g transform="translate(0 {2 * total})">{''.join(rows)}</g></g>
  <rect width="{W}" height="{H}" fill="url(#fv)"/>
</g>
</svg>"""


# ---------------------------------------------------------------- live data
def gql(query, variables):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set (use --sample for an offline preview)")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]


LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch_calendar():
    q = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
      totalContributions weeks{contributionDays{date weekday contributionCount contributionLevel}}}}}}"""
    cal = gql(q, {"login": LOGIN})["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[(d["date"], d["weekday"], d["contributionCount"], LEVELS[d["contributionLevel"]]) for d in w["contributionDays"]] for w in cal["weeks"]]
    return cal["totalContributions"], weeks


def sample_calendar():
    rnd = random.Random(42)
    start = date.today() - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    weeks, total, d = [], 0, start
    while d <= date.today():
        wk = []
        for _ in range(7):
            if d > date.today():
                break
            c = rnd.choice([0, 0, 0, 1, 2, 3, 5, 8]) if d.month in (4, 5, 7, 8, 9, 10) else rnd.choice([0, 0, 0, 0, 1])
            lvl = 0 if c == 0 else 1 if c < 2 else 2 if c < 4 else 3 if c < 6 else 4
            wk.append((d.isoformat(), (d.weekday() + 1) % 7, c, lvl))
            total += c
            d += timedelta(days=1)
        weeks.append(wk)
    return total, weeks


def fetch_progress(local=None):
    if local:
        text = Path(local).read_text(encoding="utf-8")
    else:
        with urllib.request.urlopen(PROGRESS_URL, timeout=30) as r:
            text = r.read().decode()
    phases = []
    for line in text.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*[^|]*\|\s*\**([^|*]+?)\**\s*\|", line)
        if m:
            phases.append((int(m.group(1)), m.group(2).strip(), m.group(3).strip().lower()))
    return phases


# ---------------------------------------------------------------- contribution reel
REEL = ["#17161c", "#4a0d17", "#8a1426", "#c81d35", "#ff3d5a"]


def reel(total, weeks):
    cell, gap = 12, 3.5
    pitch = cell + gap
    cols = len(weeks)
    gx, gy = 34, 92
    gw = cols * pitch
    W = int(gx * 2 + gw)
    H = 268
    sweep, cycle = 6.0, 11.0
    cells = []
    for c, wk in enumerate(weeks):
        d = c / max(cols - 1, 1) * sweep
        for (_, wd, cnt, lvl) in wk:
            x = gx + c * pitch
            y = gy + wd * pitch
            cls = f"l{lvl}"
            cells.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.5" class="{cls}" style="animation-delay:{d:.2f}s"/>'
            )
    # month labels
    months, last = [], None
    for c, wk in enumerate(weeks):
        m = wk[0][0][5:7]
        if m != last and c < cols - 2:
            label = date.fromisoformat(wk[0][0]).strftime("%b").upper()
            months.append(f'<text x="{gx + c * pitch:.1f}" y="{gy + 7 * pitch + 18:.1f}" class="s" font-size="9.5" fill="{SMOKE}" letter-spacing="1.5">{label}</text>')
            last = m
    holes_top = "".join(f'<rect x="{x}" y="58" width="9" height="12" rx="2"/>' for x in range(0, W + 40, 22))
    holes_bot = "".join(f'<rect x="{x}" y="{gy + 7 * pitch + 30:.0f}" width="9" height="12" rx="2"/>' for x in range(0, W + 40, 22))
    lvl_css = "".join(
        f".l{i}{{fill:{REEL[0]};animation:a{i} {cycle}s infinite linear both}}"
        f"@keyframes a{i}{{0%{{fill:{REEL[0]}}}1.5%{{fill:{'#ffd6dc' if i else '#2a2930'}}}5%,72%{{fill:{REEL[i]}}}82%,100%{{fill:{REEL[0]}}}}}"
        for i in range(5)
    )
    end_x = gx + gw
    css = f"""{font_css('bebas', 'inter', 'inter-bold')}
{lvl_css}
.head{{animation:head {cycle}s infinite linear}}
@keyframes head{{0%{{transform:translateX(0);opacity:1}}{sweep / cycle * 100:.1f}%{{transform:translateX({gw:.0f}px);opacity:1}}{sweep / cycle * 100 + 3:.1f}%,100%{{transform:translateX({gw:.0f}px);opacity:0}}}}
.holes{{animation:run 1.2s infinite linear}}
@keyframes run{{from{{transform:translateX(0)}}to{{transform:translateX(-22px)}}}}
.rec{{animation:rec 1.4s infinite}}
@keyframes rec{{0%,100%{{opacity:1}}50%{{opacity:.15}}}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total} contributions in the last year">
<title>The contribution reel — {total} contributions in the last year</title>
<style>{css}</style>
<defs>
  <clipPath id="rf"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{RED}" stop-opacity="0"/><stop offset="1" stop-color="{RED}" stop-opacity=".35"/></linearGradient>
  <radialGradient id="rg2" cx="50%" cy="0%" r="80%"><stop offset="0" stop-color="{CRIMSON}" stop-opacity=".18"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#rf)">
  <rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#rg2)"/>
  <circle cx="{gx + 5}" cy="33" r="5" fill="{RED}" class="rec"/>
  <text x="{gx + 18}" y="38" class="s" font-weight="700" font-size="12" fill="{BONE}" letter-spacing="3">NOW SHOWING · THE CONTRIBUTION REEL</text>
  <text x="{W - gx}" y="38" text-anchor="end" class="s" font-size="12" fill="{MIST}" letter-spacing="1"><tspan class="d" font-size="22" fill="{BONE}" letter-spacing="1">{total:,}</tspan>  CONTRIBUTIONS · LAST 12 MONTHS</text>
  <rect x="0" y="52" width="{W}" height="24" fill="#0e0e12"/>
  <rect x="0" y="{gy + 7 * pitch + 24:.0f}" width="{W}" height="24" fill="#0e0e12"/>
  <g fill="{INK}" class="holes">{holes_top}{holes_bot}</g>
  {''.join(cells)}
  {''.join(months)}
  <g class="head">
    <rect x="{gx - 60}" y="{gy - 6}" width="60" height="{7 * pitch + 8:.0f}" fill="url(#beam)"/>
    <rect x="{gx - 1}" y="{gy - 10}" width="2" height="{7 * pitch + 16:.0f}" fill="{RED}"/>
    <path d="M{gx - 6} {gy - 16} h12 l-6 7 z" fill="{RED}"/>
  </g>
</g>
</svg>"""


# ---------------------------------------------------------------- continue watching
def continue_watching(phases):
    W, H = 1000, 200
    total = len(phases) or 1
    done = sum(1 for p in phases if p[2] == "done")
    nxt = next((p for p in phases if p[2] != "done"), None)
    pct = done / total
    if nxt:
        ep = f"PHASE {nxt[0]} OF {total - 1}  ·  {nxt[1].upper()}"
        state = "IN PRODUCTION"
    else:
        ep, state = "ALL PHASES COMPLETE", "SEASON FINALE"
    bx, bw, by = 268, 560, 150
    seg_w = bw / total
    segs = []
    for i, (n, name, st) in enumerate(phases):
        x = bx + i * seg_w
        if st == "done":
            col, cls = RED, ""
        elif nxt and n == nxt[0]:
            col, cls = BONE, ' class="blink"'
        else:
            col, cls = "#2a2930", ""
        segs.append(f'<rect x="{x + 2:.1f}" y="{by + 18}" width="{seg_w - 4:.1f}" height="5" rx="2.5" fill="{col}"{cls}/>')
        segs.append(f'<text x="{x + seg_w / 2:.1f}" y="{by + 38}" text-anchor="middle" class="s" font-size="9" fill="{SMOKE}" letter-spacing="1">{n}</text>')
    css = f"""{font_css('bebas', 'inter', 'inter-bold')}
.fill{{animation:fill 2.4s cubic-bezier(.2,.7,.2,1) both .4s}}
@keyframes fill{{from{{width:0}}to{{width:{bw * pct:.1f}px}}}}
.blink{{animation:blink 1.6s infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
.sh{{animation:sh 6s infinite}}
@keyframes sh{{0%,50%{{transform:translateX(-200px) skewX(-18deg)}}80%,100%{{transform:translateX(420px) skewX(-18deg)}}}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Continue watching: CodeSage">
<title>Continue watching — CodeSage, {done} of {total} phases done</title>
<style>{css}</style>
<defs>
  <clipPath id="cw"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <clipPath id="th"><rect x="24" y="24" width="216" height="152" rx="12"/></clipPath>
  <linearGradient id="tb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#120822"/><stop offset=".55" stop-color="#3d1a6e"/><stop offset="1" stop-color="#07060c"/></linearGradient>
  <linearGradient id="shg" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".18"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#cw)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  <g clip-path="url(#th)">
    <rect x="24" y="24" width="216" height="152" fill="url(#tb)"/>
    <g fill="none" stroke="#b98bff" stroke-width="1.6" stroke-opacity=".7">
      <path d="M70 70 l-18 18 l18 18"/><path d="M194 70 l18 18 l-18 18"/>
      <path d="M90 92 h28 M90 104 h50 M90 116 h36 M90 80 h44" stroke-linecap="round" stroke-opacity=".5"/>
    </g>
    <text x="40" y="160" class="d" font-size="30" fill="{BONE}">CODESAGE</text>
    {mark(48, 46, 9)}
    <rect class="sh" x="24" y="0" width="90" height="220" fill="url(#shg)"/>
  </g>
  <text x="{bx}" y="52" class="s" font-weight="700" font-size="11" fill="{RED}" letter-spacing="3.5">CONTINUE WATCHING  ·  {state}</text>
  <text x="{bx}" y="96" class="d" font-size="44" fill="{BONE}" letter-spacing="1">CODESAGE</text>
  <text x="{bx}" y="122" class="s" font-size="13" fill="{MIST}">Multi-agent AI code review for GitHub pull requests  ·  Django · LangGraph · pgvector · Next.js</text>
  <text x="{bx}" y="{by + 4}" class="s" font-weight="700" font-size="10.5" fill="{BONE}" letter-spacing="2">{t(ep)}</text>
  <text x="{bx + bw}" y="{by + 4}" text-anchor="end" class="s" font-size="10.5" fill="{MIST}">{done} / {total} phases</text>
  <rect x="{bx}" y="{by + 10}" width="{bw}" height="3" rx="1.5" fill="#2a2930"/>
  <rect x="{bx}" y="{by + 10}" height="3" rx="1.5" fill="{RED}" class="fill"/>
  {''.join(segs)}
  <rect x="{W - 140}" y="74" width="112" height="40" rx="8" fill="{BONE}"/>
  <path d="M{W - 118} 85 l12 9 l-12 9 z" fill="{INK}"/>
  <text x="{W - 98}" y="99" class="s" font-weight="700" font-size="14" fill="{INK}">Resume</text>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="#fff" stroke-opacity=".08"/>
</svg>"""


# ---------------------------------------------------------------- main
def main():
    args = sys.argv[1:]
    mode = args[0] if args else "static"
    if mode == "static":
        out = ROOT / "assets"
        write(out / "title.svg", title_sequence())
        write(out / "credits.svg", end_credits())
        for i, p in enumerate(POSTERS):
            write(out / "originals" / f"{p['id']}.svg", poster(p, i))
    elif mode == "live":
        out = ROOT / "dist"
        sample = "--sample" in args
        total, weeks = sample_calendar() if sample else fetch_calendar()
        local = args[args.index("--progress-file") + 1] if "--progress-file" in args else None
        write(out / "reel.svg", reel(total, weeks))
        write(out / "continue-watching.svg", continue_watching(fetch_progress(local)))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
