# Ziel: Daten für Suche und KI-Recherche vorbereiten

Stand: 10.11.2026. Dieses Projekt befindet sich in der Konzeption.

## Zweck

Aus den vorhandenen Originalmaterialien nachvollziehbare Texte, Dokumentstrukturen
und Metadaten gewinnen. Der benötigte Kontext liegt noch nicht vollständig vor:
Dokumentgrenzen, Titel, Datumsangaben, Fassungen und Gliederung müssen erst durch
Skripte, Dokumentparser, gegebenenfalls OCR und gezielte LLM-Unterstützung erschlossen
werden.

Dieser Ordner enthält die Ziele, Formatentscheidungen und später gegebenenfalls
Werkzeuge und Qualitätsregeln der Datenvorbereitung. Abgeleitete Massendaten sollen
lokal getrennt von Originalen und versionierter Projektdokumentation liegen;
konkrete Ablage und Git-Ausschlüsse sind vor ihrer Erzeugung festzulegen.

## Zwei zu prüfende Markdown-Ansätze

1. **Beschreibende Markdown-Dateien:** Begleitdateien zu Originalen beziehungsweise
   erkannten Einzeldokumenten. Sie beschreiben Herkunft, Dokumenttyp, Titel, Datum,
   Struktur, Seitenbereiche und Verarbeitungsqualität. Sie können auf separat
   gespeicherte Textauszüge verweisen; eine Beschreibung allein ersetzt keinen
   durchsuchbaren Volltext.
2. **Umwandlung in Markdown mit Metadatenkopf:** Den vollständigen extrahierten
   Dokumenttext als Markdown mit YAML-Header darstellen. Überschriften, Absätze,
   Listen und Quellen-/Seitenbezug erhalten. Bei Sammelbänden möglichst einen
   einzelnen Letter je Fassung abbilden und den Bezug zum Band behalten.

Im Pilot klären, welche Variante oder Kombination sinnvoll ist. Markdown ist eine
mögliche Darstellung; strukturierte Daten für die Suchdatenbank dürfen zusätzlich
bereitgestellt werden. Noch ist kein verbindliches Ausgabeformat beschlossen.

## Aufbau der LRH-Dokumente berücksichtigen

- Einzelne Letters innerhalb von Sammelbänden erkennen. Datei, Band, Letter,
  Fassung und Textabschnitt voneinander unterscheiden.
- HCO Policy Letters und HCO Bulletins anhand ihrer Dokumentköpfe unterscheiden;
  die Zuordnung grün/rot als Zusatzhinweis behandeln, auch Schwarzweißscans zulassen.
- Titel, Dokumenttyp, Originaldatum, Issue-Kennung, Serie und Seriennummer erfassen,
  soweit sie tatsächlich belegt sind.
- Revisionskennungen, Revisionsdaten, Neufassungen und Wiederveröffentlichungen
  getrennt vom ursprünglichen Datum und der Ausgabe des Sammelbands speichern.
- Verteiler, Referenzen, Verfasser-/Freigabeangaben und ausdrückliche Hinweise auf
  Änderung, Ersetzung oder Aufhebung bewahren.
- Abschnittsüberschriften, nummerierte Regeln und Absätze erhalten. Wiederholte
  Seitenköpfe und Inhaltsverzeichnisse nicht als neue Letters missverstehen.
- Andere Dokumentarten, insbesondere CBR-Materialien, mit passenden allgemeinen
  Strukturen erfassen; ihnen kein LRH-Letter-Schema aufzwingen.

## Grober Verarbeitungsansatz

1. Geeignete vollständige Materialien anhand vorhandener Herkunftsnachweise auswählen.
   Typ aus Inhalt und Metadaten erkennen; `.php` kann beispielsweise PDF oder ZIP sein.
2. Text und Seiten-/Abschnittsbezug extrahieren, Archivmitglieder ihren Containern
   zuordnen und OCR nur bei fehlender oder unbrauchbarer Textschicht ergänzen.
3. Regelmäßige Dokumentköpfe und Strukturen zunächst per Skript erkennen.
   Für unklare Fälle gezielt LLM-Unterstützung prüfen.
4. Ausgelesene Angaben von abgeleiteten Beschreibungen und Themenzusammenfassungen
   unterscheiden. Metadaten mit Fundstelle und Erkennungsmethode versehen;
   Unbekanntes offenlassen und Unsicherheit dokumentieren.
5. Originalextrakt, bereinigten Suchtext und gegebenenfalls LLM-Beschreibung
   auseinanderhalten. LLM-Texte ersetzen weder Originalstellen noch deren Nachweis.
6. Qualität und Wiederaufnahme an einem kleinen repräsentativen Bestand prüfen,
   insbesondere Letter-Grenzen, Revisionen, Scans, Übersetzungen und Mehrfachfassungen.

## Schnittstelle und erstes Ergebnis

Mit [0-search-engine](../1-search-engine/GOAL.MD) ein Übergabeformat vereinbaren:
stabile Dokument-/Fassungskennungen, Text, Struktur, Metadaten, Herkunft und genaue
Fundstellen. Eine einfache Markdown-/Header-Konvention samt Beispielen und
Qualitätskriterien soll daraus entstehen. Die endgültige Wahl erfolgt anhand
eines Piloten, nicht allein aus der Formatpräferenz.

## Grenzen

Der aktuelle Auftrag legt Ziele und Ordner an; er startet keine Konvertierung,
OCR oder LLM-Verarbeitung des Gesamtbestands. Originale unter `raw-data/`, auch
Archive und Teilbestände, bleiben unverändert. Herkunftsmanifeste werden nicht
umgeschrieben. Ähnliche Titel beweisen weder Identität noch gleiche Fassung;
unsichere Zuordnungen und nicht erschlossene Inhalte bleiben sichtbar.
