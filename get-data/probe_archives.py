"""Inspect public Drive/cloud links and obtain advertised archive files."""
import concurrent.futures as cf
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
import requests
from download_sources import fetch, ROOT, RAW, SOURCES

def probe(job):
    source,url=job
    folder=RAW/source/'_provenance/catalog'
    folder.mkdir(parents=True, exist_ok=True)
    import hashlib
    name=hashlib.sha256(url.encode()).hexdigest()[:12]
    result={'source':source,'url':url}
    try:
        r=requests.get(url,timeout=(12,45))
        (folder/(name+'.html')).write_bytes(r.content)
        result.update(http_status=r.status_code,final_url=r.url,bytes=len(r.content),
                      title=re.findall(r'<title[^>]*>(.*?)</title>',r.text,re.S)[:1])
        if 'drive.google.com' in url:
            result['drive_data']=bool(re.search(r'_DRIVE_ivd|data-id=',r.text))
            result['folder_ids']=list(dict.fromkeys(re.findall(r'/drive/folders/([\w-]+)',r.text)))[:20]
        if 'cloud.mail.ru' in url:
            result['hints']=list(dict.fromkeys(re.findall(r'.{0,60}(?:weblink|downloadUrl|tokens|dispatcher|PUBLIC_LINK|not_exists).{0,110}',r.text)))[:12]
        if 'yandex' in url: result['hints']=re.findall(r'.{0,40}(?:resource_id|public_key|notFound|blocked).{0,100}',r.text)[:8]
    except Exception as e: result['error']=str(e)
    return result

if __name__=='__main__':
    jobs=[]
    for url in json.loads((RAW/'sptv-drive/_provenance/catalog/links.json').read_text()):
        if 'drive.google.com/drive/folders/' in url:jobs.append(('sptv-drive',url))
    jobs += [('saentowiki','https://cloud.mail.ru/public/5649/JAgSbzq1X'),
             ('galac-patra','https://cloud.mail.ru/public/DCch/aSerUyxNH'),
             ('galac-patra','https://disk.yandex.ru/d/r9QenImC9cElig'),
             ('sciento','https://sciento.org/login?next=%2Fsearch%2F'),
             ('esmb','https://forum.exscn.net/threads/the-works-of-captain-bill-robertson-cbr-%E2%80%94-excalibur-phoenix-etc.23352/'),
             ('aogp','https://www.ao-gp.org/free-scientology-books/'),
             ('ronsorg','https://www.ronsorg.org/'),
             ('lrhmaterials','https://lrhmaterials.com/')]
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(probe,jobs))
    (ROOT/'get-data/archive-probes.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    for r in results:
        print(json.dumps({k:v for k,v in r.items() if k!='hints'},ensure_ascii=False),flush=True)
    for url in ['https://galac-patra.ru/library-english.zip','https://galac-patra.ru/library-non-eglish.zip','https://galac-patra.ru/CBR_complete_library.zip']:
        row,_=fetch(('galac-patra',url,SOURCES['galac-patra'],'mixed',0));print(json.dumps(row),flush=True)
