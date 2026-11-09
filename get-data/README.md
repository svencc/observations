# Beschaffungslauf

**Stand 09.11.2026: Datensammlung auf Nutzerwunsch vorerst abgeschlossen. Keine weiteren Abrufe automatisch starten.** Der letzte Lauf einschließlich Abschlussprüfung endete regulär um 03:21 Uhr Europe/Berlin. Festgehaltener Bestand und offene Restpunkte: [STATUS.md](STATUS.md). Verbindliche Agentenvorgaben: [../AGENTS.md](../AGENTS.md). Die folgenden Abläufe sind technische Dokumentation für einen später ausdrücklich beauftragten Neustart.

- [Plan](plan1.md): Quellen und Ablage.
- [Downloadprotokoll](downloaded.md): tatsächliche Erfolge, Fehler und Teilübertragungen, je Abruf.
- [Private Zugänge / Nachprüfung](privat-data.md): offene Zugangsfragen, ohne Zugangsdaten.
- [Laufstatus](run-state.json): aktive Downloadprozesse und Abschlussstatus.
- [Maschinenlesbares Protokoll](download-manifest.jsonl): Herkunft, Dateipfad, Größe und SHA-256.

Die Rohdaten liegen im Projekt unter `raw-data/<quelle>/` und sind in `.gitignore` ausgeschlossen. Originalarchive und unfertige Torrent-Nutzdaten bleiben erhalten. Unfertige Archive sind kein erfolgreicher Materialbestand. Bei der ersten Katalogerfassung wurden auch einige Audio- und Bilddateien erfasst; diese sind im Protokoll als Begleitmedien gekennzeichnet. Die abgeschlossene Fortsetzung konzentrierte sich auf Texte und Dokumentpakete.

Der Hintergrund-Supervisor aktualisiert `downloaded.md` alle 30 Sekunden. Nach dem Ende seiner Downloadprozesse prüft er Torrent-Dateien und die lokalen Downloads erneut und schreibt den Abschlussstatus. `exited` bei einem Prozess bedeutet nur, dass der Prozess beendet ist; Dateierfolge stehen separat im Downloadprotokoll. Unter 20 GiB freiem Speicher beendet der Supervisor die aktiven Downloads und protokolliert dies.

Der Drive-Transfer wurde nach Googles HTTP-403-Sperrseite „Sorry“ gestoppt. Das ermittelte Inventar bleibt erhalten; die verbleibenden Einträge werden als ausstehend gezählt. Details stehen in `manual-blockers.json` und `privat-data.md`. Der damalige Downloadlauf wurde am 07.11.2026 bei Erreichen der Speicherreserve ebenfalls gestoppt. Die Übergabe unter `raw-data/ÜBERGABE.MD` und ihr Skriptsnapshot dokumentieren diesen historischen Stand.

Am 08.–09.11.2026 wurde die Beschaffung auf dem größeren Laufwerk fortgesetzt. Der damalige Einstieg war `.venv/bin/python get-data/resume_acquisition.py --detach`. Der Ablauf prüft zuerst alle 21.801 übernommenen erfolgreichen Dateien auf Größe und SHA-256. Nur bei erfolgreicher Prüfung startet er `extra_sources.py` und den Supervisor mit neu ermittelter Prozess-ID. `continuation-state.json` zeigt die aktuelle Phase; während der Kopierprüfung ist `run-state.json` noch der historische Supervisorstand. Ein Prozess-Lock verhindert doppelte Fortsetzungsläufe. Die Protokolle stehen unter `raw-data/_provenance/continuation.log`, `extra-sources-continuation.log` und `raw-data/_handover/migration-verification.log`.

Die gespeicherte offene LRHmaterials-Warteschlange und unterbrochene Dokumentlinks werden vor den Katalogeinstiegen eingereiht. Reine Audio-ZIP-Pakete im Bereich `02-AUDIO_Materials` sind standardmäßig zurückgestellt; erkennbare Transkript-/Textpakete und einzelne Dokumente bleiben zugelassen. Am 09.11.2026 wurde ein zu breiter Filter korrigiert, der auch ZIPs im gemischten Ordner `Audios-Videos-PDFs_and_Docs` ausgeschlossen hatte. Sechs relevante Pakete sind dadurch weiterhin offen; siehe `overlap-assessment/README.md`. `extra_sources.py --include-audio-archives` erlaubt bei einem bewusst gewählten separaten Lauf auch diese ZIPs. Vorhandene Rohdaten und Teilbestände bleiben erhalten. Google Drive wird durch diesen Fortsetzungsweg nicht erneut massenhaft abgerufen. Die 20-GiB-Reserve bleibt aktiv.

Laufprotokoll des Supervisors: `raw-data/_provenance/supervisor.log`. Inventare und Katalog-Snapshots liegen je Quelle unter `_provenance/`.

## Skripte

Die Python-Skripte enthalten die tatsächlich verwendeten Abrufwege. Sie erstellen keine Konten, verwenden keine privaten Nutzer-Cookies und versenden keine Nachrichten.

- `download_sources.py`: STSS, Freezone, Avalon und SaentoWiki; bereits erfolgreiche Dateien werden bei Wiederholung verwendet.
- `extra_sources.py`: zusätzliche öffentliche LRHmaterials-, Ron's-Org- und ESMB-Inhalte.
- `cloud_sources.py --drive-only`: öffentliche Drive-Ordner und Dateien.
- `drive_pagination.py`: zusätzliche Dateien hinter abgeschnittenen Drive-Listen.
- `drive_transfer.py`: führt beide Drive-Inventare zusammen und lädt ausstehende Dateien direkt über die getestete anonyme Download-API; bereits gespeicherte Dateien werden verwendet. Dies war der verwendete Downloadweg nach der Inventarisierung.
- `download_aogp.py`: aktueller kostenloser AOGP-Buchkatalog.
- `torrent_sources.py`: veröffentlichte Magnets und die drei Galac-Patra-Torrents. `--magnets-only --seconds 300` testet nur die beiden Magnets.
- `verify_torrent_files.py`: lokale Torrent-Prüfung ohne Peer-Verbindungen; nur vollständige Einzeldateien zählen als erfolgreich.
- `validate_downloads.py`: Existenz/Größe, PDF-Signaturen, ZIP-Prüfung und Kennzeichnung von Begleitmedien.
- `write_download_report.py`: Markdown-Bericht aus den tatsächlichen Ergebnissen neu erstellen. `privat-data.md` bleibt bei späteren Aufrufen erhalten, damit man dort eigene Notizen ergänzen kann.

Abhängigkeiten für einen späteren Neustart: Python 3.9+, `requests`; für Drive/Torrents zusätzlich `gdown==5.2.2` und `libtorrent==2.1.1`. Für die Fortsetzung sind `requests==2.32.5` und `libtorrent==2.1.1` lokal unter `.venv/` installiert; `gdown` wurde für den abgeschlossenen HTTP-Lauf nicht benötigt. Einige historische Skripte berücksichtigen zusätzlich `/tmp/observations-download-deps`, fallen aber auf regulär installierte Module zurück. Keine Passwörter oder Sitzungscookies in Skripte oder Protokolle eintragen.
