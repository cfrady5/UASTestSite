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

It only writes the expansion pages. index.html, membership.html and
membership-thanks.html predate it and are maintained directly, so their markup
is left alone.
"""

import pathlib
import re

import site_data

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://www.midwestuastestsite.us"
ASSET_V = 34          # cache buster; bump when site.css or site.js changes
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


# The expansion pages are intentionally absent from the nav for now — they are
# published for review and reachable by direct link only.
HEADER = """
<header class="site-header" id="siteHeader">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="Midwest UAS Test Site of Indiana — home">
      <img class="brand-mark" src="assets/img/logo-shield-mark.png" alt="" width="96" height="110" aria-hidden="true">
      <span class="brand-text">
        <span class="brand-line-1">Midwest UAS Test Site</span>
        <span class="brand-line-2">of Indiana</span>
      </span>
    </a>

    <button type="button" class="nav-toggle" id="navToggle" aria-expanded="false" aria-controls="primaryNav">
      <span class="nav-toggle-bars" aria-hidden="true"><span></span><span></span><span></span></span>
      <span class="sr-only">Menu</span>
    </button>

    <nav class="primary-nav" id="primaryNav" aria-label="Primary">
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/membership">Membership</a></li>
      </ul>
      <a class="btn btn-gold btn-sm nav-cta" href="/#contact">Submit an Inquiry</a>
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
      <a class="footer-logo" href="https://ari-for-review.vercel.app/" target="_blank" rel="noopener noreferrer">
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
                                    "Quarterly Test Site Leadership Meetings", "Event Sponsorship"], True),
    ("02", "Wingman", "$15,000", ["10% discount", "Early scheduling 90 days out",
                                  "Guaranteed monthly BVLOS testing access",
                                  "Annual Test Site Leadership Meeting"], False),
    ("03", "Navigator", "$5,000", ["5% discount", "Early scheduling 60 days out"], False),
    ("04", "Startup", "$3,000", ["Early scheduling 60 days out", "24-month maximum participation",
                                 "Must move to a higher tier after the startup period"], False),
    ("05", "Research", "$1,000", ["Available to universities and NGOs", "Early scheduling 60 days out",
                                  "Reciprocal data sharing", "Cost-plus pricing on range time"], False),
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
    for num, name, price, benefits, feature in TIERS:
        items = "\n".join(f"            <li>{b}</li>" for b in benefits)
        cls = "tier-card tier-card-feature" if feature else "tier-card"
        tier_cards.append(
            f"""      <li class="{cls} reveal">
        <p class="tier-num" aria-hidden="true">{num}</p>
        <h3 class="h4">{name}</h3>
        <p class="tier-price"><span class="tier-amount">{price}</span><span class="tier-per">per year</span></p>
        <ul class="tier-benefits">
{items}
        </ul>
        <a class="btn btn-outline btn-block" href="/membership">Register interest</a>
      </li>"""
        )

    head_cells = "".join(f'<th scope="col">{name}</th>' for _, name, _, _, _ in TIERS)
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


def schedule_page():
    nodes = []
    for i, label in enumerate(STEPS, 1):
        nodes.append(
            f"""        <li class="process-step">
          <span class="process-num" aria-hidden="true">{i:02d}</span>
          <h2 class="process-label">{label}</h2>
        </li>"""
        )

    return (
        page_hero(
            "Testing Access",
            "Schedule time on the range",
            "Range access follows a five-step process, from creating a member account through to "
            "reservation approval.",
        )
        + f"""
<section class="section">
  <div class="wrap">
    <div class="process reveal" data-process>
      <div class="process-rail" aria-hidden="true"><span class="process-progress"></span></div>
      <ol class="process-list">
{chr(10).join(nodes)}
      </ol>
    </div>

    <p class="note note-inline">Creating a member account begins the process. It does not approve
      range access or create a reservation — scheduling is confirmed by the test site during
      coordination.</p>
  </div>
</section>
"""
        + cta_band(
            "Ready to begin testing?",
            "Start with a member account, or talk to the operations team first if you would rather "
            "scope the requirement before registering.",
            [
                ("Create a member account", "/membership", "btn-gold"),
                ("Submit a Test Site Inquiry", "/#contact", "btn-ghost"),
            ],
        )
    )


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

# Above this many organizations a category is split across two scrolling rows
# running in opposite directions. Below it, one row reads better than two
# half-empty ones.
TWO_ROW_AT = 9


def partner_item(org):
    """One organization, as a link where a website is confirmed and as plain
    text where it is not. Never a guessed URL."""
    cls = []
    if org["logo"]:
        # Square badges get their own class so they are not scaled to the same
        # height as a long wordmark and left looming over it.
        badge = " partner-logo-badge" if org.get("badge") else ""
        inner = (f'<img class="partner-logo{badge}" src="{org["logo"]}" alt="{org["name"]}"'
                 f' loading="lazy" decoding="async">')
        if org.get("plate"):
            cls.append("partner-item-plate")
    else:
        # No logo on file. A set wordmark, not a fallback-looking chip — see the
        # note in site_data.py on why most of these have no logo yet.
        inner = f'<span class="partner-word">{org["short"]}</span>'

    # The expansion is appended rather than substituted, so the accessible name
    # still contains the visible text (WCAG 2.5.3) while "HUF" stops being an
    # unidentifiable three-letter link.
    expand = f' — {org["expand"]}' if org.get("expand") else ""

    extra = (" " + " ".join(cls)) if cls else ""

    if org["url"]:
        return (f'          <li class="partner-cell"><a class="partner-item{extra}" '
                f'href="{org["url"]}" target="_blank" rel="noopener noreferrer">'
                f'{inner}<span class="sr-only">{expand} (opens in a new tab)</span>'
                f'</a></li>')
    if expand:
        return (f'          <li class="partner-cell"><span class="partner-item '
                f'partner-item-plain{extra}">{inner}<span class="sr-only">{expand}</span>'
                f'</span></li>')
    return (f'          <li class="partner-cell"><span class="partner-item '
            f'partner-item-plain{extra}">{inner}</span></li>')


def partners_page():
    groups = []
    for slug, name, orgs in PARTNER_GROUPS:
        cells = "\n".join(partner_item(o) for o in orgs)
        rows = 2 if len(orgs) >= TWO_ROW_AT else 1
        groups.append(
            f"""      <div class="partner-group reveal" data-marquee data-rows="{rows}">
        <h3 class="h4" id="partners-{slug}">{name}</h3>
        <ul class="partner-list" aria-labelledby="partners-{slug}">
{cells}
        </ul>
      </div>"""
        )

    return (
        page_hero(
            "Partners",
            "Ecosystem &amp; partners",
            "A statewide and national network of government, defense, academic and commercial "
            "organizations connected to the test site.",
        )
        + f"""
<section class="section partner-wall">
  <div class="wrap">
    <header class="section-head reveal">
      <h2 class="h2 h2-light">Ecosystem organizations</h2>
      <p class="section-intro-copy">Grouped by each organization's own field of work.
        Select an organization to visit its website.</p>
    </header>

    <div class="partner-groups">
{chr(10).join(groups)}
    </div>

    <p class="note note-inline">Organization names are listed as supplied. Nothing here states the
      nature or status of any commercial relationship with the test site — those designations are
      confirmed before publication. A website is linked only where the organization's official
      URL has been confirmed; the rest appear unlinked rather than pointing somewhere guessed.
      Each logo is its owner's trademark, shown with permission; organizations whose artwork is
      not yet on file appear as set type.</p>
  </div>
</section>

<section class="section section-capabilities">
  <div class="wrap eco-layout">
    <figure class="eco-map reveal">
      <img src="assets/img/indiana-map.png"
           alt="Map of Indiana showing the test site network of airports, military installations and university partners."
           width="1061" height="1400" loading="lazy" decoding="async">
    </figure>
    <div class="reveal">
      <h2 class="h2">A statewide testing network</h2>
      <p class="section-intro-copy">The test site draws on airspace, military installations,
        universities and logistics corridors across Indiana — connecting design, testing and
        deployment in one onshore ecosystem.</p>
      <p><a class="link-arrow" href="/#ecosystem">See the full ecosystem list</a></p>
    </div>
  </div>
</section>
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
     "Five annual membership levels and published testing service rates at the Midwest UAS Test "
     "Site of Indiana.",
     pricing_page, ()),
    ("schedule.html", "/schedule", "Schedule a Test",
     "The five-step process for reserving range time at the Midwest UAS Test Site of Indiana.",
     schedule_page, ()),
    ("partners.html", "/partners", "Partners",
     "Government, defense, academic and commercial organizations in the Midwest UAS Test Site "
     "of Indiana ecosystem.", partners_page, ("partner-marquee.js",)),
]


def main():
    for filename, path, title, desc, body, scripts in PAGES:
        extra = "".join(
            f'\n<script src="assets/js/{s}?v={ASSET_V}" defer></script>' for s in scripts)
        html = (head(title, desc, path) + HEADER + body() + FOOTER
                + extra + "\n</body>\n</html>\n")
        # Collapse the blank lines the templating leaves behind
        html = re.sub(r"\n{3,}", "\n\n", html)
        (ROOT / filename).write_text(html)
        print(f"wrote {filename:24} -> {path}")


if __name__ == "__main__":
    main()
