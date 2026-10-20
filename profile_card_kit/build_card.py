"""Builds profile-card.svg from avatar.png + data.json."""
import base64, datetime, json, os, re, sys, textwrap
from xml.sax.saxutils import escape as esc

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(HERE, f)

# ------------------------------------------------------------------ data
try:
    with open(P("data.json"), encoding="utf-8") as data_file:
        data = json.load(data_file)
except (OSError, json.JSONDecodeError) as error:
    print(f"Could not load data.json; building an empty dashboard: {error}", file=sys.stderr)
    data = {}
data.setdefault("api_status", "unavailable")
data.setdefault("updated", None)
data.setdefault("stats", {})
data.setdefault("total", None)
data.setdefault("weeks", [])
data.setdefault("languages", [])
data.setdefault("projects", [])
data.setdefault("commits", [])
for key in ("repos", "stars", "commits", "followers"):
    data["stats"].setdefault(key, None)
LOGIN = data.get("login", "Neversplit2")
avatar = "data:image/png;base64," + base64.b64encode(open(P("avatar.png"), "rb").read()).decode()

BADGE = ('M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z')
PDF = 'M3 0h10a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2zm2 5h6m-6 4h6m-6 4h4'
STAR = 'M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z'

# ================================================================== TOP CARD (ID)
ys = [112, 138, 164, 190, 216, 242, 268, 294, 320]
T0, STEP, DUR = 0.7, 0.3, 0.9
def timing(i):
    b = T0 + i * STEP; tot = b + DUR
    return b, tot, b / tot

clips = carets = ''
for i, y in enumerate(ys):
    b, tot, kt = timing(i)
    clips += (f'<clipPath id="rc{i}"><rect x="262" y="{y-15}" width="560" height="22"><animate attributeName="width" values="0;0;560" '
              f'keyTimes="0;{kt:.4f};1" dur="{tot:.2f}s" begin="0s" fill="freeze"/></rect></clipPath>\n')
    carets += (f'<rect x="262" y="{y-12}" width="1.6" height="15" rx=".8" fill="#58a6ff" opacity="0">'
               f'<animate attributeName="x" values="262;262;822" keyTimes="0;{kt:.4f};1" dur="{tot:.2f}s" begin="0s" fill="freeze"/>'
               f'<animate attributeName="opacity" values="0;0;.9;.9;0" keyTimes="0;{kt:.4f};{kt+0.01:.4f};0.92;1" dur="{tot:.2f}s" begin="0s" fill="freeze"/></rect>\n')

def row(i, label, val):
    return f'<text y="{ys[i]}" clip-path="url(#rc{i})"><tspan x="270" class="lbl">{label}</tspan>{val}</text>\n'
rows = row(0, 'username', '<tspan x="395" class="accent">Neversplit2</tspan>')
rows += row(1, 'education', '<tspan x="395" class="val" font-weight="600">Master\'s Degree, Rural and Survey Engineering</tspan>')
rows += row(2, 'domain', '<tspan x="395" class="val">Geodesy, ML &amp; Satellite Remote Sensing</tspan>')
rows += row(3, 'core.lang', '<tspan x="395" class="val">Python<tspan class="dim"> | </tspan>JavaScript (React)<tspan class="dim"> | </tspan>HTML / CSS</tspan>')
rows += row(4, 'core.ml_stack', '<tspan x="395" class="val">Pandas, NumPy, XGBoost, Random Forest, SciPy</tspan>')
rows += row(5, 'core.frontend', '<tspan x="395" class="val">React Dashboards, Surveying Workflows, APIs</tspan>')
rows += row(6, 'proj.grace', '<tspan x="395" class="val">GRACE &amp; GRACE-FO Downscaling</tspan>')
rows += row(7, 'proj.topo', '<tspan x="395" class="val">Geodetic Suite</tspan>')
rows += row(8, 'grid.github', '<tspan x="395" class="accent">github.com/Neversplit2</tspan>').replace('<text ', '<text filter="url(#tglow)" ')

def pulse(col):
    return (f'<circle cx="8" cy="8" r="8" fill="none" stroke="{col}" stroke-width="1" opacity="0"><animate attributeName="r" values="8;16" dur="2.4s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".7;0" dur="2.4s" repeatCount="indefinite"/></circle>')
badges = f'''<g class="fade" style="animation-delay:{timing(6)[1]:.2f}s">
  <a href="https://github.com/Neversplit2/grace_project" target="_blank" title="Open GRACE Repository"><g transform="translate(594, 256)" class="repo-badge">{pulse('#58a6ff')}<rect width="16" height="16" rx="4"/><path transform="translate(2.35 2.35) scale(0.72)" d="{BADGE}"/></g></a>
  <a href="https://ikee.lib.auth.gr/record/375934/files/karachles_thesis.pdf" target="_blank" title="Download Diploma Thesis (PDF)"><g transform="translate(614, 256)" class="pdf-badge">{pulse('#ff6b81')}<rect width="16" height="16" rx="4"/><path transform="translate(3.9 2.5) scale(0.55)" d="{PDF}"/></g></a>
</g>
<g class="fade" style="animation-delay:{timing(7)[1]:.2f}s">
  <a href="https://github.com/LASCA/LASCA" target="_blank" title="Open Topo Repository"><g transform="translate(499, 282)" class="repo-badge">{pulse('#58a6ff')}<rect width="16" height="16" rx="4"/><path transform="translate(2.35 2.35) scale(0.72)" d="{BADGE}"/></g></a>
</g>'''

R = 44
lat = ''.join(f'<ellipse cx="0" cy="{o}" rx="{rx}" ry="{rx*0.2:.1f}" fill="none" stroke="#58a6ff" stroke-opacity=".38" stroke-width=".8"/>'
              for o, rx in [(-38, 22), (-22, 38), (0, 44), (22, 38), (38, 22)])
mer = ''.join(f'<ellipse cx="0" cy="0" rx="{rx0}" ry="{R}" fill="none" stroke="#79c0ff" stroke-opacity=".5" stroke-width=".9"><animate attributeName="rx" values="0.5;{R};0.5" keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" dur="8s" begin="{-2*k}s" repeatCount="indefinite"/></ellipse>'
              for k, rx0 in enumerate([44, 31, 0.5, 31]))
orbit = 'M-72,0 a72,22 0 1,0 144,0 a72,22 0 1,0 -144,0'
sat = lambda c, b: f'<g><circle r="5.5" fill="{c}" opacity=".22"/><circle r="2.6" fill="{c}"/><animateMotion path="{orbit}" dur="7s" begin="{b}s" repeatCount="indefinite"/></g>'
globe = f'''<g transform="translate(752,268)"><g class="gfloat">
<circle r="78" fill="url(#amb)"/><circle r="{R}" fill="url(#sph)" stroke="#58a6ff" stroke-opacity=".55" stroke-width="1"/>
<g transform="rotate(-20)">{lat}{mer}</g>
<g transform="rotate(-24)"><ellipse rx="72" ry="22" fill="none" stroke="#bc8cff" stroke-opacity=".55" stroke-dasharray="3 4"/>{sat('#3fb950', 0)}{sat('#ffa657', -0.55)}</g></g>
<text y="63" text-anchor="middle" class="mono" font-size="8" letter-spacing="1.5" fill="#6e7681">GRACE · GRACE-FO</text></g>'''

parts = [(735,100,1.4,'#58a6ff',0),(790,130,1.1,'#bc8cff',1.2),(815,95,1.6,'#58a6ff',2.1),(760,165,1.2,'#3fb950',.6),(722,150,1,'#bc8cff',3),
         (800,178,1.3,'#58a6ff',1.8),(775,68,1.2,'#bc8cff',2.6),(668,330,1.2,'#58a6ff',.9),(700,300,1,'#3fb950',2.3),(822,225,1.2,'#bc8cff',3.4),
         (808,320,1.4,'#58a6ff',1.5),(650,330,1,'#bc8cff',2.9)]
particles = ''.join(f'<circle class="drift" cx="{x}" cy="{y}" r="{r}" fill="{c}" style="animation-delay:{d}s;animation-duration:{4+(i%4)}s"/>' for i, (x, y, r, c, d) in enumerate(parts))
# rising hologram motes beside the photo
motes = ''.join(f'<circle class="rise-m" cx="{x}" cy="{y}" r="1.2" fill="#79c0ff" style="animation-delay:{d}s;animation-duration:{3+i%3}s"/>'
                for i, (x, y, d) in enumerate([(30,300,0),(257,290,1.1),(26,250,2),(262,240,.5),(32,200,1.7),(258,190,2.4)]))

# ================================================================== LOWER "PAGE"
Y0 = 372
y = Y0
tabs = [("Overview", 35, 50), ("Repositories", 113, 75), ("Projects", 216, 52), ("Activity", 296, 50)]
tab_svg = ''
for k, (t, x, w) in enumerate(tabs):
    s, e = k * .25 + .0001, k * .25 + .2
    tab_svg += (f'<text x="{x}" y="{Y0+55}" class="sans" font-size="12" font-weight="600" fill="#8b949e">{t}'
                f'<animate attributeName="fill" calcMode="discrete" values="#8b949e;#e6edf3;#8b949e;#8b949e" keyTimes="0;{s:.4f};{e:.4f};1" dur="14s" repeatCount="indefinite"/></text>')
xs = ';'.join(str(t[1]) for t in tabs for _ in (0, 1)) + ';35'
ws = ';'.join(str(t[2]) for t in tabs for _ in (0, 1)) + ';50'
kts = ';'.join(f'{k*.25+off:.3f}' for k in range(4) for off in (0, .2)) + ';1'
tab_svg += (f'<rect y="{Y0+62}" height="2" rx="1" fill="#58a6ff" x="35" width="50"><animate attributeName="x" values="{xs}" keyTimes="{kts}" dur="14s" repeatCount="indefinite"/>'
            f'<animate attributeName="width" values="{ws}" keyTimes="{kts}" dur="14s" repeatCount="indefinite"/></rect>')
y = Y0 + 82   # content start

# --- stat tiles
st = data["stats"]
tiles = [("Repositories", st["repos"], "#58a6ff", f'<path d="{BADGE}"/>'),
         ("Total stars", st["stars"], "#e3b341", f'<path d="{STAR}"/>'),
         ("Commits · last year", st["commits"], "#3fb950", '<circle cx="8" cy="8" r="3.2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M.5 8h4.3M11.2 8h4.3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'),
         ("Followers", st["followers"], "#bc8cff", '<circle cx="8" cy="5" r="3"/><path d="M2 14.5c0-3 2.7-5 6-5s6 2 6 5z"/>')]
tiles_svg = ''
for i, (lab, val, col, ico) in enumerate(tiles):
    x = 35 + i * 198
    value_text = f"{val:,}" if isinstance(val, int) else "—"
    tiles_svg += (f'<g class="fade tile" style="animation-delay:{.9+i*.12:.2f}s"><rect x="{x}" y="{y}" width="186" height="62" rx="10" fill="#0d1117" stroke="#30363d"/>'
                  f'<rect x="{x}" y="{y}" width="186" height="2" rx="1" fill="{col}" opacity=".7"/>'
                  f'<circle cx="{x+31}" cy="{y+31}" r="18" fill="{col}" fill-opacity=".14"/>'
                  f'<g transform="translate({x+31-9.6} {y+31-9.6}) scale(1.2)" fill="{col}" color="{col}">{ico}</g>'
                  f'<text x="{x+58}" y="{y+31}" class="sans" font-size="20" font-weight="700" fill="#e6edf3">{value_text}</text>'
                  f'<text x="{x+58}" y="{y+48}" class="sans" font-size="11" fill="#8b949e">{lab}</text></g>')
y += 62 + 16

# --- contribution heatmap
weeks = data["weeks"]; n = len(weeks)
pitch = min(13.5, 715 / max(n, 1)); cell = pitch - 2.5
gx, py, ph = 76, y, 170
gy = py + 56
def contribution_count(day):
    return day.get("count", 0) if isinstance(day, dict) else day or 0

flat = [contribution_count(day) for week in weeks for day in week if day is not None]
mx = max(flat) if flat else 1
def lvl(v):
    if not v: return 0
    q = v / mx
    return 1 if q <= .25 else 2 if q <= .5 else 3 if q <= .75 else 4
HC = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
heat = f'<g class="fade" style="animation-delay:1.3s"><rect x="35" y="{py}" width="780" height="{ph}" rx="10" fill="#0d1117" stroke="#30363d"/>'
heat += f'<text x="52" y="{py+26}" class="sans" font-size="13" font-weight="600" fill="#e6edf3">Contribution Activity</text>'
contribution_total = data["total"]
total_text = f"{contribution_total:,} contributions in the last year" if isinstance(contribution_total, int) else "Contribution data unavailable"
heat += f'<text x="798" y="{py+26}" text-anchor="end" class="sans" font-size="11.5" fill="#8b949e">{total_text}</text></g>'
last_m, last_x = None, -99
for i in range(n):
    first_day = next((day for day in weeks[i] if isinstance(day, dict) and day.get("date")), None)
    if first_day:
        d0 = datetime.date.fromisoformat(first_day["date"])
    else:
        d0 = None
    if d0 and d0.month != last_m:
        x = gx + i * pitch
        if x - last_x > 34:
            heat += f'<text class="fade" style="animation-delay:1.4s" x="{x:.1f}" y="{py+50}" font-size="10" fill="#8b949e" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">{d0.strftime("%b")}</text>'
            last_x = x
        last_m = d0.month
for r, lab in ((1, 'Mon'), (3, 'Wed'), (5, 'Fri')):
    heat += f'<text x="52" y="{gy + r*pitch + cell - 1:.1f}" font-size="9.5" fill="#8b949e" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">{lab}</text>'
for i, col in enumerate(weeks):
    heat += f'<g class="wk" style="animation-delay:{1.4+i*.025:.3f}s">'
    for day in col:
        if day is None: continue
        count = contribution_count(day)
        date_value = day.get("date") if isinstance(day, dict) else None
        if not date_value:
            continue
        row_index = (datetime.date.fromisoformat(date_value).weekday() + 1) % 7
        color = day.get("color") if isinstance(day, dict) else None
        if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            color = HC[lvl(count)]
        heat += (f'<rect x="{gx+i*pitch:.1f}" y="{gy+row_index*pitch:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2.2" fill="{color}">'
                 f'<title>{count} contributions on {esc(date_value)}</title></rect>')
    heat += '</g>'
ly = py + ph - 14
heat += f'<text x="690" y="{ly+8}" text-anchor="end" font-size="10" fill="#8b949e" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">Less</text>'
heat += ''.join(f'<rect x="{696+k*14}" y="{ly}" width="11" height="11" rx="2.2" fill="{c}"/>' for k, c in enumerate(HC))
heat += f'<text x="770" y="{ly+8}" font-size="10" fill="#8b949e" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">More</text>'
y += ph + 14

# --- languages
langs = data["languages"]; lp, lh = y, 96
lang_svg = (f'<g class="fade" style="animation-delay:1.8s"><rect x="35" y="{lp}" width="780" height="{lh}" rx="10" fill="#0d1117" stroke="#30363d"/>'
            f'<text x="52" y="{lp+24}" class="sans" font-size="13" font-weight="600" fill="#e6edf3">Top Languages</text>'
            f'<clipPath id="barclip"><rect x="52" y="{lp+33}" width="746" height="8" rx="4"/></clipPath><g clip-path="url(#barclip)">')
tot = sum(l.get("pct", 0) for l in langs) or 1; bx = 52
for k, l in enumerate(langs):
    w = 746 * l.get("pct", 0) / tot
    lang_svg += f'<rect class="seg" style="animation-delay:{2+k*.15:.2f}s" x="{bx:.1f}" y="{lp+33}" width="{w:.1f}" height="8" fill="{l["color"]}"/>'
    bx += w
lang_svg += '</g>'
if not langs:
    lang_svg += f'<text x="52" y="{lp+63}" class="sans" font-size="11" fill="#8b949e">Language data unavailable</text>'
else:
    lx, legend_row = 52, 0
    for language in langs:
        pct = language.get("pct", 0)
        pct_text = f"{pct:g}" if isinstance(pct, (int, float)) else "0"
        label = f'{language["name"]} {pct_text}%'
        item_width = 13 + len(label) * 6.1 + 22
        if lx + item_width > 798:
            lx, legend_row = 52, legend_row + 1
        legend_y = lp + 58 + legend_row * 14
        lang_svg += (f'<circle cx="{lx+4}" cy="{legend_y}" r="4" fill="{language["color"]}"/>'
                     f'<text x="{lx+13}" y="{legend_y+4}" class="sans" font-size="11" fill="#c9d1d9">{esc(label)}</text>')
        lx += item_width
lang_svg += '</g>'
y += lh + 24

def section(label, yy, delay):
    return (f'<text x="35" y="{yy}" class="mono" font-size="11" font-weight="700" fill="#e6edf3" letter-spacing="1">{label}</text>'
            f'<line x1="35" y1="{yy+7}" x2="815" y2="{yy+7}" stroke="#30363d"/>'
            f'<line class="sweep" x1="35" y1="{yy+7}" x2="815" y2="{yy+7}" stroke="#58a6ff" stroke-width="1.4" stroke-linecap="round" style="animation-delay:{delay}s"/>')

# --- projects
proj_svg = section('PROJECTS', y, 0.5)
y += 22
for k, p in enumerate(data["projects"][:2]):
    x = 35 + k * 396; w = 384; h = 132
    desc = textwrap.wrap(p.get("description") or "", 54)[:2] or ['']
    stars_text = f'{p["stars"]:,}' if isinstance(p.get("stars"), int) else "—"
    forks_text = f'{p["forks"]:,}' if isinstance(p.get("forks"), int) else "—"
    pj = (f'<a href="{esc(p["url"])}" target="_blank"><g class="fade proj" style="animation-delay:{2.2+k*.15:.2f}s">'
          f'<rect class="pc" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#0d1117" stroke="#30363d"/>'
          f'<rect x="{x}" y="{y}" width="{w}" height="2" rx="1" fill="{p["color"]}" opacity=".8"/>'
          f'<g transform="translate({x+18} {y+16}) scale(.95)" fill="#8b949e"><path d="{BADGE}"/></g>'
          f'<text x="{x+42}" y="{y+30}" class="sans" font-size="14" font-weight="700" fill="#58a6ff">{esc(p["name"])}</text>'
          f'<text x="{x+w-18}" y="{y+30}" text-anchor="end" class="sans" font-size="14" fill="#6e7681">↗</text>')
    for j, line in enumerate(desc):
        pj += f'<text x="{x+18}" y="{y+56+j*17}" class="sans" font-size="12" fill="#8b949e">{esc(line)}</text>'
    tx = x + 18
    for t in p.get("tags", [])[:4]:
        cw = len(t) * 6.3 + 16
        if tx + cw > x + w - 14: break
        pj += (f'<rect x="{tx:.1f}" y="{y+88}" width="{cw:.1f}" height="18" rx="9" fill="#0c2d6b" fill-opacity=".55" stroke="#1f6feb" stroke-opacity=".5"/>'
               f'<text x="{tx+cw/2:.1f}" y="{y+100.5}" text-anchor="middle" class="mono" font-size="10" fill="#79c0ff">{esc(t)}</text>')
        tx += cw + 6
    pj += (f'<circle cx="{x+22}" cy="{y+120}" r="4" fill="{p["color"]}"/>'
           f'<text x="{x+32}" y="{y+124}" class="sans" font-size="11" fill="#c9d1d9">{esc(p["language"] or "—")}</text>'
           f'<g transform="translate({x+120} {y+113})" fill="#8b949e"><path transform="scale(.8)" d="{STAR}"/></g>'
           f'<text x="{x+137}" y="{y+124}" class="sans" font-size="11" fill="#8b949e">{stars_text}</text>'
           f'<g transform="translate({x+170} {y+113}) scale(.8)" fill="none" stroke="#8b949e" stroke-width="1.5" stroke-linecap="round"><circle cx="4" cy="3.5" r="1.6"/><circle cx="12" cy="3.5" r="1.6"/><circle cx="8" cy="13" r="1.6"/><path d="M4 5v1.5c0 1.2 1 2 2.2 2h3.6c1.2 0 2.2-.8 2.2-2V5M8 8.5v3"/></g>'
           f'<text x="{x+188}" y="{y+124}" class="sans" font-size="11" fill="#8b949e">{forks_text}</text></g></a>')
    proj_svg += pj
y += 132 + 28

# --- commits
com_svg = section('RECENT COMMITS', y, 1.4)
y += 28
cm = data["commits"][:5]
if cm:
    com_svg += f'<line x1="52" y1="{y+4}" x2="52" y2="{y+4+(len(cm)-1)*30}" stroke="#30363d" stroke-width="1.5"/>'
else:
    com_svg += f'<text x="72" y="{y+8}" class="sans" font-size="12" fill="#8b949e">No recent public commits available</text>'
for k, c in enumerate(cm):
    yy = y + k * 30
    msg = c["msg"] if len(c["msg"]) <= 66 else c["msg"][:65] + "…"
    commit_color = "#3fb950" if k == 0 else "#58a6ff"
    live_class = ' class="live"' if k == 0 else ""
    com_svg += (f'<g class="fade" style="animation-delay:{2.6+k*.14:.2f}s">'
                f'<circle cx="52" cy="{yy+4}" r="4.5" fill="#0d1117" stroke="{commit_color}" stroke-width="2"{live_class}/>'
                f'<text x="72" y="{yy+8}" class="mono" font-size="12" fill="#e6edf3">{esc(msg)}</text>'
                f'<text x="705" y="{yy+8}" text-anchor="end" class="mono" font-size="11" fill="#58a6ff">{esc(c["repo"])}</text>'
                f'<text x="798" y="{yy+8}" text-anchor="end" class="sans" font-size="11" fill="#6e7681">{esc(c["when"])}</text></g>')
y += max(len(cm), 1) * 30 + 6
updated = data.get("updated")
if updated and data.get("api_status") == "live":
    foot_status = f"synced {updated}"
elif updated and data.get("api_status") == "partial":
    foot_status = f"checked {updated} · partial data"
elif updated:
    foot_status = f"checked {updated} · data unavailable"
else:
    foot_status = "GitHub data unavailable"
foot = f'<text x="35" y="{y+8}" class="mono" font-size="10" fill="#6e7681">{esc(foot_status)} · auto-generated · github.com/{LOGIN}</text>'
Yend = y + 28           # window bottom
H = Yend + 16

status_badges = {
    "live": ("LIVE DATA", "#0f2f1d", "#238636", "#3fb950"),
    "partial": ("PARTIAL DATA", "#3a2a07", "#9e6a03", "#e3b341"),
    "unavailable": ("API OFFLINE", "#21262d", "#484f58", "#8b949e"),
}
status_label, status_fill, status_stroke, status_color = status_badges.get(
    data.get("api_status"), status_badges["unavailable"]
)
hdr_chip = (f'<rect x="700" y="{Y0+8}" width="100" height="18" rx="9" fill="{status_fill}" stroke="{status_stroke}"/>'
            f'<text x="750" y="{Y0+21}" text-anchor="middle" class="mono" font-size="9" font-weight="700" fill="{status_color}" letter-spacing="1">{status_label}</text>')

lower = f'''<g class="card" style="animation-delay:.5s">
  <rect x="21" y="{Y0+8}" width="820" height="{Yend-Y0}" rx="11" fill="#1f6feb" opacity=".12"/>
  <rect x="15" y="{Y0}" width="820" height="{Yend-Y0}" rx="10" fill="url(#bg)" stroke="url(#border2)" stroke-width="1.5"/>
  <rect x="15" y="{Y0+34}" width="820" height="{Yend-Y0-34}" fill="url(#dots)" clip-path="url(#low-clip)"/>
  <path d="M 15,{Y0+10} A 10,10 0 0,1 25,{Y0} L 825,{Y0} A 10,10 0 0,1 835,{Y0+10} L 835,{Y0+34} L 15,{Y0+34} Z" fill="#161b22" stroke="#30363d"/>
  <circle cx="35" cy="{Y0+17}" r="5.5" fill="#ed6158"/><circle cx="53" cy="{Y0+17}" r="5.5" fill="#fcc02e"/><circle cx="71" cy="{Y0+17}" r="5.5" fill="#5fc038"/>
  <text x="425" y="{Y0+21}" class="mono" font-size="12" font-weight="600" text-anchor="middle" fill="#8b949e">activity.dashboard</text>
  {hdr_chip}
  {tab_svg}
  <line x1="15" y1="{Y0+66}" x2="835" y2="{Y0+66}" stroke="#30363d"/>
  {tiles_svg}
  {heat}
  {lang_svg}
  {proj_svg}
  {com_svg}
  {foot}
</g>'''

# ================================================================== CSS / DEFS / JS
CSS = open(P("style.css"), encoding="utf-8").read()
JS = open(P("holo.js"), encoding="utf-8").read()

svg = f'''<svg width="850" height="{H}" viewBox="0 0 850 {H}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<title>{LOGIN} – GitHub profile card</title>
<defs>
<style>{CSS}</style>
<image id="av" xlink:href="{avatar}" x="35" y="95" width="210" height="210" preserveAspectRatio="xMidYMid slice"/>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#151b2c"/></linearGradient>
<linearGradient id="border" gradientUnits="userSpaceOnUse" x1="15" y1="15" x2="835" y2="345"><stop offset="0" stop-color="#58a6ff"/><stop offset=".3" stop-color="#bc8cff"/><stop offset=".55" stop-color="#30363d"/><stop offset=".8" stop-color="#3fb950"/><stop offset="1" stop-color="#58a6ff"/><animateTransform attributeName="gradientTransform" type="rotate" from="0 425 180" to="360 425 180" dur="10s" repeatCount="indefinite"/></linearGradient>
<linearGradient id="border2" gradientUnits="userSpaceOnUse" x1="15" y1="{Y0}" x2="835" y2="{Yend}"><stop offset="0" stop-color="#30363d"/><stop offset=".3" stop-color="#58a6ff"/><stop offset=".6" stop-color="#30363d"/><stop offset=".85" stop-color="#bc8cff"/><stop offset="1" stop-color="#30363d"/><animateTransform attributeName="gradientTransform" type="rotate" from="0 425 {(Y0+Yend)//2}" to="360 425 {(Y0+Yend)//2}" dur="16s" repeatCount="indefinite"/></linearGradient>
<linearGradient id="ring" gradientUnits="userSpaceOnUse" x1="35" y1="95" x2="245" y2="305"><stop offset="0" stop-color="#58a6ff"/><stop offset=".5" stop-color="#bc8cff"/><stop offset="1" stop-color="#3fb950"/><animateTransform attributeName="gradientTransform" type="rotate" from="0 140 200" to="360 140 200" dur="6s" repeatCount="indefinite"/></linearGradient>
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7ee7ff" stop-opacity="0"/><stop offset=".5" stop-color="#7ee7ff" stop-opacity=".38"/><stop offset="1" stop-color="#7ee7ff" stop-opacity="0"/></linearGradient>
<linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#58a6ff" stop-opacity=".55"/><stop offset="1" stop-color="#58a6ff" stop-opacity="0"/></linearGradient>
<linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="sph" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#58a6ff" stop-opacity=".45"/><stop offset=".6" stop-color="#1f6feb" stop-opacity=".14"/><stop offset="1" stop-color="#0d1117" stop-opacity=".1"/></radialGradient>
<radialGradient id="amb"><stop offset="0" stop-color="#1f6feb" stop-opacity=".22"/><stop offset="1" stop-color="#1f6feb" stop-opacity="0"/></radialGradient>
<radialGradient id="base"><stop offset="0" stop-color="#58a6ff" stop-opacity=".55"/><stop offset="1" stop-color="#58a6ff" stop-opacity="0"/></radialGradient>
<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#30363d" opacity=".55"/></pattern>
<pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".4"/></pattern>
<filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="tglow" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="1.3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="fC" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 1 0"/></filter>
<filter id="fM" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0"/></filter>
<clipPath id="card-clip"><rect x="15" y="15" width="820" height="330" rx="10"/></clipPath>
<clipPath id="low-clip"><rect x="15" y="{Y0}" width="820" height="{Yend-Y0}" rx="10"/></clipPath>
<clipPath id="avatar-clip"><rect x="35" y="95" width="210" height="210" rx="8"/></clipPath>
{clips}</defs>

<g class="card">
  <rect class="plate2" x="27" y="31" width="817" height="325" rx="11" fill="#bc8cff" opacity=".10"/>
  <rect class="plate1" x="21" y="23" width="820" height="328" rx="11" fill="#1f6feb" opacity=".18"/>
  <rect x="15" y="15" width="820" height="330" rx="10" fill="none" stroke="url(#border)" stroke-width="3" opacity=".45" filter="url(#blur)"/>
  <rect x="15" y="15" width="820" height="330" rx="10" fill="url(#bg)" stroke="url(#border)" stroke-width="1.5"/>
  <rect x="15" y="48" width="820" height="297" fill="url(#dots)" clip-path="url(#card-clip)"/>
  <rect x="15" y="15" width="820" height="330" rx="10" fill="url(#gloss)" pointer-events="none"/>

  <path d="M 15,25 A 10,10 0 0,1 25,15 L 825,15 A 10,10 0 0,1 835,25 L 835,48 L 15,48 Z" fill="#161b22" stroke="#30363d"/>
  <circle cx="35" cy="31.5" r="5.5" fill="#ed6158"/><circle cx="53" cy="31.5" r="5.5" fill="#fcc02e"/><circle cx="71" cy="31.5" r="5.5" fill="#5fc038"/>
  <text x="425" y="35" class="mono" font-size="12" font-weight="600" text-anchor="middle" fill="#8b949e">profile.sh</text>
  <circle class="live" cx="790" cy="31.5" r="3" fill="#3fb950"/><text x="798" y="35" class="mono" font-size="10" fill="#8b949e">live</text>
  <line x1="15" y1="48" x2="835" y2="48" stroke="#30363d"/>

  {particles}
  {globe}

  <text x="35" y="78" class="mono" font-size="11" font-weight="700" fill="#e6edf3" letter-spacing="1">PROFILE</text>
  <line x1="35" y1="85" x2="245" y2="85" stroke="#30363d"/>
  <line class="sweep" x1="35" y1="85" x2="245" y2="85" stroke="#58a6ff" stroke-width="1.4" stroke-linecap="round"/>

  <!-- hologram projector base -->
  <ellipse cx="140" cy="327" rx="104" ry="11" fill="url(#base)"/>
  <ellipse cx="140" cy="327" rx="78" ry="7" fill="none" stroke="#58a6ff" stroke-opacity=".7"/>
  <ellipse cx="140" cy="327" rx="56" ry="5" fill="#0d1117" stroke="#79c0ff" stroke-opacity=".8"/>
  <ellipse cx="140" cy="327" rx="40" ry="4" fill="none" stroke="#58a6ff" stroke-opacity="0"><animate attributeName="rx" values="40;100" dur="2.8s" repeatCount="indefinite"/><animate attributeName="ry" values="4;10" dur="2.8s" repeatCount="indefinite"/><animate attributeName="stroke-opacity" values=".8;0" dur="2.8s" repeatCount="indefinite"/></ellipse>
  <polygon points="92,326 188,326 238,300 42,300" fill="url(#beam)" opacity=".5"/>
  {motes}

  <g id="holo" class="avatar">
    <rect x="43" y="103" width="210" height="210" rx="8" fill="#1f6feb" opacity=".25"/>
    <rect x="39" y="99" width="210" height="210" rx="8" fill="#bc8cff" opacity=".22"/>
    <rect x="35" y="95" width="210" height="210" rx="8" fill="none" stroke="url(#ring)" stroke-width="3" opacity=".5" filter="url(#blur)"/>
    <rect x="35" y="95" width="210" height="210" rx="8" fill="#0d1117"/>
    <g clip-path="url(#avatar-clip)"><g class="hflick">
      <g id="hstack" class="hstack">
        <g id="gA" class="gA" style="mix-blend-mode:screen" opacity=".55"><use xlink:href="#av" filter="url(#fC)"/></g>
        <use xlink:href="#av"/>
        <g id="gB" class="gB" style="mix-blend-mode:screen" opacity=".4"><use xlink:href="#av" filter="url(#fM)"/></g>
      </g>
      <rect x="35" y="95" width="210" height="210" fill="#58a6ff" opacity=".07"/>
      <rect class="scanl" x="35" y="92" width="210" height="216" fill="url(#scan)" opacity=".55"/>
      <rect class="band" x="35" y="95" width="210" height="26" fill="url(#band)"/>
      <g><animateTransform attributeName="transform" type="translate" values="-90 0;300 0;300 0" keyTimes="0;.35;1" dur="6s" repeatCount="indefinite"/>
        <rect x="0" y="85" width="46" height="230" fill="url(#shine)" transform="skewX(-20)"/></g>
    </g></g>
    <rect x="35" y="95" width="210" height="210" rx="8" fill="none" stroke="url(#ring)" stroke-width="1.8"/>
    <g class="bracket" fill="none" stroke="#58a6ff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M29,111 V89 H51"/><path d="M229,89 H251 V111"/><path d="M29,289 V311 H51"/><path d="M251,289 V311 H229"/></g>
    <text x="43" y="109" class="mono live" font-size="8" letter-spacing="1.5" fill="#7ee7ff">◈ HOLO·ID</text>
    <rect x="45" y="280" width="58" height="17" rx="8.5" fill="#0d1117" fill-opacity=".8" stroke="#30363d"/>
    <circle class="live" cx="56" cy="288.5" r="3" fill="#3fb950"/><text x="63" y="292" class="mono" font-size="9" fill="#c9d1d9">online</text>
  </g>

  <text x="270" y="78" class="mono" font-size="11" font-weight="700" fill="#e6edf3" letter-spacing="1">PROFILE.INFO</text>
  <line x1="270" y1="85" x2="815" y2="85" stroke="#30363d"/>
  <line class="sweep" x1="270" y1="85" x2="815" y2="85" stroke="#58a6ff" stroke-width="1.4" stroke-linecap="round" style="animation-delay:1.2s"/>
  <g class="mono" font-size="11.5">
{rows}  </g>
  {carets}
  <rect x="551" y="309" width="7" height="13" fill="#58a6ff" opacity="0"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" calcMode="discrete" dur="1s" begin="{timing(8)[1]:.2f}s" repeatCount="indefinite"/></rect>
{badges}
</g>

{lower}
<script type="text/ecmascript"><![CDATA[
{JS}
]]></script>
</svg>
'''
with open(P("profile-card.svg"), "w", encoding="utf-8") as output_file:
    output_file.write(svg)
print("built", len(svg), "bytes, height", H, data.get("api_status", "unavailable"))
