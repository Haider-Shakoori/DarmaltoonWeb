#!/usr/bin/env python3
"""Build private IPv4/IPv6 country lookup SQLite from DB-IP Lite CC BY 4.0 CSV.gz.

Example:
  python3 scripts/build_geoip_db.py --source /tmp/dbip-country-lite-2026-09.csv.gz --output /home/darmaltoon/.darmaltoon-analytics/geo-country.sqlite
Free DB-IP Lite attribution: https://db-ip.com, CC BY 4.0.
"""
import argparse,csv,gzip,ipaddress,os,sqlite3,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',required=True);args=p.parse_args()
source=Path(args.source);dest=Path(args.output)
if not source.is_file():raise SystemExit('Geo CSV missing')
dest.parent.mkdir(parents=True,exist_ok=True)
fd,tmp=tempfile.mkstemp(prefix='geo-country-',suffix='.sqlite',dir=str(dest.parent))
os.close(fd)
try:
 db=sqlite3.connect(tmp)
 db.executescript("""PRAGMA journal_mode=DELETE;
 CREATE TABLE v4(start_ip BLOB PRIMARY KEY,end_ip BLOB NOT NULL,country TEXT NOT NULL) WITHOUT ROWID;
 CREATE TABLE v6(start_ip BLOB PRIMARY KEY,end_ip BLOB NOT NULL,country TEXT NOT NULL) WITHOUT ROWID;
 """)
 rows4=[];rows6=[];total=0
 with gzip.open(source,'rt',encoding='utf-8',newline='') if str(source).endswith('.gz') else open(source,'r',encoding='utf-8',newline='') as f:
  for line in csv.reader(f):
   if len(line)!=3:continue
   a,b,code=line
   try:
    start=ipaddress.ip_address(a);end=ipaddress.ip_address(b)
    if start.version!=end.version or int(start)>int(end) or len(code)!=2 or not code.isalpha():continue
    row=(start.packed,end.packed,code.upper())
    bucket=rows4 if start.version==4 else rows6
    bucket.append(row);total+=1
   except ValueError: continue
   if len(rows4)+len(rows6)>=5000:
    db.executemany('INSERT OR REPLACE INTO v4 VALUES (?,?,?)',rows4)
    db.executemany('INSERT OR REPLACE INTO v6 VALUES (?,?,?)',rows6)
    rows4.clear();rows6.clear()
 db.executemany('INSERT OR REPLACE INTO v4 VALUES (?,?,?)',rows4)
 db.executemany('INSERT OR REPLACE INTO v6 VALUES (?,?,?)',rows6)
 db.commit()
 count=sum(db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('v4','v6'))
 if count<200000:raise RuntimeError('Suspiciously small geo database')
 db.close();os.chmod(tmp,0o600);os.replace(tmp,dest)
 print(f'IMPORTED: {count} geo ranges; saved private lookup at {dest}')
except BaseException:
 try:os.unlink(tmp)
 except OSError:pass
 raise

