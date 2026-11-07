"""Download public EN/DE source documents with an append-only provenance log.

Run from any directory. A repeat run reuses verified successful downloads.
No credentials, account creation, permission requests, or outgoing messages.
"""
import concurrent.futures as cf
import hashlib
import json
import re
import threading
import time
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urldefrag, urljoin, urlsplit, parse_qs
import requests
from inspect_sources import Links, ROOT, SOURCES

RAW = ROOT / 'raw-data'
LEDGER = ROOT / 'get-date' / 'download-manifest.jsonl'
LOCK = threading.Lock()
LIMITS = {}
DOC = ('.pdf', '.doc', '.docx', '.txt', '.djvu', '.djv', '.rtf', '.epub', '.zip', '.torrent')

def canonical(url):
    url = urldefrag(url)[0]
    # Modern freezone.org serves the same English collection without /english.
    if urlsplit(url).hostname in ('freezone.org', 'www.freezone.org'):
        url = re.sub(r'^https?://(?:www\.)?freezone\.org/(?:english/)?', 'https://freezone.org/', url)
    return url

def links(text, url):
    p = Links(); p.feed(text)
    return list(dict.fromkeys(canonical(urljoin(url, h)) for h in p.hrefs if not h.startswith(('javascript:', 'mailto:', '#'))))

def emit(row):
    line = json.dumps(row, ensure_ascii=False)
    with LOCK:
        with LEDGER.open('a') as f: f.write(line + '\n')
        path = RAW / row['source_id'] / '_provenance' / 'manifest.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as f: f.write(line + '\n')

def allowed(source, url, depth):
    p = urlsplit(url)
    if p.scheme not in ('https', 'http') or p.query or depth > 5: return False
    if source == 'saentowiki': return p.hostname == 'saentowiki.com' and p.path.startswith('/en/')
    if source == 'freezone-org':
        return p.hostname == 'freezone.org' and (p.path.startswith('/Content/CBR/Publications/') or p.path.startswith('/Content/Technology/')) and (p.path.lower().endswith(('.html', '.htm') + DOC))
    if source == 'freezone-de':
        return p.hostname in ('freezone.de', 'www.freezone.de') and p.path.lower().endswith(DOC)
    return False

def fetch(job):
    source, url, discovered, language, depth = job
    row = dict(source_id=source, source_url=url, discovered_on=discovered,
               language=language, retrieved_at=datetime.now(timezone.utc).isoformat(), status='failed')
    digest = hashlib.sha256(url.encode()).hexdigest()[:10]
    target_name = parse_qs(urlsplit(url).query).get('download', [''])[0]
    name = target_name or unquote(urlsplit(url).path.rstrip('/').rsplit('/', 1)[-1]) or 'index'
    name = re.sub(r'[^\w. ()!+-]', '_', name)[:160]
    if '.' not in name: name += '.pdf' if '/api/books/pdf/' in url else '.html'
    path = RAW / source / (Path(name).stem + '__' + digest + Path(name).suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_suffix(path.suffix + '.part')
    found = []
    with LIMITS.setdefault(source, threading.Semaphore(3)):
        for attempt in range(2):
            try:
                with requests.get(url, stream=True, timeout=(12, 50), headers={'User-Agent':'ObservationsArchive/1.0 (personal document archival)'}) as r:
                    row.update(http_status=r.status_code, final_url=r.url, content_type=r.headers.get('Content-Type', ''))
                    r.raise_for_status()
                    h = hashlib.sha256(); size = 0
                    with part.open('wb') as f:
                        for chunk in r.iter_content(1024*1024):
                            if chunk: f.write(chunk); h.update(chunk); size += len(chunk)
                    if not size: raise ValueError('Empty response')
                    with part.open('rb') as f: head = f.read(1024)
                    ext = (target_name or urlsplit(url).path).lower()
                    if (ext.endswith('.pdf') or '/api/books/pdf/' in url) and b'%PDF-' not in head:
                        raise ValueError('Response is not a PDF (possible error/login page)')
                    if ext.endswith('.zip') and not head.startswith(b'PK'):
                        raise ValueError('Response is not a ZIP archive')
                    is_html = 'html' in row['content_type'] or head.lstrip().lower().startswith((b'<!doctype html', b'<html'))
                    if is_html:
                        text = part.read_text(encoding=r.encoding or 'utf-8', errors='replace')
                        if re.search(r'<title>[^<]*(?:404|not found|access denied|just a moment)', text, re.I):
                            raise ValueError('HTML error/challenge page')
                        found = [u for u in links(text, r.url) if allowed(source, u, depth+1)]
                        row['kind'] = 'catalog' if source=='saentowiki' and '/contents/' in url else 'html'
                    else: row['kind'] = 'document'
                    part.replace(path)
                    row.update(status='successful', local_path=str(path.relative_to(ROOT)), bytes=size, sha256=h.hexdigest(), original_filename=unquote(urlsplit(url).path.rsplit('/',1)[-1]))
                    row.pop('error', None)
                    break
            except Exception as e:
                row['error'] = str(e)
                if attempt == 0: time.sleep(1)
    if row['status'] != 'successful' and part.exists(): part.unlink()
    emit(row)
    return row, [(source, u, url, language, depth+1) for u in found]

def seed_jobs():
    jobs = []
    data = json.loads((RAW/'stss/_provenance/catalog/materials.json').read_text())
    for lang in ('en', 'de'):
        for category in data.get(lang, []):
            for item in category.get('files', []):
                jobs.append(('stss', item['url'], 'https://stss.nl/api/materials.php', lang, 0))
    for source in ('freezone-de','freezone-org','project-avalon','saentowiki'):
        catalog = RAW/source/'_provenance/catalog/entry.html'
        urls = links(catalog.read_text(errors='replace'), SOURCES[source])
        if source == 'freezone-de':
            start = next(i for i,u in enumerate(urls) if 'glossar-zu-begriffen' in u)
            urls = [u for u in urls[start:] if urlsplit(u).hostname in ('freezone.de','www.freezone.de') and not any(x in u for x in ('impressum','datenschutz','/english/'))]
        elif source == 'freezone-org': urls = [u for u in urls if allowed(source,u,0)]
        elif source == 'project-avalon': urls = [u for u in urls if '/lib/Scientology/' in u and urlsplit(u).path.lower().endswith(DOC)]
        elif source == 'saentowiki': urls = [u for u in urls if allowed(source,u,0)]
        jobs.append((source, SOURCES[source], SOURCES[source], 'de' if source=='freezone-de' else 'en', 0))
        jobs.extend((source,u,SOURCES[source],'de' if source=='freezone-de' else 'en',0) for u in urls)
    # Explicit old links are attempted too; they may no longer be in today's catalog.
    plan = (ROOT/'get-date/plan1.md').read_text()
    for u in re.findall(r'https://stss\.nl/[^\s>]+\.pdf', plan):
        jobs.append(('stss',u,'get-date/plan1.md','de' if '/Deutsch/' in u else 'en',0))
    return jobs

def main():
    previous = {}
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            r=json.loads(line); previous[(r['source_id'],r['source_url'])]=r
    q=deque(seed_jobs()); seen=set(); active={}; counts=Counter()
    with cf.ThreadPoolExecutor(max_workers=12) as pool:
        while q or active:
            while q and len(active)<24:
                job=q.popleft(); key=(job[0],job[1])
                if key in seen: continue
                seen.add(key)
                old=previous.get(key)
                if old and old['status']=='successful' and (ROOT/old['local_path']).is_file():
                    if old.get('kind') in ('html','catalog'):
                        for u in links((ROOT/old['local_path']).read_text(errors='replace'),old['source_url']):
                            if allowed(job[0],u,job[4]+1): q.append((job[0],u,job[1],job[3],job[4]+1))
                    continue
                active[pool.submit(fetch,job)] = job
            if not active: continue
            done,_=cf.wait(active,return_when=cf.FIRST_COMPLETED)
            for f in done:
                active.pop(f)
                row,children=f.result(); counts[(row['source_id'],row['status'])]+=1; q.extend(children)
                if sum(counts.values())%100==0: print(json.dumps({'completed':sum(counts.values()),'queued':len(q),'counts':{str(k):v for k,v in counts.items()}}),flush=True)
    print(json.dumps({'finished':True,'counts':{str(k):v for k,v in counts.items()}}),flush=True)

if __name__=='__main__': main()
