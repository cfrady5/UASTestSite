# Midwest UAS Test Site of Indiana — Phase 1 Landing Page

A static, dependency-free landing page built from the Phase 1 content brief and the IEDC
print collateral (`iedc_midwest_uas_test_site_04_cropsbleeds.pdf`).

## Running it

There is no build step. Open `index.html`, or serve the folder:

```bash
python3 -m http.server 8000
# http://localhost:8000
```

Deploy by uploading the repository contents to any static host (Vercel, Netlify,
GitHub Pages, S3/CloudFront, or an existing CMS's static directory).

### Cache busting

`index.html` loads the stylesheet and script with a `?v=` query string. **Bump that number
whenever you edit `site.css` or `site.js`.** Without it, browsers happily serve a cached
stylesheet against freshly fetched HTML, so a CSS change appears not to have taken effect
until a hard refresh — which is easy to misread as the change never having been made.

### Before launch

`<link rel="canonical">` and `<meta property="og:url">` are commented out at the top of
`index.html`. Fill both in with this page's own public URL once it is known. They are left
out rather than guessed on purpose: a canonical pointing at another domain tells search
engines this page is a duplicate of that domain, which would suppress it from results.

## Structure

```
index.html              All page markup, meta tags and JSON-LD
assets/css/site.css     Design tokens + all styles
assets/js/site.js       Nav, scroll reveal, scroll-spy, form handling
assets/fonts/           Self-hosted woff2 (no third-party font requests)
assets/img/             Imagery and logos
```

## Brand tokens

Colors were sampled directly from a 300 DPI render of the print PDF:

| Token | Value | Use |
|---|---|---|
| `--blue` | `#254A9A` | IEDC primary blue — headings on light backgrounds |
| `--blue-deep` / `--blue-night` | `#16306B` / `#0E2050` | Dark section and header backgrounds |
| `--blue-mid` | `#1D6FC3` | Hero gradient highlight |
| `--gold` | `#FBC12C` | IEDC gold — accents, rules, headings on dark |
| `--mist` | `#E0E7E9` | Light blue-grey from the shield emblem |

### Typography

The print piece uses **Tusker Grotesk** (display) and **Montserrat** (body).

- **Montserrat** is used as-is — it is freely licensed and self-hosted here as a single
  variable woff2.
- **Tusker Grotesk is a commercial font** and is not licensed for web use in this repo.
  **Anton** is used as the display substitute; it was chosen from a rendered bake-off
  against the print headline (Anton, Oswald, Big Shoulders, Archivo Narrow, Fjalla One,
  Bebas Neue) as the closest match for Tusker's weight and condensation.

To swap in a licensed Tusker webfont later: drop the woff2 files into `assets/fonts/`,
add an `@font-face` block for them, and change `'Anton'` to `'Tusker Grotesk'` in the
one display-font rule at the top of the type scale in `site.css`.

### One deliberate deviation from the print piece

The print layout sets some headings in gold on white ("BUILT FOR TESTING. DESIGNED TO
SCALE.", "INDIANA DRONE STRATEGY"). Gold `#FBC12C` on white is roughly **1.75:1**
contrast, which fails WCAG AA for text at any size. On the web those headings are set in
`--blue` on light backgrounds with a gold rule as the accent, and gold is reserved for
text on the dark blue backgrounds, where it clears AA comfortably.

## Image assets

All imagery is derived from the supplied print PDF.

- `hero-drone-{1000,1600,2400}.jpg` — the hero photograph. The PDF stores it as a CMYK
  JPEG whose naive conversion is badly colour-shifted. The colour transform was solved by
  aligning the source against a 300 DPI poppler render (correlation 0.85) and fitting a
  degree-2 CMYK→RGB polynomial (mean residual 2.75/255). That recovers the full
  2625×1016 frame — 56% more image than the print crop exposes — free of the baked-in
  headline and emblem.
- `logo-shield.svg` — the emblem, vectorized from the embedded bitmap by colour-separating
  it into the four brand colours and tracing each layer with potrace.
- `indiana-map.png`, `logo-iedc.png`, `logo-ari.png`, `hero-uav.jpg` — cropped from the
  300 DPI render, which is colour-accurate.

### The map is a modified version of IEDC's artwork

`indiana-map.png` is no longer pixel-identical to the map in the print piece. **Indiana
State University was added to the Terre Haute cluster** at the client's request, having
been left off the original. The label is drawn in Montserrat Bold at 14px with -0.55px
tracking to match the surrounding labels, positioned in a gap verified clear of both
existing text and road lines.

ISU is set as a plain text label rather than a wordmark, because the university's own
logo was not supplied and inventing one would misrepresent their brand. If IEDC reissues
the map, that edit needs re-applying — the unmodified crop is in this repo's git history.

### Federal agencies are not named or depicted

The Test Site OTA prohibits displaying Agency or Federal Government seals, trademarks,
logos, service marks or trade names without prior written permission from the Agency:

> The Test Site Sponsor agrees not to display, or use any Agency or Federal Government
> seals, trademarks, logos, service marks, or trade names on the Company's websites,
> digital, or printed materials unless permission has been granted by the Agency in
> writing prior to the usage.

Because that clause covers **trade names** as well as marks, the site now carries no
reference to the FAA at all — not the seal, not the name, not the acronym, and not a link.
Removed: the footer seal (and its image file), the "Federal Aviation Administration (FAA)"
entry under Sponsoring Organizations, and every instance of "FAA-designated".

**The designation claim survives as "one of only 9 federally designated UAS test sites in
the nation."** The count is the load-bearing fact and it is unchanged; only the naming of
the designating agency is gone. If the sponsor reads the clause narrowly enough to permit
naming the agency descriptively, restoring "FAA-designated" is a search-and-replace and
puts back a materially stronger credibility claim.

The image file is deleted rather than just unreferenced, because an unreferenced asset
still resolves at its URL on a static host. Git history holds it for when approval lands.

## The inquiry form

The page is static, so the form has no backend. As shipped it validates client-side and
then opens the visitor's mail client addressed to `MidwestUASTestSite@theari.us` with the fields
formatted into the body. The direct email address is also shown in plain text next to the
form and in the footer, so the path never depends on JavaScript.

**To wire it to a real endpoint**, add a `data-endpoint` attribute to the form:

```html
<form class="inquiry-form" id="inquiryForm" data-endpoint="https://example.com/api/inquiry" novalidate>
```

The submit handler will then `POST` the fields as JSON instead of opening a mail client,
and will show success and failure states inline.

## Partner links

All 19 entries in the Ecosystem section link to the partner's official site, opening in a
new tab. The labels and URLs are the client-supplied canonical list — treat that list as
the source of truth over anything inferred.

Three are worth knowing about if the list is ever edited:

- **Camp Atterbury and Muscatatuck are separate pages.** They are operated jointly as
  Atterbury-Muscatatuck, but the Indiana National Guard site gives them distinct URLs
  (`/camp-atterbury/` and `/muscatatuck-training-center/`).
- **81st Troop Command and 38th Infantry Division have no standalone sites.** Both point at
  their unit pages on the Indiana National Guard site.
- **IEDC is linked without the `www.` subdomain** (`https://iedc.in.gov/`) and ARI includes
  the locale path (`https://www.theari.us/en/`). These match the supplied list; the footer
  logos use the same URLs so the two places cannot drift apart.

Several entries use the organization's full official name rather than the shorter form in
the Phase 1 brief — "Grissom Air Reserve Base" over "Grissom Air Reserve", "Defense Finance
and Accounting Service (DFAS)" over "DFAS", and so on.

The pill styling lives on the `<a>`, not the `<li>`, so the whole chip is a hit target. An
entry added as bare `<li>` text will render unstyled — wrap it in an anchor, or move the
pill rules if you need genuinely unlinked entries.

## Accessibility and progressive enhancement

- Semantic landmarks, a skip link, and visible focus rings throughout.
- Scroll-reveal animation is disabled under `prefers-reduced-motion`, and a `no-js` guard
  means content is never left hidden if JavaScript fails to load.
- The mobile nav is keyboard operable and closes on `Escape`.
- The Indiana map carries a long `alt` description listing the assets it plots.
- A print stylesheet flattens the dark sections for legible hard copy.

## Content source

All copy comes from `Phase_1_Midwest_UAS_Test_Site_Landing_Page.pdf`. Section headings,
capability descriptions, the two leadership quotes, and the partner lists are reproduced
verbatim; only light connective phrasing was added for hero and section lead-ins.

Section 7 of the brief, "Indiana Drone Strategy (Core Pillars)", was intentionally dropped
from the page at the client's request. It is the one brief section not represented here.

### Wording changed from the brief, on purpose

Two headings were softened at the client's request to avoid asserting a competitive
ranking that could be challenged:

| Brief / earlier draft | Now reads |
|---|---|
| "Why Indiana Leads in UAS Testing" | "Why test in Indiana" |
| "Indiana is ready to lead" | "What Indiana's leaders are saying" |

The second was not in the brief — it was a heading written for the quotes section, and it
made the same "leads" claim the client asked to drop, so it was changed for consistency.
The Senator Young quote beneath it says Indiana is ready to *help* lead, so the old
heading also slightly overstated its own source. The quotes themselves are untouched.

The "one of only 9" count is retained — that is a factual designation rather than a
ranking claim. See "Federal agencies are not named or depicted" above for why the
designating agency is no longer named alongside it.

### Contact

No individual is named on the page. The contact section and the inquiry form both route to
the shared inbox `MidwestUASTestSite@theari.us`, and the JSON-LD `contactPoint` carries the
address with no `name` field. The address is shown in plain text in the contact section and
the footer, so the path to reach the team never depends on JavaScript.
