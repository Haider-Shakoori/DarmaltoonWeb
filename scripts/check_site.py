#!/usr/bin/env python3
"""Fast, dependency-free checks for the public Darmaltoon marketing site."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re
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
    require(parser.headings.count("h1") == 1, f"{name}: expected one h1")
    expected = "https://darmaltoon.com/" + name.replace("index.html", "")
    canonical = [link.get("href") for link in parser.links if link.get("rel") == "canonical"]
    require(canonical == [expected], f"{name}: incorrect canonical {canonical}")
    alt = {link.get("hreflang"): link.get("href") for link in parser.links if link.get("rel") == "alternate"}
    for code, href in [("en", "https://darmaltoon.com/"), ("fa-AF", "https://darmaltoon.com/fa/"), ("ps-AF", "https://darmaltoon.com/ps/"), ("x-default", "https://darmaltoon.com/")]:
        require(alt.get(code) == href, f"{name}: missing hreflang {code}")
    require("application/ld+json" in data, f"{name}: JSON-LD missing")
    require("sample" in data.lower() or "نمونه" in data or "بېلګه" in data, f"{name}: demo data not disclosed")
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
    require(len(data.encode("utf-8")) < 28_000, f"{name}: homepage larger than 28 KB")
for path, limit in [("assets/css/showcase.css", 30_000), ("assets/js/showcase.js", 3_000), ("assets/images/brand/darmaltoon-official.svg", 6_000)]:
    f = ROOT / path
    require(f.exists() and f.stat().st_size < limit, f"{path}: missing or over budget ({limit} bytes)")
for required in ["robots.txt", "sitemap.xml", "llms.txt"]:
    require((ROOT/required).is_file(), f"Missing discovery file: {required}")
sitemap = ROOT/"sitemap.xml"
if sitemap.exists():
    try:
        urls = [node.text for node in ET.parse(sitemap).iter() if node.tag.endswith("}loc")]
        require({"https://darmaltoon.com/", "https://darmaltoon.com/fa/", "https://darmaltoon.com/ps/"}.issubset(urls), "Sitemap missing language URLs")
    except ET.ParseError as e:
        ERRORS.append(f"Sitemap XML invalid: {e}")
if ERRORS:
    print("FAIL: " + str(len(ERRORS)) + " website checks")
    for error in ERRORS: print(" - " + error)
    sys.exit(1)
print("PASS: 7 crawlable localized pages, metadata, hreflang, internal links, SEO files, and size budgets")
