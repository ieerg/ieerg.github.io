# IE Economics Research Group (IEERG) web site

Static web site, modelled on https://www.ieprg.com/, for the research faculty of the
Department of Economics at IE University (SPEGA).

## Folder layout

| Path | What it is |
|---|---|
| `docs/` | The finished web site. Upload the **contents** of this folder to any web host (GitHub Pages, IE web space, Netlify, etc.). Open `docs/index.html` locally to preview. |
| `docs/img/` | Faculty photos (400x400), the group montage on the home page, and the IE logo. |
| `data/faculty.json` | One entry per research faculty member: name, title, fields, links, bio. Order here is the order on the page. |
| `data/seminars.json` | Seminar logistics and the talks by academic year (date, speaker, affiliation, speaker web page, host, `internal: true` for internal speakers). Add a new `years` block for each academic year; older years stay as the archive. |
| `data/publications.json` | Journal articles, one object each (authors, year, title, journal, volume/pages, url). Use `"year": "forthcoming"` for accepted papers. |
| `data/home.json` | Home page text: intro, mailing-list line, organizers, visitor-access instructions. |
| `data/hiring.json` | "We are hiring" page: intro, list of open positions (title, text, deadline, url), placeholder text when there are none. |
| `build.py` | Generates the five HTML pages in `docs/` from the JSON files, plus `docs/seminars.ics`, the calendar feed people subscribe to (rebuilt from `seminars.json` on every build, so calendars update by themselves). |
| `merge_research.py` | One-off helper used to create the first `faculty.json` / `publications.json` from the web research in `data/research/`. Not needed again. |

## Where it is published

Live site: https://ieerg.github.io/
Repository: https://github.com/ieerg/ieerg.github.io (GitHub Pages serves the `docs/` folder of the `main` branch).

## Updating the site

1. Edit the relevant JSON file in `data/` (any text editor; keep the quotes and commas).
2. Run `python build.py` from this folder.
3. Publish: `git add -A`, `git commit -m "describe the change"`, `git push`. The live site updates within about a minute.

The PowerPoint, Excel and Word source documents in this folder are deliberately excluded from the repository (see `.gitignore`).

To add a faculty member: add a 400x400 JPEG named `<slug>.jpg` to `docs/img/` (slug = lower-case name, accents removed, hyphens for spaces), add the entry to `data/faculty.json`, add their papers to `data/publications.json`, and optionally regenerate `faculty-montage.jpg`.

The author-name variants listed under `author_forms` in `faculty.json` are what the publications page uses to print IEERG members in bold.
