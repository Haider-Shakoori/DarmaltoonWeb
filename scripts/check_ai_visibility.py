#!/usr/bin/env python3
"""Tests Darmaltoon's multilingual SEO assets and observable AI visibility signals."""
from pathlib import Path
from html.parser import HTMLParser
import json
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
topics=["pharmacy-inventory","expiry-tracking","offline-pharmacy-software"]
errors=[]
class Parse(HTMLParser):
    def __init__(self):
        super().__init__()
        self.head=[]
        self.h1=0
        self.jsonld=[]
        self.inscript=False
        self.buffer=""
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ("link","meta"):self.head.append((tag,a))
        if tag=="h1":self.h1+=1
        if tag=="script" and a.get("type")=="application/ld+json":
            self.inscript=True;self.buffer=""
    def handle_endtag(self,tag):
        if tag=="script" and self.inscript:
            try:self.jsonld.append(json.loads(self.buffer))
            except ValueError:errors.append("invalid JSON-LD")
            self.inscript=False
    def handle_data(self,data):
        if self.inscript:self.buffer+=data
def ensure(check,what):
    if not check:errors.append(what)
xml=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
ET.fromstring(xml)
for lang,code in (("en","en"),("fa","fa-AF"),("ps","ps-AF")):
    for topic in [None]+topics:
        prefix=f"/{lang}" if lang!="en" else ""
        target=prefix+"/guides/"+(f"{topic}.html" if topic else "")
        path=ROOT/target.lstrip("/")
        if topic is None:path=path/"index.html"
        ensure(path.is_file(),f"missing {target}")
        if not path.is_file():continue
        data=path.read_text(encoding="utf-8")
        parsed=Parse();parsed.feed(data)
        canonical="https://darmaltoon.com"+target
        ensure(parsed.h1==1,f"{target}: exactly one h1")
        ensure(any(t=="link" and a.get("rel")=="canonical" and a.get("href")==canonical for t,a in parsed.head),f"{target}: canonical")
        ensure(all(any(t=="link" and a.get("hreflang")==key for t,a in parsed.head) for key in ["en","fa-AF","ps-AF","x-default"]),f"{target}: hreflang incomplete")
        ensure(canonical in xml,f"{target}: sitemap missing")
        ensure('first-party-analytics.js' in data,f"{target}: no metrics")
        ensure('assets/css/seo-guides.css' in data,f"{target}: no shared light style")
        ensure('dark.html' not in data,f"{target}: retired theme present")
        ensure(any(any(n.get("@type")=="Article" for n in x.get("@graph",[])) for x in parsed.jsonld) if topic else bool(parsed.jsonld),f"{target}: structured data")
js=(ROOT/"assets/js/first-party-analytics.js").read_text()
store=(ROOT/"api/analytics-store.php").read_text()
dashboard=(ROOT/"admin/analytics.php").read_text()
for provider in ["chatgpt","perplexity","gemini","copilot","claude"]:
    ensure(provider in js and provider in store,f"{provider}: missing provider")
ensure("'ai_referral'" in store and "'ai_referral'" in js,"AI referrals not mapped")
ensure('ai_mention_checks' in dashboard and 'save_ai_check' in dashboard,"manual observations missing")
ensure('OAI-SearchBot' in (ROOT/"robots.txt").read_text(),"OAI-SearchBot permissions missing")
if errors:
    print("FAIL: "+str(len(errors))+" SEO/AIO checks")
    print("\n".join(errors))
    raise SystemExit(1)
print("PASS: 12 localized guides, canonical/hreflang, sitemap, AI referrals and mention log")

