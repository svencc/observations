"""Download all inventoried public Drive files using anonymous media/export APIs."""
import concurrent.futures as cf
import hashlib
import json
import re
import shutil
import threading
import time
from pathlib import Path
import requests
from probe_drive_media import client_key
from download_sources import ROOT, RAW, emit
from cloud_sources import stamp

LOCAL=threading.local()

def transfer(item,key):
    fid,name,mime,parent=item
    row=dict(source_id='sptv-drive',source_url='https://drive.google.com/file/d/'+fid+'/view',discovered_on=parent,language='unknown',retrieved_at=stamp(),status='failed',original_filename=name,kind='document',download_method='anonymous Drive API')
    safe=re.sub(r'[^\w. ()!+-]','_',name)[:170]
    endpoint='https://www.googleapis.com/drive/v3/files/'+fid
    query={'key':key,'alt':'media'}
    if mime.startswith('application/vnd.google-apps.'):
        exports={'application/vnd.google-apps.document':('application/pdf','.pdf'),'application/vnd.google-apps.spreadsheet':('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','.xlsx'),'application/vnd.google-apps.presentation':('application/pdf','.pdf')}
        if mime not in exports:
            row['error']='Unsupported Google native type: '+mime;emit(row);return row
        target,ext=exports[mime];endpoint+='/export';query={'key':key,'mimeType':target}
        if not safe.lower().endswith(ext):safe+=ext
        row['download_method']='anonymous Drive API offered export'
    row['api_endpoint']=endpoint
    out=RAW/'sptv-drive'/('file-'+fid+'__'+safe);part=Path(str(out)+'.part')
    if not hasattr(LOCAL,'session'):LOCAL.session=requests.Session()
    for attempt in range(3):
        try:
            if shutil.disk_usage(ROOT).free<20*1024**3:raise ValueError('Transfer stopped: less than 20 GiB free disk space')
            with LOCAL.session.get(endpoint,params=query,headers={'Referer':'https://drive.google.com/'},stream=True,timeout=(12,60)) as r:
                row.update(http_status=r.status_code,content_type=r.headers.get('Content-Type',''))
                if r.status_code>=400:
                    try:
                        error=r.json().get('error',{});message=error.get('message','');reason=','.join(e.get('reason','') for e in error.get('errors',[]))
                    except Exception:message='Non-JSON error response';reason=''
                    if r.status_code in (429,500,502,503) or 'rateLimit' in reason:
                        if attempt<2:time.sleep(2**(attempt+1));continue
                    raise ValueError('HTTP '+str(r.status_code)+': '+reason+' '+message)
                digest=hashlib.sha256();size=0;head=b''
                with part.open('wb') as f:
                    for chunk in r.iter_content(1024*1024):
                        if not chunk:continue
                        if not head:head=chunk[:1024]
                        f.write(chunk);digest.update(chunk);size+=len(chunk)
                if not size:raise ValueError('Empty file response')
                if safe.lower().endswith('.pdf') and b'%PDF-' not in head:raise ValueError('Response is not a valid PDF')
                if head.lstrip().lower().startswith((b'<!doctype html',b'<html')) and not safe.lower().endswith(('.html','.htm')):raise ValueError('HTML response instead of requested document')
                part.replace(out);row.update(status='successful',local_path=str(out.relative_to(ROOT)),bytes=size,sha256=digest.hexdigest());row.pop('error',None);break
        except Exception as e:
            row['error']=re.sub(r'key=[^&\s\)]+','key=<omitted>',str(e))
            if isinstance(e,requests.RequestException) and attempt<2:time.sleep(1);continue
            break
    if row['status']!='successful' and part.exists():part.unlink()
    emit(row);return row

if __name__=='__main__':
    key=client_key();inventory={}
    for filename in ('drive-inventory.json','extra-drive-inventory.json'):
        for entry in json.loads((RAW/'sptv-drive/_provenance'/filename).read_text()):inventory[entry[0]]=entry
    previous={}
    for line in (ROOT/'get-data/download-manifest.jsonl').read_text().splitlines():
        r=json.loads(line)
        if r['source_id']=='sptv-drive' and '/file/d/' in r['source_url']:previous[r['source_url']]=r
    queue=[]
    for fid,item in inventory.items():
        r=previous.get('https://drive.google.com/file/d/'+fid+'/view')
        if r and r['status']=='successful' and r.get('local_path') and (ROOT/r['local_path']).is_file():continue
        queue.append(item)
    print(json.dumps({'inventoried_files':len(inventory),'remaining_transfers':len(queue)}),flush=True)
    counts={}
    with cf.ThreadPoolExecutor(max_workers=12) as pool:
        for i,row in enumerate(pool.map(lambda item:transfer(item,key),queue),1):
            counts[row['status']]=counts.get(row['status'],0)+1
            if i%100==0:print(json.dumps({'attempted':i,'remaining':len(queue)-i,'counts':counts}),flush=True)
    print(json.dumps({'finished':True,'counts':counts}),flush=True)
