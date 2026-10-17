#!/usr/bin/env python3
"""Fast, dependency-free checks for the public Darmaltoon marketing site."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

def require(ok, message):
    if not ok:
        ERRORS.append(message)

class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.lang = None
        self.direction = None
        self.meta = {}
        self.links = []
        self.images = []
        self.headings = []
        self.auditable_text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang, self.direction = a.get("lang"), a.get("dir")
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            self.meta[a.get("name", "") or a.get("property", "")] = a.get("content", "")
        if tag == "link":
            self.links.append(a)
        if tag == "script" and a.get("src"):
            self.links.append({"href": a["src"]})
        if tag == "img":
            self.images.append(a)
            if a.get("src"): self.links.append({"href": a["src"]})
        if tag == "a" and a.get("href"):
            self.links.append({"href": a["href"]})
        if tag in {"h1", "h2", "h3"}:
            self.headings.append(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, value):
        if self.in_title:
            self.title += value

LANGS = {"index.html": ("en", "ltr"), "fa/index.html": ("fa-AF", "rtl"), "ps/index.html": ("ps-AF", "rtl"),
         "fa/features.html": ("fa-AF", "rtl"), "ps/features.html": ("ps-AF", "rtl"),
         "fa/pharmadesktop.html": ("fa-AF", "rtl"), "ps/pharmadesktop.html": ("ps-AF", "rtl")}
for name, (lang, direction) in LANGS.items():
    path = ROOT / name
    require(path.is_file(), f"Missing language homepage: {name}")
    if not path.is_file():
        continue
    data = path.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(data)
    require(parser.lang == lang, f"{name}: expected lang {lang}, got {parser.lang}")
    require(parser.direction == direction, f"{name}: incorrect text direction")
    require(bool(parser.title.strip()) and len(parser.title.strip()) < 85, f"{name}: title missing/too long")
    require(60 < len(parser.meta.get("description", "")) < 350, f"{name}: meta description missing/invalid")
    require(parser.headings.count("h1") == (2 if name == "index.html" else 1), f"{name}: expected responsive home h1 and desktop screen-reader h1 on landing")
    expected = "https://web.darmaltoon.com/" + name.replace("index.html", "")
    canonical = [link.get("href") for link in parser.links if link.get("rel") == "canonical"]
    require(canonical == [expected], f"{name}: incorrect canonical {canonical}")
    alt = {link.get("hreflang"): link.get("href") for link in parser.links if link.get("rel") == "alternate"}
    suffix = name.replace("fa/", "").replace("ps/", "").replace("index.html", "")
    for code, href in [
        ("en", "https://web.darmaltoon.com/" + suffix),
        ("fa-AF", "https://web.darmaltoon.com/fa/" + suffix),
        ("ps-AF", "https://web.darmaltoon.com/ps/" + suffix),
        ("x-default", "https://web.darmaltoon.com/" + suffix),
    ]:
        require(alt.get(code) == href, f"{name}: missing hreflang {code}")
    require("application/ld+json" in data, f"{name}: JSON-LD missing")
    require("sample" in data.lower() or "نمونه" in data or "بېلګه" in data or "بېلګې" in data, f"{name}: demo data not disclosed")
    for link in parser.links:
        href = link.get("href", "")
        if not href or href.startswith(("#", "data:", "tel:", "mailto:", "//")):
            continue
        uri = urlsplit(href)
        if uri.scheme in ("http", "https"): continue
        relative = uri.path
        if not relative: continue
        resolved = ROOT / relative.lstrip("/") if relative.startswith("/") else path.parent / relative
        if relative.endswith("/"): resolved /= "index.html"
        require(resolved.exists(), f"{name}: missing local asset/link: {href}")
    for image in parser.images:
        require("alt" in image, f"{name}: image missing alt text")
    require(len(data.encode("utf-8")) < (48_000 if name == "index.html" else 28_000), f"{name}: webpage size budget exceeded")
for path, limit in [("assets/css/showcase.css", 30_000), ("assets/js/showcase.js", 3_000), ("assets/images/brand/darmaltoon-official.svg", 6_000)]:
    f = ROOT / path
    require(f.exists() and f.stat().st_size < limit, f"{path}: missing or over budget ({limit} bytes)")
# The approved ZIP retains its desktop canvas, but mobile content must be genuine HTML.
home = (ROOT / "index.html").read_text(encoding="utf-8")
for token in ['class="zip-native"', 'class="zn-feature"', 'class="zn-plot"', 'id="native-platforms"', 'id="native-dashboard"']:
    require(token in home, f"Missing native mobile UI requirement: {token}")
require('class="mobile-original"' not in home, "Old cropped-artwork mobile fallback must not return")
require('id="bg"' not in home, "Desktop must not use a full-page raster screenshot")
require('class="zip-desktop"' in home, "Missing native desktop content")
require(home.count('class="zd-feature"') == 8, "Desktop must have eight HTML feature cards")
require('class="zd-chart-card"' in home, "Desktop must include native SVG chart")
require((ROOT / "assets/images/brand/darmaltoon-merged-wordmark.png").is_file(), "Merged approved PNG must be present")
require(home.count('class="merged-brand-wordmark"') == 2, "Combined PNG must replace both desktop and mobile brand text")
require('class="zd-platform-showcase"' in home, "Light desktop must have native platform cards")
require('class="zd-operations"' not in home, "Duplicated desktop offline/FAQ section must be absent")
require(home.count('id="faq"') == 1, "FAQ must appear only once")
require('light-premium.css' in home, "Light premium stylesheet not linked")

require('class="zd-afghan-unified"' in home, "Light desktop must include merged native Afghan/offline section")
require('class="zd-proof"' in home, "Light desktop must include selectable hero bullet points")
require((ROOT / "assets/images/hero/light-right-from-zip.webp").is_file(), "Optimized ZIP visual fallback is missing")
for new_photo in ["darmaltoon-light-hero.webp", "afghanistan-bottom.webp"]:
    require((ROOT / "assets/images/hero" / new_photo).is_file(), f"Missing exact user-supplied asset: {new_photo}")
require('light-exact.css' in home, "Light page must load exact image reference stylesheet")
require('zn-afghan-panorama' in home, "Light mobile page must show native panorama image")
# Secondary marketing pages must stay fast, genuinely crawlable and contactable.
SECONDARY = ["features.html", "pharmadesktop.html", "about.html", "demo.html", "contact.html"]
for page_name in SECONDARY:
    page = ROOT / page_name
    source = page.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(source)
    require(parser.headings.count("h1") == 1, f"{page_name}: expected one semantic h1")
    require("subpages-premium.css" in source, f"{page_name}: premium stylesheet not loaded")
    require("index.html#why" not in source, f"{page_name}: broken old home anchor")
    require("{{" not in source, f"{page_name}: unresolved contact placeholder")
    require("info@darmaltoon.com" in source, f"{page_name}: verified email missing")
    require("darmaltoon-merged-wordmark.png" in source, f"{page_name}: branded PNG missing")
    require(len(source.encode("utf-8")) < 36_000, f"{page_name}: secondary HTML exceeds 36 KB")
    canon = [link.get("href") for link in parser.links if link.get("rel") == "canonical"]
    require(canon == ["https://web.darmaltoon.com/" + page_name], f"{page_name}: incorrect canonical")
    for link in parser.links:
        href = link.get("href", "")
        if not href or href.startswith(("#", "data:", "tel:", "mailto:", "//")): continue
        uri = urlsplit(href)
        if uri.scheme in ("http", "https"): continue
        path = uri.path
        if not path: continue
        dest = ROOT / path.lstrip("/") if path.startswith("/") else page.parent / path
        if path.endswith("/"): dest /= "index.html"
        require(dest.exists(), f"{page_name}: missing local resource {href}")
    for img in parser.images: require("alt" in img, f"{page_name}: image needs alt")
require((ROOT/"assets/css/subpages-premium.css").stat().st_size < 18_000,
        "Secondary styling exceeds 18 KB")
script = (ROOT/"assets/js/forms.js").read_text(encoding="utf-8")
require("mailto:info@darmaltoon.com" in script, "Forms must prepare a real email draft")
require("showNotConfigured" not in script, "Unusable old form interception must be removed")
require((ROOT/"features.html").read_text().count("<svg") >= 16, "Feature icons should use inline SVGs")
require((ROOT/"pharmadesktop.html").read_text().count('class="pd-shot pd-preview"') >= 10,
        "Desktop feature mockups must be real HTML rather than repeated images")
# Premium localized homepages: no screenshot-only sections or manufactured proof.
for lc in ("fa", "ps"):
    source = (ROOT/lc/"index.html").read_text(encoding="utf-8")
    page = SiteParser();page.feed(source)
    require('rtl-premium.css' in source, f"{lc}: premium RTL stylesheet missing")
    require('rtl-premium.js' in source, f"{lc}: theme/mobile behavior missing")
    require(source.count('class="rtl-feature"') == 8, f"{lc}: require 8 native HTML feature cards")
    require(source.count('class="rtl-faq-item"') == 5, f"{lc}: require one FAQ section of 5 answers")
    require(source.count('id="faq"') == 1, f"{lc}: duplicate FAQ section")
    require('data-dark-src="/assets/images/design/dark-dashboard.webp"' in source, f"{lc}: theme-specific image missing")
    require(f'/demo.html?lang={lc}' in source, f"{lc}: demo link must preserve chosen language")
    require('class="rtl-logo"' in source, f"{lc}: merged wordmark missing")
    require(source.count('<main') == 1, f"{lc}: semantic main landmark missing")
    require(source.count('<h1') == 1, f"{lc}: heading duplication")
    require('{{' not in source, f"{lc}: unresolved placeholder")
    require('aggregateRating' not in source and 'Review' not in source, f"{lc}: fabricated ratings/reviews")
    graph_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', source, flags=re.S)
    if graph_match:
        try:
            graph=json.loads(graph_match.group(1))
            types=[node.get("@type") for node in graph.get("@graph",[])]
            require("FAQPage" in types and "SoftwareApplication" in types and "WebPage" in types,
                    f"{lc}: need SoftwareApplication, FAQPage, WebPage schema")
        except json.JSONDecodeError: ERRORS.append(f"{lc}: invalid JSON-LD")
    else: ERRORS.append(f"{lc}: missing crawlable JSON-LD")
require((ROOT/"assets/css/rtl-premium.css").is_file() and
        (ROOT/"assets/css/rtl-premium.css").stat().st_size < 19_000, "Premium RTL CSS >19KB")
require((ROOT/"assets/js/rtl-premium.js").is_file() and
        (ROOT/"assets/js/rtl-premium.js").stat().st_size < 3_000, "Premium RTL JS >3KB")
# Lead safety checks: forms must not silently discard requests.
lead = ROOT / "api/lead.php"
require(lead.is_file(), "Secure lead endpoint is missing")
if lead.is_file():
    endpoint = lead.read_text(encoding="utf-8")
    for marker in ["PDO('sqlite:", "php://input", "HTTP_ORIGIN", "hash_hmac", "Consent required", "Retry-After:", "dirname($siteRoot)", "mail("]:
        require(marker in endpoint, f"Lead endpoint missing guard: {marker}")
for js_path in ("assets/js/forms.js", "assets/js/light-demo-mailto.js"):
    source = (ROOT/js_path).read_text(encoding="utf-8")
    require("/api/lead.php" in source, f"{js_path}: missing lead endpoint integration")
require('href="/demo.html" class="zn-button primary"' in home,
        "Mobile demo CTA must lead to visible form")
# Crawlable trilingual privacy notices and contact links.
for rel, lang, direction in [("privacy.html","en","ltr"),("fa/privacy.html","fa-AF","rtl"),("ps/privacy.html","ps-AF","rtl")]:
    source=(ROOT/rel).read_text(encoding="utf-8")
    page=SiteParser();page.feed(source)
    require(page.lang==lang and page.direction==direction,f"{rel}: language/direction")
    require(page.headings.count("h1")==1,f"{rel}: one h1")
    canonical="https://web.darmaltoon.com/"+rel
    require(any(x.get("href")==canonical and x.get("rel")=="canonical" for x in page.links),f"{rel}: canonical")
    require("application/ld+json" in source,f"{rel}: JSON-LD")
    require("info@darmaltoon.com" in source,f"{rel}: contact")
    require("privacy-pages.css" in source,f"{rel}: stylesheet")
    require("<loc>"+canonical+"</loc>" in (ROOT/"sitemap.xml").read_text(),f"{rel}: sitemap")
for name in ("index.html","demo.html","contact.html","fa/index.html","ps/index.html"):
    require("privacy.html" in (ROOT/name).read_text(),f"{name}: privacy link")
# First-party, privacy-preserving analytics should be active across the website.
INSTRUMENTED = [
    "index.html","dark.html","about.html","features.html",
    "pharmadesktop.html","demo.html","contact.html",
    "fa/index.html","ps/index.html","fa/features.html",
    "ps/features.html","fa/pharmadesktop.html","ps/pharmadesktop.html",
]
for name in INSTRUMENTED:
    require("first-party-analytics.js" in (ROOT/name).read_text(encoding="utf-8"),
            f"{name}: first-party analytics instrumentation missing")
for name in ["api/analytics-store.php","api/analytics.php","admin/analytics.php"]:
    require((ROOT/name).is_file(), f"First-party analytics file missing: {name}")
analytics_js=(ROOT/"assets/js/first-party-analytics.js").read_text(encoding="utf-8")
for marker in ["globalPrivacyControl","doNotTrack","sendBeacon","page_view","referrer"]:
    require(marker in analytics_js, f"Privacy or attribution marker missing: {marker}")
for name in ["privacy.html","fa/privacy.html","ps/privacy.html"]:
    notice=(ROOT/name).read_text(encoding="utf-8")
    require("Global Privacy Control" in notice and "Do Not Track" in notice,
            f"{name}: analytics privacy notice missing")
native_css = ROOT / "assets/css/native-mobile.css"
require(native_css.exists() and native_css.stat().st_size < 15_000, "Native mobile CSS missing or over 15KB")
for required in ["robots.txt", "sitemap.xml", "llms.txt"]:
    require((ROOT/required).is_file(), f"Missing discovery file: {required}")
sitemap = ROOT/"sitemap.xml"
if sitemap.exists():
    try:
        urls = [node.text for node in ET.parse(sitemap).iter() if node.tag.endswith("}loc")]
        require({"https://web.darmaltoon.com/", "https://web.darmaltoon.com/fa/", "https://web.darmaltoon.com/ps/"}.issubset(urls), "Sitemap missing language URLs")
    except ET.ParseError as e:
        ERRORS.append(f"Sitemap XML invalid: {e}")
if ERRORS:
    print("FAIL: " + str(len(ERRORS)) + " website checks")
    for error in ERRORS: print(" - " + error)
    sys.exit(1)
print("PASS: 7 crawlable localized pages, responsive native mobile, metadata, hreflang, assets, and size budgets")
