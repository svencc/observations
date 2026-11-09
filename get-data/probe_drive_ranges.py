"""Diagnose anonymous API errors without exposing request configuration."""
import json
import re
import requests
from probe_drive_media import client_key
from download_sources import ROOT

if __name__=='__main__':
    key=client_key();rows=[json.loads(l) for l in (ROOT/'get-data/download-manifest.jsonl').read_text().splitlines()]
    row=next(r for r in reversed(rows) if r.get('download_method')=='anonymous Drive API' and r['status']=='failed' and r.get('original_filename','').lower().endswith('.pdf'))
    fid=row['source_url'].split('/d/')[1].split('/')[0]
    for value in [None,'bytes=0-1023','bytes=0-']:
        headers={'Referer':'https://drive.google.com/'}
        if value:headers['Range']=value
        with requests.get('https://www.googleapis.com/drive/v3/files/'+fid,params={'alt':'media','key':key},headers=headers,timeout=(12,30),stream=True) as r:
            head=next(r.iter_content(1024),b'')
            error=None
            if r.status_code>=400:
                error=re.sub(r'AIza[\w-]+','<public-client-key-omitted>',head.decode(errors='replace'))[:700]
            print(json.dumps({'file_id':fid,'range':value,'http_status':r.status_code,'server':r.headers.get('Server'),'type':r.headers.get('Content-Type'),'pdf':b'%PDF-' in head,'error':error}),flush=True)
