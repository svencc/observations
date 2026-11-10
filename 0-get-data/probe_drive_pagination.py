"""Check whether anonymous Drive API pagination is available for public folders.

Only the public web client's published API configuration is used; no user token.
Keys are never copied to reports or terminal output.
"""
import json
import re
from pathlib import Path
import requests
from download_sources import ROOT, RAW

if __name__=='__main__':
    issues=json.loads((ROOT/'0-get-data/drive-issues.json').read_text())
    item=next(r for r in issues if '50 entries' in r['issue'])
    fid=item['url'].rsplit('/',1)[-1]
    html=(RAW/'sptv-drive/_provenance/catalog'/('folder-'+fid+'.html')).read_text()
    keys=set(re.findall(r'AIza[\w-]{25,50}',html))
    results=[]
    for key in keys:
        try:
            r=requests.get('https://www.googleapis.com/drive/v3/files',params={'key':key,'q':"'"+fid+"' in parents and trashed=false",'pageSize':1000,'fields':'nextPageToken,files(id,name,mimeType,size)'},headers={'Referer':'https://drive.google.com/'},timeout=(12,30))
            obj=r.json()
            summary={'http_status':r.status_code,'files':len(obj.get('files',[])),'has_next_page':bool(obj.get('nextPageToken')),'reason':obj.get('error',{}).get('message')}
            results.append(summary)
            if r.status_code==200:
                (RAW/'sptv-drive/_provenance/pagination-test.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2));break
        except Exception as e:results.append({'error_type':type(e).__name__})
    (ROOT/'0-get-data/drive-pagination-probe.json').write_text(json.dumps({'folder_url':item['url'],'results':results},ensure_ascii=False,indent=2))
    print(json.dumps(results))
