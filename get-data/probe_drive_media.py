"""Test anonymous direct media transfer; never log the public client key."""
import json
import re
from pathlib import Path
import requests
from download_sources import ROOT, RAW

def client_key():
    issues=json.loads((ROOT/'get-data/drive-issues.json').read_text())
    url=next(r['url'] for r in issues if '50 entries' in r['issue']);fid=url.rsplit('/',1)[-1]
    text=(RAW/'sptv-drive/_provenance/catalog'/('folder-'+fid+'.html')).read_text()
    for candidate in set(re.findall(r'AIza[\w-]{25,50}',text)):
        r=requests.get('https://www.googleapis.com/drive/v3/files',params={'key':candidate,'q':"'"+fid+"' in parents",'pageSize':1,'fields':'files(id)'},headers={'Referer':'https://drive.google.com/'},timeout=(12,30))
        if r.status_code==200:return candidate
    raise RuntimeError('No working anonymous public web-client API configuration')

if __name__=='__main__':
    key=client_key();rows=[]
    for line in (ROOT/'get-data/download-manifest.jsonl').read_text().splitlines():
        r=json.loads(line)
        if r['source_id']=='sptv-drive' and r.get('kind')=='document':rows.append(r)
    picks=[next(r for r in rows if r['status']=='successful'),next(r for r in reversed(rows) if r['status']=='failed')]
    for row in picks:
        fid=row['source_url'].split('/d/')[1].split('/')[0]
        with requests.get('https://www.googleapis.com/drive/v3/files/'+fid,params={'alt':'media','key':key},headers={'Referer':'https://drive.google.com/','Range':'bytes=0-1023'},timeout=(12,30),stream=True) as r:
            head=next(r.iter_content(1024),b'')
            print(json.dumps({'previous':row['status'],'file_id':fid,'http_status':r.status_code,'content_type':r.headers.get('Content-Type'),'pdf':b'%PDF-' in head,'error':head.decode(errors='replace')[:250] if r.status_code>=400 else None}),flush=True)
