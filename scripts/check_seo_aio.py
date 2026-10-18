#!/usr/bin/env python3
"""Crawlable guide and AI-measurement checks."""
from pathlib import Path
from html.parser import HTMLParser
import json,re
ROOT=Path(__file__).resolve().parents[1]
bad=[]
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.h=[];self.links=[];self.meta={};self.lang=None;self.direction=None;self.words=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="html":self.lang=a.get("lang");self.direction=a.get("dir")
  if tag in ("h1","h2"):self.h.append(tag)
  if tag=="link":self.links.append(a)
  if tag=="meta":self.meta[a.get("name") or a.get("property")]=a.get("content")
 def handle_data(self,data):self.words.append(data)
sitemap=(ROOT/"sitemap.xml").read_text()
for code,lang,direction in [("en","en","ltr"),("fa","fa-AF","rtl"),("ps","ps-AF","rtl")]:
 for slug in ("","pharmacy-inventory.html","expiry-tracking.html","offline-pharmacy-software.html"):
  rel=("" if code=="en" else code+"/")+"guides/"+(slug or "index.html")
  f=ROOT/rel
  if not f.exists():bad.append("missing "+rel);continue
  s=f.read_text();p=P();p.feed(s)
  url="https://darmaltoon.com/"+("" if code=="en" else code+"/")+"guides/"+slug
  if p.lang!=lang or p.direction!=direction:bad.append(rel+" lang or direction")
  if p.h.count("h1")!=1 or p.h.count("h2")<1:bad.append(rel+" heading structure")
  if len(" ".join(p.words))<500:bad.append(rel+" thin content")
  if not 50<len(p.meta.get("description",""))<270:bad.append(rel+" description")
  if not any(l.get("rel")=="canonical" and l.get("href")==url for l in p.links):bad.append(rel+" canonical")
  for alt,prefix in [("en",""),("fa-AF","fa/"),("ps-AF","ps/")]:
   if not any(l.get("hreflang")==alt and l.get("href")=="https://darmaltoon.com/"+prefix+"guides/"+slug for l in p.links):bad.append(rel+" hreflang "+alt)
  if "<loc>"+url+"</loc>" not in sitemap:bad.append(rel+" sitemap")
  match=re.search(r'<script type="application/ld\+json">(.+?)</script>',s)
  if not match:bad.append(rel+" JSON-LD missing")
  else:
   try:
    data=json.loads(match.group(1))
    if data.get("url")!=url or data.get("inLanguage")!=lang:bad.append(rel+" JSON-LD identity")
   except ValueError:bad.append(rel+" invalid JSON-LD")
  if "first-party-analytics.js" not in s:bad.append(rel+" missing analytics")
for f in ["index.html","fa/index.html","ps/index.html"]:
 if "/guides/" not in (ROOT/f).read_text():bad.append(f+" guide link missing")
for service in ["chatgpt","perplexity","gemini","copilot","claude"]:
 for f in ["assets/js/first-party-analytics.js","api/analytics-store.php"]:
  if service not in (ROOT/f).read_text():bad.append(service+" missing in "+f)
admin=(ROOT/"admin/analytics.php").read_text()
if "ai_mention_checks" not in admin or "save_ai_check" not in admin:bad.append("manual audit missing")
if "isset($_POST['password']) || isset($_POST['logout'])" not in admin:bad.append("login guard missing")

# Product-specific, crawlable discovery pages: distinguish capabilities from
# educational guides and verify all native-language routes stay in the sitemap.
product_slug = "medicine-expiry-inventory-software.html"
for code, lang, direction in [("en", "en", "ltr"), ("fa", "fa-AF", "rtl"), ("ps", "ps-AF", "rtl")]:
 prefix = "" if code == "en" else code + "/"
 rel = prefix + product_slug
 page = ROOT / rel
 url = "https://darmaltoon.com/" + rel
 if not page.is_file():
  bad.append("product page missing " + rel)
  continue
 html = page.read_text()
 parser = P()
 parser.feed(html)
 if parser.lang != lang or parser.direction != direction:
  bad.append(rel + " language/direction")
 if parser.h.count("h1") != 1 or parser.h.count("h2") < 2:
  bad.append(rel + " headings")
 if parser.meta.get("robots", "").find("noindex") >= 0:
  bad.append(rel + " noindex")
 if not any(link.get("rel") == "canonical" and link.get("href") == url for link in parser.links):
  bad.append(rel + " canonical")
 for alt, target in (("en", ""), ("fa-AF", "fa/"), ("ps-AF", "ps/")):
  if not any(link.get("hreflang") == alt and link.get("href") == "https://darmaltoon.com/" + target + product_slug for link in parser.links):
   bad.append(rel + " missing hreflang " + alt)
 if "<loc>" + url + "</loc>" not in sitemap:
  bad.append(rel + " missing sitemap entry")
 if ("/" + rel) not in (ROOT / (prefix + "guides/index.html")).read_text():
  bad.append(rel + " not linked from guides")
 match = re.search(r'<script type="application/ld\+json">(.+?)</script>', html)
 if not match:
  bad.append(rel + " missing product structured data")
 else:
  try:
   structured = json.loads(match.group(1))
   graph = structured.get("@graph", [])
   if not any(node.get("@type") == "WebPage" and node.get("url") == url for node in graph):
    bad.append(rel + " WebPage URL mismatch")
   if not any(node.get("@type") == "SoftwareApplication" and node.get("name") == "Darmaltoon" for node in graph):
    bad.append(rel + " SoftwareApplication identity")
  except ValueError:
   bad.append(rel + " malformed structured data")
if bad:
 print("FAIL SEO/AIO",len(bad))
 for b in bad:print(" -",b)
 raise SystemExit(1)
print("PASS: 12 guide pages, three product pages, hreflang, structured data, AI analytics and links")
