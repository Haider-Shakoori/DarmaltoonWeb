#!/usr/bin/env python3
"""Regression checks for the CURRENT approved Darmaltoon marketing UI.

The early October ZIP image-only prototype was replaced with native HTML and
the user-approved transparent merged wordmark. Both English themes deliberately
have separate mobile and desktop roots, hence two H1 tags in the source. Exactly
one should be visible per viewport; browser QA checks that responsive behavior.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def require(ok, what):
    if not ok:
        errors.append(what)


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.images = []
        self.links = []
        self.meta = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.tags.append(tag)
        if tag == "img":
            self.images.append(d)
        elif tag in ("a", "link"):
            self.links.append(d)
        elif tag == "meta":
            self.meta.append(d)


def internal_file(src, parent):
    parsed = urlsplit(src)
    if parsed.scheme or parsed.netloc:
        return None
    path = parsed.path
    if not path or path.startswith(("mailto:", "tel:", "sms:", "#", "data:", "javascript:")):
        return None
    local = ROOT / path.lstrip("/") if path.startswith("/") else parent / path
    if path.endswith("/"):
        local /= "index.html"
    return local


for theme, rel in [("light", "index.html")]:
    source = (ROOT / rel).read_text(encoding="utf-8")
    page = Markup()
    page.feed(source)

    require(page.tags.count("h1") == 2,
            f"{rel}: expected one desktop and one mobile H1 (separate responsive roots)")
    require('class="zip-desktop"' in source or 'class="zip-desktop" ' in source,
            f"{rel}: missing native desktop root")
    require('class="zip-native"' in source or 'class="zip-native" ' in source,
            f"{rel}: missing native mobile root")
    require("data:image/jpeg;base64" not in source,
            f"{rel}: embedded full-page base64 screenshot")
    require("darmaltoon-merged-wordmark.png" in source,
            f"{rel}: user-approved merged PNG wordmark missing")
    require(source.count('class="merged-brand-wordmark"') >= 2,
            f"{rel}: desktop and mobile header should use merged wordmark")
    require("file_0000" not in source, f"{rel}: internal file references leaked")
    require("Trusted by pharmacies across Afghanistan" not in source,
            f"{rel}: unverified social proof")
    require("aggregateRating" not in source, f"{rel}: unverified reviews")
    require("AFN 1,500" not in source and "AFN 3,500" not in source,
            f"{rel}: unapproved prices")
    require("privacy.html" in source, f"{rel}: privacy link missing")
    require("first-party-analytics.js" in source, f"{rel}: privacy-aware analytics missing")
    require("https://darmaltoon.com/" in source, f"{rel}: canonical/identity missing")
    require("/dark.html" not in source and "switch-theme" not in source, f"{rel}: old dark navigation remains")

    for img in page.images:
        src = img.get("src")
        require(img.get("alt") is not None, f"{rel}: image alt missing for {src}")
        if src:
            path = internal_file(src, (ROOT / rel).parent)
            if path:
                require(path.is_file(), f"{rel}: image not found: {src}")
    for d in page.links:
        href = d.get("href")
        if not href or href.startswith("#"):
            continue
        path = internal_file(href, (ROOT / rel).parent)
        if path:
            require(path.is_file(), f"{rel}: broken internal link: {href}")

    expected = f"https://darmaltoon.com/"
    canonical = [e.get("href") for e in page.links if e.get("rel") == "canonical"]
    require(canonical == [expected], f"{rel}: must canonicalize to public English homepage")

    if theme == "light":
        require('class="zd-afghan-unified"' in source,
                "light page: approved merged Afghanistan section missing")
        require('class="zd-platform-showcase"' in source,
                "light page: native platform comparison missing")
        require("light-premium.css" in source and "light-hd-hero.css" in source,
                "light page: HD hero styling missing")
        require("darmaltoon-light-dashboard-hd.avif" in source,
                "light page: optimized HD hero missing")
        require('id="faq"' in source and source.count('id="faq"') == 1,
                "light page: duplicate/missing FAQ")


for lc, code in [("fa", "fa-AF"), ("ps", "ps-AF")]:
    rel = f"{lc}/index.html"
    source = (ROOT / rel).read_text(encoding="utf-8")
    page = Markup()
    page.feed(source)
    require('id="designSwitch"' not in source, f"{rel}: old theme switch remains")
    require(f'lang="{code}"' in source and 'dir="rtl"' in source,
            f"{rel}: wrong locale or direction")
    require(page.tags.count("h1") == 1, f"{rel}: needs one semantic H1")
    require(source.count('class="rtl-feature"') == 8, f"{rel}: eight native feature cards")
    require(source.count('class="rtl-faq-item"') == 5, f"{rel}: five native FAQ rows")
    require('class="rtl-platform"' in source, f"{rel}: platform comparison missing")
    require("rtl-premium.css" in source and "rtl-premium.js" in source,
            f"{rel}: premium theme assets missing")
    require("darmaltoon-merged-wordmark.png" in source,
            f"{rel}: approved logo missing")
    require(f'/demo.html?lang={lc}' in source, f"{rel}: local-language CTA missing")
    require("privacy.html" in source, f"{rel}: privacy notice missing")
    require('href="https://darmaltoon.com/' + lc + '/"' in source,
            f"{rel}: localized canonical missing")
    for img in page.images:
        require(img.get("alt") is not None, f"{rel}: img alt missing")


# Marketing forms use server-side validation, private storage and user consent.
for src in ["assets/js/forms.js", "assets/js/light-demo-mailto.js"]:
    content = (ROOT / src).read_text(encoding="utf-8")
    require("/api/lead.php" in content, f"{src}: lead endpoint missing")
    require("mailto:" in content, f"{src}: offline/email fallback missing")
for src, limit in [
    ("assets/images/hero/darmaltoon-light-dashboard-hd.avif", 320_000),
    ("assets/images/hero/darmaltoon-light-dashboard-hd.webp", 480_000),
    ("assets/css/ui-enhancements.css", 12_000),
    ("assets/js/ui-enhancements.js", 6_000),
    ("assets/css/rtl-premium.css", 19_000),
    ("assets/js/rtl-premium.js", 3_000),
]:
    p = ROOT / src
    require(p.is_file() and p.stat().st_size < limit,
            f"{src}: absent or exceeds performance budget ({limit})")

if errors:
    print(f"FAIL: {len(errors)} current design regressions")
    for error in errors:
        print(" - " + error)
    sys.exit(1)
print("PASS: approved English light-only design, native RTL pages, merged logo, links, SEO, forms and asset budgets")
