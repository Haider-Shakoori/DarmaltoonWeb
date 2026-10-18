#!/usr/bin/env python3
"""Verify that the published Darmaltoon website matches the source sitemap.

Run after deploying: python3 scripts/check_live_seo.py
External HTTP checks are intentionally separate from the offline CI suite.
"""
from __future__ import annotations

import argparse
import concurrent.futures
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITEMAP_NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.canonical = None
        self.robots = ""

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "html":
            self.lang = attributes.get("lang")
        elif tag == "link" and attributes.get("rel") == "canonical":
            self.canonical = attributes.get("href")
        elif tag == "meta" and attributes.get("name") == "robots":
            self.robots = attributes.get("content", "")


def sitemap_urls(contents):
    root = ET.fromstring(contents)
    return [node.text.strip() for node in root.findall(".//s:url/s:loc", SITEMAP_NS) if node.text]


def fetch(url, timeout=12):
    req = Request(url, headers={
        "User-Agent": "DarmaltoonSEOReleaseCheck/1.0 (+https://darmaltoon.com/)"
    })
    with urlopen(req, timeout=timeout) as response:
        return response.geturl(), response.status, response.read()


def check_page(args):
    url, origin, timeout = args
    path = urlsplit(url).path
    try:
        final_url, code, body = fetch(origin.rstrip("/") + path, timeout)
        expected = origin.rstrip("/") + path
        if final_url.rstrip("/") != expected.rstrip("/"):
            return url, "REDIRECT", "resolved to " + final_url
        if code != 200:
            return url, "HTTP", str(code)
        html = body.decode("utf-8", "replace")
        if "<html" not in html.lower():
            return url, "NOT_HTML", "Missing HTML document"
        parser = HeadParser()
        parser.feed(html[:14000])
        if "/fa/" in path and parser.lang not in ("fa", "fa-AF"):
            return url, "LANG", "Expected fa-AF; found " + str(parser.lang)
        if "/ps/" in path and parser.lang not in ("ps", "ps-AF"):
            return url, "LANG", "Expected ps-AF; found " + str(parser.lang)
        if path in ("/", "/fa/", "/ps/", "/medicine-expiry-inventory-software.html",
                    "/fa/medicine-expiry-inventory-software.html",
                    "/ps/medicine-expiry-inventory-software.html"):
            if not parser.canonical or urlsplit(parser.canonical).path.rstrip("/") != path.rstrip("/"):
                return url, "CANONICAL", str(parser.canonical)
        if "noindex" in parser.robots.lower():
            return url, "NOINDEX", parser.robots
        return url, "OK", "200"
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return url, "ERROR", str(exc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", default="https://darmaltoon.com")
    ap.add_argument("--timeout", type=int, default=12)
    opts = ap.parse_args()
    source_urls = sitemap_urls((ROOT / "sitemap.xml").read_bytes())
    expected_origin = "https://darmaltoon.com"
    bad = []
    if len(set(source_urls)) != len(source_urls):
        bad.append("Source sitemap has duplicate URLs")
    if not all(u.startswith(expected_origin + "/") for u in source_urls):
        bad.append("Unexpected canonical origin in source sitemap")
    try:
        resolved, _, live_sitemap = fetch(opts.origin.rstrip("/") + "/sitemap.xml", opts.timeout)
        live_urls = set(sitemap_urls(live_sitemap))
        missing = sorted(set(source_urls) - live_urls)
        extra = sorted(live_urls - set(source_urls))
        if missing:
            bad.append("Live sitemap is missing " + str(len(missing)) + " source URLs: " + ", ".join(missing))
        if extra:
            print("NOTE: live sitemap has additional URLs: " + ", ".join(extra))
        print("Sitemap: source=" + str(len(source_urls)) + ", live=" + str(len(live_urls)))
    except (HTTPError, URLError, TimeoutError, OSError, ET.ParseError) as exc:
        bad.append("Cannot read live sitemap: " + str(exc))

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for url, status, message in pool.map(check_page, [
            (url, opts.origin, opts.timeout) for url in source_urls
        ]):
            print(status.ljust(10), url, message if status != "OK" else "")
            if status != "OK":
                bad.append(url + ": " + status + " " + message)

    try:
        _, _, robots = fetch(opts.origin.rstrip("/") + "/robots.txt", opts.timeout)
        robots_text = robots.decode("utf-8", "replace")
        if "Sitemap:" not in robots_text:
            bad.append("robots.txt lacks Sitemap directive")
        if "Disallow: /fa/" in robots_text or "Disallow: /ps/" in robots_text:
            bad.append("robots.txt blocks a translated section")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        bad.append("Cannot read robots.txt: " + str(exc))

    if bad:
        print("\\nFAIL — published search visibility issues:", len(bad), file=sys.stderr)
        for issue in bad:
            print(" -", issue, file=sys.stderr)
        return 1
    print("\\nPASS — all public sitemap pages are live, language-correct and crawlable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
