"""Check recorded local transfers; clarify media captured during catalog discovery."""
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from download_sources import ROOT, emit

if __name__=='__main__':
    latest={}
    for line in (ROOT/'get-date/download-manifest.jsonl').read_text().splitlines():
        r=json.loads(line)
        if r.get('local_path'):latest[r['local_path']]=r
    issues=[];types=Counter();n=0
    torrent_checks={}
    for checked in (ROOT/'raw-data').rglob('verified-files.json'):
        base=checked.parent if checked.is_relative_to(ROOT/'raw-data/scientolipedia') else checked.parent/'payload'
        for item in json.loads(checked.read_text()):torrent_checks[str((base/item['path']).relative_to(ROOT))]=item
    for local,r in latest.items():
        if r['status']!='successful':continue
        p=ROOT/local
        if not p.exists() or p.stat().st_size!=r['bytes']:
            issues.append({'path':local,'issue':'Missing or size differs from recorded transfer'});continue
        target=parse_qs(urlsplit(r['source_url']).query).get('download',[''])[0]
        ext=Path(target or r.get('original_filename') or p.name).suffix.lower()
        changed=False
        check=torrent_checks.get(local)
        if check and not check.get('complete'):
            r.update(status='partial',error='Torrent piece recheck: incomplete or excluded file; not part of the verified text download',verified_bytes=check.get('verified_bytes',0));changed=True
        if target and r.get('original_filename')!=target:r['original_filename']=target;changed=True
        if ext in ('.mp3','.wav','.flac','.m4a','.mp4','.avi','.mkv') and r.get('kind')!='ancillary_media':r['kind']='ancillary_media';changed=True
        if ext in ('.jpg','.jpeg','.png') and r.get('kind')!='ancillary_image':r['kind']='ancillary_image';r['language']='unknown';changed=True
        if ext=='.pdf':
            with p.open('rb') as f:head=f.read(1024)
            if b'%PDF-' not in head:
                issues.append({'path':local,'issue':'Invalid PDF signature'});r.update(status='failed',error='Offline validation: invalid PDF signature');changed=True
        if ext=='.zip' or r['source_id']=='galac-patra' and r.get('kind')=='document' and not r.get('infohash'):
            if zipfile.is_zipfile(p):
                try:
                    with zipfile.ZipFile(p) as z:
                        bad=z.testzip()
                        if bad:issues.append({'path':local,'issue':'Bad ZIP member '+bad})
                except Exception as e:issues.append({'path':local,'issue':str(e)})
        if changed:emit(r)
        types[r.get('kind','unknown')]+=1;n+=1
    result={'checked_files':n,'kinds':dict(types),'issues':issues}
    (ROOT/'get-date/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result))
