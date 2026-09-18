# -*- coding: utf-8 -*-
"""
Builds the static IEERG web site from the JSON files in data/ into docs/.

Usage:  python build.py
Edit data/faculty.json, data/seminars.json, data/publications.json or
data/hiring.json, run the script again, and upload the contents of docs/.
"""
import json, html, datetime, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
SITE = os.path.join(ROOT, "docs")

def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)

def esc(s):
    return html.escape(s or "", quote=True)

def link(text, url, cls=None, new_tab=True):
    if not url:
        return esc(text)
    c = f' class="{cls}"' if cls else ""
    tgt = ' target="_blank" rel="noopener"' if new_tab else ""
    return f'<a href="{esc(url)}"{c}{tgt}>{esc(text)}</a>'

SCHOOL_URL = "https://www.ie.edu/school-politics-economics-global-affairs/"
DEPT_URL = ("https://www.ie.edu/school-politics-economics-global-affairs/faculty/"
            "?FACULTY_CATEGORY=17173&ACADEMIC_AREA=29470&page=1")
IE_RESEARCH_URL = "https://www.ie.edu/research/"

NAV = [
    ("index.html", "Home"),
    ("faculty.html", "Faculty"),
    ("seminars.html", "Seminar series"),
    ("publications.html", "Publications"),
    ("hiring.html", "We are hiring"),
]

def page(title, active, body, description=""):
    nav = "".join(
        f'<li><a href="{href}"{" class=\"active\"" if href == active else ""}>{esc(label)}</a></li>'
        for href, label in NAV
    )
    year = datetime.date.today().year
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | IEERG</title>
<meta name="description" content="{esc(description or 'IE Economics Research Group (IEERG), Department of Economics, IE University School of Politics, Economics and Global Affairs, Madrid.')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="top">
  <div class="wrap">
    <div class="topbar">
      <a class="brand" href="index.html">
        <img src="img/ie-logo.jpg" alt="IE University, School of Politics, Economics and Global Affairs">
        <span class="name">IE Economics Research Group<small>Department of Economics · IEERG</small></span>
      </a>
      <div class="school-link"><a href="{SCHOOL_URL}" target="_blank" rel="noopener">IE School of Politics, Economics and Global Affairs</a></div>
    </div>
    <nav class="main"><ul>{nav}</ul></nav>
  </div>
</header>
<main>
  <div class="wrap">
{body}
  </div>
</main>
<footer>
  <div class="wrap">
    <span>© {year} IE Economics Research Group · <a href="{DEPT_URL}" target="_blank" rel="noopener">Department of Economics</a>, <a href="{SCHOOL_URL}" target="_blank" rel="noopener">IE University</a></span>
    <span><a href="{IE_RESEARCH_URL}" target="_blank" rel="noopener">Research at IE University</a> · Madrid, Spain</span>
  </div>
</footer>
</body>
</html>
"""

def write(name, content):
    with open(os.path.join(SITE, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", name)

# ---------- helpers for dates ----------
def fmt_date(iso):
    d = datetime.date.fromisoformat(iso)
    day = d.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{d.strftime('%B')} {day}{suffix}, {d.year}"

def fmt_short(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%d %b %Y").lstrip("0")

# ---------- pages ----------
def build_home(faculty, seminars, home):
    now = datetime.datetime.now()
    today = now.date()
    cur = next((y for y in seminars["years"] if y.get("current")), seminars["years"][0])
    # a talk stays "next" until 15:00 on its own day, then the following one takes over
    upcoming = [t for t in sorted(cur["talks"], key=lambda t: t["date"])
                if datetime.date.fromisoformat(t["date"]) > today
                or (datetime.date.fromisoformat(t["date"]) == today and now.hour < 15)]
    nxt = upcoming[0] if upcoming else None
    lg = seminars["logistics"]

    next_box = ""
    if nxt:
        title = f'<div class="ttl">“{esc(nxt["title"])}”</div>' if nxt.get("title") else ""
        where = nxt.get("room") or f"{lg['venue']} ({lg['room']})"
        next_box = f"""
      <div class="next-talk">
        <div class="label">Next seminar · {esc(fmt_date(nxt['date']))}</div>
        <div class="who">{link(nxt['speaker'], nxt.get('url'))} <span class="muted">({esc(nxt['affiliation'])})</span></div>
        {title}
        <div class="note">{esc(lg['weekday'])}, {esc(lg['time'])} · {esc(where)} · <a href="seminars.html">Full programme</a> · <a href="seminars.html#subscribe">Add to your calendar</a></div>
      </div>"""

    def org(o):
        s = link(o["name"], o.get("url"))
        if o.get("email"):
            s += f' (<a href="mailto:{esc(o["email"])}">{esc(o["email"])}</a>)'
        return s
    orgs = home.get("organizers", [])
    parts = [org(o) for o in orgs]
    organizers = " and ".join(parts) if len(parts) <= 2 else ", ".join(parts[:-1]) + " and " + parts[-1]
    organizers_line = (f"<p>The seminar series is currently organized by {organizers}.</p>"
                       if organizers else "")

    body = f"""
    <h1 class="page-title">IE Economics Research Group</h1>
    <hr>
    <div class="home-grid">
      <div>
        <p class="lead">The IE Economics Research Group (IEERG) brings together the research faculty of the
        <a href="{DEPT_URL}" target="_blank" rel="noopener">Department of Economics</a> at
        <a href="{SCHOOL_URL}" target="_blank" rel="noopener">IE University's School of Politics, Economics and Global Affairs (SPEGA)</a>
        in Madrid.</p>
        <p>{esc(home['intro'])}</p>
        <p>The <a href="seminars.html">Economics Research Seminar Series</a> is the main speaker series of the department.
        Talks take place on {esc(lg['weekday'])}, {esc(lg['time'])}, at the {link(lg['venue'], lg.get('venue_url'))}.
        {esc(home.get('mailing_list', ''))}</p>
        {organizers_line}
        {next_box}
        <h2>Visiting us</h2>
        <p>{esc(home['access'])}</p>
        <p class="note">To learn more about research across IE University, visit <a href="{IE_RESEARCH_URL}" target="_blank" rel="noopener">IE Research</a>.</p>
      </div>
      <figure>
        <a href="faculty.html"><img src="img/faculty-montage.jpg" alt="Research faculty of the IE Economics Research Group"></a>
        <figcaption>Research faculty of the Department of Economics. <a href="faculty.html">Meet the group</a>.</figcaption>
      </figure>
    </div>
"""
    return page("Home", "index.html", body)

def build_faculty(faculty):
    cards = []
    for p in faculty:
        links = []
        if p.get("website"): links.append(link("Website", p["website"]))
        if p.get("google_scholar"): links.append(link("Scholar", p["google_scholar"]))
        if p.get("ie_profile"): links.append(link("IE profile", p["ie_profile"]))
        cards.append(f"""
      <div class="person">
        <a href="#{esc(p['slug'])}"><img src="img/{esc(p['slug'])}.jpg" alt="{esc(p['name'])}"></a>
        <div class="pname">{link(p['name'], p.get('website'))}</div>
        <div class="ptitle">{esc(p['title'])}</div>
        <div class="pfields">{esc(p['fields'])}</div>
        <div class="plinks">{' · '.join(links)}</div>
      </div>""")

    bios = []
    for p in faculty:
        links = []
        if p.get("website"): links.append(link("Personal website", p["website"]))
        if p.get("google_scholar"): links.append(link("Google Scholar", p["google_scholar"]))
        if p.get("ie_profile"): links.append(link("IE University profile", p["ie_profile"]))
        for lab, url in (p.get("other_links") or {}).items():
            links.append(link(lab, url))
        bios.append(f"""
      <div class="bio" id="{esc(p['slug'])}">
        <img src="img/{esc(p['slug'])}.jpg" alt="{esc(p['name'])}">
        <div>
          <div class="bname">{esc(p['name'])}</div>
          <div class="btitle">{esc(p['title'])} · {esc(p['fields'])}</div>
          <p>{esc(p['bio'])}</p>
          <div class="blinks">{''.join(links)}</div>
        </div>
      </div>""")

    body = f"""
    <h1 class="page-title">Research Faculty</h1>
    <hr>
    <p class="lead">The research faculty of the Department of Economics work in labor, health, education and inequality;
    development and environmental economics; macroeconomics and finance; and econometrics.
    Click on a name to visit the personal web page.</p>
    <div class="faculty-grid">{''.join(cards)}
    </div>
    <h2>Biographies</h2>
    <div class="bio-list">{''.join(bios)}
    </div>
"""
    return page("Faculty", "faculty.html", body)

def build_seminars(seminars, faculty):
    lg = seminars["logistics"]
    fac_by_name = {p["name"]: p for p in faculty}
    sections = []
    for y in seminars["years"]:
        items = []
        current_month = None
        for t in sorted(y["talks"], key=lambda t: t["date"]):
            d = datetime.date.fromisoformat(t["date"])
            m = d.strftime("%B %Y")
            if m != current_month:
                if items: items.append("</ul>")
                items.append(f'<div class="month">{esc(m)}</div><ul class="talks">')
                current_month = m
            url = t.get("url")
            if t.get("internal") and not url:
                fp = fac_by_name.get(t["speaker"])
                url = fp.get("website") if fp else None
            internal = '<span class="internal">Internal speaker</span>' if t.get("internal") else ""
            meta = []
            if t.get("room"): meta.append(f"Room: {esc(t['room'])}")
            if t.get("host"): meta.append(f"Host: {esc(t['host'])}")
            host = f'<div class="host">{" · ".join(meta)}</div>' if meta else ""
            title = f'<div class="ttl">“{esc(t["title"])}”</div>' if t.get("title") else ""
            items.append(f"""
        <li>
          <div class="date">{esc(fmt_date(t['date']))}</div>
          <div>
            <span class="speaker">{link(t['speaker'], url)}</span> <span class="aff">({esc(t['affiliation'])})</span>{internal}
            {title}{host}
          </div>
        </li>""")
        if items: items.append("</ul>")
        heading = f"Academic year {y['label']}"
        sections.append(f"<h2>{esc(heading)}</h2>" + "".join(items))

    body = f"""
    <h1 class="page-title">Economics Research Seminar Series</h1>
    <hr>
    <div class="logistics">
      <strong>{esc(lg['weekday'])}, {esc(lg['time'])}</strong> · {link(lg['venue'], lg.get('venue_url'))} ({esc(lg['room'])}).
      Economics and Political Science faculty, researchers and students are warmly invited.
    </div>
    {subscribe_box()}
    {''.join(sections)}
    <p class="note" style="margin-top:22px">Dates may change; the page is updated as the programme is confirmed.</p>
"""
    return page("Seminar series", "seminars.html", body)

SITE_URL = "https://ieerg.github.io/"
ICS_NAME = "seminars.ics"

def ics_escape(s):
    return (s or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def ics_fold(line):
    # RFC 5545: lines longer than 75 octets are folded with CRLF + space
    out, cur = [], ""
    for ch in line:
        if len((cur + ch).encode("utf-8")) > 74:
            out.append(cur); cur = " " + ch
        else:
            cur += ch
    out.append(cur)
    return "\r\n".join(out)

def build_ics(seminars, faculty):
    lg = seminars["logistics"]
    fac_by_name = {p["name"]: p for p in faculty}
    t0, t1 = lg["time"].replace("–", "-").split("-")   # "14:00–15:00"
    h0, m0 = t0.strip().split(":"); h1, m1 = t1.strip().split(":")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//IEERG//Economics Research Seminar Series//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        "X-WR-CALNAME:IEERG Economics Research Seminar Series",
        "X-WR-TIMEZONE:Europe/Madrid",
        "X-WR-CALDESC:Economics Research Seminar Series of the IE Economics Research Group (IEERG)\\, IE University\\, Madrid. Updated automatically from " + SITE_URL + "seminars.html",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H",
        "BEGIN:VTIMEZONE", "TZID:Europe/Madrid",
        "BEGIN:DAYLIGHT", "TZOFFSETFROM:+0100", "TZOFFSETTO:+0200", "TZNAME:CEST",
        "DTSTART:19700329T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU", "END:DAYLIGHT",
        "BEGIN:STANDARD", "TZOFFSETFROM:+0200", "TZOFFSETTO:+0100", "TZNAME:CET",
        "DTSTART:19701025T030000", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU", "END:STANDARD",
        "END:VTIMEZONE",
    ]
    for y in seminars["years"]:
        for t in y["talks"]:
            if not t.get("speaker"): continue
            d = t["date"].replace("-", "")
            url = t.get("url")
            if t.get("internal") and not url:
                fp = fac_by_name.get(t["speaker"]); url = fp.get("website") if fp else None
            summary = f"IEERG Seminar: {t['speaker']} ({t['affiliation']})"
            desc = []
            if t.get("title"): desc.append(f"\u201c{t['title']}\u201d")
            if t.get("host"): desc.append(f"Host: {t['host']}")
            if url: desc.append(f"Speaker: {url}")
            desc.append(f"Programme: {SITE_URL}seminars.html")
            location = t.get("room") or f"{lg['venue']} ({lg['room']})"
            lines += [
                "BEGIN:VEVENT",
                f"UID:ieerg-seminar-{t['date']}@ieerg.github.io",
                f"DTSTAMP:{stamp}",
                f"DTSTART;TZID=Europe/Madrid:{d}T{h0}{m0}00",
                f"DTEND;TZID=Europe/Madrid:{d}T{h1}{m1}00",
                f"SUMMARY:{ics_escape(summary)}",
                f"DESCRIPTION:{ics_escape(chr(10).join(desc))}",
                f"LOCATION:{ics_escape(location)}",
                f"URL:{url or SITE_URL + 'seminars.html'}",
                "END:VEVENT",
            ]
    lines.append("END:VCALENDAR")
    body = "\r\n".join(ics_fold(l) for l in lines) + "\r\n"
    with open(os.path.join(SITE, ICS_NAME), "w", encoding="utf-8", newline="") as f:
        f.write(body)
    print("wrote", ICS_NAME)

def subscribe_box():
    import urllib.parse
    ics_url = SITE_URL + ICS_NAME
    webcal = "webcal://" + ics_url.split("://", 1)[1]
    gcal = "https://calendar.google.com/calendar/r?cid=" + webcal
    return f"""
    <div class="subscribe" id="subscribe">
      <strong>Add the seminar series to your calendar.</strong>
      Subscribe once and every talk, with any later change of date, speaker or room, appears in your calendar automatically.
      <div class="sub-links">
        <a href="{gcal}" target="_blank" rel="noopener">Google Calendar</a>
        <a href="{webcal}">Outlook / Apple Calendar</a>
        <a href="{ics_url}" target="_blank" rel="noopener">Download .ics</a>
      </div>
      <div class="note">Feed address, for any other calendar app: <code>{ics_url}</code><br>
      In Google Calendar you can also add it by hand: next to “Other calendars” click <strong>+</strong>, choose <strong>From URL</strong>, paste the address above and click <strong>Add calendar</strong>.</div>
    </div>"""

def build_publications(pubs, faculty):
    fac_names = {p["name"] for p in faculty}
    # map surnames/short forms to bold IEERG members inside author strings
    bold_keys = []
    for p in faculty:
        bold_keys.extend(p.get("author_forms", []) or [])
    bold_keys.sort(key=len, reverse=True)

    def mark_authors(a):
        out = esc(a)
        for k in bold_keys:
            out = re.sub(r"(?<![\w])(" + re.escape(esc(k)) + r")(?![\w])", r'<span class="ieerg">\1</span>', out)
        return out

    def year_key(p):
        y = str(p["year"]).lower()
        return 9999 if "forth" in y else int(y)

    years = sorted({year_key(p) for p in pubs}, reverse=True)
    sections = []
    for yk in years:
        label = "Forthcoming" if yk == 9999 else str(yk)
        entries = sorted([p for p in pubs if year_key(p) == yk], key=lambda p: p["authors"].lower())
        lis = []
        for p in entries:
            vol = f", {esc(p['volume_pages'])}" if p.get("volume_pages") else ""
            fc = ' <span class="fc">(forthcoming)</span>' if "forth" in str(p["year"]).lower() and yk != 9999 else ""
            yr = "" if yk == 9999 else f" ({esc(str(p['year']))})"
            lis.append(
                f'<li>{mark_authors(p["authors"])}{yr}. '
                f'<span class="t">{link(p["title"], p.get("url"), cls="t")}</span>. '
                f'<span class="j">{esc(p["journal"])}</span>{vol}.{fc}</li>'
            )
        sections.append(f'<div class="pub-year">{label}</div><ul class="pubs">{"".join(lis)}</ul>')

    body = f"""
    <h1 class="page-title">Publications</h1>
    <hr>
    <p class="lead">Peer-reviewed journal articles by the research faculty of the IE Economics Research Group,
    listed by year of publication. Names of IEERG members appear in <span class="ieerg">bold</span>.</p>
    {''.join(sections)}
"""
    return page("Publications", "publications.html", body)

def build_hiring(hiring):
    positions = hiring.get("positions") or []
    if positions:
        blocks = []
        for pos in positions:
            facts = "".join(f"<li><strong>{esc(k)}:</strong> {esc(v)}</li>" for k, v in pos.get("facts", []))
            facts = f'<ul class="facts">{facts}</ul>' if facts else ""
            body = []
            for item in pos.get("body", []):
                if "h" in item:
                    body.append(f"<h3>{esc(item['h'])}</h3>")
                elif "ul" in item:
                    body.append("<ul>" + "".join(f"<li>{esc(t)}</li>" for t in item["ul"]) + "</ul>")
                elif "p" in item:
                    t = esc(item["p"])
                    t = re.sub(r"([\w.]+@[\w.]+\.\w+)", r'<a href="mailto:\1">\1</a>', t)
                    body.append(f"<p>{t}</p>")
            apply = f"<p>{link(pos['url_label'], pos['url'])}</p>" if pos.get("url") else ""
            blocks.append(f"""
      <div class="callout">
        <h3 style="margin-top:0">{esc(pos['title'])}</h3>
        {facts}
        {''.join(body)}
        {apply}
      </div>""")
        content = "".join(blocks)
    else:
        content = f'<div class="callout"><p>{esc(hiring["placeholder"])}</p></div>'

    body = f"""
    <h1 class="page-title">We Are Hiring</h1>
    <hr>
    <p class="lead">{esc(hiring['intro'])}</p>
    {content}
    <p>{esc(hiring.get('contact', ''))}</p>
"""
    return page("We are hiring", "hiring.html", body)

def main():
    faculty = load("faculty.json")
    seminars = load("seminars.json")
    pubs = load("publications.json")
    home = load("home.json")
    hiring = load("hiring.json")
    write("index.html", build_home(faculty, seminars, home))
    write("faculty.html", build_faculty(faculty))
    write("seminars.html", build_seminars(seminars, faculty))
    write("publications.html", build_publications(pubs, faculty))
    write("hiring.html", build_hiring(hiring))
    build_ics(seminars, faculty)

if __name__ == "__main__":
    main()
