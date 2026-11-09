# Fehlende Bestände und mögliche Überschneidungen

Stand: 09.11.2026. Auswertung mit `assess_missing_overlap.py`, ausschließlich anhand der gespeicherten Inventare und des validierten Manifests. Keine Rohdateien gelöscht, umsortiert oder entpackt; keine OCR oder Inhaltskonvertierung durchgeführt.

## Google Drive

20.436 inventarisierte Dateiverweise, davon 458 erfolgreich gespeichert. Offen sind **19.978**, bestehend aus 19.446 unversuchten und 532 fehlgeschlagenen Abrufen.

| Abgleich mit erfolgreichen Dokumenten anderer Quellen | Fehlende Drive-Dateien |
| --- | ---: |
| Gleicher normalisierter Dateiname einschließlich Endung | 3.385 |
| Gleicher Name nach zusätzlichem Entfernen des OCR-Vermerks | 172 |
| Kein entsprechender Dateiname | 16.421 |

Die Normalisierung vereinheitlicht Unicode, Groß-/Kleinschreibung und Satzzeichen. Datums-/Ausgabeangaben werden nicht gezielt entfernt. Namen mit sehr kurzem oder generischem Schlüssel werden nicht zugeordnet. Treffer sind Kandidaten, keine nachgewiesenen Dubletten. Kein Treffer beweist keine inhaltliche Lücke: Inhalte können anders heißen oder in Archiven enthalten sein.

Die fehlenden Drive-Einträge enthalten weder Dateigröße noch Prüfsumme. Für keinen dieser fehlenden Einträge kann dieser Abgleich Bytegleichheit belegen. Bei den 458 bereits gespeicherten Drive-Dateien ist eine Datei anhand der protokollierten SHA-256 auch in einer anderen Quelle vorhanden. Für 50 gibt es Dateinamenskandidaten, aber keinen identischen Hash unter diesen Kandidaten. Unterschiedliche Hashes können unter anderem andere Scans, OCR-Fassungen oder PDF-Metadaten bedeuten; sie beweisen keine unterschiedlichen Werke. Die 458 Dateien sind keine Zufallsstichprobe und erlauben keine Hochrechnung des Dublettenanteils.

## Offene Links der ursprünglichen LRHmaterials-Liste

66 offene Links: 60 fehlgeschlagen, sechs unversucht. Für sieben gibt es Dateinamenskandidaten, für 59 nicht. Auch hier ist keine Bytegleichheit einer fehlenden Datei bewiesen.

Bei der Prüfung wurde ein zu breiter Audio-ZIP-Filter entdeckt und in `extra_sources.py` korrigiert: Der gemischte Ordner `00_2TB_New_Collection_Audios-Videos-PDFs_and_Docs` darf nicht als reiner Audiobereich gelten. Außerdem werden erkennbare Transkript-/Textpakete im eigentlichen Audiobereich zugelassen. Die sechs bislang unversuchten Pakete enthalten laut Namen Transkripte, Indexe, HCOPL-Updates, Management-Series-DOC-Dateien oder Wörterbuch-TIFFs. Sie sind deshalb relevante Prüfkandidaten für eine Textsammlung. Ein korrigierter Filter allein lädt sie noch nicht herunter.

## Beurteilung

Die fehlenden Bestände können derzeit nicht als entbehrliche Kopien eingestuft werden. Die 3.557 Drive-Namenstreffer können gezielt auf gleiche Werke und gleiche Ausgaben geprüft werden; die übrigen 16.421 benötigen zusätzliche bibliografische Zuordnung. Zuerst die sechs zurückgestellten Textpakete und offene EN-/DE-Texte prüfen. Anschließend fehlende Drive-Titel nach Sprache, Ausgabe, Dokumenttyp und bereits vorhandenem Werk priorisieren, statt allein nach Rohdateizahl vorzugehen.

Eine vollständige LRH-/CBR-Werksammlung ist ohne eine definierte Sollbibliografie nicht nachweisbar. Vollständigkeit kann sich auf Werke, Ausgaben, Sprachen oder konkrete Scans beziehen; diese Ziele sind nicht gleichbedeutend.

Details: `summary.json`, `missing-drive-candidates.jsonl`, `missing-lrh-candidates.jsonl`. Erneut erzeugen mit `.venv/bin/python get-data/assess_missing_overlap.py`.
