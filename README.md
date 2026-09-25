# Midwest UAS Test Site of Indiana — Phase 1 Landing Page

A static, dependency-free landing page built from the Phase 1 content brief and the IEDC
print collateral (`iedc_midwest_uas_test_site_04_cropsbleeds.pdf`).

## Running it

There is no build step, but the site uses **clean URLs** (`/membership`, not
`/membership.html`), so a plain file server is not enough for local preview — internal
links would 404. Use a server that resolves extensionless paths:

```bash
npx serve .          # clean URLs by default
# or, to match production exactly:
vercel dev
```

Opening `index.html` straight off disk no longer works for navigation either, for the same
reason. `python3 -m http.server` still serves assets fine but will 404 on `/membership`.

Deploy target is **Vercel**, which `vercel.json` now configures. See "Clean URLs" below
before moving to another host.

### Cache busting

`index.html` loads the stylesheet and script with a `?v=` query string. **Bump that number
whenever you edit `site.css` or `site.js`.** Without it, browsers happily serve a cached
stylesheet against freshly fetched HTML, so a CSS change appears not to have taken effect
until a hard refresh — which is easy to misread as the change never having been made.

### Clean URLs

`vercel.json` sets `cleanUrls: true` and `trailingSlash: false`, so pages are served
without the `.html` extension:

| File | URL |
|---|---|
| `index.html` | `/` |
| `membership.html` | `/membership` |
| `membership-thanks.html` | `/membership-thanks` |

Vercel also **308-redirects the old `.html` URLs to the clean ones**, so links already
shared — including the Midwest UAS Test Site tile on ARI's site — keep working rather than
breaking.

Internal links are root-relative (`/`, `/membership`, `/#contact`). Two consequences:

- **This is now Vercel-specific.** `cleanUrls` is a Vercel feature. Moving to GitHub Pages
  or S3 would mean restructuring pages into directories (`membership/index.html`) instead,
  which achieves the same URLs on any host.
- **Local preview needs a clean-URL server** — see "Running it" above.

### Before launch

**Attach the custom domain in Vercel.** The site is built for
`https://www.midwestuastestsite.us/` — canonical URLs, `og:url`, and the Salesforce
`retURL` all point there — but the domain is **not yet connected to the Vercel project**.
Until it is, those URLs resolve to nothing. In Vercel: Project → Settings → Domains, add
`www.midwestuastestsite.us`, point DNS as instructed, and redirect the apex
(`midwestuastestsite.us`) to `www`.

**Attaching the domain also makes the site public.** The project has SSO protection set to
`all_except_custom_domains`, so every `.vercel.app` URL requires a Vercel login while the
custom domain does not. Connecting the domain is what opens the site to visitors — no
protection setting needs changing.

**Swap the ARI links off the review deployment.** Both the footer logo and the Ecosystem
entry point at `https://ari-for-review.vercel.app/`, ARI's staging build, at the client's
request. Preview deployments are not permanent addresses — move both to ARI's production
domain before this page is announced. There is a comment above the footer link marking it.

## Structure

```
index.html              Landing page
membership.html         Membership registration — hosts the Salesforce form
membership-thanks.html  Post-submission confirmation (Salesforce retURL target)
assets/css/site.css     Design tokens + all styles
assets/js/site.js       Nav, scroll reveal, scroll-spy, form handling
assets/fonts/           Self-hosted woff2 (no third-party font requests)
assets/img/             Imagery and logos
tools/apps-script/      Inquiry-form endpoint for Google Apps Script
```

The header and footer are duplicated across the three HTML files. At three pages that is
still cheaper than introducing a build step, but it is the thing to watch: a change to the
nav or footer has to be made in every file. **Past about four pages, add a small static
site generator** rather than keeping that up by hand.

## Membership registration pages

`membership.html` carries the live Salesforce Web-to-Lead form, wrapped in `div.sf-embed`.
`membership-thanks.html` is the `retURL` target Salesforce redirects to on success, and is
`noindex` so it cannot surface in search ahead of the registration page.

### Two edits were made to the Salesforce export

Everything else is byte-for-byte as Salesforce generated it. **Re-apply only these two
after any re-export:**

1. **The `<script>` tags were unwrapped from their `<p>`**, which otherwise renders a stray
   empty paragraph above the form.
2. **The trailing `<style>` block was dropped.** It set `input[type=text], select { … }`
   with no scoping — that restyles every input on any page the markup lands on — and
   painted the submit button ARI navy rather than test-site gold. Everything it did is
   covered by the `.sf-embed` rules in `site.css`, scoped to the wrapper.

**Do not hand-edit the markup for styling or accessibility.** Salesforce regenerates it
whenever the form changes, so those edits vanish on the next export. Styling is handled by
`.sf-embed` rules, and labelling by the runtime fix below.

### Check `retURL` on every re-export

```
name="retURL" value="https://www.midwestuastestsite.us/membership-thanks"
```

Without it, submitters land on a blank Salesforce page. It is an absolute URL, so it will
**not** follow the site to a custom domain — update it when the domain changes. Note it is
the extensionless URL; the `.html` form still reaches the page via redirect, but point new
exports at the clean one.

### Half the fields arrive without labels

Web-to-Lead labels the "About You" fields properly but writes the organization fields as a
loose text node before the control (`Organization Name:<input>`), with no element at all.
Those fields reach screen readers unnamed, and because a text node cannot be styled, they
also render as plain body copy beside the properly labelled fields above.

`site.js` fixes this at runtime by wrapping that text in a real `<label for=…>`. That is a
genuine programmatic label rather than an `aria-label` patch, it picks up the `.sf-embed`
label styling so the form reads as one form, and — being runtime — it handles the next
export instead of silently regressing. Verified: all 18 controls are labelled, and clicking
a generated label focuses its field.

### reCAPTCHA: key and domains must line up in three places

The widget's **site key is public and lives in `membership.html`** (`data-sitekey`). It is
currently `6Lcz…pqJF`. A Google Cloud **API key is not used by this site at all** — it is a
server-side credential for reCAPTCHA Enterprise assessments, and a static site has no
server. Never commit one here.

Three things have to agree, or the form fails in different ways:

1. **The site key in `membership.html`** — wrong key, or a key that does not cover the
   host, renders "ERROR for site owner: Invalid domain for site key" instead of the
   checkbox. The page's own script then blocks submit, so **nobody can register at all**.
2. **The domain list on that key**, in the
   [reCAPTCHA admin console](https://www.google.com/recaptcha/admin). It needs every host
   the page is served from: `www.midwestuastestsite.us`, the apex if it serves directly,
   and `uas-test-site.vercel.app` while that URL is still in use for review.
3. **The key registered in Salesforce Setup.** The form posts
   `captcha_settings` with `"keyname":"ARI_Communities"`, which names a key pair configured
   inside Salesforce. If the site key in the HTML is changed without repointing that
   Salesforce entry at the same key pair, the captcha will render and solve correctly in
   the browser and Salesforce will still reject the lead server-side — a failure that looks
   like nothing is wrong on the page.

Item 3 is the one that bites silently. Confirm it with a real test submission whenever the
key changes.

### Known, and not defects

- **`html-validate` reports errors on the membership page.** Every one is inherent to the
  Salesforce markup: inline `style` attributes, record IDs beginning with digits,
  `multiple="multiple"` boolean style, a deprecated `width` on the hidden table. None
  affect rendering, and none are fixable without hand-editing generated markup.
- **Salesforce IDs start with digits**, so `#00NHs…` is not a valid CSS selector. Target
  those fields by attribute (`[id="00NHs…"]`) if you ever need to.
- **reCAPTCHA adds a third-party dependency.** The page loads
  `google.com/recaptcha/api.js`; the rest of the site makes no third-party requests (fonts
  are self-hosted). It also sets Google cookies, which is worth a look from whoever owns
  the privacy position — the site has no privacy policy yet.

### Navigation

The nav is deliberately minimal: **Home, Membership, and the Submit an Inquiry CTA.** The
landing page's own sections (Why Indiana, Infrastructure, Capabilities, Ecosystem) were
removed from it at the client's request — they are page sections rather than pages.

Those sections keep their ids and are still reachable from the hero's "Explore
Capabilities" button and from the membership page's sidebar link, but **not from the nav**.
If the site grows to more real pages, they are easy to restore.

The nav breakpoint is **820px** — the row needs about 750px, and below ~820 the drawer
takes over. It is declared in two places, `site.css` and the `matchMedia` query in
`site.js`; **both must move together**, and each carries a comment saying so. It has moved
twice already as links were added and removed, so re-measure rather than guess: the sweep
that set it checks for overflow and horizontal scroll from 1600px down to 320px.

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

### Making it deliver to the shared inbox

The `mailto:` handoff works, but it depends on the visitor having a mail client
configured, and the inquiry is lost if they close the compose window. To have
submissions arrive at `MidwestUASTestSite@theari.us` without that dependency, the form
needs an endpoint to POST to. A static page has no server of its own, so this step
cannot be skipped.

**Chosen route: Google Apps Script**, so mail is sent by ARI's own Google Workspace
tenant and no third-party service ever sees an inquirer's details.

#### Deploying the endpoint

Do this from a `theari.us` Google account — the mail is sent by whoever deploys it, so
prefer a shared or service account over a personal one.

1. Go to <https://script.google.com> and create a new project. Name it something like
   "Midwest UAS Test Site — inquiry form".
2. Replace the contents of `Code.gs` with `tools/apps-script/Code.gs` from this repo.
   Confirm the `TO` constant at the top is the shared inbox.
3. Run the `sendTestEmail` function once from the editor. Google will prompt for
   authorization — grant it, then confirm the test mail reaches the inbox. This proves
   the script can send before any web wiring exists.
4. **Deploy → New deployment → Web app**, with:
   - *Execute as*: **Me**
   - *Who has access*: **Anyone**

   "Anyone" is required — the visitor is not signed into Google. It exposes only this
   script, which does nothing but validate a payload and email the inbox.
5. Copy the Web app URL. It looks like
   `https://script.google.com/macros/s/AKfycb.../exec`.
6. Add two attributes to the `<form>` in `index.html`:

   ```html
   <form class="inquiry-form" id="inquiryForm"
         data-endpoint="https://script.google.com/macros/s/AKfycb.../exec"
         data-content-type="text/plain;charset=utf-8" novalidate>
   ```

7. Submit a real inquiry through the live page and confirm it arrives.

**`data-content-type` is not optional here.** An `application/json` POST is a
preflighted cross-origin request, and Apps Script never answers the `OPTIONS`
preflight, so the request fails before it is delivered. `text/plain` keeps it a simple
request; the body is still JSON and the script parses it identically.

Re-deploying after editing the script creates a **new URL** unless you use
*Deploy → Manage deployments → Edit → Version: New version*, which keeps the existing
one. Use that, or step 6 has to be repeated each time.

#### Microsoft 365 instead

If ARI is on Microsoft 365 rather than Google Workspace, the equivalent is a Power
Automate flow: trigger **When an HTTP request is received**, action **Send an email
(V2)** to the shared inbox, mapping the same JSON fields. Paste the generated URL into
`data-endpoint`. Test whether it needs `data-content-type` too — if the browser console
shows a CORS error, set it to `text/plain;charset=utf-8` as above.

#### Other backends

Any URL accepting a JSON `POST` works. The body is:

```json
{ "name": "...", "email": "...", "organization": "...", "interest": "...",
  "message": "...", "subject": "Test Site Inquiry — Name (Org)" }
```

`_subject` is sent alongside `subject` because services differ on which key they read,
and `access_key` is included when `data-access-key` is set (Web3Forms and similar).
Hosted options such as Formspree work with `data-endpoint` alone — but note they put a
third party in the path of every inquirer's details, which is what the Apps Script route
avoids.

#### How failures are reported

Apps Script cannot return a non-200 status, so it signals rejection with `{"ok": false}`
in a 200 response. The page checks the body as well as the status code, so a rejected
submission shows the error state rather than falsely telling the visitor their inquiry
was sent. Any failure falls back to "please email the inbox directly", so there is
always a route to the team.

### Spam protection

The form carries a honeypot field (`#f-website`) that is off-canvas and `aria-hidden`, so
neither sighted visitors nor screen readers encounter it. When it comes back filled, the
page shows the normal success message and sends nothing — the bot gets no signal that it
was caught. This handles naive bots; if the inbox still attracts spam, add the chosen
service's own captcha rather than replacing the honeypot.

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

Headings and claims softened at the client's request, so the page does not assert more
than the programme can currently support:

| Brief / earlier draft | Now reads |
|---|---|
| "Why Indiana Leads in UAS Testing" | "Why test in Indiana" |
| "Indiana is ready to lead" | "What Indiana's leaders are saying" |
| "Advanced Urban & BVLOS Testing" | "Expanding Urban & BVLOS Testing" |

"Indiana is ready to lead" was not in the brief — it was a heading written for the quotes
section, and it made the same "leads" claim the client asked to drop. The Senator Young
quote beneath it says Indiana is ready to *help* lead, so it also overstated its own
source. The quotes themselves are untouched.

**"Advanced" was changed because the corridor and the urban canyon component are not yet
operational.** The brief's body copy already hedged ("preliminarily-approved",
"proposed"), but the heading read as a present-tense capability, and headings are what
visitors scan. The body now says both are "in development and subject to regulatory
approval" — worded without naming the approving agency, per the OTA constraint above.

**Still worth reviewing:** the "Public Safety & Urban Operations" capability card lists
"dense urban conditions and extended BVLOS corridors" among environments the site tests
in. That is brief copy and reads as present-tense capability for the same two things.
If the corridor and urban canyon are pre-operational, that card carries the same overclaim
and should be softened to match.

### Added beyond the brief

"Defense Installation Access" was added to the *Why test in Indiana* list at the client's
request, so the military relationship appears in the section answering "why here" rather
than only further down under Infrastructure.

**The brief's "no DoD contract required" clause was then removed at the client's request,
from both that bullet and the Infrastructure card**, so the two now differ only in that
Infrastructure also mentions "programs". If that reads as repetition, the Why Indiana
bullet is the one to reword — Infrastructure carries the brief's original line.

### Contact

No individual is named on the page. The contact section and the inquiry form both route to
the shared inbox `MidwestUASTestSite@theari.us`, and the JSON-LD `contactPoint` carries the
address with no `name` field. The address is shown in plain text in the contact section and
the footer, so the path to reach the team never depends on JavaScript.
