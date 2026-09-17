# -*- coding: utf-8 -*-
"""One-off helper: merges data/research/group*.json (web research) with the
titles/fields from the department deck into data/faculty.json and
data/publications.json. After the first build you can edit those two files
directly and never run this again."""
import json, glob, os, re, unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")

# Order, title and fields come from the department deck (slide 1)
DECK = [
    ("Galo Nuño Barrau", "Full Professor", "Monetary economics, macro-finance", ["Galo Nuño"]),
    ("Daniel Fernández Kranz", "Associate Professor", "Labor, family and gender economics; policy evaluation", ["Daniel Fernández Kranz", "Daniel Fernández-Kranz", "Daniel Fernandez-Kranz"]),
    ("Liliana Gelabert", "Associate Professor", "Innovation and environmental economics", ["Liliana Gelabert"]),
    ("Patricia Gabaldón", "Associate Professor", "Gender economics, corporate governance", ["Patricia Gabaldón", "Patricia Gabaldon", "Patricia Gabaldón Quiñones"]),
    ("Sasha Cheipesh", "Postdoctoral Fellow", "Health and labor economics", ["Sasha Cheipesh", "Oleksandra Cheipesh"]),
    ("Toni Roldán", "Assistant Professor", "Education economics, AI and labor markets", ["Toni Roldán", "Toni Roldán Monés", "Antonio Roldán-Monés", "Toni Roldan"]),
    ("Lorenzo Sileci", "Assistant Professor", "Environmental and development economics", ["Lorenzo Sileci"]),
    ("Mattia Fracchia", "Assistant Professor", "Development, behavioral and health economics", ["Mattia Fracchia"]),
    ("Ghassane Benmir", "Assistant Professor", "Macroeconomics, finance and climate economics", ["Ghassane Benmir"]),
    ("Siqi Wei", "Assistant Professor", "Applied econometrics; income and health risks", ["Siqi Wei"]),
    ("Ainara González de San Román", "Assistant Professor", "Gender, education and labor markets", ["Ainara González de San Román"]),
]

def slug(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")

research = {}
for f in glob.glob(os.path.join(DATA, "research", "group*.json")):
    with open(f, encoding="utf-8") as fh:
        for p in json.load(fh):
            research[p["name"]] = p

faculty, pubs, seen = [], [], {}
for name, title, fields, forms in DECK:
    r = research.get(name, {})
    faculty.append({
        "name": name,
        "slug": slug(name),
        "title": title,
        "fields": fields,
        "author_forms": forms,
        "website": r.get("personal_website") or r.get("ie_profile"),
        "ie_profile": r.get("ie_profile"),
        "google_scholar": r.get("google_scholar"),
        "other_links": r.get("other_links") or {},
        "bio": r.get("bio") or "Biography to be added.",
    })
    if not r:
        print("!! no research data yet for", name)
    for p in r.get("publications", []):
        key = re.sub(r"[^a-z0-9]", "", p["title"].lower())[:60]
        if key in seen:            # same paper reached from two co-authors
            continue
        seen[key] = True
        pubs.append({
            "authors": p["authors"], "year": p["year"], "title": p["title"],
            "journal": p["journal"], "volume_pages": p.get("volume_pages") or "",
            "url": p.get("url"),
        })

with open(os.path.join(DATA, "faculty.json"), "w", encoding="utf-8") as f:
    json.dump(faculty, f, ensure_ascii=False, indent=2)
with open(os.path.join(DATA, "publications.json"), "w", encoding="utf-8") as f:
    json.dump(pubs, f, ensure_ascii=False, indent=2)
print(len(faculty), "faculty,", len(pubs), "publications")
