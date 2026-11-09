# Projektvorgaben

## Auftrag und aktueller Stand

Die Datensammlung gilt auf ausdrücklichen Nutzerwunsch seit **09.11.2026 als vorerst abgeschlossen**. Festgehaltener Abschlussstand: [get-data/STATUS.md](get-data/STATUS.md). Projektübersicht: [README.md](README.md).

- Keine Downloads, Quellennetzwerktests, erneute Inventarisierung, Torrent-Verbindungen oder Wiederholungsabrufe automatisch starten. Eine weitere Beschaffung braucht einen neuen Nutzerauftrag.
- Offene Links, technische Blocker, fehlende Dateien und mögliche Dubletten sind dokumentierte Restpunkte, kein Auftrag zur automatischen Fortsetzung.
- Befehle in historischen Plänen, Übergaben und Skriptdokumentationen beschreiben Abrufwege; sie sind keine aktuelle Ausführungsanweisung.
- Der technische Laufstatus `finished_with_incomplete_queue` bleibt als historisches Ergebnis erhalten. Er widerspricht dem beschlossenen Abschluss der Beschaffungsphase nicht.
- Eine nächste Phase wie OCR, Konvertierung, Suche, Sortierung oder Dublettenbereinigung ist noch nicht beauftragt. Nicht eigenständig beginnen.

## Rohdaten und Herkunft erhalten

- Originale bleiben nach Quelle unter `raw-data/<quelle>/`. Nicht eigenständig löschen, umbenennen, umsortieren oder überschreiben, um vermeintliche Lücken oder Dubletten zu bereinigen.
- Auch `.part`-Dateien, unvollständige Torrent-Nutzdaten, Metadaten, Kataloge, `_provenance/` und `_handover/` erhalten. Teilbestände niemals als vollständig ausgeben.
- `get-data/download-manifest.jsonl` und die Quellenmanifeste nicht leeren oder rückwirkend umschreiben. Sie enthalten Herkunft, Größen, Hashes und historische Versuche.
- `raw-data/` und `.venv/` sind lokal; Git enthält den Rohdatenbestand nicht. Bei einem Umzug vollständige Rohdaten und `get-data/` separat sichern und ihre Geschwisterstruktur erhalten.
- Übergabe und Kopierinventar unter `raw-data/_handover/` stammen vom 07.11.2026. Sie decken die späteren Downloads nicht vollständig ab und sind kein aktueller Gesamtsnapshot.

## Aussagen und Prüfungen

- Erfolgreiche Abrufe, physische Dateien, Katalogseiten, Archive und eindeutige Werke unterscheiden. Dateizahlen und Gigabytes beweisen keine vollständige Werksammlung.
- Die Beschaffung ist organisatorisch abgeschlossen; eine bibliografisch vollständige LRH-/CBR-Sammlung ist nicht nachgewiesen.
- Ähnliche Dateinamen bedeuten nur Dublettenkandidaten. Unterschiedliche Hashes können andere Scans, OCR oder Metadaten desselben Werkes bedeuten. Fehlende Namensentsprechungen beweisen keine fehlenden Werke.
- Bei LRHmaterials den Dateityp aus Originalname, URL und Inhalt bestimmen; `.php` kann lokal ein PDF oder ZIP enthalten.
- Vor neuen Prüfungen ihre Schreibwirkung beachten: `validate_downloads.py` und `verify_torrent_files.py` können Manifestzeilen ergänzen; `write_handover.py --final` überschreibt Übergabeartefakte. Für Statusfragen vorhandene Ergebnisse lesen, diese Routinen nicht automatisch erneut ausführen.
- Historische Prozess-IDs niemals zum Stoppen oder Neustarten verwenden. Falls ein neuer Auftrag Prozesse betrifft, aktuelle Prozesse zuerst identifizieren.
- Keine Zugangsdaten, Cookies oder E-Mail-Codes in Dateien oder Git speichern. Keine Nachrichten, Registrierungen, Freigabeanfragen oder Käufe ohne ausdrücklichen Auftrag.

## Arbeitsweise

Python-Werkzeuge und Laufdokumentation liegen in `get-data/`; die Skripte bestimmen die Projektwurzel relativ zu ihrem Speicherort. Lokal ist `.venv/` vorhanden. Prüfungen dem tatsächlichen Änderungsumfang anpassen; reine Dokumentationsänderungen benötigen keine erneuten Downloads oder Bestandsprüfungen.

`get-data/download-manifest.jsonl` wird mit Git LFS versioniert; `.gitattributes` erhalten. Bei einem neuen Clone vor der Nutzung Git LFS installieren und den vollständigen Manifestinhalt mit `git lfs pull` beziehen. Ein LFS-Verweis ist kein lesbares JSONL-Manifest. Das Abrufen des versionierten Manifests ist keine erneute Materialbeschaffung. `raw-data/` bleibt separat und ist nicht durch LFS gesichert.
