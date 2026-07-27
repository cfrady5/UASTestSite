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
- `indiana-map.png`, `logo-iedc.png`, `logo-faa.png`, `logo-ari.png`, `hero-uav.jpg` —
  cropped from the 300 DPI render, which is colour-accurate.

## The inquiry form

The page is static, so the form has no backend. As shipped it validates client-side and
then opens the visitor's mail client addressed to `dale.lyles@theari.us` with the fields
formatted into the body. The direct email address is also shown in plain text next to the
form and in the footer, so the path never depends on JavaScript.

**To wire it to a real endpoint**, add a `data-endpoint` attribute to the form:

```html
<form class="inquiry-form" id="inquiryForm" data-endpoint="https://example.com/api/inquiry" novalidate>
```

The submit handler will then `POST` the fields as JSON instead of opening a mail client,
and will show success and failure states inline.

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
