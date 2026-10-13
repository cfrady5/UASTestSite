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

Every page loads the stylesheet and script with a `?v=` query string. **Bump that number
whenever you edit `site.css` or `site.js`.** Without it, browsers happily serve a cached
stylesheet against freshly fetched HTML, so a CSS change appears not to have taken effect
until a hard refresh — which is easy to misread as the change never having been made.

It lives in two places: `ASSET_V` at the top of `tools/build_pages.py` (for the generated
pages), and literally in `index.html`, `membership.html` and `membership-thanks.html`.
Change both and re-run the generator, or half the site runs on a stale stylesheet. Current
value: **31**.

### Clean URLs

`vercel.json` sets `cleanUrls: true` and `trailingSlash: false`, so pages are served
without the `.html` extension:

| File | URL |
|---|---|
| `index.html` | `/` |
| `membership.html` | `/membership` |
| `membership-thanks.html` | `/membership-thanks` |
| `capabilities.html` | `/capabilities` |
| `industries.html` | `/industries` |
| `pricing.html` | `/pricing` |
| `schedule.html` | `/schedule` |
| `partners.html` | `/partners` |

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

capabilities.html       ┐
industries.html         │ Expansion pages. Generated — see "Expansion pages" below.
pricing.html            │ Not in the nav; reachable by direct link only.
schedule.html           │
partners.html           ┘

assets/css/site.css     Design tokens + all styles
assets/js/site.js       Nav, scroll reveal, scroll-spy, tabs, form handling
assets/js/map-data.js   GENERATED geometry + tables for the capabilities map
assets/js/capabilities-map.js   The interactive capabilities explorer
assets/js/partner-marquee.js    The scrolling partner rows
assets/fonts/           Self-hosted woff2 (no third-party font requests)
assets/img/             Imagery and logos
tools/site_data.py      Capabilities, facilities and partners — one copy, shared
tools/build_pages.py    Generator for the five expansion pages
tools/build_map.py      Generator for assets/js/map-data.js
tools/fetch_geo.py      Cuts the upstream geodata down to tools/geo-src/
tools/geo-src/          Committed Indiana-only geodata extracts
tools/apps-script/      Inquiry-form endpoint for Google Apps Script
```

## Expansion pages

Five pages — capabilities, industries, pricing and membership, schedule a test, and
partners — are **generated**, not hand-written:

```bash
python3 tools/build_pages.py
```

It writes plain `.html` files that are committed and served directly. **Vercel never runs
it**; there is still no build step in the deploy. Run it by hand after editing a page body
or a shared partial, and commit the result.

It exists because the header and footer were already duplicated across three files, and
eight is where that stops being realistic — one nav change would mean eight correct edits
or a silent inconsistency. `index.html`, `membership.html` and `membership-thanks.html`
predate the generator and are still maintained directly, so **a change to the shared header
or footer has to be made in `tools/build_pages.py` and in those three files.** Folding them
into the generator is the obvious next cleanup.

### They are not in the nav, on purpose

The client asked for these published but not linked, for review by direct URL:

```
/capabilities   /industries   /pricing   /schedule   /partners
```

`HEADER` in the generator deliberately carries only Home, Membership and the CTA. Nothing
on `index.html` links to them either. When they are ready to go live, add them to the nav
in `tools/build_pages.py` **and** in the three hand-maintained files, and re-run it.

### The capabilities map

`/capabilities` is an interactive explorer: the ten capabilities on the left, a
layered SVG of the Indiana testing network on the right, a detail panel under the
navigation and a legend under the map. Selecting a capability highlights its
locations and dims the rest to 20%; selecting a marker — or a chip in the list
under the map — works the other way and shows what is at that location.

**The geometry is real, and none of it is traced from the IEDC print map.**
`assets/js/map-data.js` is generated by `tools/build_map.py`:

| Layer | Source |
|---|---|
| State outline | Dissolved from the county polygons — the perimeter of the same geometry, so the two can never disagree |
| 92 counties | US Census cartographic boundary file, 1:500,000 (2010) |
| Interstates | Natural Earth 10m roads |
| Rivers, Lake Michigan | Natural Earth 10m rivers and lakes |
| City markers | Natural Earth 10m populated places |
| Airport markers | OurAirports, via the `airportsdata` package |
| Campus and installation markers | Site centroids, approximate to about a kilometre and labelled as such in the detail panel |

Everything is projected through one Albers equal-area conic (standard parallels
38°N and 41.5°N), so every layer registers against every other exactly.

```bash
pip install airportsdata
python3 tools/fetch_geo.py     # only when a source changes upstream
python3 tools/build_map.py     # after editing tools/site_data.py
```

`tools/geo-src/` holds Indiana-only extracts of the upstream files, committed so
the build runs offline. `fetch_geo.py` is what cut them down, and documents where
each came from.

**Markers are nudged apart where they overlap.** Several are co-located — the
38th Infantry Division and 81st Troop Command share Stout Field exactly — and
would otherwise be one unclickable blob. `declutter()` pushes markers to a
minimum of 20 SVG units apart, about 6.5 km, which on a 450 km-tall state is
under half a percent. Only the display position moves: the coordinates in the
detail panel are as sourced, and any marker that moved says so.

**What the map does not draw.** There are layers for testing range polygons,
BVLOS corridors and coverage areas, and all three are empty. No approved
geometry has been published, so none is drawn and none is estimated. The legend
names the missing layers rather than leaving a visitor to assume there is
nothing there. Add real geometry to `RANGES` / `CORRIDORS` / `AREAS` in
`site_data.py` and it renders; anything marked `illustrative` renders dashed and
is labelled as illustrative, so it can never read as an approved boundary.

**Capability-to-location assignments are not invented.** Every capability's
`sites` list is empty, because none has been supplied. While a list is empty the
map highlights the whole testing network and the panel says the assignment is
unconfirmed. Fill a list in and that capability starts highlighting only its own
sites — no other change needed. Remote COA Development and the Pilot
Certification Course are marked `kind: "service"` and deliberately highlight
nothing: they have no testing footprint, and drawing one would be a geographic
claim about something with no geography.

**One deviation from the print map.** The IEDC piece fills Indiana with brand
gold. Here the land is near-white and gold is spent only on selection and
highlight — on a map where gold means "this is selected", a gold landmass leaves
the highlight nowhere to go.

### The partner marquees

`/partners` scrolls each category as one or two rows, adjacent rows running in
opposite directions, built by `assets/js/partner-marquee.js`.

The loop is seamless because the track is the sequence repeated until it is wider
than the viewport plus one sequence, and the animation moves it by the **measured**
width of exactly one sequence — so the frame at the end of the cycle is
pixel-identical to the frame at the start. The width is measured from the DOM and
re-measured on resize, after logos load and after fonts settle; a guessed width is
what produces a visible stutter. Movement is a CSS animation on `transform`, so it
runs off the main thread; JavaScript only measures. Hovering or focusing a row
sets `animation-play-state: paused`, which freezes the track where it is rather
than resetting it.

Only the first sequence is real content. Every repeat is `aria-hidden` with its
links taken out of the tab order, so each organization is announced once and
tabbed to once.

**Most organizations have no logo yet, and that is not an oversight.** Two
constraints:

1. Third-party logos are trademarks. Each needs permission from its owner before
   it goes on this site.
2. The Test Site OTA separately forbids displaying federal and agency seals,
   trademarks, logos and service marks without prior written permission — the
   same clause that keeps the FAA logo off the site. That covers NSWC Crane and
   the Indiana National Guard here.

Organizations without a logo render as a set wordmark at the same height, not as
a missing image. To add one: drop the asset in `assets/img/partners/`, set `logo`
on that organization in `site_data.py`, and re-run `build_pages.py`. SVG is
preferred; the cell has a fixed height and a free width, so proportions are
never forced.

**Websites are linked only where the URL is confirmed.** 33 of the 36 link out,
from the client's own sponsor asset pack. Three deliberately do not:

| Organization | Why it is unlinked |
|---|---|
| **HUF** | The pack resolves it to Terre Haute Regional Airport but supplies `huf.com`, which is an apparel brand. The two do not match. |
| **Ecodyne** | The pack resolves it to *Echodyne* — different spelling, different company — and says to confirm first. |
| **Raider** | The pack offers Raider Technologies but flags the identity as unverified. |

A wrong link on a partner's name is worse than no link. Add a confirmed URL in
`site_data.py` and it becomes a link.

**Four entries are airport codes, not associations.** The client's slide groups
HUF, BMG, LAF and BAK under Industry Associations, and they are Terre Haute
Regional, Monroe County, Purdue University and Columbus Municipal airports. The
grouping and the on-screen labels are the client's to change, so both stay as
given; the `expand` field carries the real identity into the link's accessible
name, appended to the visible text rather than replacing it so WCAG 2.5.3 still
holds.

### Claims that were deliberately softened

The expansion brief is a working document and several things in it would be assertions the
site cannot yet support. Each is handled in `tools/build_pages.py`, with a comment:

- **BVLOS and urban testing carry an "In development" badge.** The corridor holds
  preliminary approval and the dense urban canyon component is proposed; neither is
  operational, and the page says so.
- **No capability is mapped to a location.** The brief supplied a list of capabilities and
  a list of sites, not a mapping. Inventing one would misstate where work can be performed.
- **Blank rates render as "Contact for pricing"**, which asserts no particular price, and a
  note says published rates are list prices confirmed before scheduling.
- **Partners are not labelled "Sponsors (Tier 1 Members)."** That is a claim about a paying
  commercial relationship, and several entries are federal or state bodies unlikely to hold
  one. They are grouped by field of work, with a note saying nothing about status.
- **Membership benefits referencing guaranteed BVLOS access carry a qualifier**, since they
  depend on a corridor that is not yet operational.
- **Creating a member account is stated not to approve range access.**

If any of these is wrong — if the corridor is operational, or those organisations really
are Tier 1 members — fix the data in the generator and re-run it.

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

### Required fields

Seven fields are required: first name, last name, email, title, organization name,
organization state and organization type. Organization country was already required in the
Salesforce export.

**This is applied in `site.js`, not in the markup**, keyed by field name so it survives a
re-export — marking them up by hand would be silently undone the next time the form is
regenerated. Each gets a red asterisk in its label, unless Salesforce already put one
there, and the panel carries a "\* Indicates a required field" legend.

Invalid fields are outlined using `:user-invalid` rather than `:invalid`, so nothing turns
red until the visitor has actually interacted with it.

**Client-side only.** This catches honest mistakes; it does not stop a direct POST to
Web-to-Lead. For real enforcement the same fields should be marked required in Salesforce,
which would also mean future exports carry `required` themselves.

### Re-importing the Salesforce export

When Salesforce regenerates this form, **three values in the export must not be copied
over as-is:**

- **`retURL`** — exports carry whatever URL was configured when the form was built. It must
  be `https://www.midwestuastestsite.us/membership-thanks` (the live domain, extensionless).
  The exports seen so far still say `uas-test-site.vercel.app/membership-thanks.html`.
- **The `<script>` tags** need unwrapping from their `<p>`.
- **The trailing `<style>` block** must be dropped — it restyles inputs site-wide.

Everything else can be pasted verbatim. Diff a new export against the live form before
swapping it in; so far the only real changes between exports have been `captcha_settings`
keyname and `data-sitekey`, with every field id, the org id and the record type identical.

### reCAPTCHA: the key must be v2 Checkbox, and three places must agree

**The key type is not interchangeable.** The form loads classic `api.js` with a
`g-recaptcha` div, and Salesforce verifies the response with a v2 secret. So the site key
has to be a classic **reCAPTCHA v2 "I'm not a robot" Checkbox** key, created at
[google.com/recaptcha/admin](https://www.google.com/recaptcha/admin).

A reCAPTCHA **Enterprise** or **v3** key in that slot renders

> ERROR for site owner: Invalid key type

and the form cannot be submitted. Enterprise keys are created in Google Cloud, come paired
with an `AIza…` Cloud API key, and require `enterprise.js` plus a server-side assessment
call — none of which fits a static page posting to Salesforce Web-to-Lead.

The two error messages mean different things and are worth telling apart:

| Message | Cause |
|---|---|
| `Invalid domain for site key` | Right key type, host missing from the key's domain list |
| `Invalid key type` | Wrong kind of key — Enterprise or v3 where v2 Checkbox is required |

Three things must agree, or the form fails in different ways:

1. **The site key in `membership.html`** — must be v2 Checkbox, currently `6LdL…v7Yj`.
2. **The domain list on that key**, in the reCAPTCHA admin console. It needs every host the
   page is served from: `www.midwestuastestsite.us`, the apex if it serves directly, and
   `uas-test-site.vercel.app` while that URL is still used for review.
3. **The key pair registered in Salesforce Setup**, named by `captcha_settings` in the form
   — currently `ARI_UAS_WebToLead`. If the site key in the markup is changed without
   repointing that Salesforce entry at the same pair, the captcha renders and solves
   correctly in the browser and Salesforce still rejects the lead server-side.

Item 3 fails silently — nothing on the page looks wrong. Confirm it with a real test
submission whenever the key changes.

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
- **The pricing tabs are built by JavaScript, not shipped in the markup.** Each rate group
  is a plain `<section>` under its own heading; `site.js` folds them into a tablist and
  takes each button's label from that heading, so the label lives in one place. Without the
  script there are no tabs and all four groups are simply on the page — nothing is hidden
  behind a control that does not work. The tablist follows the ARIA tabs pattern: one tab
  stop for the list, arrows/Home/End to move between tabs.
- The membership comparison table scrolls inside a focusable named region rather than
  forcing the page wide.
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
