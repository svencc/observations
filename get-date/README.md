# Beschaffungslauf

- [Plan](plan1.md): Quellen und Ablage.
- [Downloadprotokoll](downloaded.md): tatsächliche Erfolge, Fehler und Teilübertragungen, je Abruf.
- [Private Zugänge / Nachprüfung](privat-data.md): offene Zugangsfragen, ohne Zugangsdaten.
- [Laufstatus](run-state.json): aktive Downloadprozesse und Abschlussstatus.
- [Maschinenlesbares Protokoll](download-manifest.jsonl): Herkunft, Dateipfad, Größe und SHA-256.

Die Rohdaten liegen im Projekt unter `raw-data/<quelle>/` und sind in `.gitignore` ausgeschlossen. Originalarchive und unfertige Torrent-Nutzdaten bleiben erhalten. Unfertige Archive sind kein erfolgreicher Materialbestand. Bei der ersten Katalogerfassung wurden auch einige Audio- und Bilddateien erfasst; diese sind im Protokoll als Begleitmedien gekennzeichnet. Die weitere Beschaffung konzentriert sich auf Texte und Dokumentpakete.

Der Hintergrund-Supervisor aktualisiert `downloaded.md` alle 30 Sekunden. Nach dem Ende seiner Downloadprozesse prüft er Torrent-Dateien und die lokalen Downloads erneut und schreibt den Abschlussstatus. `exited` bei einem Prozess bedeutet nur, dass der Prozess beendet ist; Dateierfolge stehen separat im Downloadprotokoll. Unter 20 GiB freiem Speicher beendet der Supervisor die aktiven Downloads und protokolliert dies.

Der Drive-Transfer wurde nach Googles HTTP-403-Sperrseite „Sorry“ gestoppt. Das ermittelte Inventar bleibt erhalten; die verbleibenden Einträge werden als ausstehend gezählt. Details stehen in `manual-blockers.json` und `privat-data.md`. Die übrigen offenen öffentlichen Downloads laufen weiter.

Laufprotokoll des Supervisors: `raw-data/_provenance/supervisor.log`. Inventare und Katalog-Snapshots liegen je Quelle unter `_provenance/`.

## Skripte

Die Python-Skripte enthalten die tatsächlich verwendeten Abrufwege. Sie erstellen keine Konten, verwenden keine privaten Nutzer-Cookies und versenden keine Nachrichten.

- `download_sources.py`: STSS, Freezone, Avalon und SaentoWiki; bereits erfolgreiche Dateien werden bei Wiederholung verwendet.
- `extra_sources.py`: zusätzliche öffentliche LRHmaterials-, Ron's-Org- und ESMB-Inhalte.
- `cloud_sources.py --drive-only`: öffentliche Drive-Ordner und Dateien.
- `drive_pagination.py`: zusätzliche Dateien hinter abgeschnittenen Drive-Listen.
- `drive_transfer.py`: führt beide Drive-Inventare zusammen und lädt ausstehende Dateien direkt über die getestete anonyme Download-API; bereits gespeicherte Dateien werden verwendet. Dies ist der laufende Downloadweg nach der Inventarisierung.
- `download_aogp.py`: aktueller kostenloser AOGP-Buchkatalog.
- `torrent_sources.py`: veröffentlichte Magnets und die drei Galac-Patra-Torrents. `--magnets-only --seconds 300` testet nur die beiden Magnets.
- `verify_torrent_files.py`: lokale Torrent-Prüfung ohne Peer-Verbindungen; nur vollständige Einzeldateien zählen als erfolgreich.
- `validate_downloads.py`: Existenz/Größe, PDF-Signaturen, ZIP-Prüfung und Kennzeichnung von Begleitmedien.
- `write_download_report.py`: Markdown-Bericht aus den tatsächlichen Ergebnissen neu erstellen. `privat-data.md` bleibt bei späteren Aufrufen erhalten, damit man dort eigene Notizen ergänzen kann.

Abhängigkeiten für einen späteren Neustart: Python 3.9+, `requests`; für Drive/Torrents zusätzlich `gdown==5.2.2` und `libtorrent==2.1.1`. Diese Zusatzpakete wurden temporär nach `/tmp/observations-download-deps` installiert. Falls das Verzeichnis später fehlt, müssen die Pakete dort erneut installiert werden. Keine Passwörter oder Sitzungscookies in Skripte oder Protokolle eintragen.
