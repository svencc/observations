"""Attempt the two published magnets and torrents in downloaded Galac ZIPs."""
import sys
sys.path.insert(0,'/tmp/observations-download-deps')
import libtorrent as lt
import hashlib
import html
import json
import re
import time
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from download_sources import ROOT, RAW, emit

if __name__=='__main__':
    seconds=int(sys.argv[sys.argv.index('--seconds')+1]) if '--seconds' in sys.argv else 600
    magnets_only='--magnets-only' in sys.argv
    session=lt.session({'listen_interfaces':'0.0.0.0:49172','upload_rate_limit':32768,'download_rate_limit':0,'enable_dht':True})
    jobs=[]
    hashes=[('essential-written-material','0b8272f4830838212c24049fc88ea812ffe0a6a6'),('cbr-non-confidential','1D6AE72A795AF57DD28C6537A95E37D6ADB2F054')]
    for name,infohash in hashes:
        url='magnet:?xt=urn:btih:'+infohash
        catalog=(RAW/'scientolipedia/_provenance/catalog/entry.html').read_text()
        match=re.search(r'magnet:[^<"\s]*'+infohash+r'[^<"\s]*',catalog,re.I)
        transport=html.unescape(match.group(0)) if match else url
        params=lt.parse_magnet_uri(transport);out=RAW/'scientolipedia'/name;out.mkdir(parents=True,exist_ok=True);params.save_path=str(out)
        jobs.append(('scientolipedia',url,out,session.add_torrent(params)))
    for archive in (RAW/'galac-patra').glob('*.zip'):
        if magnets_only:continue
        out=RAW/'galac-patra'/archive.stem;out.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist():
                if not name.endswith('.torrent'):continue
                payload=z.read(name);meta=out/Path(name).name;meta.write_bytes(payload)
                params=lt.add_torrent_params();params.ti=lt.torrent_info(payload);params.save_path=str(out/'payload')
                jobs.append(('galac-patra',str(meta.relative_to(ROOT)),out,session.add_torrent(params)))
    start=time.monotonic();states=[]
    while time.monotonic()-start<seconds:
        states=[]
        for source,url,out,h in jobs:
            s=h.status()
            if s.has_metadata and not (out/'torrent-inventory.json').exists():
                ti=h.torrent_file();files=ti.files();inventory=[];priorities=[]
                for i in range(files.num_files()):
                    path=files.file_path(i);size=files.file_size(i)
                    skip=path.lower().endswith(('.mp3','.mp4','.avi','.wav','.flac','.m4a','.vob','.mkv'))
                    priorities.append(0 if skip else 4);inventory.append({'path':path,'bytes':size,'selected':not skip})
                h.prioritize_files(priorities)
                (out/'torrent-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
                (out/'metadata.torrent').write_bytes(lt.bencode(lt.create_torrent(ti).generate()))
            states.append(dict(source=source,url=url,metadata=s.has_metadata,peers=s.num_peers,seeds=s.num_seeds,progress=s.progress,downloaded=s.total_done,error=s.errc.message() if s.errc.value() else None))
        (ROOT/'0-get-data/torrent-progress.json').write_text(json.dumps(states,indent=2))
        print(json.dumps(states),flush=True)
        if all(h.status().is_finished for _,_,_,h in jobs):break
        time.sleep(15)
    for source,url,out,h in jobs:
        s=h.status();h.pause()
        row=dict(source_id=source,source_url=url,discovered_on='0-get-data/plan1.md',language='mixed',retrieved_at=datetime.now(timezone.utc).isoformat(),status='failed',kind='torrent-payload',bytes=0)
        if s.is_finished:row['status']='successful'
        elif s.total_done:row['status']='partial'
        row['error']=None if s.is_finished else (f'No torrent metadata/peers within {seconds}-second attempt' if not s.has_metadata else f'Torrent incomplete after {seconds}-second attempt')
        row['downloaded_bytes']=s.total_done;row['infohash']=str(h.info_hashes().v1);emit(row)
        complete_paths=set()
        if s.has_metadata:
            ti=h.torrent_file();files=ti.files();progress=h.file_progress();priorities=h.get_file_priorities()
            for i in range(files.num_files()):
                if priorities[i] and progress[i]==files.file_size(i):complete_paths.add(str(Path(ti.files().file_path(i))))
        for p in out.rglob('*'):
            if not p.is_file() or p.name.endswith(('.json','.torrent')):continue
            # Do not label partially written payload files as successful documents.
            if not s.is_finished:continue
            relative=str(p.relative_to(out if source=='scientolipedia' else out/'payload')) if source=='scientolipedia' or out/'payload' in p.parents else ''
            if relative not in complete_paths:continue
            digest=hashlib.sha256()
            with p.open('rb') as f:
                for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
            emit(dict(source_id=source,source_url=url,discovered_on='0-get-data/plan1.md',language='mixed',retrieved_at=row['retrieved_at'],status='successful',kind='document',local_path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=digest.hexdigest()))
    session.pause()
