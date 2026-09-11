#!/usr/bin/env python3
"""Generates the SLPL static site. Shared chrome lives here so the eight
pages can never drift apart. Run:  python3 build.py"""
import os, re, pathlib, datetime

ROOT = pathlib.Path(__file__).parent
HERO_SVG = '''<svg class="switchyard" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
    <defs>
      <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#536FA5" stop-opacity="0"/>
        <stop offset="100%" stop-color="#536FA5" stop-opacity=".14"/>
      </linearGradient>
    </defs>

    <g transform="translate(250,-40) scale(.94)">
    <!-- lattice gantry towers -->
    <g class="tower">
      <!-- tower 1 -->
      <path d="M170 880 L215 300 M330 880 L285 300 M215 300 L285 300"/>
      <path d="M196 570 L304 570 M186 700 L314 700 M206 440 L294 440"/>
      <path d="M196 570 L304 700 M304 570 L196 700 M206 440 L294 570 M294 440 L206 570 M186 700 L314 880 M314 700 L186 880"/>
      <path d="M120 340 L380 340 M132 262 L368 262"/>
      <path d="M215 340 L215 262 M285 340 L285 262 M150 340 L150 300 M350 340 L350 300"/>
      <!-- tower 2 -->
      <path d="M900 880 L945 300 M1060 880 L1015 300 M945 300 L1015 300"/>
      <path d="M926 570 L1034 570 M916 700 L1044 700 M936 440 L1024 440"/>
      <path d="M926 570 L1034 700 M1034 570 L926 700 M936 440 L1024 570 M1024 440 L936 570 M916 700 L1044 880 M1044 700 L916 880"/>
      <path d="M850 340 L1110 340 M862 262 L1098 262"/>
      <path d="M945 340 L945 262 M1015 340 L1015 262 M880 340 L880 300 M1080 340 L1080 300"/>
    </g>

    <!-- insulator strings -->
    <g class="insulator">
      <path d="M150 340 v46 M350 340 v46 M880 340 v46 M1080 340 v46 M215 262 v40 M945 262 v40"/>
      <ellipse cx="150" cy="352" rx="9" ry="3.4"/><ellipse cx="150" cy="362" rx="9" ry="3.4"/><ellipse cx="150" cy="372" rx="9" ry="3.4"/>
      <ellipse cx="350" cy="352" rx="9" ry="3.4"/><ellipse cx="350" cy="362" rx="9" ry="3.4"/><ellipse cx="350" cy="372" rx="9" ry="3.4"/>
      <ellipse cx="880" cy="352" rx="9" ry="3.4"/><ellipse cx="880" cy="362" rx="9" ry="3.4"/><ellipse cx="880" cy="372" rx="9" ry="3.4"/>
      <ellipse cx="1080" cy="352" rx="9" ry="3.4"/><ellipse cx="1080" cy="362" rx="9" ry="3.4"/><ellipse cx="1080" cy="372" rx="9" ry="3.4"/>
    </g>

    <!-- catenary conductors + earth wire -->
    <path id="c1" class="conductor" d="M-60 300 Q 80 316 150 386 Q 500 520 880 386 Q 1180 262 1500 320"/>
    <path id="c2" class="conductor" d="M-60 340 Q 120 356 350 386 Q 620 470 1080 386 Q 1280 340 1500 366"/>
    <path id="c3" class="conductor" d="M-60 240 Q 100 250 215 302 Q 580 420 945 302 Q 1220 226 1500 262"/>

    <use href="#c1" class="pulse"/>
    <use href="#c2" class="pulse d2"/>
    <use href="#c3" class="pulse d3"/>

    </g>
    <rect x="0" y="700" width="1440" height="200" fill="url(#fade)"/>
    <path class="conductor" style="opacity:.22" d="M0 880 H1440"/>
  </svg>'''

NAV = [
    ('index.html',   'Home',     None),
    ('about.html',   'About',    None),
    ('services.html','Services', [
        ('service-testing-commissioning.html', 'Testing &amp; Commissioning', 'Up to 765 kV'),
        ('service-om.html',                    'Operation &amp; Maintenance',  '33&ndash;400 kV'),
        ('service-power-system-studies.html',  'Power System Studies',        'ETAP modelling'),
    ]),
    ('case-studies.html', 'Case studies', None),
    ('careers.html', 'Careers',  None),
    ('contact.html', 'Contact',  None),
]

SITE = 'https://www.slplpower.com'   # used for canonical + Open Graph URLs

ORG_JSONLD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Storeleaf Private Limited",
  "alternateName": "SLPL",
  "url": "https://www.slplpower.com",
  "logo": "https://www.slplpower.com/assets/img/logo_full.png",
  "foundingDate": "2016",
  "description": "Testing and commissioning, operation and maintenance, and power system studies for extra high voltage substations and transmission lines.",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "303 Imperial Heights, Near Akshar Chowk, Sun Pharma Road",
    "addressLocality": "Vadodara",
    "addressRegion": "Gujarat",
    "postalCode": "390020",
    "addressCountry": "IN"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+91-96382-99491",
    "email": "info@slplpower.com",
    "contactType": "sales"
  },
  "sameAs": ["https://www.linkedin.com/company/slplpower"],
  "hasCredential": [
    {"@type": "EducationalOccupationalCredential", "credentialCategory": "ISO 9001:2015"},
    {"@type": "EducationalOccupationalCredential", "credentialCategory": "ISO 45001:2018"}
  ]
}
</script>"""


def head(title, desc, page):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE}/assets/img/og-card.png">
<meta property="og:site_name" content="SLPL — Storeleaf Pvt. Ltd.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/assets/img/og-card.png">
<meta name="theme-color" content="#182966">
<link rel="canonical" href="{SITE}/{'' if page == 'index.html' else page}">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="assets/icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/icons/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="assets/icons/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,75..125,400..900&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/base.css">
<link rel="stylesheet" href="assets/css/pages.css">
{ORG_JSONLD if page == "index.html" else ""}
</head>
<body>

<div class="field" aria-hidden="true">
  <div class="orb a"></div><div class="orb b"></div><div class="orb c"></div>
</div>
<a class="skip" href="#main">Skip to content</a>
<div class="scrim" id="scrim" aria-hidden="true"></div>
'''

def nav(page):
    out = ['<nav class="nav" id="nav" aria-label="Main">',
           '  <a href="index.html" aria-label="SLPL home"><img class="logo" src="assets/img/logo_full.png" alt="SLPL — Storeleaf Pvt. Ltd."></a>',
           '  <div class="nav-links" id="links">']
    for href, label, sub in NAV:
        cur = ' aria-current="page"' if href == page else ''
        if sub:
            kids = ''.join(
                f'<a href="{h}">{l}<span>{s}</span></a>' for h, l, s in sub)
            out.append(f'    <div class="has-sub"><a href="{href}"{cur}>{label}</a><div class="sub">{kids}</div></div>')
        else:
            out.append(f'    <a href="{href}"{cur}>{label}</a>')
    out += ['  </div>',
            '  <a href="contact.html" class="btn btn-solid">Request a quote</a>',
            '  <button class="burger" id="burger" aria-label="Toggle menu" aria-expanded="false"><span></span></button>',
            '</nav>']
    return '\n'.join(out) + '\n'

CTA = '''
<section class="band">
  <div class="wrap">
    <div class="glass cta-band rv">
      <h2>Tell us what needs testing, running or solving.</h2>
      <p>Send us the voltage class, location and equipment schedule. We'll come back with a
        view on approach, mobilisation and commercials.</p>
      <div class="hero-cta">
        <a href="contact.html" class="btn btn-solid">Start a conversation
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
        <a href="services.html" class="btn btn-ghost">See what we do</a>
      </div>
    </div>
  </div>
</section>
'''

FOOTER = '''
<footer>
  <div class="wrap">
    <div class="f-grid">
      <div>
        <img class="flogo" src="assets/img/logo_full_white.png" alt="SLPL">
        <p>Storeleaf Private Limited. EHV power infrastructure specialists — testing &amp;
          commissioning, O&amp;M and power system studies, since 2016.</p>
        <div class="f-iso">
          <img src="assets/img/iso_9001.png" alt="ISO 9001:2015">
          <img src="assets/img/iso_45001.png" alt="ISO 45001:2018">
        </div>
      </div>
      <div class="f-col"><h4>Services</h4>
        <a href="service-testing-commissioning.html">Testing &amp; Commissioning</a>
        <a href="service-om.html">Operation &amp; Maintenance</a>
        <a href="service-power-system-studies.html">Power System Studies</a>
      </div>
      <div class="f-col"><h4>Company</h4>
        <a href="about.html">About</a><a href="about.html#vision">Vision &amp; mission</a>
        <a href="about.html#team">Team</a><a href="case-studies.html">Case studies</a>
        <a href="careers.html">Careers</a>
      </div>
      <div class="f-col"><h4>Reach us</h4>
        <a href="tel:+919638299491">+91 96382 99491</a>
        <a href="mailto:info@slplpower.com">info@slplpower.com</a>
        <a href="https://www.linkedin.com/company/slplpower" target="_blank" rel="noopener">LinkedIn</a>
      </div>
    </div>
    <div class="f-bot">
      <span>© <span id="yr">2026</span> Storeleaf Private Limited</span>
      <span>Engineering precision. Operational excellence. Trusted performance.</span>
    </div>
  </div>
</footer>

<script src="assets/js/base.js"></script>
</body>
</html>
'''

def page_hero(crumb, h1, lede):
    trail = ''.join(
        f'<a href="{h}">{l}</a><span>/</span>' if h else f'{l}'
        for h, l in crumb)
    return f'''
<header class="page-hero">
  <div class="wrap">
    <p class="crumb load">{trail}</p>
    <h1 class="load l2">{h1}</h1>
    <p class="lede load l3">{lede}</p>
  </div>
</header>
'''

# ══════════════════════════════════════════════════════════════════
#  Shared content blocks
# ══════════════════════════════════════════════════════════════════

METRICS = '''
<section class="band">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">By the numbers</p>
      <h2>Scale, stated plainly.</h2>
    </div>
    <div class="metrics stg">
      <div class="glass metric"><b>2016</b><span>Year founded<br>in Vadodara</span></div>
      <div class="glass metric"><b>765<em>kV</em></b><span>Highest class<br>commissioned</span></div>
      <div class="glass metric pending"><b>&mdash;<em>km</em></b><span>EHV assets under O&amp;M<br><span class="todo">figure needed</span></span></div>
      <div class="glass metric"><b>3</b><span>Countries with<br>executed projects</span></div>
    </div>
  </div>
</section>
'''

CLIENTS = '''
<section class="band">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">Who we work for</p>
      <h2>Utilities, PSUs <br>and EPC majors.</h2>
      <p class="lede" style="margin-top:20px">Our work reaches the grid through the contractors and
        developers who build it, and directly through the transmission companies who own it. Client
        names and project references are provided on request, subject to their consent.</p>
    </div>
    <div class="clients stg">
      <div class="glass client">State transmission utilities</div>
      <div class="glass client">Central transmission PSUs</div>
      <div class="glass client">EPC contractors</div>
      <div class="glass client">Interstate transmission licensees</div>
      <div class="glass client">Renewable energy developers</div>
      <div class="glass client">Industrial &amp; mining operators</div>
      <div class="glass client">International engineering firms</div>
    </div>
  </div>
</section>
'''

VISION = '''
<section class="band" id="vision">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">What we're aiming at</p>
      <h2>Vision &amp; mission.</h2>
    </div>
    <div class="vm-grid stg">
      <div class="glass vm">
        <h3>Vision</h3>
        <ul>
          <li>To be a trusted leader in EHV power system operations and maintenance, ensuring the
            reliability and resilience of critical transmission infrastructure.</li>
          <li>Deliver technically superior testing, commissioning and protection system services
            that uphold the stability and safety of power networks.</li>
          <li>Set industry benchmarks in operational excellence, quality assurance and electrical
            safety across all substation and transmission projects.</li>
          <li>Strengthen national power infrastructure through engineering precision, disciplined
            execution and continuous technical advancement.</li>
          <li>Create long-term value for utilities, infrastructure operators and stakeholders
            through dependable, standards-driven electrical services.</li>
        </ul>
      </div>
      <div class="glass vm">
        <h3>Mission</h3>
        <ul>
          <li>Deliver reliable O&amp;M services for EHV substations and transmission systems,
            ensuring uninterrupted and safe grid performance.</li>
          <li>Execute testing, commissioning and protection system validation with technical
            precision and strict adherence to national and international standards.</li>
          <li>Uphold uncompromising safety, quality and engineering discipline across all
            substation and transmission assignments.</li>
          <li>Strengthen power system reliability through preventive maintenance, diagnostic
            evaluation and systematic condition monitoring of high-voltage assets.</li>
          <li>Build long-term partnerships with utilities and infrastructure operators through
            dependable service execution and technical excellence.</li>
        </ul>
      </div>
    </div>
  </div>
</section>
'''

# The original draft here was a first-person founder's message written in
# H. D. Sharma's voice. It was never reviewed by him, so it has been
# rewritten as an unattributed company statement — same argument, no words
# put in a real person's mouth. If he writes or approves his own version
# later, restore the personal format: it is stronger when it is genuine.
NOTE = '''
<section class="band">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">Why we exist</p>
      <h2>The gap between the study <br>and the switchyard.</h2>
    </div>
    <div class="glass stmt rv">
      <p class="stmt-lead">Most firms in this sector either model networks or energise them.
        Very few do both — and the gap between the two is where problems hide.</p>
      <div class="stmt-cols">
        <p>A relay setting that is correct on paper can behave differently at two in the morning,
          when a bay is being charged for the first time and the schedule has already slipped.
          Somebody on site has to be able to read the study, read the equipment, and make the call.</p>
        <p>That capability does not come from a procedure manual. It comes from having stood in a
          switchyard for thirty years — which is what our senior technical staff bring, after
          careers spent in state utility service and with multinational contractors.</p>
        <p><strong>SLPL was formed in 2016 to hold both halves of that.</strong> We model networks
          and we commission them. The engineer who prepares a coordination document sits in the
          same team as the engineer who verifies the scheme on site. When something doesn't match,
          it gets caught during the shutdown window rather than in a closeout report six weeks
          later.</p>
        <p>The company has stayed specialised on purpose. We have not diversified into adjacent
          work that would dilute the technical depth, and we have grown carefully —
          <strong>every voltage class on this site is one we have actually worked at</strong>,
          not one we are willing to attempt.</p>
      </div>
    </div>
  </div>
</section>
'''

TEAM = '''
<section class="band" id="team">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">Leadership</p>
      <h2>Sixty-plus years of <br>switchyard experience.</h2>
    </div>
    <div class="team-grid stg">
      <article class="glass member">
        <div class="avatar">HD</div>
        <h3>H. D. Sharma</h3><p class="role">Founder &amp; Technical Advisor</p>
        <p>30+ years in the electrical industry, with a career in state utility services. Maintenance
          of EHV substations and transmission lines, electrical testing and troubleshooting, and
          safety standards in high-voltage environments.</p>
      </article>
      <article class="glass member">
        <div class="avatar">NC</div>
        <h3>Narendra Chauhan</h3><p class="role">Technical Officer</p>
        <p>30+ years with leading multinationals in the operation, maintenance and testing of EHV
          substations. A cornerstone of SLPL's technical delivery capability.</p>
      </article>
      <article class="glass member">
        <div class="avatar">RS</div>
        <h3>Rajhans Sharma</h3><p class="role">Director &amp; Co-Founder</p>
        <p>Master's in engineering from a university in the USA and 12+ years working with
          multinational corporations. Drives growth, innovation and strategic direction across
          project management and advanced engineering solutions.</p>
      </article>
      <article class="glass member">
        <div class="avatar">SS</div>
        <h3>Sagar Sharma</h3><p class="role">Director — Finance &amp; Strategy</p>
        <p>MBA from a university in the USA. Leads financial management, strategic planning and
          business development, bringing depth in financial modelling and risk management.</p>
      </article>
    </div>
  </div>
</section>
'''

SERVICE_CARDS = '''
    <div class="svc-grid stg">
      <a class="glass svc tilt" href="service-testing-commissioning.html">
        <svg class="ic" viewBox="0 0 48 48" stroke-linecap="round" stroke-linejoin="round">
          <rect x="7" y="14" width="34" height="22" rx="3"/><path d="M13 22h7l3 8 4-14 3 6h5"/>
          <path d="M17 14V8M31 14V8M17 42v-6M31 42v-6"/></svg>
        <h3>Testing &amp; Commissioning</h3>
        <p>Pre-commissioning and charging of EHV substations and their equipment — transformers,
          circuit breakers, isolators, CTs, PTs and protection schemes — with calibrated instruments
          and traceable reports.</p>
        <ul>
          <li>Insulation resistance &amp; tan delta</li>
          <li>Breaker timing &amp; dynamic contact resistance</li>
          <li>Relay calibration &amp; scheme verification</li>
          <li>GIS testing up to 765 kV</li>
        </ul>
      </a>
      <a class="glass svc tilt" href="service-om.html">
        <svg class="ic" viewBox="0 0 48 48" stroke-linecap="round" stroke-linejoin="round">
          <path d="M41 24a17 17 0 01-29 12M7 24a17 17 0 0129-12"/><path d="M36 4v8h-8M12 44v-8h8"/>
          <rect x="18" y="18" width="12" height="12" rx="2"/></svg>
        <h3>Operation &amp; Maintenance</h3>
        <p>We take over live substations and transmission lines from 33 kV to 400 kV and keep them
          available — scheduled inspections, predictive diagnostics, shutdown execution and
          breakdown response, with the reporting discipline utilities expect.</p>
        <ul>
          <li>Substation O&amp;M, 33&ndash;400 kV</li>
          <li>Transmission line O&amp;M</li>
          <li>Shutdown planning &amp; execution</li>
          <li>Condition monitoring of HV assets</li>
        </ul>
      </a>
      <a class="glass svc tilt" href="service-power-system-studies.html">
        <svg class="ic" viewBox="0 0 48 48" stroke-linecap="round" stroke-linejoin="round">
          <path d="M7 40V10M7 40h34"/><path d="M13 32l8-11 7 7 11-16"/>
          <circle cx="21" cy="21" r="2.4"/><circle cx="28" cy="28" r="2.4"/></svg>
        <h3>Power System Studies</h3>
        <p>Load flow, short circuit and protection coordination studies in ETAP — the analytical
          layer behind safe, code-compliant operation. We model source to load and hand over
          coordinated relay-setting documents with grading curves.</p>
        <ul>
          <li>Load flow analysis</li>
          <li>Short circuit studies</li>
          <li>Protection coordination &amp; relay settings</li>
          <li>Root cause analysis of failures</li>
        </ul>
      </a>
    </div>
'''

LADDER = '''
<section class="band" id="capability">
  <div class="wrap">
    <div class="glass ladder-shell rv">
      <p class="eyebrow">Voltage classes we work at</p>
      <h2>From 33 kV panels <br>to 765 kV GIS.</h2>
      <p class="lede" style="margin-top:20px">Every class below is work we've actually executed — not a
        capability statement. The higher you go, the fewer contractors can hold the schedule. We hold it.</p>
      <div class="ladder">
        <div class="rail"><i></i></div>
        <div class="ticks">
          <div class="tick"><b>33<em>kV</em></b><p>Panel and switchgear testing on industrial and mining networks. Failure investigation on distribution systems.</p></div>
          <div class="tick"><b>66<em>kV</em></b><p>Substations executed for a state transmission utility.</p></div>
          <div class="tick"><b>220<em>kV</em></b><p>O&amp;M of pooling substations evacuating utility-scale renewable generation.</p></div>
          <div class="tick"><b>400<em>kV</em></b><p>Substation and GIS testing across multiple states, including interstate transmission projects.</p></div>
          <div class="tick"><b>765<em>kV</em></b><p>GIS testing and commissioning — the highest voltage class on the Indian grid.</p></div>
        </div>
      </div>
    </div>
  </div>
</section>
'''


# ══════════════════════════════════════════════════════════════════
#  EVIDENCE BLOCKS
#  The material that separates a credible industrial site from a
#  brochure: things a procurement engineer can check.
# ══════════════════════════════════════════════════════════════════

# ── Test equipment inventory ──────────────────────────────────────
#  (instrument, make & model, used for, calibration status)
#  Replace the placeholder rows with what SLPL actually owns. Do not
#  list an instrument that is hired in — that is the exact claim this
#  table exists to make verifiable.
EQUIPMENT = [
    ('Primary injection set',        '', 'CT saturation, primary current tests',       ''),
    ('Secondary injection / relay test set', '', 'Relay calibration, scheme verification', ''),
    ('Circuit breaker analyser',     '', 'Breaker timing, travel, DCRM',               ''),
    ('CT / VT analyser',             '', 'Ratio, polarity, burden, magnetisation',     ''),
    ('Tan delta / capacitance kit',  '', 'Insulation condition of bushings and CTs',   ''),
    ('Insulation resistance tester', '', 'IR and polarisation index',                  ''),
    ('Winding resistance meter',     '', 'Transformer winding resistance',             ''),
    ('Turns ratio tester',           '', 'Ratio and vector group',                     ''),
    ('Earth resistance tester',      '', 'Earth mat and electrode resistance',         ''),
    ('Thermal imaging camera',       '', 'Hot-spot detection during O&amp;M',              ''),
    ('SF6 gas analyser / handling',  '', 'GIS commissioning and maintenance',          ''),
]

def equipment_rows():
    rows = []
    for inst, model, use, cal in EQUIPMENT:
        m   = model or '<span class="todo">make / model</span>'
        c   = (f'<span class="cal ok">{cal}</span>' if cal
               else '<span class="todo">cal. status</span>')
        rows.append(f'<tr><td>{inst}</td><td class="num">{m}</td><td>{use}</td><td>{c}</td></tr>')
    return '\n        '.join(rows)

EQUIPMENT_SECTION = f"""
<section class="band" id="equipment">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">Resources</p>
      <h2>The instruments <br>we own.</h2>
      <p class="lede" style="margin-top:20px">Most contractors write "state-of-the-art equipment from
        reputed brands." Here is the actual list. It answers the question a technical evaluator is
        really asking — whether we can execute your scope with our own resources, or will be hiring
        instruments when the shutdown window opens.</p>
    </div>
    <div class="glass tbl-wrap rv">
      <table class="tbl">
        <thead><tr><th>Instrument</th><th>Make &amp; model</th><th>Used for</th><th>Calibration</th></tr></thead>
        <tbody>
        {equipment_rows()}
        </tbody>
      </table>
    </div>
    <p class="tbl-note">Calibration certificates are issued against traceable standards and travel
      with the crew to site. Certificates for any listed instrument are available on request.</p>
  </div>
</section>
"""

# ── Manpower ──────────────────────────────────────────────────────
MANPOWER = [
    ('Testing &amp; commissioning engineers', ''),
    ('O&amp;M engineers and shift engineers', ''),
    ('Protection &amp; system studies engineers', ''),
    ('Field technicians', ''),
    ('Total deployable strength', ''),
]

def manpower_rows():
    return '\n        '.join(
        f'<tr><td>{role}</td><td class="num">{n or chr(60)+"span class=" + chr(34) + "todo" + chr(34) + chr(62) + "count" + chr(60) + "/span" + chr(62)}</td></tr>'
        for role, n in MANPOWER)

MANPOWER_SECTION = f"""
<section class="band">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">Resources</p>
      <h2>People on the ground.</h2>
      <p class="lede" style="margin-top:20px">Utilities ask for this at pre-qualification anyway.
        Stating it up front saves a round of correspondence.</p>
    </div>
    <div class="glass tbl-wrap rv">
      <table class="tbl">
        <thead><tr><th>Discipline</th><th>Strength</th></tr></thead>
        <tbody>
        {manpower_rows()}
        </tbody>
      </table>
    </div>
  </div>
</section>
"""

# ── Downloads ─────────────────────────────────────────────────────
#  (filename in assets/docs/, title, meta)
DOCUMENTS = [
    ('slpl-company-profile.pdf', 'Company Profile',            'PDF'),
    ('iso-9001-2015.pdf',        'ISO 9001:2015 certificate',  'Quality management · cert. no. on certificate'),
    ('iso-45001-2018.pdf',       'ISO 45001:2018 certificate', 'Occupational health &amp; safety'),
    ('slpl-hse-policy.pdf',      'HSE policy',                 'Health, safety &amp; environment'),
    ('slpl-quality-policy.pdf',  'Quality policy',             'Signed policy statement'),
    ('slpl-gst-certificate.pdf', 'GST registration',           'Statutory'),
]

DOC_ICON = ('<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>'
            '<path d="M14 2v6h6M12 18v-6M9 15l3 3 3-3"/></svg>')

def document_cards():
    out = []
    for fn, title, meta in DOCUMENTS:
        path = 'assets/docs/' + fn
        if (ROOT / path).exists():
            size = (ROOT / path).stat().st_size // 1024
            out.append(f'<a class="glass dl" href="{path}" download>{DOC_ICON}'
                       f'<div><b>{title}</b><span>{meta} · {size} KB</span></div></a>')
        else:
            out.append(f'<div class="glass dl missing">{DOC_ICON}'
                       f'<div><b>{title}</b><span>{meta}</span><code>{fn}</code></div></div>')
    return '\n      '.join(out)

DOWNLOADS_SECTION = f"""
<section class="band" id="downloads">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">Documents</p>
      <h2>Everything you need <br>for a vendor file.</h2>
      <p class="lede" style="margin-top:20px">Certificates and policies, downloadable rather than
        described. If your procurement team needs something that isn't here, ask and we'll send it.</p>
    </div>
    <div class="dl-grid stg">
      {document_cards()}
    </div>
  </div>
</section>
"""

# ── Governance / registration ─────────────────────────────────────
GOVERNANCE = f"""
<section class="band" id="registration">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">Registration &amp; compliance</p>
      <h2>Company details.</h2>
    </div>
    <div class="glass gov rv">
      <div><span>Legal name</span><p>Storeleaf Private Limited</p></div>
      <div><span>Trading as</span><p>SLPL</p></div>
      <div><span>Incorporated</span><p>2016</p></div>
      <div><span>GSTIN</span><p>24AAXCS4243D1Z8</p></div>
      <div><span>CIN</span><p><span class="todo">CIN</span></p></div>
      <div><span>PAN</span><p><span class="todo">PAN</span></p></div>
      <div><span>Quality</span><p>ISO 9001:2015</p></div>
      <div><span>Cert. no.</span><p><span class="todo">9001 cert. no.</span></p></div>
      <div><span>Safety</span><p>ISO 45001:2018</p></div>
      <div><span>Cert. no.</span><p><span class="todo">45001 cert. no.</span></p></div>
      <div><span>Valid to</span><p><span class="todo">expiry date</span></p></div>
      <div><span>Certifying body</span><p><span class="todo">body / accreditation</span></p></div>
      <div><span>MSME / Udyam</span><p><span class="todo">if registered</span></p></div>
    </div>
    <p class="tbl-note">Registration documents are downloadable above. Vendor registration forms
      and tender-specific declarations can be completed on request.</p>
  </div>
</section>
"""


# ══════════════════════════════════════════════════════════════════
#  Pages
# ══════════════════════════════════════════════════════════════════

PAGES = {}

# ── HOME ──────────────────────────────────────────────────────────
PAGES['index.html'] = dict(
    title='SLPL — EHV Testing, Commissioning &amp; O&amp;M up to 765 kV',
    desc='SLPL (Storeleaf Private Limited), Vadodara. Testing &amp; commissioning, O&amp;M and power '
         'system studies for EHV substations and transmission lines up to 765 kV. ISO 9001:2015 and '
         'ISO 45001:2018 certified.',
    body=f'''
<header class="hero" id="top">
  {HERO_SVG}
  <div class="wrap hero-grid">
    <div class="glass hero-card load">
      <p class="eyebrow">Storeleaf Pvt. Ltd. · Vadodara, Gujarat</p>
      <h1>Testing, commissioning and O&amp;M <br>for networks up to <span class="kv">765&nbsp;kV</span>.</h1>
      <p class="lede">SLPL is an EHV specialist. We test and commission substations and transmission
        assets, run them once they're live, and model them when something needs explaining —
        for utilities, PSUs and EPC contractors across India and overseas.</p>
      <div class="hero-cta">
        <a href="contact.html" class="btn btn-solid">Start a conversation
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
        <a href="services.html" class="btn btn-ghost">See what we do</a>
      </div>
    </div>
    <div class="hero-side">
      <div class="glass stat load l2"><b>2016</b><span>Year<br>founded</span></div>
      <div class="glass stat load l3"><b>Pan-India</b><span>&amp; overseas<br>footprint</span></div>
      <div class="glass iso-row load l4">
        <img src="assets/img/iso_9001.png" alt="ISO 9001:2015 certified">
        <img src="assets/img/iso_45001.png" alt="ISO 45001:2018 certified">
        <p>Quality<br>&amp; safety<br>certified</p>
      </div>
    </div>
  </div>
  <div class="scroll-hint" aria-hidden="true"><i></i>Scroll</div>
</header>
{LADDER}
{METRICS}
<section class="band" id="services">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">What we do</p>
      <h2>Three disciplines, <br>one engineering team.</h2>
    </div>
{SERVICE_CARDS}
  </div>
</section>
{CLIENTS}
{NOTE}
{CTA}
''')

# ── ABOUT ─────────────────────────────────────────────────────────
PAGES['about.html'] = dict(
    title='About — SLPL | Storeleaf Pvt. Ltd.',
    desc='Storeleaf Private Limited (SLPL), founded 2016 in Vadodara. EHV substation and '
         'transmission specialists. Vision, mission, history and leadership.',
    body=page_hero([('index.html','Home'),(None,'About')],
        'A specialist firm, deliberately.',
        "SLPL was established in 2016 to do one thing properly: keep extra high voltage "
        "infrastructure safe, tested and running. We have not diversified away from that.") + f'''
<section class="band">
  <div class="wrap">
    <div class="vm-grid rv" style="align-items:start">
      <div class="glass vm">
        <h3>Who we are</h3>
        <p style="color:var(--muted);margin-bottom:15px">Storeleaf Private Limited trades as SLPL and
          operates from Vadodara, Gujarat. Since 2016 we have provided specialised services for extra
          high voltage power system infrastructure — comprehensive operation and maintenance for EHV
          substations and transmission lines, ensuring system reliability, operational safety and
          sustained performance across critical power networks.</p>
        <p style="color:var(--muted);margin-bottom:15px">We specialise in testing, commissioning and
          diagnostic evaluation of EHV substations and associated transmission assets. Our expertise
          covers protection system testing, relay coordination verification, electrical diagnostic
          services and condition assessment of high-voltage equipment.</p>
        <p style="color:var(--muted)">Our strength lies in combining engineering rigour with field
          execution capability — supporting utilities, government bodies and private sector clients
          in maintaining resilient and efficient power transmission infrastructure.</p>
      </div>
      <div class="glass vm">
        <h3>Company facts</h3>
        <div class="spec"><span>Legal entity</span><p>Storeleaf Private Limited (SLPL)</p></div>
        <div class="spec"><span>Established</span><p>2016</p></div>
        <div class="spec"><span>Industry</span><p>Power &amp; energy infrastructure</p></div>
        <div class="spec"><span>Specialisation</span><p>EHV substations, transmission lines, O&amp;M, T&amp;C</p></div>
        <div class="spec"><span>Service geographies</span><p>Pan-India, and overseas</p></div>
        <div class="spec"><span>Certifications</span><p>ISO 9001:2015 · ISO 45001:2018<br>
          <span style="font-family:var(--mono);font-size:.72rem;color:var(--steel)">Certified by <span class="todo">certifying body</span> under <span class="todo">accreditation</span></span></p></div>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">How we got here</p>
      <h2>Ten years, <br>one direction.</h2>
    </div>
    <div class="timeline rv">
      <div class="tl">
        <b>2016</b>
        <h4>Storeleaf Private Limited incorporated</h4>
        <p>Founded in Vadodara, with O&amp;M of EHV substations and transmission lines as the
          initial scope.</p>
      </div>
      <div class="tl">
        <b><span class="todo">YEAR</span></b>
        <h4>Testing &amp; commissioning added as a discipline</h4>
        <p>Investment in calibrated diagnostic instruments moved SLPL from maintaining assets to
          proving them — insulation resistance, tan delta, breaker timing and relay calibration.</p>
      </div>
      <div class="tl">
        <b><span class="todo">YEAR</span></b>
        <h4>ISO 9001:2015 and ISO 45001:2018 certified</h4>
        <p>Formal quality management and occupational health &amp; safety systems, audited and
          maintained across all substation and transmission assignments.</p>
      </div>
      <div class="tl">
        <b><span class="todo">YEAR</span></b>
        <h4>First international assignment</h4>
        <p>Panel and equipment testing for a mining operation in East Africa, followed by root
          cause analysis of 33 kV PT and RMU failures for a distribution utility in the Middle East.</p>
      </div>
      <div class="tl">
        <b>2025–26</b>
        <h4>765 kV — the highest class on the Indian grid</h4>
        <p>Testing and commissioning of 765 kV gas insulated switchgear on a major renewable
          energy park transmission build-out, alongside 400 kV substation testing in several states.</p>
      </div>
      <div class="tl now">
        <b>2026–27</b>
        <h4>Power system studies as a third pillar</h4>
        <p>ETAP-based load flow, short circuit and protection coordination studies now run
          alongside field delivery, closing the loop between analysis and execution.</p>
      </div>
    </div>
  </div>
</section>
{VISION}
{NOTE}
{TEAM}
{CTA}
''')

# ── SERVICES HUB ──────────────────────────────────────────────────
PAGES['services.html'] = dict(
    title='Services — SLPL | EHV Testing, O&amp;M and Power System Studies',
    desc='Testing &amp; commissioning up to 765 kV, operation &amp; maintenance of EHV substations and '
         'transmission lines, and ETAP power system studies.',
    body=page_hero([('index.html','Home'),(None,'Services')],
        'Three disciplines, one engineering team.',
        "The engineer who prepares the coordination study is in the same team as the engineer who "
        "verifies the scheme on site. That is the whole point of how we're organised.") + f'''
<section class="band" style="padding-top:0">
  <div class="wrap">
{SERVICE_CARDS}
  </div>
</section>
{LADDER}
{EQUIPMENT_SECTION}
{MANPOWER_SECTION}
{CLIENTS}
{CTA}
''')

# ── SERVICE DETAIL PAGES ──────────────────────────────────────────
def service_page(slug, title, desc, h1, lede, blocks, specs):
    spec_html = ''.join(
        f'<div class="spec"><span>{k}</span><p>{v}</p></div>' for k, v in specs)
    body_html = ''
    for heading, paras, items in blocks:
        body_html += f'<h2>{heading}</h2>'
        for p in paras:
            body_html += f'<p>{p}</p>'
        if items:
            body_html += '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
    PAGES[slug] = dict(title=title, desc=desc,
        body=page_hero([('index.html','Home'),('services.html','Services'),(None,h1)], h1, lede) + f'''
<section class="band" style="padding-top:0">
  <div class="wrap detail">
    <div class="glass detail-main rv">{body_html}</div>
    <aside class="glass aside rv">
      <h4>At a glance</h4>
      {spec_html}
      <a href="contact.html" class="btn btn-solid">Request a quote
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
    </aside>
  </div>
</section>
{CTA}
''')

service_page('service-testing-commissioning.html',
  'Testing &amp; Commissioning — SLPL',
  'Pre-commissioning, charging and diagnostic testing of EHV substation equipment up to 765 kV.',
  'Testing &amp; Commissioning',
  'Proving that a substation will do what the drawings say it will — before it is energised, '
  'and with documentation that survives audit.',
  [
   ('What we do', [
     'SLPL offers comprehensive substation testing for all critical equipment, including power '
     'transformers, circuit breakers, isolators, instrument transformers and protection relays. '
     'Testing establishes that equipment has arrived undamaged, has been erected correctly, and '
     'will behave as designed under fault conditions.',
     'We use calibrated instruments from established manufacturers, and calibration certificates '
     'travel with the crew. Test values are recorded against nameplate and design figures, and '
     'anything anomalous is raised during the shutdown window rather than in the closeout report.'], []),
   ('Tests we perform', [], [
     'Insulation resistance and polarisation index','Tan delta and capacitance',
     'Winding resistance','Turns ratio and vector group',
     'Breaker timing and dynamic contact resistance','Circuit breaker operation and interlock checks',
     'Relay calibration and secondary injection','Protection scheme verification and end-to-end testing',
     'CT ratio, polarity, magnetisation and burden','PT ratio and polarity',
     'GIS testing and SF6 handling','Transformer oil analysis',
     'Earth resistance and earth mat continuity','Cable HV testing']),
   ('Equipment classes', [
     'We work across the full band — 765 kV gas insulated switchgear, 400 kV substations across '
     'several states, 220 kV pooling substations, 66 kV substations for a state transmission '
     'utility, and 33 kV panels and switchgear on industrial and mining sites.'], []),
   ('What you receive', [
     'A complete test file: individual equipment test formats in your reporting template, '
     'instrument calibration certificates, a summary of deviations with recommended action, '
     'and charging clearance documentation.'], []),
  ],
  [('Voltage range','33 kV to 765 kV'),('Equipment','Transformers, breakers, CTs, PTs, isolators, relays'),
   ('Technologies','AIS and GIS'),('Deliverable','Test file, calibration certificates, deviation report'),
   ('Certification','ISO 9001:2015 · ISO 45001:2018')])

service_page('service-om.html',
  'Operation &amp; Maintenance — SLPL',
  'O&amp;M of EHV substations and transmission lines — inspections, predictive diagnostics, '
  'shutdown execution and breakdown response.',
  'Operation &amp; Maintenance',
  'Taking responsibility for live assets from 33 kV to 400 kV and keeping them available — with '
  'the reporting discipline a utility expects from its own staff.',
  [
   ('What we do', [
     'SLPL provides specialised operation and maintenance for transmission lines and electrical '
     'substations from 33 kV to 400 kV. Our teams handle regular inspections, predictive '
     'diagnostics and timely repairs, minimising downtime and protecting the longevity of the '
     'asset.',
     'For substations we deliver system monitoring, troubleshooting and preventive maintenance to '
     'ensure uninterrupted power delivery and operational safety, working to the highest industry '
     'standards and with dedicated, trained personnel deployed on site.'], []),
   ('Scope of work', [], [
     'Round-the-clock substation operation','Preventive maintenance to schedule',
     'Predictive and condition-based diagnostics','Transmission line patrolling and inspection',
     'Shutdown planning, execution and restoration','Breakdown response and fault rectification',
     'Spares management and consumables','Statutory compliance and log maintenance',
     'Thermography and hot-spot detection','Battery bank and DC system upkeep']),
   ('How we mobilise', [
     'Scope is agreed against the equipment schedule and maintenance formats before mobilisation, '
     'not after. Manpower deployment, shift patterns, escalation routes and reporting cadence are '
     'fixed at contract stage so there is no ambiguity when something goes wrong at 2 a.m.'], []),
   ('Track record', [
     'Current and recent assignments include a 220 kV pooling substation evacuating 300 MW of '
     'solar generation in northwestern India, and windfarm plus transmission line O&amp;M in '
     'Gujarat. References are available on request, subject to client consent.'], []),
  ],
  [('Assets','Substations and transmission lines'),('Voltage range','33 kV to 400 kV'),
   ('Coverage','Pan-India'),('Model','Deployed teams, AMC or campaign basis'),
   ('Certification','ISO 9001:2015 · ISO 45001:2018')])

service_page('service-power-system-studies.html',
  'Power System Studies — SLPL',
  'ETAP load flow, short circuit and protection coordination studies for industrial and utility '
  'electrical networks.',
  'Power System Studies',
  'The analytical layer behind safe operation — modelled source to load, and handed over as '
  'documents your protection engineer can actually apply.',
  [
   ('What we do', [
     'SLPL delivers comprehensive power system studies for industrial and utility electrical '
     'networks, covering load flow analysis, short circuit studies and protection coordination, '
     'executed using industry-standard software including ETAP. Our studies provide the analytical '
     'foundation for safe, reliable and code-compliant electrical system design and operation.',
     'Our engineering team reviews existing protection settings, models the complete network from '
     'source to load, and prepares fully coordinated relay-setting documents with time-current '
     'grading curves. Studies are conducted across MV and LV systems including indoor '
     'switchboards, outdoor reclosers, transformers and large motor drives.'], []),
   ('Studies we run', [], [
     'Load flow analysis','Short circuit and fault level studies',
     'Protection coordination and grading','Relay setting calculation and documentation',
     'Motor starting and acceleration','Network modelling from source to load',
     'Root cause analysis of equipment failures','Review of existing protection settings']),
   ('Why field experience matters here', [
     'A coordination study prepared by someone who has never commissioned a bay tends to produce '
     'settings that are theoretically correct and practically unworkable. Because the same team '
     'tests and energises substations, our studies account for what the equipment actually does — '
     'CT saturation, breaker operating times, and the realities of the installed base.'], []),
   ('What you receive', [
     'A study report with assumptions and methodology stated, time-current grading curves, a '
     'relay setting schedule ready for application, and the ETAP model files themselves so your '
     'team can maintain the model as the network changes.'], []),
  ],
  [('Software','ETAP'),('Network levels','EHV, MV and LV'),
   ('Typical scope','Load flow, short circuit, coordination'),
   ('Deliverable','Study report, grading curves, setting schedule, ETAP model files'),
   ('Also available','Failure root cause analysis')])

# ── CAREERS ───────────────────────────────────────────────────────
PAGES['careers.html'] = dict(
    title='Careers — SLPL | Storeleaf Pvt. Ltd.',
    desc='Work with SLPL on EHV substations and transmission lines up to 765 kV. '
         'Testing, commissioning, O&amp;M and power system studies.',
    body=page_hero([('index.html','Home'),(None,'Careers')],
        'Work where the voltage is real.',
        "There are a lot of places to be an electrical engineer. Very few of them put you in a "
        "765 kV switchyard in your first years.") + '''
<section class="band" style="padding-top:0">
  <div class="wrap">
    <div class="values stg">
      <div class="glass value">
        <b>01 — Exposure</b>
        <h3>The full voltage range</h3>
        <p>Our engineers work at 33 kV and at 765 kV, on AIS and GIS, in the field and in the model.
          You are not assigned to one narrow equipment type and left there.</p>
      </div>
      <div class="glass value">
        <b>02 — Safety</b>
        <h3>Non-negotiable, not decorative</h3>
        <p>We hold ISO 45001:2018 certification for occupational health and safety. Nobody is asked
          to take a shortcut to hold a schedule. If a permit isn't right, work stops.</p>
      </div>
      <div class="glass value">
        <b>03 — Depth</b>
        <h3>Learn from thirty-year engineers</h3>
        <p>Our senior technical staff have three decades each in EHV substations. That knowledge
          transfers by working alongside them, which is how this trade has always been taught.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">Who we hire</p>
      <h2>What we look for.</h2>
      <p class="lede" style="margin-top:20px">Electrical engineering qualifications matter, but they
        are the entry condition rather than the decision. What separates candidates is whether they
        are careful with detail under time pressure, willing to be mobile — much of this work happens
        at remote substation sites for weeks at a stretch — and honest when a reading doesn't look
        right. We can teach the rest.</p>
    </div>

    <div class="roles stg">
      <div class="glass role-row">
        <div>
          <h4>Testing &amp; Commissioning Engineer</h4>
          <p>EHV substations · Site-based, pan-India · <span class="todo">openings?</span></p>
        </div>
        <a href="mailto:info@slplpower.com?subject=Application%20%E2%80%94%20Testing%20%26%20Commissioning%20Engineer" class="btn btn-ghost">Apply</a>
      </div>
      <div class="glass role-row">
        <div>
          <h4>O&amp;M Engineer / Shift Engineer</h4>
          <p>Substations &amp; transmission lines · Deployed · <span class="todo">openings?</span></p>
        </div>
        <a href="mailto:info@slplpower.com?subject=Application%20%E2%80%94%20O%26M%20Engineer" class="btn btn-ghost">Apply</a>
      </div>
      <div class="glass role-row">
        <div>
          <h4>Protection &amp; Power System Studies Engineer</h4>
          <p>ETAP modelling · Vadodara office · <span class="todo">openings?</span></p>
        </div>
        <a href="mailto:info@slplpower.com?subject=Application%20%E2%80%94%20Power%20System%20Studies%20Engineer" class="btn btn-ghost">Apply</a>
      </div>
      <div class="glass role-row">
        <div>
          <h4>Field Technician</h4>
          <p>Substation testing support · Site-based · <span class="todo">openings?</span></p>
        </div>
        <a href="mailto:info@slplpower.com?subject=Application%20%E2%80%94%20Field%20Technician" class="btn btn-ghost">Apply</a>
      </div>
    </div>

    <div class="glass cta-band rv" style="margin-top:40px">
      <h2>Nothing listed that fits?</h2>
      <p>Send your CV anyway. We keep good engineers on file and our project pipeline moves faster
        than this page does.</p>
      <div class="hero-cta">
        <a href="mailto:info@slplpower.com?subject=Speculative%20application" class="btn btn-solid">Send your CV
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      </div>
    </div>
  </div>
</section>
''')

# ── CONTACT ───────────────────────────────────────────────────────
PAGES['contact.html'] = dict(
    title='Contact — SLPL | Storeleaf Pvt. Ltd., Vadodara',
    desc='Contact SLPL for EHV testing &amp; commissioning, O&amp;M and power system studies. '
         'Vadodara, Gujarat. info@slplpower.com · +91 96382 99491',
    body=page_hero([('index.html','Home'),(None,'Contact')],
        'Tell us what needs testing, running or solving.',
        "We work with utilities, government bodies, EPC contractors and private developers. Send the "
        "scope and we'll come back with a view on approach, mobilisation and commercials.") + '''
<section class="band" style="padding-top:0">
  <div class="wrap">
    <div class="contact-grid stg">
      <div class="glass info">
        <div class="info-row">
          <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2 2 2 0 014.1 2h3a2 2 0 012 1.7c.1 1 .4 1.9.7 2.8a2 2 0 01-.5 2.1L8.1 9.9a16 16 0 006 6l1.3-1.3a2 2 0 012.1-.4c.9.3 1.8.6 2.8.7a2 2 0 011.7 2z"/></svg>
          <div><span>Phone</span><a href="tel:+919638299491">+91 96382 99491</a></div>
        </div>
        <div class="info-row">
          <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 7l10 6 10-6"/></svg>
          <div><span>Email</span><a href="mailto:info@slplpower.com">info@slplpower.com</a></div>
        </div>
        <div class="info-row">
          <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/><path d="M10 21V9m0 4a4 4 0 018 0v8"/></svg>
          <div><span>LinkedIn</span><a href="https://www.linkedin.com/company/slplpower" target="_blank" rel="noopener">linkedin.com/company/slplpower</a></div>
        </div>
        <div class="info-row">
          <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V7l7-4 7 4v14M9 9h2m4 0h2M9 13h2m4 0h2M9 17h2m4 0h2"/></svg>
          <div><span>Certifications</span><p>ISO 9001:2015 · ISO 45001:2018</p></div>
        </div>
      </div>

      <div class="glass form">
        <div class="f-row">
          <div class="fld"><label for="nm">Name</label><input id="nm" type="text" placeholder="Your name"></div>
          <div class="fld"><label for="org">Organisation</label><input id="org" type="text" placeholder="Company"></div>
        </div>
        <div class="f-row">
          <div class="fld"><label for="em">Email</label><input id="em" type="email" placeholder="you@company.com"></div>
          <div class="fld"><label for="ph">Phone</label><input id="ph" type="tel" placeholder="+91"></div>
        </div>
        <div class="fld"><label for="sv">Service required</label>
          <select id="sv">
            <option>Testing &amp; Commissioning</option>
            <option>Operation &amp; Maintenance</option>
            <option>Power System Studies</option>
            <option>Careers</option>
            <option>Something else</option>
          </select>
        </div>
        <div class="fld"><label for="ms">Scope</label>
          <textarea id="ms" placeholder="Voltage class, location, equipment schedule, target dates…"></textarea></div>
        <div class="fld hp" aria-hidden="true"><label for="wb">Website</label>
          <input id="wb" type="text" tabindex="-1" autocomplete="off"></div>
        <button class="btn btn-solid" id="send">Send enquiry
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>
        <p class="form-status" id="fs" role="status" aria-live="polite"></p>
        <small>Goes straight to info@slplpower.com. We reply within one working day.</small>
      </div>
    </div>
  </div>
</section>

<section class="band" style="padding-top:0">
  <div class="wrap">
    <div class="rv">
      <p class="eyebrow">Where to find us</p>
      <h2>Our offices.</h2>
    </div>
    <div class="offices stg">
      <div class="glass office">
        <b>Corporate office</b>
        <p>303, Imperial Heights<br>Near Akshar Chowk, Sun Pharma Road<br>Vadodara, Gujarat 390020<br>India</p>
        <a href="https://maps.app.goo.gl/FSakBF4zrxXLy9jH6" target="_blank" rel="noopener" class="btn btn-ghost" style="margin-top:20px">Open in Maps</a>
      </div>
      <div class="glass office">
        <b>Registered office</b>
        <p><span class="todo">Confirm registered office address</span><br>
          <span style="font-size:.88rem;color:var(--muted)">If this is the same as the corporate
          office above, this card should be deleted rather than duplicated.</span></p>
      </div>
    </div>
  </div>
</section>
''' + DOWNLOADS_SECTION + GOVERNANCE)


# ══════════════════════════════════════════════════════════════════
#  CASE STUDIES
#  Structure only. The "Situation" text is drawn from the project
#  table in the company profile and is safe to publish. Everything
#  under "What we did" and "Result" is marked TODO on purpose —
#  writing it would mean inventing engineering: the failure mechanism
#  in the Saudi PT/RMU case, the test findings at Khavda, the
#  availability figures at Nokhra. Those come from the job file.
#
#  A good case study is one problem, one method, one measurable
#  result. Three strong ones beat ten thin ones.
# ══════════════════════════════════════════════════════════════════
def T(s):
    return '<span class="todo">' + s + '</span>'

CASES = [
    dict(
        kv='33<em>kV</em>',
        title='Root cause analysis of repeated PT and RMU failures',
        meta=[('Client', 'International engineering firm'), ('End user', 'Distribution utility, Middle East'),
              ('Scope', 'System study &amp; RCA'), ('Discipline', 'Power system studies')],
        situation=[
            'Potential transformers and ring main units on a 33 kV network were failing '
            'repeatedly. Replacement had not stopped recurrence, which meant the cause lay in '
            'the system rather than in the individual units.',
            'SLPL was engaged through the project consultancy to establish why.'],
        did=[T('Describe the investigation: what was measured or modelled, what network data was '
               'pulled, which failure modes were tested and eliminated.')],
        result=[T('State the root cause found and the corrective recommendation, then the '
                  'outcome — whether failures stopped after implementation.')],
        outcomes=[('&mdash;', 'Failures before'), ('&mdash;', 'Failures after'),
                  ('&mdash;', 'Time to diagnosis')]),

    dict(
        kv='765<em>kV</em>',
        title='GIS testing and commissioning on a 765 kV transmission build-out',
        meta=[('Client', 'EPC contractor'), ('End user', 'Central transmission PSU'),
              ('Scope', 'Testing &amp; commissioning'), ('Period', '2025&ndash;26, 2026&ndash;27')],
        situation=[
            'The substation forms part of the transmission build-out for the largest renewable '
            'energy park in India. At 765 kV, gas insulated switchgear leaves no margin for a test '
            'regime that is anything less than complete.',
            'SLPL was appointed for testing and commissioning of the GIS.'],
        did=[T('Describe the scope in numbers: how many bays, which equipment, which tests, over '
               'what duration, with how many engineers deployed.')],
        result=[T('State the outcome — charging achieved on schedule, defects caught before '
                  'energisation, or whatever the job file actually supports.')],
        outcomes=[('&mdash;', 'Bays commissioned'), ('&mdash;', 'Engineers deployed'),
                  ('&mdash;', 'Schedule variance')]),

    dict(
        kv='220<em>kV</em>',
        title='O&amp;M of a 300 MW solar pooling substation',
        meta=[('Client', 'Renewable energy developer'), ('Region', 'Northwestern India'),
              ('Scope', 'Operation &amp; maintenance'), ('Discipline', 'O&amp;M')],
        situation=[
            'A 220 kV pooling substation evacuating 300 MW of solar generation. Every hour the '
            'substation is unavailable is generation that cannot reach the grid, so availability '
            'is the metric the contract turns on.',
            'SLPL took over operation and maintenance of the station.'],
        did=[T('Describe the O&amp;M regime: manpower deployed, shift pattern, preventive '
               'schedule, diagnostics used, escalation and response arrangements.')],
        result=[T('State availability achieved, breakdowns attended and mean restoration time — '
                  'figures the client can confirm.')],
        outcomes=[('&mdash;', 'Availability'), ('&mdash;', 'Breakdowns attended'),
                  ('&mdash;', 'Mean restoration')]),
]


def case_blocks():
    out = []
    for c in CASES:
        meta = ''.join('<div><span>%s</span><p>%s</p></div>' % kv for kv in c['meta'])
        sit = ''.join('<p>%s</p>' % p for p in c['situation'])
        did = ''.join('<p>%s</p>' % p for p in c['did'])
        res = ''.join('<p>%s</p>' % p for p in c['result'])
        outs = ''.join('<div><b>%s</b><span>%s</span></div>' % nl for nl in c['outcomes'])
        out.append(
            '<article class="glass case rv">\n'
            '      <div class="case-head">\n'
            '        <h3>' + c['title'] + '</h3>\n'
            '        <div class="case-kv">' + c['kv'] + '</div>\n'
            '      </div>\n'
            '      <div class="case-meta">' + meta + '</div>\n'
            '      <div class="case-body">\n'
            '        <div><h4>Situation</h4>' + sit + '</div>\n'
            '        <div><h4>What we did</h4>' + did + '</div>\n'
            '        <div><h4>Result</h4>' + res + '</div>\n'
            '      </div>\n'
            '      <div class="case-out">' + outs + '</div>\n'
            '    </article>')
    return '\n    '.join(out)


PAGES['case-studies.html'] = dict(
    title='Case studies — SLPL | EHV testing, commissioning and O&amp;M',
    desc='Detailed accounts of SLPL work: 765 kV GIS testing and commissioning, 220 kV substation '
         'O&amp;M for a solar pooling station, and root cause analysis of repeated 33 kV PT and RMU failures.',
    body=page_hero([('index.html', 'Home'), (None, 'Case studies')],
                   'One problem, one method, one result.',
                   'Three jobs described properly, rather than a list of everything we have ever '
                   'touched. Client and site identities are withheld; full references are available '
                   'on request, subject to their consent.')
         + '\n<section class="band" style="padding-top:0">\n  <div class="wrap">\n    '
         + case_blocks()
         + '\n  </div>\n</section>\n' + CTA)


# ══════════════════════════════════════════════════════════════════
#  GALLERY
#  Add a photo: drop the file into assets/img/gallery/ and add a row
#  below, then run `python3 build.py`. A row whose file is missing
#  renders as a dashed empty slot naming the file it wants — so the
#  page always tells you what is outstanding.
#
#    (filename, caption, meta line, category, wide?)
#  category must be one of: substation | tc | om | team
# ══════════════════════════════════════════════════════════════════
GALLERY_ENABLED = False   # flip to True (and re-add the nav entry) to restore the gallery

GALLERY_CATS = [('all','All'),('substation','Substations'),
                ('tc','Testing &amp; Commissioning'),('om','O&amp;M'),('team','Team &amp; site')]

GALLERY = [
    ('khavda-765-gis.jpg',      '765 kV GIS bay, KPS-2 Khavda',              'Testing &amp; commissioning · KEC for PGCIL · Gujarat', 'substation', True),
    ('khavda-gis-hall.jpg',     'GIS hall during commissioning',             'KPS-2 Khavda · Gujarat',                               'substation', False),
    ('getco-66kv.jpg',          '66 kV substation for GETCO',                'Gujarat state transmission utility',                   'substation', False),
    ('nagaland-400kv.jpg',      '400 kV substation, Nagaland',               'Kohima-Mariani Transmission Ltd.',                     'substation', False),
    ('koppal-400kv.jpg',        '400 kV switchyard, Koppal',                 'Karnataka Power Transmission Corp.',                   'substation', False),
    ('transformer-testing.jpg', 'Power transformer testing',                 'Tan delta and winding resistance',                     'tc',         False),
    ('breaker-timing.jpg',      'Circuit breaker timing test',               'Dynamic contact resistance measurement',               'tc',         True),
    ('relay-testing.jpg',       'Protection relay calibration',              'Secondary injection and scheme verification',          'tc',         False),
    ('ct-testing.jpg',          'Instrument transformer testing',            'CT ratio, polarity and magnetisation',                 'tc',         False),
    ('nokhra-om.jpg',           '220 kV Nokhra NTPC pooling substation',     'O&amp;M · Vikram Solar · Rajasthan',                   'om',         False),
    ('line-patrol.jpg',         'Transmission line patrolling',              'Routine inspection',                                   'om',         False),
    ('shutdown-work.jpg',       'Shutdown maintenance',                      'Planned outage execution',                             'om',         False),
    ('tanzania-panels.jpg',     '33 kV panel testing, Barrick Goldmines',    'Ishan Ltd. · Tanzania',                                'tc',         False),
    ('site-team.jpg',           'Commissioning crew on site',                'Full PPE, permit-to-work in force',                    'team',       False),
    ('etap-modelling.jpg',      'Network modelling in ETAP',                 'Protection coordination study',                        'team',       False),
]

def gallery_tiles():
    out = []
    for fn, cap, meta, cat, wide in GALLERY:
        w = ' wide' if wide else ''
        path = 'assets/img/gallery/' + fn
        if (ROOT / path).exists():
            out.append(
                f'<figure class="tile{w}" data-c="{cat}" data-full="{path}" '
                f'data-caption="{cap}" data-meta="{meta}" tabindex="0" role="button">'
                f'<img src="{path}" alt="{cap}" loading="lazy">'
                f'<figcaption>{cap}<span>{meta}</span></figcaption></figure>')
        else:
            out.append(
                f'<figure class="tile empty{w}" data-c="{cat}">'
                f'<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">'
                f'<rect x="3" y="5" width="18" height="14" rx="2"/>'
                f'<circle cx="8.5" cy="10" r="1.5"/><path d="M21 15l-5-5-9 9"/></svg>'
                f'<b>{cap}</b><i>{meta}</i><code>{fn}</code></figure>')
    return '\n      '.join(out)

def gallery_filters():
    return '\n      '.join(
        f'<button{" class=\"on\"" if k=="all" else ""} data-f="{k}">{l}</button>'
        for k, l in GALLERY_CATS)

if GALLERY_ENABLED: PAGES['gallery.html'] = dict(
    title='Gallery — SLPL | EHV substation and testing work',
    desc='Photographs of SLPL work in the field — EHV substations, testing and commissioning, '
         'and operation and maintenance.',
    body=page_hero([('index.html','Home'),(None,'Gallery')],
        'The work, as it actually looks.',
        "Substations mid-commissioning, instruments on test, crews on site. No stock photography — "
        "every image here is from an SLPL job.") + f'''
<section class="band" style="padding-top:0">
  <div class="wrap">
    <div class="filters rv" id="gfilters">
      {gallery_filters()}
    </div>
    <div class="gal-grid stg" id="gal">
      {gallery_tiles()}
    </div>
  </div>
</section>

<div class="lb" id="lb" aria-hidden="true">
  <button class="lb-btn lb-close" aria-label="Close">
    <svg viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg></button>
  <button class="lb-btn lb-prev" aria-label="Previous">
    <svg viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg></button>
  <button class="lb-btn lb-next" aria-label="Next">
    <svg viewBox="0 0 24 24"><path d="M9 18l6-6-6-6"/></svg></button>
  <figure><img src="" alt=""><figcaption></figcaption></figure>
  <div class="lb-count"></div>
</div>
{CTA}
''')

# ══════════════════════════════════════════════════════════════════
def a11y(html):
    """Every inline SVG here is decorative — icons beside text, or inside a
    button that already carries an aria-label. Hide them from assistive tech
    rather than having a screen reader announce a bare graphic."""
    return re.sub(r'<svg (?![^>]*aria-hidden)', '<svg aria-hidden="true" focusable="false" ', html)


for name, p in PAGES.items():
    html = (head(p['title'], p['desc'], name) + nav(name)
            + '<main id="main">' + p['body'] + '</main>' + FOOTER)
    html = a11y(html)
    (ROOT / name).write_text(html)
    print(f'  {name:44} {len(html)//1024:>4} KB')
print(f'\n{len(PAGES)} pages written.')

# ══════════════════════════════════════════════════════════════════
#  Site-level files: sitemap, robots, 404
# ══════════════════════════════════════════════════════════════════
today = datetime.date.today().isoformat()
PRIORITY = {'index.html': '1.0', 'services.html': '0.9', 'contact.html': '0.9',
            'about.html': '0.8', 'case-studies.html': '0.8'}

_urls = ''.join(
    '  <url>\n    <loc>%s/%s</loc>\n    <lastmod>%s</lastmod>\n'
    '    <priority>%s</priority>\n  </url>\n'
    % (SITE, '' if n == 'index.html' else n, today, PRIORITY.get(n, '0.7'))
    for n in PAGES)

(ROOT / 'sitemap.xml').write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + _urls + '</urlset>\n')

(ROOT / 'robots.txt').write_text(
    'User-agent: *\nAllow: /\n\nSitemap: ' + SITE + '/sitemap.xml\n')

_404_body = (
    '\n<header class="page-hero">\n'
    '  <div class="wrap">\n'
    '    <p class="crumb load"><a href="index.html">Home</a><span>/</span>404</p>\n'
    '    <h1 class="load l2">That page is not here.</h1>\n'
    '    <p class="lede load l3">The link may be out of date, or the page may have moved during\n'
    '      the site rebuild. Everything is reachable from the menu above.</p>\n'
    '    <div class="hero-cta load l4" style="margin-top:34px">\n'
    '      <a href="index.html" class="btn btn-solid">Back to home</a>\n'
    '      <a href="contact.html" class="btn btn-ghost">Contact us</a>\n'
    '    </div>\n'
    '  </div>\n'
    '</header>\n')

(ROOT / '404.html').write_text(a11y(
    head('Page not found — SLPL', 'The page you were looking for is not here.', '404.html')
    + nav('') + '<main id="main">' + _404_body + '</main>' + FOOTER))

print('\nAlso written: sitemap.xml (%d urls), robots.txt, 404.html' % len(PAGES))
