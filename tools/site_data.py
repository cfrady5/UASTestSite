#!/usr/bin/env python3
"""
Shared site data.

`build_pages.py` (page copy) and `build_map.py` (the capabilities map) both
import from here, so a capability or a partner organisation is written down once
and cannot drift between the two.

Read the comments before editing. Several fields exist specifically to keep the
site from asserting things it has not been told, and quietly filling them in
changes what the published pages claim.
"""

# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------
# status      'operational' | 'in-development'
#             'in-development' prints an "In development" badge and pulls in the
#             regulatory qualifier. The BVLOS corridor holds preliminary
#             approval and the urban canyon component is proposed.
#
# kind        'range'   — performed at one or more physical sites
#             'service' — delivered as a service, with no testing footprint of
#                         its own. These deliberately highlight nothing on the
#                         map; inventing a coverage area for a paperwork service
#                         would be a geographic claim about something that has
#                         no geography.
#
# definition  Defines the capability TYPE, in ordinary industry terms. It is not
#             a description of what this test site offers — see `description`.
#
# description What the test site provides. Left None for all ten: the expansion
#             brief supplied capability names only. Fill these in from approved
#             copy and the detail panel picks them up automatically.
#
# sites       Facility ids (see FACILITIES) with a CONFIRMED relationship to the
#             capability. Empty everywhere today, because no capability-to-site
#             assignment has been supplied. While a list is empty the map shows
#             the whole testing network in an explicit "assignment pending"
#             state rather than guessing. Fill one in and that capability starts
#             highlighting only its own sites.
#
# counties    County ids (FIPS, 3-digit) with a confirmed relationship. Same
#             rule as `sites`.
# ---------------------------------------------------------------------------
CAPABILITIES = [
    {
        "id": "basic-los",
        "name": "Basic LOS Testing",
        "status": "operational",
        "kind": "range",
        "definition": "Flight testing conducted while the aircraft stays within "
                      "the operator's unaided visual line of sight.",
        "description": None,
        "sites": [],
        "counties": [],
    },
    {
        "id": "bvlos",
        "name": "BVLOS Testing",
        "status": "in-development",
        "kind": "range",
        "definition": "Flight testing beyond the operator's visual line of sight, "
                      "relying on detect-and-avoid and command-and-control systems "
                      "rather than direct observation.",
        "description": None,
        "sites": [],
        "counties": [],
        "corridors": [],   # no approved corridor geometry has been published
    },
    {
        "id": "kinetic",
        "name": "Kinetic Testing",
        "status": "operational",
        "kind": "range",
        "definition": "Testing that involves live ordnance, projectiles or "
                      "physical interception, which requires a range cleared and "
                      "controlled for it.",
        "description": None,
        "sites": [],
        "counties": [],
    },
    {
        "id": "urban",
        "name": "Urban Testing",
        "status": "in-development",
        "kind": "range",
        "definition": "Testing in a built environment, where structures restrict "
                      "line of sight, obstruct GPS and create the signal "
                      "conditions of a real city.",
        "description": None,
        "sites": [],
        "counties": [],
    },
    {
        "id": "cuas",
        "name": "cUAS Testing",
        "status": "operational",
        "kind": "range",
        "definition": "Counter-UAS testing: evaluating systems that detect, track, "
                      "identify or defeat unmanned aircraft.",
        "description": None,
        "sites": [],
        "counties": [],
    },
    {
        "id": "sensor",
        "name": "Sensor Testing",
        "status": "operational",
        "kind": "range",
        "definition": "Characterising payload and onboard sensors — optical, "
                      "infrared, radar and radio frequency — against known "
                      "references.",
        "description": None,
        "sites": [],
        "counties": [],
    },
    {
        "id": "motion-capture",
        "name": "Motion Capture Lab",
        "status": "operational",
        "kind": "range",
        "definition": "An indoor volume instrumented for precise position and "
                      "attitude tracking, used to validate flight control and "
                      "autonomy before outdoor flight.",
        "description": None,
        "sites": [],
        "counties": [],
    },
    {
        "id": "hypersonics",
        "name": "Hypersonics Lab",
        "status": "operational",
        "kind": "range",
        "definition": "Laboratory facilities for testing at speeds above roughly "
                      "Mach 5, where aerodynamic heating and material behaviour "
                      "dominate.",
        "description": None,
        "sites": [],
        "counties": [],
    },
    {
        "id": "remote-coa",
        "name": "Remote COA Development",
        "status": "operational",
        "kind": "service",
        "definition": "Preparing and submitting a Certificate of Waiver or "
                      "Authorization — the airspace authorization an operator "
                      "needs before flying a given profile.",
        "description": None,
        "service_note": "An airspace authorization service rather than a testing "
                        "location. It is prepared for the airspace your operation "
                        "needs, so it has no testing footprint of its own on this "
                        "map.",
        "sites": [],
        "counties": [],
    },
    {
        "id": "pilot-certification",
        "name": "Pilot Certification Course",
        "status": "operational",
        "kind": "service",
        "definition": "Training and certification for remote pilots.",
        "description": None,
        "service_note": "A training course rather than a testing location. "
                        "Delivery is arranged with the operations team, so it has "
                        "no testing footprint of its own on this map.",
        "sites": [],
        "counties": [],
    },
]

# ---------------------------------------------------------------------------
# Facilities plotted on the map
# ---------------------------------------------------------------------------
# Mirrors the facilities on the IEDC network map (assets/img/indiana-map.png),
# which is the reference this map reconstructs.
#
# type       'city' | 'airport' | 'port' | 'military' | 'university' | 'agency'
#
# network    True marks one of the six locations the client named as "Locations
#            in the testing network". Everything else is context, and dims when a
#            capability is selected.
#
# precision  'dataset' — the coordinate comes from a cited dataset, exactly as
#                        published. Airports are OurAirports (via the
#                        `airportsdata` package); cities are Natural Earth 10m
#                        populated places.
#            'approx'  — a campus or installation centroid, good to roughly a
#                        kilometre. A campus is an area, not a point, so no
#                        single coordinate is "correct"; these place the marker
#                        on the site, not on a surveyed datum.
#
# iata       Set instead of lat/lon to take the coordinate from the airport
#            dataset at build time. Never hand-copy an airport coordinate.
#
# url        Only client-confirmed URLs (the list supplied for the home page
#            ecosystem section). An organisation with no confirmed URL gets no
#            link rather than a guessed one.
# ---------------------------------------------------------------------------
IN_GOV = "https://www.in.gov/indiana-national-guard/"

FACILITIES = [
    # --- Cities (Natural Earth) ---------------------------------------------
    {"id": "indianapolis", "name": "Indianapolis", "type": "city", "place": "Indianapolis", "capital": True},
    {"id": "fort-wayne",   "name": "Fort Wayne",   "type": "city", "place": "Fort Wayne"},
    {"id": "south-bend",   "name": "South Bend",   "type": "city", "place": "South Bend"},
    {"id": "evansville",   "name": "Evansville",   "type": "city", "place": "Evansville"},
    {"id": "gary",         "name": "Gary",         "type": "city", "place": "Gary"},
    {"id": "lafayette",    "name": "Lafayette",    "type": "city", "place": "Lafayette"},
    {"id": "terre-haute",  "name": "Terre Haute",  "type": "city", "place": "Terre Haute",
     "network": True,
     "note": "Named by the test site as a location in the testing network."},
    {"id": "chicago",      "name": "Chicago, IL",  "type": "city", "place": "Chicago",    "outside": True},
    {"id": "cincinnati",   "name": "Cincinnati, OH", "type": "city", "place": "Cincinnati", "outside": True},
    {"id": "louisville",   "name": "Louisville, KY", "type": "city", "place": "Louisville", "outside": True},
    {"id": "portage",      "name": "Portage",      "type": "city", "lat": 41.5753, "lon": -87.1760,
     "precision": "approx"},

    # --- Airports (OurAirports, by IATA code) -------------------------------
    {"id": "ind", "name": "Indianapolis International",  "short": "IND", "type": "airport", "iata": "IND"},
    {"id": "sbn", "name": "South Bend International",    "short": "SBN", "type": "airport", "iata": "SBN"},
    {"id": "fwa", "name": "Fort Wayne International",    "short": "FWA", "type": "airport", "iata": "FWA"},
    {"id": "evv", "name": "Evansville Regional",         "short": "EVV", "type": "airport", "iata": "EVV"},
    {"id": "gyy", "name": "Gary/Chicago International",  "short": "GYY", "type": "airport", "iata": "GYY"},
    {"id": "huf", "name": "Terre Haute Regional",        "short": "HUF", "type": "airport", "iata": "HUF"},
    {"id": "ord", "name": "Chicago O'Hare International", "short": "ORD", "type": "airport", "iata": "ORD", "outside": True},
    {"id": "luk", "name": "Cincinnati Municipal (Lunken)", "short": "LUK", "type": "airport", "iata": "LUK", "outside": True},
    {"id": "sdf", "name": "Louisville Muhammad Ali International", "short": "SDF", "type": "airport", "iata": "SDF", "outside": True},

    # --- Ports of Indiana ---------------------------------------------------
    {"id": "port-burns-harbor", "name": "Port of Indiana — Burns Harbor", "type": "port",
     "lat": 41.6347, "lon": -87.1575, "precision": "approx"},
    {"id": "port-jeffersonville", "name": "Port of Indiana — Jeffersonville", "type": "port",
     "lat": 38.3406, "lon": -85.6836, "precision": "approx"},
    {"id": "port-mount-vernon", "name": "Port of Indiana — Mount Vernon", "type": "port",
     "lat": 37.9253, "lon": -87.8936, "precision": "approx"},

    # --- Military installations and units ------------------------------------
    {"id": "camp-atterbury", "name": "Camp Atterbury", "type": "military",
     "lat": 39.3403, "lon": -86.0447, "precision": "approx", "network": True,
     "url": IN_GOV + "camp-atterbury/",
     "note": "Named by the test site as a location in the testing network."},
    {"id": "muscatatuck", "name": "Muscatatuck", "type": "military",
     "lat": 38.9350, "lon": -85.5950, "precision": "approx", "network": True,
     "url": IN_GOV + "muscatatuck-training-center/",
     "note": "Named by the test site as a location in the testing network."},
    {"id": "nswc-crane", "name": "NSWC Crane", "type": "military",
     "lat": 38.8447, "lon": -86.8558, "precision": "approx", "network": True,
     "url": "https://www.navsea.navy.mil/Home/Warfare-Centers/NSWC-Crane/",
     "note": "Named by the test site as a location in the testing network."},
    {"id": "crane-army", "name": "Crane Army Ammunition Activity", "type": "military",
     "lat": 38.8694, "lon": -86.8197, "precision": "approx"},
    {"id": "grissom", "name": "Grissom Air Reserve Base", "type": "military",
     "sub": "434th Air Refueling Wing", "iata": "GUS",
     "url": "https://www.grissom.afrc.af.mil/"},
    {"id": "122fw", "name": "122nd Fighter Wing", "type": "military", "iata": "FWA",
     "url": "https://www.122fw.ang.af.mil/",
     "note": "Based at Fort Wayne Air National Guard Station, co-located with the airport."},
    {"id": "181iw", "name": "181st Intelligence Wing", "type": "military", "iata": "HUF",
     "url": "https://www.181iw.ang.af.mil/",
     "note": "Based at Hulman Field, co-located with Terre Haute Regional Airport."},
    {"id": "81tc", "name": "81st Troop Command", "type": "military",
     "lat": 39.7490, "lon": -86.2060, "precision": "approx",
     "url": IN_GOV + "indiana-army-national-guard/81st-troop-command/"},
    {"id": "38id", "name": "38th Infantry Division", "type": "military",
     "lat": 39.7490, "lon": -86.2060, "precision": "approx",
     "url": IN_GOV + "indiana-army-national-guard/38th-infantry-division/"},

    # --- Federal agency -------------------------------------------------------
    {"id": "dfas", "name": "Defense Finance & Accounting Service", "short": "DFAS",
     "type": "agency", "lat": 39.8133, "lon": -86.0789, "precision": "approx",
     "url": "https://www.dfas.mil/"},

    # --- Universities ---------------------------------------------------------
    {"id": "purdue", "name": "Purdue University", "type": "university",
     "lat": 40.4237, "lon": -86.9212, "precision": "approx", "network": True,
     "url": "https://www.purdue.edu/",
     "note": "Named by the test site as a location in the testing network."},
    {"id": "notre-dame", "name": "University of Notre Dame", "type": "university",
     "lat": 41.7001, "lon": -86.2379, "precision": "approx", "url": "https://www.nd.edu/"},
    {"id": "iu", "name": "Indiana University", "type": "university",
     "lat": 39.1682, "lon": -86.5230, "precision": "approx", "url": "https://www.iu.edu/"},
    {"id": "indiana-state", "name": "Indiana State University", "type": "university",
     "lat": 39.4713, "lon": -87.4106, "precision": "approx", "url": "https://www.indstate.edu/"},
    {"id": "rose-hulman", "name": "Rose-Hulman Institute of Technology", "type": "university",
     "lat": 39.4829, "lon": -87.3250, "precision": "approx", "url": "https://www.rose-hulman.edu/"},
    {"id": "butler", "name": "Butler University", "type": "university",
     "lat": 39.8403, "lon": -86.1696, "precision": "approx", "url": "https://www.butler.edu/"},
    {"id": "trine", "name": "Trine University", "type": "university",
     "lat": 41.6442, "lon": -84.9986, "precision": "approx", "url": "https://www.trine.edu/"},
    {"id": "vincennes", "name": "Vincennes University", "type": "university",
     "lat": 38.6710, "lon": -87.5286, "precision": "approx"},
]

# Monroe County is the sixth named network location. It is a county rather than
# a point, so it is highlighted as a polygon from the county layer instead of
# carrying a marker. The value is its 3-digit county FIPS code.
NETWORK_COUNTIES = [
    {"id": "105", "name": "Monroe County",
     "note": "Named by the test site as a location in the testing network."},
]

# ---------------------------------------------------------------------------
# Verified operational geometry
# ---------------------------------------------------------------------------
# Nothing here yet, and that is the point. The layers exist in the renderer and
# the legend reports them as having no published geometry, so the map never
# shows a boundary or a corridor the test site has not published.
#
# RANGES    {"id", "name", "kind": "range", "rings": [[(lon, lat), …], …]}
# CORRIDORS {"id", "name", "path": [(lon, lat), …], "width_nm": float|None}
# AREAS     {"id", "name", "rings": [...]} — coverage or operating areas
#
# Anything added here is rendered as VERIFIED. Illustrative geometry must carry
# "illustrative": True, which renders it dashed and labels it as illustrative in
# the legend.
# ---------------------------------------------------------------------------
RANGES = []
CORRIDORS = []
AREAS = []

# ---------------------------------------------------------------------------
# Partner organisations
# ---------------------------------------------------------------------------
# url    A website is listed ONLY where the client confirmed it (the list they
#        supplied for the home page ecosystem section). Everything else is None.
#        Do not fill these in by guessing a domain from a brand name — a wrong
#        link on a partner's name is worse than no link.
#
# logo   Path under assets/img/partners/, or None. None renders a wordmark in
#        the same cell instead, which on this dark band reads as white type.
#
#        The marquee band is navy because of what the supplied artwork is: 13 of
#        the 24 logos the client sent are white or reversed versions, which only
#        exist to go on a dark field. A logo that is dark-on-light stays None
#        until a reversed version arrives — recolouring someone's trademark to
#        fit our background is not ours to do.
#
# restricted
#        A federal or agency seal. The Test Site OTA says the Sponsor "agrees
#        not to display, or use any Agency or Federal Government seals,
#        trademarks, logos, service marks, or trade names on the Company's
#        websites, digital, or printed materials unless permission has been
#        granted by the Agency in writing prior to the usage" — the same clause
#        that keeps the FAA logo off this site. SHOW_RESTRICTED_MARKS below
#        gates them; it is on, because the client confirmed the permission is on
#        file. With it off they fall back to text and nothing else changes.
# ---------------------------------------------------------------------------
# Agency and federal marks. The Test Site OTA forbids displaying these without
# prior written permission from the agency — the clause that keeps the FAA logo
# off the site. The client confirmed on 2026-10-13 that written permission is on
# file for the Indiana National Guard and for NAVSEA (NSWC Crane), so both are
# shown. Set this back to False if that ever lapses, and both revert to text
# with no other change.
SHOW_RESTRICTED_MARKS = True


def _org(name, url=None, logo=None, short=None, expand=None, restricted=False,
         badge=False, plate=False):
    """One partner organization.

    name    The full name, used as the accessible name and image alt text.
    short   What appears on screen. Kept exactly as the client's slide labels
            it — several are bare airport codes, and renaming them is their
            call, not ours.
    expand  Appended to the link's accessible name where `short` alone would
            not identify the organization ("HUF" on its own means nothing).
            It never replaces the visible text, so the accessible name still
            contains it and WCAG 2.5.3 holds.
    """
    if restricted and not SHOW_RESTRICTED_MARKS:
        logo = None
    return {"name": name, "url": url, "logo": logo,
            "short": short or name, "expand": expand, "restricted": restricted,
            "badge": badge, "plate": plate}


PARTNER_GROUPS = [
    ("government", "Government &amp; Economic Development", [
        _org("Indiana Economic Development Corporation (IEDC)", "https://iedc.in.gov/",
             "assets/img/partners/iedc.png", "IEDC"),
        # REVIEW BUILD. The sponsor pack gives https://www.theari.us/ as ARI's
        # official site; this points at their staging deployment to match the
        # footer, which was set that way deliberately. Swap both before launch.
        _org("Applied Research Institute (ARI)", "https://ari-for-review.vercel.app/",
             "assets/img/partners/ari.png", short="ARI"),
        _org("Indiana National Guard (INNG)", IN_GOV, "assets/img/partners/indiana-national-guard.png", badge=True,
             short="INNG", expand="Indiana National Guard", restricted=True),
        _org("Purdue Research Foundation (PRF)", "https://prf.org/",
             "assets/img/partners/purdue-research-foundation.png", short="PRF",
             expand="Purdue Research Foundation"),
    ]),
    ("defense", "Defense &amp; National Security", [
        _org("NSWC Crane", "https://www.navsea.navy.mil/Home/Warfare-Centers/NSWC-Crane/",
             "assets/img/partners/nswc-crane.png",
             expand="Naval Surface Warfare Center, Crane Division", restricted=True),
        _org("Anduril", "https://www.anduril.com/", expand="Anduril Industries"),
        _org("HII", "https://hii.com/", "assets/img/partners/hii.svg",
             expand="Huntington Ingalls Industries", badge=True),
        # The sponsor pack notes BlueHalo is now part of AV. Shown under the
        # name the client's list uses.
        _org("BlueHalo", "https://bluehalo.com/", "assets/img/partners/av.svg"),
        _org("Thales", "https://www.thalesgroup.com/", expand="Thales Group"),
        _org("AEVEX Aerospace", "https://aevex.com/", "assets/img/partners/aevex.svg"),
    ]),
    ("academic", "Academic &amp; Research", [
        _org("Purdue University", "https://www.purdue.edu/", "assets/img/partners/purdue-university.svg",
            ),
        _org("Indiana University", "https://www.iu.edu/"),
        _org("Indiana State University", "https://www.indstate.edu/"),
        _org("Rose-Hulman Institute of Technology", "https://www.rose-hulman.edu/",
             "assets/img/partners/rose-hulman.png", short="Rose-Hulman"),
        _org("Ivy Tech Community College", "https://www.ivytech.edu/", "assets/img/partners/ivy-tech.png",
             short="Ivy Tech"),
    ]),
    ("commercial", "Aerospace &amp; Commercial Technology", [
        _org("Pierce Aerospace", "https://www.pierceaerospace.net/", "assets/img/partners/pierce-aerospace.png"),
        _org("Precision Planting", "https://www.precisionplanting.com/"),
        _org("SkyfireAI", "https://www.skyfireai.com/", "assets/img/partners/skyfire-ai.png"),
        _org("ResilienX", "https://resilienx.com/", "assets/img/partners/resilienx.svg"),
        _org("Motorola Solutions", "https://www.motorolasolutions.com/"),
        _org("Lighthouse Avionics", "https://lighthouseavionics.com/", "assets/img/partners/lighthouse-avionics.svg"),
        _org("Calhoun Analytics", "https://www.calanalytics.com/", "assets/img/partners/cal-analytics.webp",
             expand="Calhoun Analytics, LLC, trading as CAL Analytics"),
        # UNLINKED ON PURPOSE. The sponsor pack resolves this to Echodyne, a
        # different spelling and a different company, and says to confirm before
        # publication. Linking a partner's name to the wrong company is worse
        # than not linking it.
        _org("Ecodyne", "https://www.echodyne.com/", "assets/img/partners/echodyne.png",
             expand="Echodyne"),
        _org("INVOLI", "https://www.involi.com/"),
        _org("ANRA Technologies", "https://www.anratechnologies.com/"),
        # UNLINKED ON PURPOSE. The pack offers Raider Technologies but flags the
        # identity as unverified.
        _org("Raider", "https://raidertechnologies.com/", "assets/img/partners/raider-technologies.svg",
             expand="Raider Technologies"),
        _org("WayPoint Aerospace", "https://waypointaerospace.com/",
             "assets/img/partners/waypoint-aerospace.webp"),
        _org("AMVIC", "https://amvictechnology.org/", "assets/img/partners/amvic.png",
             expand="Advanced Machine and Vehicle Innovation Center"),
        _org("Sonetics Wireless", "https://www.sonetics.com/", "assets/img/partners/sonetics.webp"),
    ]),
    # The client's slide groups four airport codes here. They are airports, not
    # associations, but the grouping and the on-screen labels are theirs to
    # change — so the labels stay and `expand` carries the identity into the
    # link's accessible name.
    ("associations", "Industry Associations &amp; Ecosystem Partners", [
        _org("AUVSI", "https://www.auvsi.org/", "assets/img/partners/auvsi.svg",
             expand="Association for Uncrewed Vehicle Systems International"),
        _org("DroneResponders", "https://www.droneresponders.org/", "assets/img/partners/droneresponders.png", badge=True),
        _org("NUAIR", "https://www.nuair.org/"),
        _org("BMG", "https://flymonroecounty.com/", short="BMG",
             expand="Monroe County Airport, Bloomington"),
        # UNLINKED ON PURPOSE. The pack resolves HUF to Terre Haute Regional
        # Airport but supplies huf.com, which is an apparel brand. The two do
        # not match, so no link until the airport's own URL is confirmed.
        _org("HUF", logo="assets/img/partners/terre-haute-airport.png", short="HUF",
             expand="Terre Haute Regional Airport, Hulman Field"),
        _org("LAF", "https://www.purdue.edu/airport/", short="LAF",
             expand="Purdue University Airport"),
        _org("BAK", "https://www.columbus.in.gov/aviation/", "assets/img/partners/columbus-aviation.png",
             short="BAK", expand="Columbus Municipal Airport"),
    ]),
]
