# slplpower.com — static site

Eight pages, shared stylesheet, no build step required to deploy.

## Favicons

Generated from `V4_LOGO_TRANSPARENT.png` by a one-off script, not by
build.py — they only need regenerating if the mark itself changes.

The tab icons are a navy rounded tile with the mark reversed out in white,
rather than the bare mark on transparent. The mark's bars are thin: at
16px, navy-on-transparent all but disappears against dark browser chrome.
The filled tile reads at every size on any background.

iOS and Android icons are flat navy with no transparency (iOS ignores it),
and the maskable icon keeps the mark inside a 40% safe zone so circular
launcher crops don't clip it.

`site.webmanifest` uses absolute paths (`/assets/icons/...`), so it assumes
the site sits at the domain root. If you deploy into a subfolder, edit
those paths.

## Before you deploy — one edit

`SITE` at the top of `build.py` sets the canonical URLs, the Open Graph
image path and the sitemap. It is currently:

    SITE = 'https://www.slplpower.com'

If the live site ends up on a different host or without the `www`, change
it there and re-run `python3 build.py`. Canonical tags pointing at the
wrong hostname will quietly hurt search ranking.

Point your 404 handler at `404.html`. On Apache:

    ErrorDocument 404 /404.html

## Deploying

Upload the whole folder to your web root. `index.html` is the home page.
Nothing here needs PHP, a database, or a plugin.

If you keep WordPress on the domain, this replaces it — set up 301 redirects
from the old URLs (`/services/`, `/about-us/`, `/service/*`, `/portfolio/*`)
or anything indexed by Google will 404.

## Files

    index.html                          Home
    about.html                          About, history, vision & mission, team
    services.html                       Services hub
    service-testing-commissioning.html  T&C detail
    service-om.html                     O&M detail
    service-power-system-studies.html   Studies detail
    case-studies.html                   Case studies
    careers.html                        Careers
    contact.html                        Contact & offices
    assets/css/base.css                 Layout, glass system, responsive tiers
    assets/css/pages.css                Multi-page components
    assets/js/base.js                   Nav, reveals, dropdown, enquiry form
    assets/img/                         Logo and ISO badges
    404.html                            Not-found page
    sitemap.xml                         Generated — do not edit by hand
    robots.txt                          Generated — do not edit by hand
    assets/img/og-card.png              Social share card (1200x630)
    favicon.ico                         Multi-res tab icon (16/32/48)
    assets/icons/                       PNG favicons, apple-touch, PWA icons
    site.webmanifest                    PWA manifest
    build.py                            Regenerates everything (see below)

## Editing

Nav, footer and repeated sections live in `build.py` so the eight pages
can't drift apart. Change them there and run:

    python3 build.py

Editing an `.html` file directly works too, but the next `build.py` run
overwrites it. For one-off copy edits that's fine; for anything shared,
edit `build.py`.

## Before launch — placeholders

Search the folder for `class="todo"`. Every match is a figure or fact that
needs confirming, and each renders as a loud amber dashed chip so it can't
ship unnoticed. Currently:

  - About / timeline: three years (T&C added, ISO certified, first
    international assignment)
  - Contact: registered office address (delete the card if it's the
    same as the corporate office)

The home metrics band shows two figures only (founded, highest class
commissioned). The km and countries tiles were removed rather than left
as placeholders.

Delete the `<span class="todo">…</span>` wrapper once the real value is in.

## Case studies

The `CASES` table in `build.py` holds three studies. Each has a Situation
(drawn from the company profile), a "What we did", a "Result" and three
outcome tiles. The last three were supplied by SLPL from the job files.

Any change to those figures has to come from the job file, not from a
copywriter. The outcome tiles take only numbers a client could confirm.

If a study can't be filled with real figures, delete it rather than
soften it. Two solid studies beat three vague ones.

## Evidence sections

Three tables in `build.py` drive the material that makes the site
checkable rather than promotional:

  EQUIPMENT   Test instrument inventory -> services.html
  MANPOWER    Engineers by discipline   -> services.html
  DOCUMENTS   Downloadable PDFs         -> contact.html

For DOCUMENTS, drop the PDF into `assets/docs/` using the filename in the
table. A missing file renders as a dashed card naming the file it wants,
and file size is read off disk automatically once it's there.

For EQUIPMENT: list only instruments SLPL actually owns. The entire value
of that table is that it can be verified — an instrument that gets hired
in for a job does not belong on it.

## Gallery (currently off)

Built and working, but disabled. Set `GALLERY_ENABLED = True` in
`build.py` and re-add the nav entry to restore it. Photos go in
`assets/img/gallery/`; read the README.txt there first — it covers PPE,
client-confidential detail and consent.

## Forms

Both forms post JSON to a Vercel function, which sends the mail through
Resend. Nothing depends on the visitor having a mail client.

    api/enquiry.js   Contact page  -> info@slplpower.com
                     ("Careers" chosen as the service -> hr@slplpower.com)
    api/apply.js     Careers page  -> hr@slplpower.com, CV attached
    api/_lib/mail.js Shared validation, rendering and Resend call

The careers form takes a CV as PDF, DOC or DOCX up to 4 MB. The server
checks the file's leading bytes against its extension, so a renamed file of
another type is refused.

Environment variables (Vercel project settings):

    RESEND_API_KEY   required
    ENQUIRY_TO       optional, default info@slplpower.com
    CAREERS_TO       optional, default hr@slplpower.com
    MAIL_FROM        optional, default "SLPL Website <website@send.slplpower.com>"

Tests for both handlers, no dependencies:

    node --test 'tests/*.test.js'
