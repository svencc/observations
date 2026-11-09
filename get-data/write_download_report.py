"""Render the requested Markdown reports from actual transfer results."""
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from inspect_sources import ROOT

def esc(s):return str(s or '').replace('|','\\|').replace('\n',' ')

def main():
    records=[]
    p=ROOT/'get-data/download-manifest.jsonl'
    if p.exists():records=[json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    latest={}
    for r in records:
        if r['source_url'].startswith('magnet:'):
            key=(r['source_id'],'torrent-file',r['local_path']) if r.get('local_path') else (r['source_id'],r['source_url'].lower(),'')
        else:key=(r['source_id'],r['source_url'],'')
        latest[key]=r
    sources=defaultdict(list)
    for r in latest.values():sources[r['source_id']].append(r)
    now=datetime.now(timezone.utc).isoformat()
    total=sum(r.get('bytes',0) for r in latest.values() if r['status']=='successful')
    lines=['# Downloadprotokoll', '',f'Aktualisiert: {now}.', '',
        'Statuswerte: **successful** = lokal gespeichert und geprüft; **failed** = Abruf oder Formatprüfung fehlgeschlagen; **partial** = nur teilweise übertragen. Eine erfolgreiche Katalog-/HTML-Sicherung ist kein Beleg für heruntergeladene verlinkte PDFs oder komplette Archivpakete.', '',
        'Die Datei wird aus den tatsächlichen Ergebnissen erstellt. Solange `run-state.json` laufende Prozesse ausweist, ist sie ein Zwischenstand. Zugangsthemen stehen in [privat-data.md](privat-data.md).', '',
        f'Erfolgreich protokollierte Bytes: **{total/1024**3:.3f} GiB** (einschließlich HTML und Katalogen, ohne unvollständige Torrent-Dateien).', '',
        '| Quelle | successful | failed | partial | Davon Binärdokumente / Pakete |', '| --- | ---: | ---: | ---: | ---: |']
    for source,rows in sorted(sources.items()):
        c=Counter(r['status'] for r in rows)
        lines.append(f"| {source} | {c['successful']} | {c['failed']} | {c['partial']} | {sum(r['status']=='successful' and r.get('kind')=='document' for r in rows)} |")
    lines += ['', '## Einordnung der Ergebnisse', '',
        '- **STSS:** Der öffentliche JSON-Katalog `https://stss.nl/api/materials.php` enthält 458 englische und 329 deutsche Einträge. Der Abruf verwendet beide Sprachbereiche. Alte Direktlinks aus dem Plan werden zusätzlich versucht.',
        '- **Freezone / Ron\'s Org:** HTML-Seiten und tatsächlich verlinkte Dokumente bleiben als Rohdateien erhalten; Übersichten und Kapitel können sich inhaltlich überschneiden.',
        '- **Project Avalon:** Der öffentlich verlinkte Scientology-Bereich wird als Quellenbestand gesichert; darin können auch ergänzende Fremdautoren stehen.',
        '- **SaentoWiki:** Englische Textseiten und Kataloge. Der aktuell verlinkte Mail.ru-Ordner enthält nach bisher sichtbarer Struktur russisch benannte Materialien; das frühere Versprechen eines großen englischen Scanarchivs ist damit nicht bestätigt.',
        '- **Galac-Patra:** Die drei kleinen ZIPs enthalten jeweils eine `.torrent`-Datei. Ein erfolgreicher ZIP-Download bedeutet ausdrücklich noch keinen Download der darin beschriebenen GB-Bibliothek. Die ZIP-Integritätsprüfung war erfolgreich.',
        '- **BitTorrent:** Eigentliche Nutzdaten werden separat als `torrent-payload` protokolliert. Ein unvollständiger Transfer zählt nicht als fertiges Dokument; Metadaten und Inventare bleiben zur späteren Wiederaufnahme erhalten.',
        '- **SPTV / Drive:** Dateinamen und IDs aus aktuell öffentlich lesbaren Unterordnern verwenden. Sieben alte Direktordner liefern 404. Die Begrenzung der HTML-Listen auf 50 Einträge wurde durch getestete anonyme API-Paginierung überwunden. Weitere Unterordner und Dateien werden darüber erfasst; Stand in `drive-pagination-result.json` und den Inventaren unter `raw-data/sptv-drive/_provenance/`.',
        '- **LRHmaterials:** Entgegen der alten Gesprächsnotiz ist die Website beim aktuellen Abruf erreichbar. Öffentlich angebotene Text-/Dokumentdateien werden mitgenommen. Im ersten Abruf wurden auch einige öffentlich verlinkte Audiodateien erfasst; weitere Abrufe beschränken sich auf Textdateien und Transkripte.',
        '- **AOGP:** Aktueller kostenloser Buchkatalog: https://www.ao-gp.org/scientology-free-books-pdfs-by-l-ron-hubbard . Die dort verlinkten 19 englischen PDFs sind ohne Anmeldung erhältlich. Der alte Bücherpfad liefert weiterhin 404.', '',
        'Prüfsummen, Abrufzeiten, Dateigrößen und Herkunftslinks stehen vollständig in [download-manifest.jsonl](download-manifest.jsonl), zusätzlich je Quelle unter `raw-data/<quelle>/_provenance/manifest.jsonl`. Rohdaten sind von Git ausgeschlossen.', '',
        '## Zugriffstests der weiteren Quellen', '',
        '| Quelle / URL | Ergebnis | Hinweis |','| --- | --- | --- |']
    probe=ROOT/'get-data/archive-probes.json'
    if probe.exists():
        for r in json.loads(probe.read_text()):
            status=r.get('http_status');hint=r.get('error') or ('; '.join(r.get('title',[])))
            if r['source']=='sciento':hint='Loginseite erreichbar; Bibliotheksdownload benötigt E-Mail-Code.'
            outcome='successful (Seite)' if status==200 else 'failed'
            lines.append(f"| [{esc(r['source'])}]({r['url']}) | {outcome}; HTTP {status or '—'} | {esc(hint)} |")
    state=ROOT/'get-data/run-state.json'
    if state.exists():
        obj=json.loads(state.read_text())
        lines += ['', '## Laufstatus', '', f"Status: **{obj.get('state','unknown')}**. Aktualisiert: {obj.get('updated_at','—')}."]
        for task in obj.get('tasks',[]):lines.append(f"- {task.get('name')}: {task.get('state')}")
        coverage=obj.get('drive_coverage')
        if coverage:lines += ['',f"Drive-Inventar: **{coverage['inventoried_files']}** Dateien; **{coverage['files_attempted']}** bereits versucht; **{coverage['not_yet_attempted']}** noch ausstehend. Erfolgreiche und fehlgeschlagene Versuche stehen getrennt in der Quellentabelle."]
    pagination=ROOT/'get-data/drive-pagination-result.json'
    if pagination.exists():
        obj=json.loads(pagination.read_text())
        lines += ['',f"Drive-Paginierung: **{len(obj.get('resolved',[]))}** Ordner vollständig aufgelistet; **{obj.get('extra_files',0)}** zusätzliche Dateiverweise; **{len(obj.get('failed',[]))}** Listenfehler."]
    blockers=ROOT/'get-data/manual-blockers.json'
    if blockers.exists():
        lines += ['', '## Blockierte Quellen / ausstehende Dateien', '']
        for source,item in json.loads(blockers.read_text()).items():
            lines.append(f"- **{source}: {item['status']}** — {item['reason']} {item['next_step']}")
    validation=ROOT/'get-data/validation.json'
    if validation.exists():
        obj=json.loads(validation.read_text())
        lines += ['',f"Letzte lokale Prüfung: **{obj.get('checked_files',0)}** Dateien geprüft; **{len(obj.get('issues',[]))}** Hinweise."]
        for item in obj.get('issues',[]):lines.append(f"- `{esc(item.get('path'))}`: {esc(item.get('issue'))}")
    for filename in ['drive-issues.json','cloud-issues.json']:
        file=ROOT/'get-data'/filename
        if file.exists():
            issues=json.loads(file.read_text())
            lines += ['',f'### Hinweise aus {filename}', '']
            if filename=='drive-issues.json':lines.append('Diese Liste dokumentiert die ursprüngliche HTML-Grenze. Erfolgreich paginierte Ordner sind in `drive-pagination-result.json` als aufgelöst erfasst.')
            if not issues:lines.append('Keine zusätzlichen Probleme protokolliert.')
            for r in issues:lines.append(f"- [{esc(r.get('name') or r.get('url'))}]({r.get('url')}): {esc(r.get('issue'))}")
    for source,rows in sorted(sources.items()):
        lines += ['',f'## {source}: einzelne Abrufe', '', '| Status | Typ | Sprache | Datei / Ablage | Quelle | Fehler |','| --- | --- | --- | --- | --- | --- |']
        for r in sorted(rows,key=lambda r:r['source_url']):
            local=r.get('local_path');name=r.get('original_filename') or (Path(local).name if local else '—')
            file=f'[{esc(name)}](../{quote(local,safe="/")})' if local else esc(name)
            url=r['source_url'];label='Magnet' if url.startswith('magnet:') else 'URL'
            lines.append(f"| {r['status']} | {r.get('kind','—')} | {r.get('language','unknown')} | {file} | [{label}]({url}) | {esc(r.get('error'))} |")
    output=ROOT/'get-data/downloaded.md'
    tmp=output.with_suffix('.md.tmp');tmp.write_text('\n'.join(lines)+'\n');tmp.replace(output)
    private='''# Zugänge und Punkte zur gemeinsamen Nachprüfung

Hier stehen nur Zugangsvoraussetzungen und offene Fragen, keine Passwörter, Codes oder Cookies. Technische Abruffehler und Einzelstatus stehen in [downloaded.md](downloaded.md).

## Tatsächlich privater Zugang erforderlich

| Quelle | Was fehlt | Vorgehen |
| --- | --- | --- |
| [Sciento.org](https://sciento.org/login?next=%2Fsearch%2F) | Vom Nutzer kontrollierte E-Mail-Adresse bzw. angemeldete Sitzung. Die Bibliothek verwendet einen per E-Mail versandten Login-Code. | Nutzer übernimmt die Anmeldung oder stellt eine geeignete Sitzung bereit. Es wurde kein Code angefordert und kein Konto angelegt. Ohne Login kein vollständiges Bibliotheksinventar möglich. |

## Nachprüfen; privater Zugang bislang nicht als nötig belegt

- **SPTV / Google Drive:** Sieben der neun direkt verlinkten Ordner liefern HTTP 404. Das kann ein veralteter Link oder eine beschränkte Freigabe sein; daraus lässt sich keine sichere Loginpflicht ableiten. Zwei Ordner sind anonym lesbar, und deren aktuelle Unterordner werden erfasst. Bei fehlenden Beständen aktuelle Links beim Eigentümer erfragen oder mit eigenem Google-Konto prüfen. Bisher keine Freigabeanfrage gestellt.
- **Drive-Downloadlimits:** Falls eine Datei trotz öffentlicher Liste nicht herunterladbar ist, Fehlermeldung im Downloadprotokoll prüfen. Ein eigenes Konto hilft nicht zwangsläufig bei Quoten oder gesperrten Downloads. Betroffene Dateien werden nicht als erfolgreich markiert.
- **Mail.ru / Yandex:** Öffentliche Metadaten sind ohne Login erreichbar. Downloadversuche und etwaige Fehler stehen im Downloadprotokoll. Nicht pauschal ein Konto anlegen; zuerst den konkreten Fehler prüfen.
- **SaentoWiki-Scanarchiv:** Der verlinkte Cloudbestand entspricht nach aktuell sichtbarer Struktur nicht dem angekündigten englischen Großarchiv. Einen aktuellen EN-/DE-Scanlink suchen oder beim Betreiber erfragen. Ein Login ist dafür bislang nicht als Lösung belegt.
- **ESMB:** Der Thread ist öffentlich lesbar. Fehlende Anhänge mit 404 können gelöscht sein; ein Forenkonto ist nicht automatisch die Lösung. Gültige Ersatzlinks suchen, bei einer ausdrücklichen Loginmeldung eigenes Konto prüfen.
- **AOGP:** Der alte Bücherpfad liefert 404; der aktuelle kostenlose Katalog wurde gefunden: <https://www.ao-gp.org/scientology-free-books-pdfs-by-l-ron-hubbard>. Dessen 19 PDFs sind ohne Login heruntergeladen. Für diese Bücher sind keine privaten Daten nötig. Eine kostenpflichtige Mitgliedschaft für weitere Angebote wurde nicht abgeschlossen.
- **Torrents:** Bei fehlenden Peers/Metadaten ist kein Passwort erforderlich. Später erneut versuchen oder einen aktiven Spiegel suchen. Die kleinen Galac-Patra-ZIPs sind nur Metadatencontainer, nicht die Materialbibliotheken selbst.

## Falls wir Betreiber kontaktieren wollen

- STSS / Ron's Org: `theta@ronsorg.ch` — aktueller Index oder Spiegel.
- Freezone.de: <https://www.freezone.de/kontakt/> — fehlende CBR-Texte oder Transkripte.
- Galac-Patra / Timecops: `timecops@mail.ru` — aktive EN-/DE-Spiegel oder Seeds.
- Historische Excal-Kontaktadresse aus goal1.md: `Independent_scientologist@hotmail.com` — unbestätigte Altspur; keine Anfrage verschickt.

Es wurden keine Nachrichten versandt, Registrierungen durchgeführt oder privaten Zugangsdaten gesucht. Öffentliche Downloads laufen unabhängig von diesen offenen Punkten weiter.
'''
    private_path=ROOT/'get-data/privat-data.md'
    if not private_path.exists():private_path.write_text(private)
    print(json.dumps({'records':len(records),'latest':len(latest),'bytes_successful':total,'sources':{s:dict(Counter(r['status'] for r in rows)) for s,rows in sources.items()}}))

if __name__=='__main__':main()
