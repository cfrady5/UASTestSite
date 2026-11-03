#!/usr/bin/env python3
"""
Build the expansion pages from shared partials.

Why this exists
---------------
The site is static HTML with no build step, which is deliberate: it deploys
anywhere and has no dependency to rot. That worked at three pages. At eight,
hand-maintaining an identical header and footer in every file stops being
realistic — one edit to the nav means eight correct edits or a silent
inconsistency.

This script is NOT part of the deploy. It writes plain .html files which are
committed and served directly; Vercel never runs it. Run it by hand after
editing a shared partial or a page body:

    python3 tools/build_pages.py

It writes the expansion pages in full. membership.html and
membership-thanks.html predate it and are maintained directly, so their markup
is left alone.

index.html is also hand-maintained, with one exception: the leadership
remarks. Those come from SPEAKERS in site_data.py and are written into the
region between the `leadership:start` / `leadership:end` markers, so adding a
speaker is a dict and a re-run rather than hand-copied markup. Everything
outside those markers is left exactly as found.
"""

import pathlib
import re

from PIL import Image

import site_data

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://www.midwestuastestsite.us"
ASSET_V = 71          # cache buster; bump when site.css or site.js changes
INBOX = "MidwestUASTestSite@theari.us"


def head(title, desc, path):
    return f"""<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.classList.remove('no-js');</script>
<title>{title} — Midwest UAS Test Site of Indiana</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{path}">
<meta name="theme-color" content="#254A9A">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Midwest UAS Test Site of Indiana">
<meta property="og:title" content="{title} — Midwest UAS Test Site of Indiana">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}{path}">

<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">

<link rel="preload" href="/assets/fonts/Anton-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/Montserrat-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/site.css?v={ASSET_V}">
</head>
<body>

<a class="skip-link" href="#main">Skip to main content</a>
"""


# Every destination lives in the drawer behind the menu button, at every width.
#
# This markup is duplicated by hand in index.html, membership.html and
# membership-thanks.html, which predate the generator. Change one, change all
# four — verify/nav.mjs fails if they drift apart.
# No Home entry — the wordmark is the link home, on every page.
NAV_LINKS = [
    ("/capabilities", "Capabilities"),
    ("/industries", "Industries"),
    ("/pricing", "Pricing &amp; Scheduling"),
    ("/partners", "Partners"),
    ("/membership", "Membership"),
]


def nav_items(current=None):
    out = []
    for href, label in NAV_LINKS:
        mark = ' class="is-active" aria-current="page"' if href == current else ""
        out.append(f'        <li><a href="{href}"{mark}>{label}</a></li>')
    return "\n".join(out)


def header(current=None):
    return f"""
<header class="site-header" id="siteHeader">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="Midwest UAS Test Site of Indiana — home">
      <img class="brand-mark" src="assets/img/logo-shield-mark.png" alt="" width="96" height="110" aria-hidden="true">
      <span class="brand-text">
        <span class="brand-line-1">Midwest UAS Test Site</span>
        <span class="brand-line-2">of Indiana</span>
      </span>
    </a>

    <div class="header-actions">
      <a class="btn btn-gold btn-sm nav-cta nav-cta-bar" href="/#contact">Submit an Inquiry</a>
      <button type="button" class="nav-toggle" id="navToggle" aria-label="Menu"
              aria-expanded="false" aria-controls="primaryNav">
        <span class="nav-toggle-bars" aria-hidden="true"><span></span><span></span><span></span></span>
      </button>
    </div>

    <nav class="primary-nav" id="primaryNav" aria-label="Primary">
      <ul>
{nav_items(current)}
      </ul>
      <a class="btn btn-gold btn-sm nav-cta nav-cta-drawer" href="/#contact">Submit an Inquiry</a>
    </nav>
  </div>
</header>

<main id="main">
"""

FOOTER = f"""
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-logos">
      <a class="footer-logo" href="https://iedc.in.gov/" target="_blank" rel="noopener noreferrer">
        <img src="assets/img/logo-iedc.png" alt="Indiana Economic Development Corporation"
             width="738" height="144" loading="lazy" decoding="async">
      </a>
      <!-- Federal agency seals and logos are intentionally absent. Under the Test Site
           OTA, Agency and Federal Government seals, trademarks, logos, service marks and
           trade names may not be displayed without prior written permission. -->
      <a class="footer-logo" href="https://theari.us/" target="_blank" rel="noopener noreferrer">
        <img src="assets/img/logo-ari.png" alt="Applied Research Institute"
             width="458" height="97" loading="lazy" decoding="async">
      </a>
    </div>

    <div class="footer-bar">
      <p class="footer-brand">Midwest UAS Test Site of Indiana</p>
      <p class="footer-meta">
        Testing operations inquiries:
        <a href="mailto:{INBOX}">{INBOX}</a>
      </p>
    </div>
  </div>
</footer>

<script src="assets/js/site.js?v={ASSET_V}" defer></script>"""


def page_hero(eyebrow, title, lead):
    return f"""
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow eyebrow-gold">{eyebrow}</p>
    <h1 class="page-title">{title}</h1>
    <p class="page-lead">{lead}</p>
  </div>
  <div class="page-hero-band" aria-hidden="true"></div>
</section>
"""


def cta_band(heading, copy, buttons):
    btns = "\n      ".join(
        f'<a class="btn {cls}" href="{href}">{label}</a>' for label, href, cls in buttons
    )
    return f"""
<section class="section cta-band">
  <div class="wrap cta-inner">
    <div>
      <h2 class="h2 h2-light">{heading}</h2>
      <p class="cta-copy">{copy}</p>
    </div>
    <div class="cta-actions">
      {btns}
    </div>
  </div>
</section>
"""


# --------------------------------------------------------------------------
# Capabilities
# --------------------------------------------------------------------------
# The capability list, their statuses and the network locations all come from
# tools/site_data.py, which the capabilities map is built from too. Keeping one
# copy is the point: the page and the map can no longer disagree about what the
# test site offers or where.
CAPABILITIES = [(c["name"], "In development" if c["status"] == "in-development" else None)
                for c in site_data.CAPABILITIES]

LOCATIONS = ([f["name"] for f in site_data.FACILITIES if f.get("network")]
             + [c["name"] for c in site_data.NETWORK_COUNTIES])


def capabilities_page():
    rows = []
    for i, (name, status) in enumerate(CAPABILITIES, 1):
        badge = f'\n          <span class="cap-status">{status}</span>' if status else ""
        rows.append(
            f"""        <li class="cap-item">
          <span class="cap-num" aria-hidden="true">{i:02d}</span>
          <span class="cap-name">{name}</span>{badge}
        </li>"""
        )
    locs = "\n".join(f"          <li>{l}</li>" for l in LOCATIONS)

    return (
        page_hero(
            "Capabilities",
            "Testing capabilities",
            "Ten testing and training capabilities spanning line-of-sight and beyond-visual-line-of-sight "
            "flight, kinetic and counter-UAS work, sensor and laboratory testing, airspace authorization "
            "and pilot certification.",
        )
        + f"""
<section class="section">
  <div class="wrap">
    <header class="section-head reveal">
      <h2 class="h2">Capability areas</h2>
      <p class="section-intro-copy">Select a capability to see where it sits in the Indiana
        testing network, or select a location on the map to work the other way.</p>
    </header>

    <!-- The explorer is built by assets/js/capabilities-map.js. Everything
         inside this element is the no-script version: the ten capabilities as
         an ordinary list, and the IEDC network map. The script hides the list
         and adds the interactive explorer; if it never runs, the page is what
         it was before. -->
    <div class="reveal" data-cap-explorer>
      <ol class="cap-list">
{chr(10).join(rows)}
      </ol>

      <noscript>
        <figure class="cap-map">
          <img src="assets/img/indiana-map.png"
               alt="Map of Indiana showing the test site network: airports, military installations including Camp Atterbury, Muscatatuck, NSWC Crane and Grissom Air Reserve, and university partners across the state."
               width="1061" height="1400" loading="lazy" decoding="async">
          <figcaption>Statewide testing network.</figcaption>
        </figure>
      </noscript>

      <div class="loc-block cap-list-note">
        <h3 class="h4">Locations in the testing network</h3>
        <ul class="chip-list">
{locs}
        </ul>
      </div>
    </div>

    <p class="note note-inline">Capabilities marked <strong>In development</strong> are not yet
      operational. The 225+ mile BVLOS corridor holds preliminary approval and the dense urban
      canyon component is proposed; both remain subject to regulatory approval before flight
      operations begin. The map plots verified facility locations only — no testing range
      boundary or flight corridor is drawn, because none has been published, and none is
      estimated here.</p>
  </div>
</section>
"""
        + cta_band(
            "Discuss testing requirements",
            "Tell us what you need to fly, and the operations team will confirm the right environment, "
            "scheduling window and supporting services.",
            [
                ("Submit a Test Site Inquiry", "/#contact", "btn-gold"),
                ("View pricing", "/pricing", "btn-ghost"),
            ],
        )
    )


# --------------------------------------------------------------------------
# Industries
# --------------------------------------------------------------------------
INDUSTRIES = [
    ("Shipping &amp; Logistics", ["Drone delivery", "Warehouse-to-hub operations", "Middle-mile logistics",
                                  "BVLOS cargo workflows", "Supply chain efficiency trials"]),
    ("Agriculture", ["Crop health monitoring", "Spraying", "Automated field mapping",
                     "Livestock observation", "Heavy-lift agricultural drone applications"]),
    ("Transportation &amp; Infrastructure", ["Traffic monitoring", "Roadway incident assessment",
                                             "Bridge and rail inspections", "Utility corridor surveys",
                                             "Integrated infrastructure analytics"]),
    ("Public Safety &amp; Emergency Response", ["Disaster assessment", "Overwatch", "Hazmat assessment",
                                                "Rapid-deployment aerial situational awareness"]),
    ("Environmental &amp; Land Management", ["Land surveys", "Wildlife monitoring", "Conservation",
                                             "Floodplain modeling",
                                             "Environmental sensing for air and surface conditions"]),
    ("Other Commercial Applications", ["Emerging drone use cases", "Industrial inspections",
                                       "Telecommunications support", "Energy sector applications",
                                       "Innovative commercial concepts"]),
]


def industries_page():
    cards = []
    for i, (name, uses) in enumerate(INDUSTRIES, 1):
        items = "\n".join(f"            <li>{u}</li>" for u in uses)
        cards.append(
            f"""      <li class="ind-card reveal">
        <span class="ind-num" aria-hidden="true">{i:02d}</span>
        <h3 class="h4">{name}</h3>
        <ul class="ind-uses">
{items}
        </ul>
      </li>"""
        )

    return (
        page_hero(
            "Industries",
            "One testing ecosystem.<br>Multiple industries.",
            "The test site supports development, validation and real-world application of unmanned systems "
            "across commercial and public-sector use cases — not defense alone.",
        )
        + f"""
<section class="section">
  <div class="wrap">
    <header class="section-head reveal">
      <h2 class="h2">Application areas</h2>
      <p class="section-intro-copy">Six industry groups, with the use cases named for each.</p>
    </header>

    <ul class="ind-grid">
{chr(10).join(cards)}
    </ul>
  </div>
</section>

<div class="band" role="img" aria-label="An engineer inspects a fixed-wing unmanned aircraft in a test facility."></div>
"""
        + cta_band(
            "Testing for your sector",
            "Whether your application is commercial, agricultural, public safety or infrastructure, "
            "the operations team can scope the testing environment it needs.",
            [
                ("Submit a Test Site Inquiry", "/#contact", "btn-gold"),
                ("Explore capabilities", "/capabilities", "btn-ghost"),
            ],
        )
    )


# --------------------------------------------------------------------------
# Pricing & Membership
# --------------------------------------------------------------------------
# "Contact for pricing" is a display treatment for services whose rate was left
# blank in the source. It asserts no particular price.
RATE_CATEGORIES = [
    ("ranges", "Testing Ranges &amp; Facilities", [
        ("Basic Range", "$500", "per day"),
        ("BVLOS Range", "$500", "per hour"),
        ("Secure/DoW Range", "$750", "per day"),
        ("Kinetic Range", "$2,000", "per day"),
        ("Urban Range", "$2,000", "per day"),
        ("Hypersonic Lab", None, None),
        ("Motion Capture Lab", None, None),
        ("Sensor Testing", None, None),
    ]),
    ("equipment", "UAS Equipment Rentals", [
        ("UAS Group 1 Rental", "$350", "per day"),
        ("UAS Group 2 Rental", "$575", "per day"),
        ("UAS Group 3 Rental", "$750", "per day"),
    ]),
    ("personnel", "Pilots, Personnel &amp; Training", [
        ("UAS Group 1 Pilot", "$125", "per hour"),
        ("UAS Group 2 Pilot", "$155", "per hour"),
        ("UAS Group 3 Pilot", "$325", "per hour"),
        ("UAS Observer", "$50", "per hour"),
        ("Pilot Certification Course", "$150", "per student"),
    ]),
    ("airspace", "Airspace Coordination &amp; Data Services", [
        ("Remote COA", "$2,500", "per COA"),
        ("Remote COA Use", "$500", "per day / N#"),
        ("Data Capture Fee", "$300", "per hour"),
    ]),
]

TIERS = [
    ("01", "Commander", "$30,000", ["15% discount", "Early scheduling 120 days out",
                                    "Guaranteed monthly BVLOS testing access",
                                    "Quarterly Test Site Leadership Meetings", "Event Sponsorship"]),
    ("02", "Wingman", "$15,000", ["10% discount", "Early scheduling 90 days out",
                                  "Guaranteed monthly BVLOS testing access",
                                  "Annual Test Site Leadership Meeting"]),
    ("03", "Navigator", "$5,000", ["5% discount", "Early scheduling 60 days out"]),
    ("04", "Startup", "$3,000", ["Early scheduling 60 days out", "24-month maximum participation",
                                 "Must move to a higher tier after the startup period"]),
    ("05", "Research", "$1,000", ["Available to universities and NGOs", "Early scheduling 60 days out",
                                  "Reciprocal data sharing", "Cost-plus pricing on range time"]),
]

MATRIX_ROWS = [
    ("Annual membership", ["$30,000", "$15,000", "$5,000", "$3,000", "$1,000"]),
    ("Discount", ["15%", "10%", "5%", "—", "Cost-plus on range time"]),
    ("Advance scheduling", ["120 days", "90 days", "60 days", "60 days", "60 days"]),
    ("Guaranteed monthly BVLOS access", ["Yes", "Yes", "—", "—", "—"]),
    ("Leadership meetings", ["Quarterly", "Annual", "—", "—", "—"]),
    ("Event sponsorship", ["Yes", "—", "—", "—", "—"]),
    ("Eligibility", ["Open", "Open", "Open", "Startups", "Universities &amp; NGOs"]),
    ("Special provisions", ["—", "—", "—", "24-month maximum", "Reciprocal data sharing"]),
]


def pricing_page():
    # The tab buttons are not in the markup. Shipping them would mean shipping a
    # tablist that does nothing if site.js fails to load, with three of the four
    # rate groups hidden behind it. Instead each group ships as a plain headed
    # section and site.js folds them into tabs, reading the button labels from
    # the headings. No script, no tabs — but every rate is still on the page.
    panels = []
    for slug, label, rows in RATE_CATEGORIES:
        items = []
        for name, rate, unit in rows:
            if rate:
                value = f'<span class="rate-amount">{rate}</span><span class="rate-unit">{unit}</span>'
            else:
                value = '<span class="rate-tbd">Contact for pricing</span>'
            items.append(
                f"""          <li class="rate-row">
            <span class="rate-name">{name}</span>
            <span class="rate-value">{value}</span>
          </li>"""
            )
        panels.append(
            f"""      <section class="tab-panel" id="panel-{slug}">
        <h3 class="tab-panel-title">{label}</h3>
        <ul class="rate-list">
{chr(10).join(items)}
        </ul>
      </section>"""
        )

    tier_cards = []
    for num, name, price, benefits in TIERS:
        items = "\n".join(f"            <li>{b}</li>" for b in benefits)
        tier_cards.append(
            f"""      <li class="tier-card reveal">
        <p class="tier-num" aria-hidden="true">{num}</p>
        <h3 class="h4">{name}</h3>
        <p class="tier-price"><span class="tier-amount">{price}</span><span class="tier-per">per year</span></p>
        <ul class="tier-benefits">
{items}
        </ul>
        <a class="btn btn-outline btn-block" href="/membership">Register interest</a>
      </li>"""
        )

    head_cells = "".join(f'<th scope="col">{name}</th>' for _, name, _, _ in TIERS)
    body_rows = []
    for label, cells in MATRIX_ROWS:
        tds = "".join(f"<td>{c}</td>" for c in cells)
        body_rows.append(f'          <tr><th scope="row">{label}</th>{tds}</tr>')

    return (
        page_hero(
            "Pricing &amp; Membership",
            "Pricing &amp; membership",
            "Five annual membership levels, alongside published rates for testing ranges, "
            "equipment, personnel and airspace services.",
        )
        + f"""
<section class="section">
  <div class="wrap">
    <header class="section-head reveal">
      <h2 class="h2">Annual membership</h2>
      <p class="section-intro-copy">Five membership levels, from research access through to the
        Commander tier. Membership benefits are confirmed at registration.</p>
    </header>

    <ul class="tier-grid">
{chr(10).join(tier_cards)}
    </ul>

    <p class="note note-inline">Benefits referencing BVLOS access depend on the corridor reaching
      operational status; it currently holds preliminary approval and remains subject to regulatory
      approval. Membership terms are confirmed in writing at registration.</p>

    <h3 class="h3 rule-top">Compare membership levels</h3>
    <!-- A named <section> is an implicit landmark region; tabindex makes the
         overflow reachable by keyboard where the table is wider than the page. -->
    <section class="matrix-scroll" tabindex="0" aria-label="Membership comparison, scrollable">
      <table class="matrix">
        <thead>
          <tr><th scope="col">Benefit</th>{head_cells}</tr>
        </thead>
        <tbody>
{chr(10).join(body_rows)}
        </tbody>
      </table>
    </section>
  </div>
</section>

<section class="section section-capabilities">
  <div class="wrap">
    <header class="section-head reveal">
      <h2 class="h2">Testing service rates</h2>
      <p class="section-intro-copy">Rates are grouped by service type. A membership discount, where
        one applies, comes off these. Final pricing and availability are confirmed with the test
        site during coordination.</p>
    </header>

    <div class="tabs reveal" data-tabs data-tabs-label="Pricing categories">
      <div class="tab-list" hidden></div>
{chr(10).join(panels)}
    </div>

    <p class="note note-inline">Rates shown are list prices for planning purposes. Final pricing,
      availability and any applicable membership discount are confirmed with the test site before
      scheduling. Services shown as <strong>Contact for pricing</strong> are quoted per engagement.</p>
  </div>
</section>
"""
        + schedule_section()
        + cta_band(
            "Discuss testing requirements",
            "Pricing depends on the environment, aircraft group and support you need. "
            "The operations team will scope it with you.",
            [
                ("Submit a Test Site Inquiry", "/#contact", "btn-gold"),
                ("Register for membership", "/membership", "btn-ghost"),
            ],
        )
    )


# --------------------------------------------------------------------------
# Schedule a Test
# --------------------------------------------------------------------------
STEPS = [
    "Create a Member Account",
    "Request a Range Reservation",
    "Receive / Accept Coordination Invite",
    "Complete Required Documentation",
    "Receive Reservation Approval",
]


def schedule_section():
    """The five-step range-access process.

    This was its own page. It had no booking form on it — reserving range time
    runs through the operations team, not a self-service calendar — so a page
    whose only content was "here is the process" was a stop on the way to
    somewhere else. It reads better directly under the rates it applies to, and
    /schedule now redirects here (see vercel.json) so any link already shared
    still lands in the right place.
    """
    nodes = []
    for i, label in enumerate(STEPS, 1):
        nodes.append(
            f"""        <li class="process-step">
          <span class="process-num" aria-hidden="true">{i:02d}</span>
          <h3 class="process-label">{label}</h3>
        </li>"""
        )

    return f"""
<section class="section" id="schedule">
  <div class="wrap">
    <header class="section-head reveal">
      <h2 class="h2">Scheduling a test</h2>
      <p class="section-intro-copy">Range access follows a five-step process, from creating a
        member account through to reservation approval.</p>
    </header>

    <div class="process reveal" data-process>
      <div class="process-rail" aria-hidden="true"><span class="process-progress"></span></div>
      <ol class="process-list">
{chr(10).join(nodes)}
      </ol>
    </div>

    <p class="note note-inline">There is no booking form here on purpose. Creating a member
      account begins the process; it does not approve range access or create a reservation.
      Dates are confirmed by the test site during coordination.</p>
  </div>
</section>
"""


# --------------------------------------------------------------------------
# Partners
# --------------------------------------------------------------------------
# The expansion document lists these under "Sponsors (Tier 1 Members)". That
# designation is not asserted here: naming an organization a paying Tier 1
# member is a claim about a commercial relationship, and several entries are
# federal or state bodies unlikely to hold one. Shown as ecosystem
# organizations pending confirmation, grouped only where the category is
# unambiguous from the organization's own identity.
#
# The list itself lives in site_data.py, with each organization's logo and
# confirmed website alongside its name.
PARTNER_GROUPS = site_data.PARTNER_GROUPS



# --------------------------------------------------------------------------
# Optical sizing for the partner logos
# --------------------------------------------------------------------------
# Scaling every logo to the same HEIGHT makes a square badge look twice the
# weight of a long wordmark. Scaling them to the same AREA goes too far the
# other way and leaves wide wordmarks as thin slivers. This splits the
# difference: height falls off with aspect ratio raised to EXPONENT, where 0
# would be equal height and 0.5 equal area.
#
# The height is computed here, from each file's real dimensions, and emitted as
# a custom property on the cell. Doing it at build time means no layout shift —
# the browser knows the box before the image arrives.
LOGO_BASE = 72      # px tall for a square mark
LOGO_EXP = 0.34
LOGO_MIN_H = 24
LOGO_MAX_W = 232


def logo_box(path):
    """(width, height) in px for a logo, from its own aspect ratio."""
    import math
    import re as _re

    f = ROOT / path
    if f.suffix == ".svg":
        head = f.read_text()
        head = head[head.index("<svg"):]
        head = head[:head.index(">") + 1]
        m = _re.search(r'viewBox\s*=\s*"[\d.\-]+\s+[\d.\-]+\s+([\d.]+)\s+([\d.]+)"', head)
        if not m:
            m = _re.search(r'width="([\d.]+)"[^>]*height="([\d.]+)"', head)
        nw, nh = float(m.group(1)), float(m.group(2))
    else:
        from PIL import Image
        with Image.open(f) as im:
            nw, nh = im.size

    ratio = nw / nh
    h = LOGO_BASE / (ratio ** LOGO_EXP)
    w = h * ratio
    if w > LOGO_MAX_W:                     # very wide marks get capped on width
        w, h = LOGO_MAX_W, LOGO_MAX_W / ratio
    # The floor wins over the width cap. A 11:1 wordmark capped on width alone
    # would come out 21px tall, which is below the point where it still reads as
    # a logo rather than a smudge; letting it run a little wider is the better
    # trade.
    h = max(h, LOGO_MIN_H)
    return round(h * ratio), round(h)


def partner_lead(total):
    """What opens the page: the ribbon-cutting photograph where a second
    heading used to be.

    The page hero already says what this page is, so the heading under it was
    saying it twice. The photograph does the same work better — and if the
    file is missing the old heading comes back, because a page cannot open on
    nothing.
    """
    ph = getattr(site_data, "LAUNCH_PHOTO", None)
    if ph and (ROOT / ph["src"]).exists():
        return f"""    <figure class="partner-lead reveal">
      <img src="{ph['src']}" alt="{esc(ph['alt'])}"
           width="1600" height="1067" loading="eager" decoding="async" fetchpriority="high">
      <figcaption>{esc(ph['caption'])} {total} organizations are listed below,
        grouped by each one\'s own field of work.</figcaption>
    </figure>"""
    return f"""    <header class="section-head partner-intro-head reveal">
      <h2 class="h2">Ecosystem organizations</h2>
      <p class="section-intro-copy">{total} organizations, grouped by each one\'s own field of
        work. Select an organization to visit its website.</p>
    </header>"""


def partner_card(org):
    """One organization as a directory card: logo, name, and the expanded
    name where the short one does not already carry it. A link where a
    website is confirmed, plain text where it is not — never a guessed URL."""
    if org["logo"]:
        w, h = logo_box(org["logo"])
        # width/height reserve the box before the file loads, so a card never
        # changes height underneath the grid.
        # alt is empty on purpose: the name is right there as visible text in
        # the same link, and duplicating it only makes the link announce twice.
        art = (f'<img class="pc-img" src="{org["logo"]}" alt=""'
               f' width="{w}" height="{h}" style="--lw:{w}px;--lh:{h}px"'
               f' loading="lazy" decoding="async">')
    else:
        # No logo on file — set type at the same size, so the slot still
        # reads as a mark rather than as a missing image.
        art = f'<span class="pc-word">{org["short"]}</span>'

    # Only when it adds something: "Purdue Research Foundation (PRF)" already
    # contains its own expansion, while "HUF" and "AMVIC" do not.
    expand = org.get("expand")
    sub = ""
    if expand and expand.lower() not in org["name"].lower():
        sub = f'<span class="pc-sub">{expand}</span>'

    body = (f'<span class="pc-logo">{art}</span>'
            f'<span class="pc-text"><span class="pc-name">{org["name"]}</span>{sub}</span>')

    if org["url"]:
        return (f'        <li class="pc"><a class="pc-link" href="{org["url"]}"'
                f' target="_blank" rel="noopener noreferrer">{body}'
                f'<span class="sr-only"> (opens in a new tab)</span></a></li>')
    return f'        <li class="pc"><span class="pc-link pc-plain">{body}</span></li>'


def partners_page():
    """Five category sections, each a responsive grid of cards.

    This replaced a set of scrolling logo marquees. A marquee cannot hold a
    logo in a fixed position, so nothing lined up, names could not sit under
    the marks, and whatever was mid-travel at the edge was cut off — none of
    which a directory can afford. The logos, links and optical sizing carry
    over unchanged; only the arrangement is new.
    """
    jump, sections = [], []

    for i, (slug, name, orgs) in enumerate(PARTNER_GROUPS):
        cards = "\n".join(partner_card(o) for o in orgs)
        # Alternating tone, not alternating darkness: all 36 marks are dark ink
        # on transparent, so a dark panel would swallow every one of them.
        tone = " partner-section-alt" if i % 2 else ""
        count = len(orgs)
        jump.append(
            f'        <li><a href="#partners-{slug}">{name}'
            f'<span class="pj-n" aria-hidden="true">{count}</span>'
            f'<span class="sr-only"> ({count} organizations)</span></a></li>'
        )
        sections.append(
            f"""<section class="section partner-section{tone}" id="partners-{slug}"
         aria-labelledby="partners-{slug}-h">
  <div class="wrap">
    <header class="partner-section-head reveal">
      <h2 class="h3" id="partners-{slug}-h">{name}</h2>
    </header>
    <ul class="partner-grid reveal">
{cards}
    </ul>
  </div>
</section>
"""
        )

    total = sum(len(o) for _, _, o in PARTNER_GROUPS)

    return (
        page_hero(
            "Partners",
            "Ecosystem &amp; partners",
            "A statewide and national network of government, defense, academic and commercial "
            "organizations connected to the test site.",
        )
        + f"""
<section class="section section-intro partner-intro" aria-label="Ecosystem organizations">
  <div class="wrap">
{partner_lead(total)}

    <nav class="partner-jump reveal" aria-label="Partner categories">
      <ul>
{chr(10).join(jump)}
      </ul>
    </nav>
  </div>
</section>

{"".join(sections)}
"""
        + cta_band(
            "Become part of the network",
            "Organizations join the test site ecosystem through membership or by scoping a testing "
            "engagement with the operations team.",
            [
                ("Register for membership", "/membership", "btn-gold"),
                ("Submit a Test Site Inquiry", "/#contact", "btn-ghost"),
            ],
        )
    )


# filename, URL, <title>, meta description, body builder, page-only scripts.
# The scripts load after site.js and only on the page that needs them — the
# map data alone is bigger than everything else on the site put together, and
# four of the five pages have no use for it.
PAGES = [
    ("capabilities.html", "/capabilities", "Capabilities",
     "Ten UAS testing and training capabilities at the Midwest UAS Test Site of Indiana, "
     "from line-of-sight and BVLOS flight to kinetic, counter-UAS, sensor and laboratory testing.",
     capabilities_page, ("map-data.js", "capabilities-map.js")),
    ("industries.html", "/industries", "Industries",
     "Commercial and public-sector applications supported at the Midwest UAS Test Site of Indiana, "
     "across logistics, agriculture, infrastructure, public safety and environmental management.",
     industries_page, ()),
    ("pricing.html", "/pricing", "Pricing &amp; Membership",
     "Five annual membership levels, published testing service rates and the five-step "
     "process for reserving range time at the Midwest UAS Test Site of Indiana.",
     pricing_page, ()),
    ("partners.html", "/partners", "Partners",
     "Government, defense, academic and commercial organizations in the Midwest UAS Test Site "
     "of Indiana ecosystem.", partners_page, ()),
]


# --------------------------------------------------------------------------
# Leadership remarks, written into index.html between its markers
# --------------------------------------------------------------------------
LEAD_START = "<!-- leadership:start — generated from SPEAKERS in site_data.py -->"
LEAD_END = "<!-- leadership:end -->"
LAUNCH_START = "<!-- launchphoto:start — generated from LAUNCH_PHOTO in site_data.py -->"
LAUNCH_END = "<!-- launchphoto:end -->"


def launch_photo_block():
    """The ribbon-cutting photograph under the video.

    Rendered only when the file is actually on disk — the section is complete
    without it, so a missing asset degrades to video-only rather than to a
    broken image in the middle of the page.
    """
    ph = getattr(site_data, "LAUNCH_PHOTO", None)
    if not ph or not (ROOT / ph["src"]).exists():
        return f"{LAUNCH_START}\n    {LAUNCH_END}"
    return f"""{LAUNCH_START}
    <figure class="launch-photo reveal">
      <img src="{ph['src']}" alt="{esc(ph['alt'])}"
           width="1600" height="1067" loading="lazy" decoding="async">
      <figcaption>{esc(ph['caption'])}</figcaption>
    </figure>
    {LAUNCH_END}"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def speaker_card(sp, missing):
    """One speaker.

    A portrait is optional and its absence is a first-class state, not a hole
    to fill: no silhouette, no initials tile, no grey box. The card simply
    sets the quote wider and reads as a pull quote until a real photograph
    arrives.

    A path that is set but not yet on disk counts as absent. That keeps a
    photograph's arrival to one step — drop the file in and re-run — without
    ever publishing an <img> pointing at a 404.
    """
    photo, alt = sp.get("photo"), sp.get("alt")
    if photo and not alt:
        raise SystemExit(
            f"SPEAKERS: {sp['name']} has a photo but no alt text. A portrait "
            f"without a description is unreadable to anyone using a screen "
            f"reader, so the build stops here rather than shipping it.")
    if photo and not (ROOT / photo).exists():
        missing.append(f"{sp['name']} -> {photo}")
        photo = None

    portrait = ""
    if photo:
        # Real dimensions, read from the file. The crops are not all the same
        # size — one source was too small to reach the others' width — so a
        # hardcoded pair would reserve the wrong box and shift the card.
        with Image.open(ROOT / photo) as im:
            w, h = im.size
        portrait = (
            f'\n        <div class="speaker-portrait">'
            f'<img src="{photo}" alt="{esc(alt)}" width="{w}" height="{h}" '
            f'loading="lazy" decoding="async"></div>')

    # Quote, then the photograph, then who said it. The words come first, the
    # face introduces the attribution directly under it.
    return f"""      <figure class="speaker{' speaker-has-photo' if photo else ''} reveal">
        <div class="speaker-body">
          <blockquote class="speaker-quote"><p>{esc(sp['quote'])}</p></blockquote>
        </div>{portrait}
        <figcaption class="speaker-id">
          <span class="speaker-name">{esc(sp['name'])}</span>
          <span class="speaker-role">{esc(sp['role'])}</span>
        </figcaption>
      </figure>"""


def leadership_block(missing):
    cards = "\n".join(speaker_card(s, missing) for s in site_data.SPEAKERS)
    return f"""{LEAD_START}
    <div class="speaker-grid">
{cards}
    </div>
    {LEAD_END}"""


def patch_index():
    """Rewrite only the marked region of index.html, leaving the rest alone."""
    f = ROOT / "index.html"
    s = f.read_text()
    if LEAD_START not in s or LEAD_END not in s:
        print("index.html: leadership markers not found, skipped")
        return

    missing = []
    start = s.index(LEAD_START)
    end = s.index(LEAD_END) + len(LEAD_END)
    out = s[:start] + leadership_block(missing) + s[end:]

    # Counted before the launch photo joins the list — that one is not a
    # speaker, and folding it in here reported a negative portrait count.
    n = len(site_data.SPEAKERS)
    shown = n - len(missing)

    if LAUNCH_START in out and LAUNCH_END in out:
        a = out.index(LAUNCH_START)
        b = out.index(LAUNCH_END) + len(LAUNCH_END)
        out = out[:a] + launch_photo_block() + out[b:]
        ph = getattr(site_data, "LAUNCH_PHOTO", None)
        if ph and not (ROOT / ph["src"]).exists():
            missing.append(f"launch recap photo -> {ph['src']}")

    if out != s:
        f.write_text(out)
    print(f"wrote index.html             -> leadership remarks "
          f"({n} speaker{'s' if n != 1 else ''}, {shown} with a portrait)")

    if missing:
        print("  portraits not yet on disk, so those cards render without one:")
        for m in missing:
            print(f"    - {m}")

    # Not a nag: a quote assembled from separate excerpts puts words in a named
    # person's mouth in an order they did not use. It stays on screen at every
    # build until someone decides it is cleared.
    unapproved = [sp for sp in site_data.SPEAKERS
                  if sp.get("composite") and not sp.get("approved")]
    if unapproved:
        print("  REVIEW — quotes assembled from separate excerpts, not yet approved:")
        for sp in unapproved:
            print(f"    - {sp['name']}: {sp['composite']}")
        print("    Mark approved=True in site_data.py once the wording is signed off,")
        print("    or add ellipses at the omissions and approve that version.")


def main():
    for filename, path, title, desc, body, scripts in PAGES:
        extra = "".join(
            f'\n<script src="assets/js/{s}?v={ASSET_V}" defer></script>' for s in scripts)
        html = (head(title, desc, path) + header(path) + body() + FOOTER
                + extra + "\n</body>\n</html>\n")
        # Collapse the blank lines the templating leaves behind
        html = re.sub(r"\n{3,}", "\n\n", html)
        (ROOT / filename).write_text(html)
        print(f"wrote {filename:24} -> {path}")
    patch_index()


if __name__ == "__main__":
    main()
