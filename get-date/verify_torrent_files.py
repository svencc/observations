"""Recheck local torrent pieces offline and register individually complete files."""
import sys
sys.path.insert(0,'/tmp/observations-download-deps')
import libtorrent as lt
import hashlib
import json
import time
from datetime import datetime, timezone
from download_sources import ROOT, RAW, emit

if __name__=='__main__':
    session=lt.session({'listen_interfaces':'127.0.0.1:0','enable_dht':False,'enable_lsd':False,'enable_upnp':False,'enable_natpmp':False,'enable_outgoing_utp':False,'enable_outgoing_tcp':False,'enable_incoming_utp':False,'enable_incoming_tcp':False})
    jobs=[]
    inventories=list((RAW/'galac-patra').rglob('torrent-inventory.json'))+list((RAW/'scientolipedia').rglob('torrent-inventory.json'))
    for inv in inventories:
        out=inv.parent;meta=out/'metadata.torrent'
        if not meta.exists():continue
        entries=json.loads(inv.read_text())
        p=lt.add_torrent_params();p.ti=lt.torrent_info(str(meta));p.save_path=str(out if out.is_relative_to(RAW/'scientolipedia') else out/'payload');p.trackers=[]
        p.flags |= lt.torrent_flags.override_trackers
        p.flags &= ~lt.torrent_flags.auto_managed
        p.file_priorities=[4 if e['selected'] else 0 for e in entries]
        h=session.add_torrent(p);h.force_recheck();h.resume()
        jobs.append((h,entries,out))
    deadline=time.monotonic()+180
    time.sleep(2)
    while time.monotonic()<deadline and any(h.status().state in (lt.torrent_status.checking_files,lt.torrent_status.checking_resume_data) for h,_,_ in jobs):time.sleep(1)
    count=0;checks=[]
    for h,entries,out in jobs:
        h.pause();progress=h.file_progress();infohash=str(h.info_hashes().v1);files=[]
        for i,e in enumerate(entries):
            complete=bool(e['selected'] and e['bytes']>0 and progress[i]==e['bytes'])
            files.append(dict(e,verified_bytes=progress[i],complete=complete))
            if not complete:continue
            source='scientolipedia' if out.is_relative_to(RAW/'scientolipedia') else 'galac-patra'
            path=(out if source=='scientolipedia' else out/'payload')/e['path']
            if not path.is_file() or path.stat().st_size!=e['bytes']:continue
            digest=hashlib.sha256()
            with path.open('rb') as f:
                for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
            emit(dict(source_id=source,source_url='magnet:?xt=urn:btih:'+str(h.info_hash()),discovered_on=str((out/'metadata.torrent').relative_to(ROOT)),infohash=infohash,language='mixed',retrieved_at=datetime.now(timezone.utc).isoformat(),status='successful',kind='document',original_filename=path.name,local_path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,sha256=digest.hexdigest(),validation='libtorrent piece recheck, complete file'))
            count+=1
        (out/'verified-files.json').write_text(json.dumps(files,ensure_ascii=False,indent=2))
        h.save_resume_data()
        checks.append({'infohash':infohash,'complete_selected_files':sum(f['complete'] for f in files),'total_selected_files':sum(f['selected'] for f in files)})
    end=time.monotonic()+10
    while time.monotonic()<end:
        for alert in session.pop_alerts():
            if isinstance(alert,lt.save_resume_data_alert):
                for h,_,out in jobs:
                    if alert.handle==h:(out/'resume.fastresume').write_bytes(lt.write_resume_data_buf(alert.params))
        time.sleep(.2)
    print(json.dumps({'complete_files_added':count,'torrents':checks}),flush=True)
