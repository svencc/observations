# Ziel: Semantische Suchdatenbank

Stand: 10.11.2026. Dieses Projekt befindet sich in der Konzeption.

## Zweck

Eine lokale, semantisch und lexikalisch durchsuchbare Datenbasis für die vorhandenen
LRH-/CBR-Materialien konzipieren. Eine KI soll darüber recherchieren, relevante
Originalstellen abrufen und Antworten mit überprüfbaren Quellen belegen können.
Die Bedienung erfolgt über HTTP/API, curl oder ein kleines Skript. Eine eigene
Oberfläche und ein eigenes Antwort-LLM sind nicht erforderlich.

Dieser Ordner enthält die Ziele, Architekturentscheidungen und später gegebenenfalls
Konfiguration, Suchdienst und Recherchewerkzeuge dieses Teilprojekts.

## Grober Umfang

- Vorhandene Lösungen prüfen und möglichst wiederverwenden, insbesondere den
  txtai-Dienst unter `~/apps/knowledge`. Fertige Komponenten sind Eigenentwicklung
  vorzuziehen, sofern sie Herkunft, Fundstellen und benötigte Suche unterstützen.
- Eine einfache lokale Speicherung bevorzugen: SQLite für Text und Metadaten;
  Vektorindex beziehungsweise SQLite-Vektorerweiterung nach Eignung auswählen.
  txtai mit SQLite und Faiss ist ein bisheriger Vorschlag, keine endgültige Festlegung.
- Semantische Suche mit exakter Wort-/Titelsuche kombinieren; deutsche und englische
  Materialien auch sprachübergreifend recherchierbar machen.
- Filter nach Dokumenttyp, Datum, Fassung, Sprache, Serie und Quelle vorsehen.
- Fundstellen mit Originaltext, Dokumentidentität, Fassungsangaben, Originaldatei
  und Seiten-/Abschnittsbezug liefern. Nachbarabschnitte gezielt abrufbar machen.
- Abdeckung, Fehler und noch nicht erschlossene Materialien sichtbar machen.
- Einen wiederaufnehmbaren Indexbau und eine überprüfbare Zuordnung zwischen
  vorbereiteten Daten und Suchindex konzipieren.
- Später einen Bash-Client und/oder Recherche-Skill für die KI bereitstellen.

## Schnittstelle zur Datenvorbereitung

[1-prepare-data](../2-prepare-data/GOAL.MD) erschließt Texte, Struktur und Metadaten
aus den Originalen. Dieses Projekt übernimmt die vorbereiteten Ergebnisse und
macht sie durchsuchbar. Das gemeinsame Übergabeformat ist noch festzulegen.

Suchbare Einheiten sollen einzelne Dokumente beziehungsweise einzelne LRH-Letters
in einer bestimmten Fassung sein, auch wenn viele davon in einem Sammelband liegen.
Textabschnitte behalten ihre Dokument-, Fassungs- und Quellenzuordnung.

## Angestrebtes erstes Ergebnis

Ein begründeter Architekturvorschlag mit Datenmodell, Übergabeformat und kleinem
Pilotplan. Der Pilot soll Suchqualität, Belegstellen, deutsch-englische Suche,
Laufzeit und Ressourcenbedarf prüfen, bevor ein Gesamtindex aufgebaut wird.

## Ausgangspunkt und Grenzen

Die bisherige Analyse liegt in [search/README.md](../search/README.md); dort liegt
auch ein rein lesendes Beispiel für die bestehende knowledge-API. Ein
Observations-Suchindex existiert noch nicht.

Der aktuelle Auftrag legt die Projektstruktur und groben Ziele fest. Er startet
keinen Indexbau oder Gesamtimport. Beschaffung bleibt abgeschlossen; Originale
und Herkunftsmanifeste bleiben erhalten.
