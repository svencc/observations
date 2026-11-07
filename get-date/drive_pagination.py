"""Resolve public Drive folder truncation using anonymous API pagination.

The public web-client API key stays in memory and is never written to reports.
"""
import sys
sys.path.insert(0,'/tmp/observations-download-deps')
import concurrent.futures as cf
import hashlib
import json
import re
from collections import deque
from pathlib import Path
import requests
from cloud_sources import drive_file, stamp
from download_sources import ROOT, RAW, emit

API='https://www.googleapis.com/drive/v3/files'
FIELDS='nextPageToken,files(id,name,mimeType,size)'
def params(fid):return {'q':"'"+fid+"' in parents and trashed=false",'pageSize':1000,'fields':FIELDS}

if __name__=='__main__':
    issues=json.loads((ROOT/'get-date/drive-issues.json').read_text())
    initial=[r['url'] for r in issues if '50 entries' in r['issue']]
    fid=initial[0].rsplit('/',1)[-1]
    html=(RAW/'sptv-drive/_provenance/catalog'/('folder-'+fid+'.html')).read_text()
    key=None
    for candidate in set(re.findall(r'AIza[\w-]{25,50}',html)):
        r=requests.get(API,params=dict(params(fid),key=candidate),headers={'Referer':'https://drive.google.com/'})
        if r.status_code==200:key=candidate;break
    if not key:raise SystemExit('Anonymous pagination unavailable')
    existing=json.loads((RAW/'sptv-drive/_provenance/drive-inventory.json').read_text())
    existing_ids={r[0] for r in existing}
    known_folders={p.stem[len('folder-'):] for p in (RAW/'sptv-drive/_provenance/catalog').glob('folder-*.html')}
    queue=deque(initial);seen=set();extra={};failures=[];resolved=[];size=0
    def listing(url):
        fid=url.rsplit('/',1)[-1];token=None;all_files=[];pages=0
        while True:
            query=dict(params(fid),key=key)
            if token:query['pageToken']=token
            r=requests.get(API,params=query,headers={'Referer':'https://drive.google.com/'})
            if r.status_code!=200:raise ValueError('Anonymous listing returned HTTP '+str(r.status_code))
            obj=r.json();all_files.extend(obj.get('files',[]));pages+=1
            path=RAW/'sptv-drive/_provenance/catalog'/('api-'+fid+'-'+str(pages)+'.json');path.write_text(json.dumps(obj,ensure_ascii=False))
            token=obj.get('nextPageToken')
            if not token:break
        return url,all_files,pages
    with cf.ThreadPoolExecutor(max_workers=5) as pool:
        while queue:
            active={}
            while queue and len(active)<5:
                url=queue.popleft()
                if url in seen:continue
                seen.add(url);active[pool.submit(listing,url)]=url
            for future in cf.as_completed(active):
                url=active[future]
                try:
                    url,files,pages=future.result();resolved.append({'url':url,'entries':len(files),'pages':pages})
                    for f in files:
                        if f['mimeType']=='application/vnd.google-apps.folder':
                            if f['id'] not in known_folders:queue.append('https://drive.google.com/drive/folders/'+f['id'])
                        elif f['id'] not in existing_ids and not f['name'].lower().endswith(('.mp3','.mp4','.avi','.wav','.jpg','.png','.jpeg','.mkv','.flac','.m4a','.gif','.exe','.dmg')):
                            extra[f['id']]=(f['id'],f['name'],f['mimeType'],url)
                            size+=int(f.get('size',0))
                except Exception as e:failures.append({'url':url,'issue':type(e).__name__+': '+str(e).split('?')[0]})
            print(json.dumps({'paginated_folders':len(resolved),'extra_files':len(extra),'remaining_folders':len(queue)}),flush=True)
    (RAW/'sptv-drive/_provenance/extra-drive-inventory.json').write_text(json.dumps(list(extra.values()),ensure_ascii=False,indent=2))
    (ROOT/'get-date/drive-pagination-result.json').write_text(json.dumps({'resolved':resolved,'failed':failures,'extra_files':len(extra),'reported_extra_bytes':size},ensure_ascii=False,indent=2))
    with cf.ThreadPoolExecutor(max_workers=5) as pool:
        for i,row in enumerate(pool.map(drive_file,extra.values()),1):
            if i%50==0:print(json.dumps({'extra_files_attempted':i,'last_status':row['status']}),flush=True)
