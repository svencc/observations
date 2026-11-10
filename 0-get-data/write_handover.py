"""Create a self-contained migration handover; optionally wait for final stop.

No network requests, credentials or private sessions. The raw-data bundle also
contains the scripts and ledgers that otherwise live outside raw-data.
"""
import argparse
import collections
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit, urldefrag

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'raw-data'
BUNDLE=RAW/'_handover'

def atomic(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp');tmp.write_text(text);tmp.replace(path)

def records():
    data=(ROOT/'0-get-data/download-manifest.jsonl').read_bytes()
    if not data.endswith(b'\n'):data=data.rsplit(b'\n',1)[0]+b'\n'
    return [json.loads(line) for line in data.splitlines() if line.strip()]

def snapshot(final=False):
    rows=records();latest={};by_path={}
    for r in rows:
        if r['source_url'].startswith('magnet:'):
            key=(r['source_id'],'file',r['local_path']) if r.get('local_path') else (r['source_id'],r['source_url'].lower())
        else:key=(r['source_id'],r['source_url'])
        latest[key]=r
        if r.get('local_path'):by_path[r['local_path']]=r
    state=json.loads((ROOT/'0-get-data/run-state.json').read_text())
    partials=[]
    prior_file=BUNDLE/'partial-http-files.json'
    prior={(r['local_path'],r['bytes_on_disk']):r for r in json.loads(prior_file.read_text())} if prior_file.exists() else {}
    for p in RAW.rglob('*.part'):
        if BUNDLE in p.parents:continue
        item={'local_path':str(p.relative_to(ROOT)),'bytes_on_disk':p.stat().st_size,'status':'partial','note':'Interrupted HTTP download; not successful. extra_sources.py will restart its URL, not byte-resume it.'}
        old=prior.get((item['local_path'],item['bytes_on_disk']),{})
        if old.get('source_url'):
            for key in ('source_url','discovered_on','original_filename','note'):
                if key in old:item[key]=old[key]
        partials.append(item)
    atomic(BUNDLE/'partial-http-files.json',json.dumps(partials,ensure_ascii=False,indent=2))
    successful=[];missing=[]
    for path,r in by_path.items():
        if r['status']!='successful':continue
        p=ROOT/path
        if not p.is_file() or p.stat().st_size!=r.get('bytes'):
            missing.append({'local_path':path,'issue':'missing or size mismatch'});continue
        if r.get('sha256'):successful.append({'local_path':path,'bytes':r['bytes'],'sha256':r['sha256'],'source_id':r['source_id'],'source_url':r['source_url']})
    atomic(BUNDLE/'copy-verification.jsonl',''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in successful))
    atomic(BUNDLE/'file-presence-check.json',json.dumps({'checked_successful_paths':len(successful),'issues':missing},ensure_ascii=False,indent=2))
    if final:
        drive_items={}
        for filename in ('drive-inventory.json','extra-drive-inventory.json'):
            p=RAW/'sptv-drive/_provenance'/filename
            if p.exists():
                for entry in json.loads(p.read_text()):drive_items[entry[0]]=entry
        for item in partials:
            if not item['local_path'].startswith('raw-data/sptv-drive/'):continue
            filename=Path(item['local_path']).name
            matches=[entry for fid,entry in drive_items.items() if filename.startswith('file-'+fid+'__')]
            if len(matches)==1:
                fid,name,mime,parent=matches[0]
                item.update(source_url='https://drive.google.com/file/d/'+fid+'/view',discovered_on=parent,original_filename=name)
                item['note']='Interrupted Drive transfer; identity recovered from the saved Drive inventory. Check whether a successful complete copy already exists before restarting.'
        # Reconstruct the unique known frontier from locally stored catalogs.
        known={r['source_url']:r for r in latest.values() if r['source_id']=='lrhmaterials'}
        discovered={}
        for r in known.values():
            if r['status']!='successful' or r.get('kind')!='html' or not r.get('local_path'):continue
            for href in re.findall(r'href\s*=\s*[\"\x27]([^\"\x27]+)',(ROOT/r['local_path']).read_text(errors='replace'),re.I):
                u=urldefrag(urljoin(r.get('final_url',r['source_url']),html.unescape(href)))[0];p=urlsplit(u);q=parse_qs(p.query);target=q.get('download',[''])[0]
                if p.hostname not in ('www.lrhmaterials.com','lrhmaterials.com') or not p.path.endswith('materials.php'):continue
                if target and not target.lower().endswith(('.pdf','.doc','.docx','.txt','.djvu','.djv','.rtf','.epub','.zip','.torrent')):continue
                if any(x in u.lower() for x in ('french','spanish','italian','russian')):continue
                q={k:v for k,v in q.items() if k in ('dir','download')};u=urlunsplit((p.scheme,p.netloc,p.path,urlencode(q,doseq=True),''))
                if u not in known or known[u]['status']!='successful':discovered[u]={'source_url':u,'discovered_on':r['source_url'],'kind':'download' if target else 'directory'}
        atomic(BUNDLE/'pending-lrhmaterials.jsonl',''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in discovered.values()))
        candidates=collections.defaultdict(list)
        for url,item in discovered.items():candidates[hashlib.sha256(url.encode()).hexdigest()[:10]].append(item)
        added=0
        for item in partials:
            if not item['local_path'].startswith('raw-data/lrhmaterials/'):continue
            m=re.search(r'__([0-9a-f]{10})\.',Path(item['local_path']).name)
            matches=candidates.get(m.group(1),[]) if m else []
            if len(matches)!=1:continue
            target=matches[0];item.update(source_url=target['source_url'],discovered_on=target['discovered_on'])
            item['note']='Interrupted HTTP download; URL uniquely matched by the downloader URL hash against the saved catalog frontier. Restart from beginning; not successful.'
            existing=known.get(target['source_url'],{})
            if existing.get('status')=='partial' and existing.get('local_path')==item['local_path']:continue
            row=dict(source_id='lrhmaterials',source_url=target['source_url'],discovered_on=target['discovered_on'],language='unknown',retrieved_at=datetime.now(timezone.utc).isoformat(),status='partial',kind='document',local_path=item['local_path'],bytes=item['bytes_on_disk'],error='Interrupted by disk-space stop; .part retained; HTTP request must be restarted',url_recovery='unique SHA-256 URL-prefix match against saved catalogs')
            line=json.dumps(row,ensure_ascii=False)+'\n'
            for ledger in [ROOT/'0-get-data/download-manifest.jsonl',RAW/'lrhmaterials/_provenance/manifest.jsonl']:
                with ledger.open('a') as f:f.write(line)
            latest[('lrhmaterials',row['source_url'])]=row;added+=1
        atomic(BUNDLE/'partial-http-files.json',json.dumps(partials,ensure_ascii=False,indent=2))
        if added:subprocess.run([sys.executable,str(ROOT/'0-get-data/write_download_report.py')],cwd=ROOT,check=True)
    sources=collections.defaultdict(list)
    for r in latest.values():sources[r['source_id']].append(r)
    total=sum(r.get('bytes',0) for r in latest.values() if r['status']=='successful')
    now=datetime.now(timezone.utc).isoformat()
    stopped=any(t.get('state')=='stopped_low_disk_space' for t in state.get('tasks',[]))
    phase='FINALER ÜBERGABESTAND nach Ende der überwachten Prozesse' if final else 'VORLÄUFIG — der Download/Abschlusslauf arbeitet noch; wird automatisch ersetzt'
    lines=['# Übergabe: Beschaffung LRH / Captain Bill Robertson', '',f'**{phase}**', '',f'Erstellt: {now}.', '',
      '## Auftrag und Grenzen', '',
      'Englisches und deutsches LRH-/CBR-Material beschaffen. Originale nach Bezugsquelle unter `raw-data/<quelle>/` ablegen. Noch keine inhaltliche Sortierung, OCR, Markdown-Konvertierung oder Dublettenbereinigung. Manche unteilbaren Pakete sind mehrsprachig; einige Bild-/Audiodateien wurden bei der ersten Erfassung ebenfalls gesichert. Dateizahlen sind Kopien/Abrufe, keine eindeutigen Werke.', '',
      '## Aktueller Status', '',
      f"- Laufstatus: `{state.get('state')}`; letzter Supervisor-Stand: {state.get('updated_at')}.",
      f"- Speicherstopp bei weniger als 20 GiB frei: **{'ausgelöst' if stopped else 'im vorliegenden Status noch nicht ausgelöst'}**.",
      f'- Erfolgreich protokollierte Daten: {total/1e9:.1f} GB / {total/1024**3:.1f} GiB. Physischer Platzverbrauch kann wegen Teilübertragungen, Katalogen und Archiven abweichen.',
      f'- Gefundene HTTP-Teilübertragungen (`.part`): {len(partials)}. Diese sind **keine fertigen Dateien**.',
      f"- Eindeutig aus den gespeicherten Katalogen zugeordnete Quell-URLs dieser Teilübertragungen: {sum('source_url' in p for p in partials)} von {len(partials)}.",
      f'- Existenz-/Größenprüfung erfolgreicher Dateipfade: {len(successful)} mit SHA-256 im Kopierinventar; {len(missing)} Auffälligkeiten.', '',
      '| Quelle | successful | failed | partial | Dokumentdateien erfolgreich |', '| --- | ---: | ---: | ---: | ---: |']
    for source,rs in sorted(sources.items()):
        c=collections.Counter(r['status'] for r in rs)
        lines.append(f"| {source} | {c['successful']} | {c['failed']} | {c['partial']} | {sum(r['status']=='successful' and r.get('kind')=='document' for r in rs)} |")
    lines += ['', '## Unbedingt mit umziehen', '',
      'Den gesamten Ordner `raw-data/` kopieren, einschließlich aller versteckten/mit Unterstrich beginnenden Provenienz- und Übergabeordner, `.part`-Dateien, Torrent-Metadaten und Teilbestände. Nicht nur PDFs kopieren. `raw-data/` ist in Git ignoriert und reist **nicht** automatisch mit einem Git-Clone mit.', '',
      'Zusätzlich den Projektordner `0-get-data/` mitnehmen. Für den Fall, dass ausschließlich `raw-data/` übertragen wird, liegt dessen vollständiger Dokumentations-/Skriptstand auch unter `_handover/0-get-data/` in diesem Rohdatenordner. Das enthält insbesondere:', '',
      '- `download-manifest.jsonl`: Masterprotokoll mit relativen Dateipfaden, Originalnamen, Quell-URLs, Abrufzeiten, Größen und SHA-256. Nicht löschen oder durch ein leeres Protokoll ersetzen.',
      '- `downloaded.md`: lesbares Ergebnisprotokoll; `privat-data.md`: Logins und offene Nachprüfungen.',
      '- `plan1.md`, `goal1.md`, `run-state.json`, `manual-blockers.json`, Validierungs- und Drive-Inventarberichte sowie die tatsächlich verwendeten Python-Skripte.',
      '- `_handover/copy-verification.jsonl`: SHA-256 und Größe der als erfolgreich protokollierten Dateien für die Prüfung nach dem Kopieren.',
      '- `_handover/partial-http-files.json`: Liste unterbrochener HTTP-Dateien. Die zugehörige URL ist nicht in jedem Fall eindeutig rekonstruierbar; nicht aus Dateinamen erraten.',
      '- `_handover/pending-lrhmaterials.jsonl`: nach Abschluss aus gespeicherten Katalogen rekonstruierte, deduplizierte offene Links. Neue Verzeichnisse können weitere Links liefern; keine abschließende Gesamtliste aller Werke.', '',
      '## Verzeichnisstruktur auf dem neuen Rechner', '',
      '```text\nObservations/\n  0-get-data/                  # Originalordner oder Kopie aus raw-data/_handover/0-get-data/\n  raw-data/\n    ÜBERGABE.MD\n    _handover/\n    stss/\n    lrhmaterials/\n    freezone-de/\n    freezone-org/\n    sptv-drive/\n    ...\n```', '',
      'Die Skripte bestimmen die Projektwurzel relativ zu ihrem Speicherort. Deshalb `0-get-data/` und `raw-data/` als Geschwister erhalten. Alte absolute Pfade in historischen Notizen und alte Prozess-IDs gelten nur für den bisherigen Mac. **Diese PIDs auf dem neuen Rechner niemals übernehmen oder zum Beenden von Prozessen verwenden.**', '',
      '## Fortsetzung auf dem anderen Rechner', '',
      '1. Erst den finalen Übergabestand abwarten und dann kopieren. Bei vorherigem Kopieren anschließend einen zweiten Abgleich durchführen: laufende Downloads können Dateien und Protokolle noch verändern.',
      '2. Kopierte Dateien anhand `_handover/copy-verification.jsonl` prüfen. Dafür kann aus der wiederhergestellten Projektwurzel `python3 0-get-data/verify_migrated_copy.py` verwendet werden. Prüfsummen beziehen sich auf erfolgreiche Dateien; unvollständige Torrent-/HTTP-Dateien sind separat gekennzeichnet. Eine Größenprüfung allein ersetzt die SHA-256-Prüfung beim Umzug nicht.',
      '3. Python 3.9 oder neuer und `requests` installieren, vorzugsweise in einer neuen virtuellen Umgebung. Beispiel für macOS/Linux aus der Projektwurzel:', '',
      '```sh\npython3 -m venv .venv\n.venv/bin/python -m pip install requests\n.venv/bin/python 0-get-data/extra_sources.py\n```', '',
      'Unter Windows entsprechend `.venv\\Scripts\\python.exe` verwenden. `extra_sources.py` ist der Fortsetzungsweg für LRHmaterials und die Zusatzquellen. Es spielt vorhandene Kataloge erneut durch, verwendet das Masterprotokoll und überspringt erfolgreiche Dateien mit passender Größe. Abgebrochene HTTP-Downloads werden neu geladen, nicht byteweise fortgesetzt. Die frühere In-Memory-Warteschlange ist nicht direkt gespeichert; sie lässt sich aus Katalogen/Protokoll neu aufbauen.', '',
      '4. Beim Neustart eine eigene neue Prozess-ID ermitteln und gegebenenfalls `supervise_downloads.py --detach NAME=NEUE_PID` starten. Dessen bisherige Prozessprüfung nutzt `ps` und ist für macOS/Linux ausgelegt; unter Windows anpassen oder einen passenden Prozesswächter verwenden. Die 20-GiB-Reserve überwacht das Dateisystem der Projektwurzel. **Für das externe Laufwerk daher die gesamte Arbeitswurzel auf das externe Laufwerk legen**, nicht lediglich `raw-data/` dorthin verlinken.',
      '5. Berichte bei Bedarf mit `python 0-get-data/write_download_report.py` erneuern. Für die reine LRHmaterials-Fortsetzung sind `gdown` und `libtorrent` nicht nötig. Optional für Drive/Torrents: `gdown==5.2.2`, `libtorrent==2.1.1` in einer zum neuen System passenden Installation. Das bisherige `/tmp/observations-download-deps` wird nicht vorausgesetzt; regulär installierte Module können über den normalen Python-Pfad geladen werden.', '',
      '## Offene Quellen und bekannte Stolperstellen', '',
      '- **Google Drive / SPTV:** 20.436 Dateiverweise inventarisiert; 458 Dateien erfolgreich, 532 fehlgeschlagen, 19.446 noch nicht versucht. Der Lauf wurde nach Googles HTTP-403-„Sorry“-Sperrseite beendet. Nicht blind weiterbeschießen. Nach Wartezeit im Browser prüfen; es ist keine allgemeine Loginpflicht bestätigt. Beide Inventare unter `sptv-drive/_provenance/` erhalten. Die 50-Einträge-Grenze der öffentlichen HTML-Listen wurde mittels anonymer API-Paginierung gelöst.',
      '- **Sciento.org:** E-Mail-Code-Login nötig; es wurden keine Codes angefordert, Konten angelegt oder privaten Sitzungen gespeichert. Öffentliche Bibliothek noch nicht vollständig inventarisiert.',
      '- **Torrents:** Die großen LRH-RAR-Pakete sind unvollständig. `.torrent`, `metadata.torrent`, `resume.fastresume`, `torrent-inventory.json`, `verified-files.json` und Nutzdaten mitnehmen. Resume-Dateien können alte absolute Speicherpfade enthalten; auf neuem Rechner den Zielpfad ausdrücklich neu setzen und vorhandene Stücke prüfen lassen. Nicht durch einfaches Umbenennen als fertig ausgeben.',
      '- **CBR:** Kleines Scientolipedia-Paket: 60 ausgewählte Textdateien per Torrent-Stückprüfung vollständig bestätigt. Aus dem großen Galac-Patra-CBR-Torrent wurden 108 vollständige Einzeldateien bestätigt; darin auch Begleitbilder. Ganze Sammlung deshalb nicht als vollständig bezeichnen.',
      '- **SaentoWiki:** Englische HTML-Texte gesichert. Der verlinkte Mail.ru-Cloudordner enthielt ein Fotoalbum statt des angekündigten englischen Scanarchivs; aktueller Scanlink bleibt offen.',
      '- **AOGP:** Alter Pfad 404, neuer kostenloser Buchkatalog funktioniert ohne Anmeldung; 19 PDFs gespeichert.',
      '- **LRHmaterials-Dateinamen:** Viele Dateien heißen lokal `materials__<URL-Hash>.php`, obwohl ihr Inhalt PDF/DOC/ZIP ist. Originalnamen und MIME/URL im Masterprotokoll verwenden; nicht anhand der lokalen Endung aussortieren. Teilweise große ZIP-Pakete und anfänglich erfasste Medien tragen wesentlich zum Speicherverbrauch bei.',
      '- **Wichtig zur Dateiauswahl:** Der bisherige Filter lässt ZIP-Pakete auch unter `02-AUDIO_Materials` zu. Solche Pakete können komplette Audioserien statt Texte enthalten und erheblich größer als Einzel-PDFs sein. Die als „Dokumentdateien“ gezählten Downloads enthalten daher auch Archive; sie sind keine Zählung einzelner Textwerke. Bei der Fortsetzung die Auswahl großer Audio-ZIPs bewusst prüfen. Bestehende Rohdateien hier nicht ungefragt löschen oder umsortieren.',
      '- **Validierung:** Transport-SHA-256, Dateigrößen und PDF-Signaturen protokolliert. ZIP-Prüfung kann lange dauern. Beim LRH-Fotoarchiv wurde eine UTF-8-Dateinamenwarnung festgestellt; siehe `validation.json`. Keine pauschale Behauptung einer vollständigen inhaltlichen oder bibliografischen Prüfung.',
      '- **Keine Kommunikation versandt:** Betreiberkontakte stehen in `privat-data.md`; keine E-Mails, Freigabeanfragen, Registrierungen oder Käufe vorgenommen. Keine privaten Passwörter/Codes in die Übergabe schreiben.', '',
      '## Abschluss- und Kontrollartefakte', '',
      'Der finale Snapshot unter `_handover/0-get-data/` enthält die tatsächlichen Exit-/Validierungsstände. `_provenance/supervisor.log` und `_handover/abschluss.log` dokumentieren den Abschluss. Fehlgeschlagene oder ausstehende Quellen bleiben ausdrücklich offen. Die ursprüngliche Gesamtsumme ist wegen noch unerschlossener Verzeichnisse und Dubletten nicht abschließend bekannt.', '']
    validation=ROOT/'0-get-data/validation.json'
    if validation.exists():
        result=json.loads(validation.read_text())
        lines += ['## Konkrete Hinweise der Abschlussprüfung', '',f"Geprüfte Dateien: {result.get('checked_files',0)}. Hinweise: {len(result.get('issues',[]))}. Ungültige PDF-Antworten sind im Masterprotokoll als `failed` markiert; Originalantworten bleiben zur Nachprüfung erhalten. ZIP-Warnungen bedeuten, dass nicht pauschal von einem fehlerfrei entpackbaren Archiv ausgegangen werden darf.", '']
        for issue in result.get('issues',[]):lines.append(f"- `{issue['path']}`: {issue['issue']}")
    atomic(RAW/'ÜBERGABE.MD','\n'.join(lines))
    target=BUNDLE/'0-get-data';target.mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'0-get-data').iterdir():
        if p.is_file() and p.suffix in ('.md','.MD','.json','.jsonl','.py','.txt'):
            shutil.copy2(p,target/p.name)
    bundle_checks=[]
    for p in target.iterdir():
        if p.is_file():bundle_checks.append({'local_path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    atomic(BUNDLE/'documentation-checksums.json',json.dumps(bundle_checks,ensure_ascii=False,indent=2))
    logs=BUNDLE/'run-logs';logs.mkdir(parents=True,exist_ok=True)
    for p in Path('/tmp').glob('observations-*.log'):
        if p.is_file():shutil.copy2(p,logs/p.name)
    atomic(BUNDLE/'snapshot-status.json',json.dumps({'final':final,'created_at':now,'source_state':state,'partial_http_files':len(partials),'copy_check_files':len(successful),'presence_issues':len(missing)},ensure_ascii=False,indent=2))
    print(json.dumps({'handover_final':final,'successful_paths':len(successful),'http_partials':len(partials),'presence_issues':len(missing)}),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--watch',action='store_true');parser.add_argument('--detach',action='store_true');parser.add_argument('--final',action='store_true');args=parser.parse_args()
    if args.final:
        state=json.loads((ROOT/'0-get-data/run-state.json').read_text())
        if state.get('state') in ('running','finalizing'):raise SystemExit('Final snapshot requires a finished supervisor state')
        snapshot(final=True);return
    if args.detach:
        BUNDLE.mkdir(parents=True,exist_ok=True)
        with (BUNDLE/'abschluss.log').open('a') as log:
            p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--watch'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        print(json.dumps({'handover_watcher_pid':p.pid}));return
    snapshot(final=False)
    if args.watch:
        while True:
            state=json.loads((ROOT/'0-get-data/run-state.json').read_text())
            if state.get('state') not in ('running','finalizing'):break
            time.sleep(15)
        # The supervisor has finished validation/report generation before this copy.
        time.sleep(3)
        snapshot(final=True)

if __name__=='__main__':main()
