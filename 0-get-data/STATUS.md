# Abschlussstand der Datensammlung

**Festgehalten am 09.11.2026. Die Datensammlung gilt auf Nutzerwunsch vorerst als abgeschlossen. Keine automatische Fortsetzung.**

Dies ist der beschlossene Abschluss der Beschaffungsphase, kein Nachweis einer vollständigen Gesamtedition aller LRH-/CBR-Werke. Eine nächste Verarbeitungsphase ist noch nicht beauftragt.

## Abgeschlossener Lauf

Der Fortsetzungslauf vom 08.–09.11.2026 endete einschließlich Abschlussprüfung am **09.11.2026 um 03:21 Uhr Europe/Berlin** (02:21 UTC). Downloadprozess und Supervisor endeten mit Exitcode 0. Beim abschließenden Prozesscheck liefen keine Beschaffungs- oder Prüfprozesse mehr.

| Kennzahl | Abschlussstand |
| --- | ---: |
| Erfolgreich protokollierte Daten insgesamt | 555,4 GB (dezimal) |
| Im Fortsetzungslauf neu erfolgreich protokolliert | 368,4 GB (dezimal) |
| Dateien in der lokalen Abschlussvalidierung | 91.731 |
| Davon als `document` eingeordnet | 81.329 |
| Weitere Arten | 8.522 HTML, 1.717 Kataloge, 118 Begleitbilder, 45 Begleitmedien |
| Freier Speicher beim Abschluss | ca. 1,30 TiB auf dem 2-TB-Laufwerk |
| Durch Internetunterbrechung gescheiterte und nachgeholte Abrufe | 33 von 33 erfolgreich |

Diese Zahlen zählen protokollierte Daten und Dateien, keine eindeutigen Werke. Archive können viele Dokumente oder weitere Medien enthalten; mehrere Quellen können sich überschneiden. Physischer Speicherverbrauch kann von der Summe erfolgreicher Dateigrößen abweichen.

## Prüfung und Warnungen

- Vor der Fortsetzung wurden alle **21.801 übernommenen erfolgreichen Dateien** anhand des Übergabeinventars auf Größe und SHA-256 geprüft: keine Abweichungen. Das deckt den damaligen Bestand ab, nicht alle später hinzugekommenen Dateien.
- Torrent-Stückprüfung und lokale Abschlussvalidierung endeten mit Exitcode 0. Die lokale Validierung prüfte Existenz, Größen, PDF-Signaturen und ZIP-Inhalte; sie ist keine vollständige inhaltliche oder bibliografische Prüfung.
- Zwei bekannte Archivwarnungen bleiben in [validation.json](validation.json): UTF-8-Dateinamenproblem bei `raw-data/lrhmaterials/materials__729b341fa1.php` und beschädigter ZIP-Eintrag `Solo\.DS_Store` bei `raw-data/lrhmaterials/materials__5113a28bc5.php`.
- Unvollständige HTTP-/Torrent-Bestände bleiben erhalten und gelten nicht als fertige Dokumente.

## Bewusst offen gelassene Bestände

### LRHmaterials

Von den 20.072 Dateilinks der ursprünglichen offenen Übergabeliste sind **20.006 erfolgreich**, **60 fehlgeschlagen**, **6 unversucht**. Das entspricht 99,7 % Erfolg für diese feste Liste, nicht für alle Quellen oder Werke. Zusätzlich wurden weitere Kataloglinks verarbeitet.

Bei der anschließenden Analyse wurde ein zu breiter Audio-ZIP-Filter korrigiert. Er hatte auch Textpakete im gemischten Verzeichnis `Audios-Videos-PDFs_and_Docs` ausgeschlossen. Nach der Korrektur wurde kein neuer Downloadlauf gestartet. Die sechs unversuchten Pakete bleiben offen:

- `Transcripts_Tapes_1-50_and_Booklet.zip`
- `00-indexes.zip`
- `0_HCOPL_Update_Packs_1974-1983_Entire-Folder.zip`
- `Management_Series-doc_files.zip`
- `MGMT DICT-tiff images.zip`
- `OEC SUBJECT INDEX.zip`

### Google Drive / SPTV

20.436 Dateiverweise inventarisiert: 458 erfolgreich gespeichert, 532 fehlgeschlagen, 19.446 unversucht. Insgesamt fehlen **19.978 inventarisierte Dateien**. Der frühere HTTP-403-Blocker bleibt dokumentiert; kein erneuter Massentransfer wurde gestartet.

Der Namensabgleich ergab 3.385 normalisierte Namenstreffer und 172 weitere Treffer nach Entfernen des OCR-Vermerks. Für 16.421 fehlende Dateien gibt es keine entsprechende Namenszuordnung. **Diese 3.557 Treffer sind Dublettenkandidaten, keine nachgewiesenen identischen Dateien.** Für fehlende Drive-Dateien liegen im Inventar weder Größen noch Prüfsummen vor. Anders benannte Dateien oder Archivmitglieder können bereits vorhandene Werke enthalten.

### Weitere Quellen

Große LRH-Torrents bleiben teilweise unvollständig. Sciento benötigt einen E-Mail-Code-Login; das öffentliche Bibliotheksinventar ist nicht vollständig erfasst. Der angekündigte englische SaentoWiki-Scanbestand bleibt offen. Weitere Fehler und Zugangsfragen stehen in den vorhandenen Berichten. Diese Punkte sind zurückgestellt und lösen keinen automatischen Folgeauftrag aus.

## Maßgebliche Artefakte

- [Downloadbericht](downloaded.md) und [Mastermanifest](download-manifest.jsonl): tatsächliche Abrufe und Herkunft.
- [Fortsetzungsstatus](continuation-state.json): technischer Ablauf `finished`, beide Exitcodes 0.
- [Supervisorstatus](run-state.json): `finished_with_incomplete_queue` wegen offener Quellen, insbesondere Drive; historische technische Kennzeichnung bleibt unverändert.
- [Validierung](validation.json), [Netzwerk-Wiederholung](network-retry-state.json), [Blocker](manual-blockers.json) und [Zugangsfragen](privat-data.md).
- [Überschneidungsanalyse](overlap-assessment/README.md), [Zusammenfassung](overlap-assessment/summary.json) und Kandidatenlisten.
- Rohprotokolle: `raw-data/_provenance/continuation.log`, `extra-sources-continuation.log`, `network-retry.log`; Kataloge und Quellenmanifeste unter den jeweiligen `_provenance/`-Ordnern.

Die alte Übergabe `raw-data/ÜBERGABE.MD`, das Kopierinventar und der Skriptsnapshot unter `raw-data/_handover/` dokumentieren den Stand vom 07.11.2026 und umfassen nicht die gesamte spätere Sammlung. Bei einer später beauftragten Sicherung den vollständigen aktuellen Rohdatenbestand und `0-get-data/` gemeinsam sichern; Git allein genügt nicht.

Am 09.11.2026 wurde auf Nutzerwunsch der Beschaffungsordner in `get-data/` umbenannt, einschließlich der Übergabekopie unter `raw-data/_handover/get-data/`. Pfadreferenzen in Skripten, Dokumentation, Herkunftsmanifesten, Laufprotokollen und IDE-Konfiguration wurden entsprechend korrigiert. Die Dokumentationsprüfsummen der Übergabekopie wurden neu berechnet. Heruntergeladene Originaldateien, ihre Größen und SHA-256 sowie historische Abrufzeiten und Ergebnisse wurden dadurch nicht verändert. Die Beschaffung bleibt abgeschlossen.

Am 10.11.2026 wurde der Projektordner auf Nutzerwunsch von `get-data/` in `0-get-data/` umbenannt. Aktuelle Skript-, Dokumentations- und Git-LFS-Verweise wurden angepasst. Historische Manifeste und die Übergabekopie unter `raw-data/_handover/get-data/` bleiben unverändert; deren alte Pfadangaben beziehen sich auf den damaligen Stand.
