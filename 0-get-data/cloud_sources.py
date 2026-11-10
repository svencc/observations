"""Read public Drive folders and public cloud shares without account credentials."""
import sys
sys.path.insert(0,'/tmp/observations-download-deps')
import concurrent.futures as cf
import hashlib
import json
import re
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import requests
import gdown
from gdown.download_folder import _parse_google_drive_file
from download_sources import ROOT, RAW, emit, fetch

_request=requests.Session.request
def bounded_request(self,*args,**kwargs):
    kwargs.setdefault('timeout',(12,60))
    return _request(self,*args,**kwargs)
requests.Session.request=bounded_request

def stamp():return datetime.now(timezone.utc).isoformat()
def drive_file(item):
    fid,name,mime,folder=item
    row=dict(source_id='sptv-drive',source_url='https://drive.google.com/file/d/'+fid+'/view',discovered_on=folder,language='unknown',retrieved_at=stamp(),status='failed',original_filename=name,kind='document')
    safe=re.sub(r'[^\w. ()!+-]','_',name)[:170]
    out=RAW/'sptv-drive'/('file-'+fid+'__'+safe);part=Path(str(out)+'.part')
    try:
        result=gdown.download(id=fid,output=str(part),quiet=True,use_cookies=False,resume=True)
        if not result:raise ValueError('No downloadable response')
        with part.open('rb') as f: head=f.read(1024)
        if name.lower().endswith('.pdf') and b'%PDF-' not in head:raise ValueError('Not a PDF')
        if head.lstrip().lower().startswith((b'<!doctype html',b'<html')):raise ValueError('HTML returned instead of document')
        digest=hashlib.sha256()
        with part.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):digest.update(b)
        part.replace(out);row.update(status='successful',local_path=str(out.relative_to(ROOT)),bytes=out.stat().st_size,sha256=digest.hexdigest())
    except Exception as e:row['error']=str(e)
    emit(row);return row

def drives():
    probes=json.loads((ROOT/'0-get-data/archive-probes.json').read_text())
    q=deque(r['url'] for r in probes if r['source']=='sptv-drive' and r.get('http_status')==200)
    seen=set();files={};issues=[]
    def folder_page(url):
        p=RAW/'sptv-drive/_provenance/catalog'/('folder-'+url.rsplit('/',1)[-1]+'.html')
        if p.exists():return url,p,p.read_bytes()
        r=requests.get(url+'?hl=en',timeout=(12,45));r.raise_for_status();p.write_bytes(r.content)
        return url,p,r.content
    folder_pool=cf.ThreadPoolExecutor(max_workers=6)
    while q:
        active={}
        while q and len(active)<6:
            url=q.popleft()
            if url in seen:continue
            seen.add(url);active[folder_pool.submit(folder_page,url)]=url
        for future in cf.as_completed(active):
            url=active[future]
            try:
                url,p,content=future.result()
                _,entries=_parse_google_drive_file(url,content.decode('utf-8'))
                if len(entries)>=50:issues.append({'url':url,'issue':'At least 50 entries: public HTML listing may be truncated; requires pagination/browser follow-up'})
                emit(dict(source_id='sptv-drive',source_url=url,discovered_on='https://resources.sptv.space/list/lrh/',language='unknown',retrieved_at=stamp(),status='successful',kind='catalog',local_path=str(p.relative_to(ROOT)),bytes=len(content),sha256=hashlib.sha256(content).hexdigest()))
                for fid,name,mime in entries:
                    if mime=='application/vnd.google-apps.folder':q.append('https://drive.google.com/drive/folders/'+fid)
                    elif not name.lower().endswith(('.mp3','.mp4','.avi','.wav','.jpg','.png','.mkv')):files[fid]=(fid,name,mime,url)
            except Exception as e:
                issues.append({'url':url,'issue':str(e)})
                emit(dict(source_id='sptv-drive',source_url=url,discovered_on='public parent folder',language='unknown',retrieved_at=stamp(),status='failed',error=str(e),kind='catalog'))
        if len(seen)%30<6:print(json.dumps({'drive_folders':len(seen),'files_discovered':len(files),'remaining_folders':len(q)}),flush=True)
    folder_pool.shutdown()
    (RAW/'sptv-drive/_provenance/drive-inventory.json').write_text(json.dumps(list(files.values()),ensure_ascii=False,indent=2))
    (ROOT/'0-get-data/drive-issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2))
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        for i,row in enumerate(pool.map(drive_file,files.values()),1):
            if i%25==0:print(json.dumps({'drive_files_attempted':i,'last_status':row['status']}),flush=True)

def cloud():
    issues=[]
    for source,root in [('saentowiki','5649/JAgSbzq1X'),('galac-patra','DCch/aSerUyxNH')]:
        q=deque([root]);seen=set()
        while q:
            key=q.popleft()
            if key in seen:continue
            seen.add(key);url='https://cloud.mail.ru/public/'+quote(key,safe='/')
            try:
                r=requests.get(url,timeout=(12,45));r.raise_for_status()
                p=RAW/source/'_provenance/catalog'/('cloud-'+hashlib.sha256(key.encode()).hexdigest()[:10]+'.html');p.write_bytes(r.content)
                marker='"serverSideFolders":';pos=r.text.find(marker)
                if pos<0:raise ValueError('No public folder/file metadata in response')
                obj,_=json.JSONDecoder().raw_decode(r.text[pos+len(marker):])
                (p.with_suffix('.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
                print(json.dumps({'cloud':source,'key':key,'metadata':obj},ensure_ascii=False)[:2500],flush=True)
                for entry in obj.get('list',[]):
                    if entry.get('type')=='folder':q.append(entry['weblink'])
                # Public download dispatch is exposed by the anonymous web client.
                files=[e for e in obj.get('list',[]) if e.get('type')=='file']
                if obj.get('type')=='file':files=[obj]
                for e in files:
                    name=e.get('name','')
                    if not name.lower().endswith(('.pdf','.doc','.docx','.txt','.rtf','.djvu','.zip','.torrent','.rar')):
                        continue
                    if source=='saentowiki' and re.search('[А-Яа-я]',name):
                        issues.append({'url':url,'issue':'Russian-named material outside EN/DE selection','name':name});continue
                    m=re.search(r'"weblink_get":\{"count":"\d+","url":"([^"]+)"',r.text)
                    if not m:raise ValueError('No anonymous download dispatcher')
                    target=m.group(1).rstrip('/')+'/'+quote(e['weblink'],safe='/')
                    row,_=fetch((source,target,url,'mixed' if source=='galac-patra' else 'unknown',0))
                    if row['status']!='successful':issues.append({'url':url,'issue':row.get('error')})
            except Exception as e:issues.append({'url':url,'issue':str(e)})
    # Official public Yandex download endpoint, no account required.
    public='https://disk.yandex.ru/d/r9QenImC9cElig'
    try:
        r=requests.get('https://cloud-api.yandex.net/v1/disk/public/resources/download',params={'public_key':public},timeout=(12,45));r.raise_for_status();href=r.json()['href']
        row,_=fetch(('galac-patra',href,public,'mixed',0))
        if row['status']!='successful':issues.append({'url':public,'issue':row.get('error')})
    except Exception as e:issues.append({'url':public,'issue':str(e)})
    (ROOT/'0-get-data/cloud-issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2))

if __name__=='__main__':
    if '--drive-only' in sys.argv:drives()
    else:
        with cf.ThreadPoolExecutor(max_workers=2) as pool:
            for result in pool.map(lambda fn:fn(),[cloud,drives]):pass
