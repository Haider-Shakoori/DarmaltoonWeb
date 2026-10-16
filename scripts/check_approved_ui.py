from pathlib import Path
from html.parser import HTMLParser
import sys
root=Path(__file__).resolve().parents[1]
errors=[]
def check(ok,s):
 if not ok:errors.append(s)
class Reader(HTMLParser):
 def __init__(self):super().__init__();self.tags=[];self.links=[];self.images=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs);self.tags.append(t)
  if t=='a':self.links.append(a.get('href'))
  if t=='img':self.images.append(a.get('src'))
for theme,path in [('light','index.html'),('dark','dark.html')]:
 text=(root/path).read_text(encoding='utf8');p=Reader();p.feed(text)
 check(p.tags.count('h1')==1,path+' must have one h1')
 check('data:image/jpeg;base64' not in text,path+' embeds giant base64 artwork')
 check(f'/assets/images/design/{theme}.webp' in p.images,path+' image missing')
 check('/assets/images/brand/darmaltoon-selected.png' in p.images,path+' approved mark missing')
 check('https://web.darmaltoon.com/' in text,path+' canonical missing')
 check('file_0000' not in text,path+' internal attachment reference leaked')
 check('AFN 1,500' not in text and 'AFN 3,500' not in text,path+' unverified prices')
 check('Trusted by pharmacies across Afghanistan' not in text,path+' fake reviews')
 check('have <strong>not</strong> been sent' in (root/'assets/js/ui-enhancements.js').read_text(), 'unsent demo forms must not claim delivery')
 for src in p.images:
  if src and src.startswith('/assets/'):check((root/src.lstrip('/')).is_file(),path+' missing asset: '+src)
 for href in p.links:
  if href and href.startswith('/') and not href.startswith('//'):
   dest=root/href.split('?')[0].lstrip('/')
   if href.split('?')[0].endswith('/'):dest=dest/'index.html'
   check(dest.is_file(),path+' broken link '+href)
for fname,maximum in [('assets/images/design/light.webp',420_000),('assets/images/design/dark.webp',420_000),('assets/css/ui-enhancements.css',10_000),('assets/js/ui-enhancements.js',5_000)]:
 f=root/fname;check(f.is_file() and f.stat().st_size<maximum,fname+' exceeds size budget or is missing')
if errors:
 for x in errors:print('FAIL',x)
 sys.exit(1)
print('PASS approved ZIP designs, links, logo, form integrity and data budgets')
