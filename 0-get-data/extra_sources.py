"""Crawl the additional public CBR/LRH catalogs and the ESMB thread."""
import concurrent.futures as cf
import json
import argparse
import shutil
from collections import deque
from urllib.parse import urlsplit, parse_qs, urlencode, urlunsplit
from download_sources import fetch, links, ROOT, RAW, DOC

THREAD='/threads/the-works-of-captain-bill-robertson-cbr-'
INCLUDE_AUDIO_ARCHIVES=False
SEEDS=[('ronsorg','https://ronsorg.org/'),('lrhmaterials','https://www.lrhmaterials.com/materials.php'),
       ('esmb','https://forum.exscn.net/threads/the-works-of-captain-bill-robertson-cbr-%E2%80%94-excalibur-phoenix-etc.23352/')]

def ok(source,url):
    p=urlsplit(url)
    if source=='ronsorg':return p.hostname=='ronsorg.org' and not p.query and not any(x in p.path for x in ('/feed','/contact','wp-json')) and not p.path.endswith(('.jpg','.png','.mp3','.mp4'))
    if source=='lrhmaterials':
        query=parse_qs(p.query)
        target=query.get('download',[''])[0]
        audio_directory=any(segment.lower()=='02-audio_materials' for segment in query.get('dir',[''])[0].split('/'))
        text_package=any(word in target.lower() for word in ('transcript','booklet','written','text','pdf','doc','index'))
        if not INCLUDE_AUDIO_ARCHIVES and target.lower().endswith('.zip') and audio_directory and not text_package:
            return False
        return p.hostname in ('www.lrhmaterials.com','lrhmaterials.com') and (p.path.lower().endswith(DOC) or p.path.endswith('materials.php')) and (not target or target.lower().endswith(DOC)) and not any(x in url.lower() for x in ['french','spanish','italian','russian'])
    if source=='esmb':return p.hostname=='forum.exscn.net' and ((p.path.startswith(THREAD) and not '/post-' in p.path and not p.query) or p.path.startswith('/attachments/'))
    return False

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--include-audio-archives',action='store_true')
    args=parser.parse_args();INCLUDE_AUDIO_ARCHIVES=args.include_audio_archives
    q=deque(); seen=set(); n=0
    partials=RAW/'_handover/partial-http-files.json'
    if partials.exists():
        for row in json.loads(partials.read_text()):
            u=row.get('source_url','')
            if ok('lrhmaterials',u):q.append(('lrhmaterials',u,row['discovered_on'],'en',0))
    pending=RAW/'_handover/pending-lrhmaterials.jsonl'
    if pending.exists():
        for line in pending.read_text().splitlines():
            row=json.loads(line);u=row['source_url']
            if ok('lrhmaterials',u):q.append(('lrhmaterials',u,row['discovered_on'],'en',0))
    q.extend((s,u,u,'en',0) for s,u in SEEDS)
    previous={}
    ledger=ROOT/'0-get-data/download-manifest.jsonl'
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            r=json.loads(line);previous[(r['source_id'],r['source_url'])]=r
    with cf.ThreadPoolExecutor(max_workers=5) as pool:
        while q:
            if shutil.disk_usage(ROOT).free<20*1024**3:
                print(json.dumps({'stopped_low_disk_space':True,'queued':len(q)}),flush=True)
                break
            batch=[]
            while q and len(batch)<10:
                j=q.popleft()
                key=(j[0],j[1])
                if key in seen:continue
                seen.add(key)
                old=previous.get(key)
                if old and old['status']=='successful' and old.get('local_path') and (ROOT/old['local_path']).is_file() and (ROOT/old['local_path']).stat().st_size==old.get('bytes'):
                    if old.get('kind')=='html':
                        for u in links((ROOT/old['local_path']).read_text(errors='replace'),old.get('final_url',old['source_url'])):
                            if ok(j[0],u):
                                if j[0]=='lrhmaterials':
                                    p=urlsplit(u);query=parse_qs(p.query);query={k:v for k,v in query.items() if k in ('dir','download')};u=urlunsplit((p.scheme,p.netloc,p.path,urlencode(query,doseq=True),''))
                                q.append((j[0],u,j[1],'en',0))
                    continue
                batch.append(j)
            for row,_ in pool.map(fetch,batch):
                n+=1
                if row['status']=='successful' and row.get('kind') in ('html','catalog'):
                    for u in links((ROOT/row['local_path']).read_text(errors='replace'),row['final_url']):
                        if ok(row['source_id'],u):
                            if row['source_id']=='lrhmaterials':
                                p=urlsplit(u);query=parse_qs(p.query);query={k:v for k,v in query.items() if k in ('dir','download')};u=urlunsplit((p.scheme,p.netloc,p.path,urlencode(query,doseq=True),''))
                            q.append((row['source_id'],u,row['source_url'],'en',0))
                if n%30==0:print(json.dumps({'completed':n,'queued':len(q)}),flush=True)
    print(json.dumps({'finished':True,'completed':n}),flush=True)
