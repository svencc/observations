# Semantische Recherche für Observations

Analyse und Architekturvorschlag vom 10.11.2026. Es existiert noch kein
Observations-Suchindex. Diese Ausarbeitung startet keine Extraktion, OCR,
Indexierung oder Beschaffung. Der Beschaffungsabschluss bleibt unverändert.

## Empfehlung

Aktuelle Nutzerpräferenz: **keine Oberfläche und kein eigenes Antwort-LLM nötig**.
Die recherchierende KI fragt den lokalen Dienst per HTTP/curl ab. Fertige
Chat-Anwendungen bleiben Vergleichsoptionen, sind aber kein Implementierungsziel.

Python und **txtai mit SQLite-Inhaltsspeicher und lokalem Vektorindex** verwenden.
Den Ansatz aus `~/apps/knowledge` übernehmen, aber eine eigene Observations-Instanz
mit eigenem Datenverzeichnis betreiben. Den vorhandenen persönlichen Wissensindex
nicht mit der Sammlung vermischen. Zunächst einen repräsentativen Pilotbestand
verarbeiten; erst nach Qualitäts- und Laufzeitmessung den Gesamtbestand indexieren.

Eine vorherige Übersetzung aller Dokumente in Markdown ist unnötig. Benötigt werden
extrahierte, zitierbare Texte mit Seiten-/Abschnittsbezug. Diese können direkt in
SQLite gespeichert werden. Auch txtai extrahiert Text vor dem Embedding: Der
Verzicht auf Markdown spart eine zusätzliche Darstellung, nicht die Textextraktion.
Bildscans benötigen OCR, Audio ohne Transkript benötigt Transkription, um über
denselben Textindex inhaltlich durchsuchbar zu werden.

Die Suchmaschine liefert Belege. Die recherchierende KI formuliert daraus eine
Antwort und kann weitere Suchanfragen stellen. Ein eigenes lokales Antwort-LLM
ist für diesen Ablauf zunächst nicht nötig. Embeddings und Suche sollen lokal
laufen; ausgewählte Belegtexte gelangen bei der Recherche in den Kontext der
jeweils verwendeten KI. Das ist bei einer Cloud-KI kein vollständig lokaler Ablauf.

## Was bereits vorhanden ist

Gelesen wurden die Projektvorgaben, README und Abschlussberichte von Observations,
die README/AGENTS von `knowledge` und `KanbAIn`, die Suchimplementierung und
Konfiguration von `knowledge` sowie die Knowledge-Verweise in `KanbAIn`.
Keine neue Rohdateninventur oder Inhaltsprüfung wurde durchgeführt. Die tatsächliche
Verteilung von Formaten, Scanqualität, Seiten und Textmengen ist deshalb noch offen.

Der Abschlussbericht nennt 555,4 GB erfolgreich protokollierte Daten und 91.731
validierte Dateien. Davon sind 81.329 als `document` klassifiziert; das bedeutet
weder 81.329 PDFs noch ebenso viele eindeutige Werke. Pakete, Mehrfachfassungen und
Teilbestände müssen bei der Suchabdeckung gesondert behandelt werden.

### knowledge

Relevante lokale Dateien unter `/Users/sven.carrillo-castillo/apps/knowledge/`:

| Datei | Vorhandene Funktion |
| --- | --- |
| `config.yml` | Mehrsprachiges MPNet-Modell, `content: true`, `hybrid: true` |
| `compose.yml` | Loopback-API, persistentes `/data`, Quellen read-only unter `/knowledge` |
| `indexer/indexer.py` | SHA-256-Dateistand in SQLite, Textractor, Upserts, Nachbarabsätze, Quellenfilter |
| `indexer/router.py` | `/index`, `/search`, `/topics`, `/search/multi`, `/neighbours` |
| `extras/knowledge` | Bash-Client für Suche und Verwaltung |
| `extras/skills/knowledge/SKILL.md` | Agentenablauf: suchen, Kontext holen, Quellen nennen |

`state.db` ist dabei nur die Datei-Zustandsverwaltung. Der txtai-Inhaltsspeicher
verwendet ebenfalls SQLite; Vektoren liegen standardmäßig im separaten
Faiss-Index. Es handelt sich also nicht um eine einzige SQLite-Datei.

Für diesen Bestand vor einer Übernahme zu ändern:

- `sha256()` nutzt `read_bytes()`: Eine große Datei wird vollständig in den RAM
  geladen, jeder Lauf hasht den gesamten sichtbaren Bestand erneut. Vorhandene
  Manifest-Hashes als Herkunft verwenden; lokale Änderungsprüfung mit gespeichertem
  Größen-/Zeitstand und bei Bedarf gestreamtem Hash. Ein übernommener Manifest-Hash
  ist keine neue Integritätsprüfung.
- `scan_files()` unterscheidet nicht zwischen vollständigen Dokumenten, Teilbeständen,
  Katalogen, Metadaten und Archivcontainern. Auswahl aus den vorhandenen Manifesten
  statt pauschalem rekursivem Import von `raw-data/`.
- `to_upsert` sammelt alle neuen Chunks im RAM. Begrenzte Batches, dauerhafte
  Jobzustände und Wiederaufnahme pro Dokument sind für den großen Bestand nötig.
- Es fehlen Seitenangaben, Archivmitgliedpfade, Autoren-/Datumsfelder und
  Extraktionsqualität. Nachbar-Chunknummern allein reichen für belastbare Zitate nicht.
- Extraktionsfehler werden als leere Chunkliste gespeichert und bei unverändertem
  Hash später übersprungen. Fehler, leere Seiten und OCR-Bedarf brauchen eigene,
  erneut bearbeitbare Zustände.
- SQLite-Dateistand und txtai-Index werden nicht gemeinsam atomar aktualisiert.
  Insbesondere werden reine Löschläufe nicht explizit gespeichert. Ein nicht
  erreichbares Laufwerk darf außerdem nicht als Löschung aller Dokumente gelten.
- `urls.txt` löst Abrufe aus. Für Observations ausschließlich lokale Eingaben
  zulassen und diese Funktion deaktivieren; auch HTML-Extraktion darf keine
  externen Ressourcen nachladen.
- Bei Quellenfiltern wird der Suchtext direkt in einen SQL-String eingesetzt;
  Nachbarabfragen interpolieren die Chunk-ID ebenfalls. Apostrophe können diese
  Abfragen beschädigen. Vor Übernahme sichere Query-Konstruktion und Tests vorsehen.
- Das Image `neuml/txtai-cpu` ist nicht auf eine Version festgelegt. Bibliotheken,
  Modellrevision und Extraktions-/Chunkkonfiguration reproduzierbar festhalten.
- Der vorhandene CLI verschluckt curl-Fehler mit `|| true`. Ein Recherchewerkzeug
  muss einen nicht erreichbaren Dienst von einer leeren Treffermenge unterscheiden.
- Der vorhandene Skill empfiehlt bei leerem Index automatisch `knowledge index`.
  Für Observations Suche und Indexbau trennen; Recherche darf keinen Massenvorgang starten.

Das vorhandene Modell `paraphrase-multilingual-mpnet-base-v2` ist als Vergleichsbasis
brauchbar, hat laut Modellkonfiguration aber **128 Tokens Eingabelänge**. Die
Absatzextraktion im Indexer setzt keine entsprechende Tokenobergrenze durch.
Lange Absätze können daher im gespeicherten Text vollständig erscheinen, während
das Embedding nur ihren Anfang repräsentiert.

### KanbAIn

In der untersuchten Kotlin-Implementierung wurde keine eigene semantische
Suchmaschine gefunden. `docs/tickets/KAIn-0011.md` beschreibt die Rückführung von
Review-Wissen nach `~/knowledge` und verweist auf dessen CLI/Skill. Das ist ein
Integrationsansatz für denselben Dienst, keine zweite Suchlösung.
Beide fremden Repositories wurden ausschließlich gelesen und bleiben unverändert.

## SQLite oder eine andere Datenbank?

### Fertige Anwendungen als Alternative

Ergänzung auf Nutzerwunsch, 10.11.2026: Eine fertige Anwendung ist ausdrücklich
eine Option. Die txtai-Empfehlung oben bezieht sich vor allem auf eine schlanke,
skriptfähige Suchbasis unter Wiederverwendung des vorhandenen Dienstes. Wenn eine
fertige Rechercheoberfläche Vorrang hat, zunächst eine Anwendung im Pilot prüfen,
bevor eine eigene Import-/Suchanwendung entwickelt wird.

| Lösung | Bereits vorhanden | Bewertung für dieses Projekt |
| --- | --- | --- |
| AnythingLLM | Desktop-/Docker-Anwendung, Dokumenten-Chat, Workspaces, lokale LanceDB; SQLite für Anwendungsdaten | Mein erster Kandidat für einen unkomplizierten Test einer fertigen Anwendung. Keine reine SQLite-Vektorlösung; Belegqualität und automatisierten Import am Pilot prüfen. |
| Open WebUI | Chat-Oberfläche, Wissenssammlungen, Hybrid-Suche mit BM25/Reranking, Quellenangaben, REST-API | Gute Wahl, wenn eine vielseitige Oberfläche mit lokalen Modellen gewünscht ist. Extraktion und Metadaten bestimmen, ob Seitenangaben tatsächlich verfügbar sind. |
| RAGFlow | Dokumentenverarbeitung, OCR/Layoutanalyse und RAG mit Belegstellen | Kandidat für einen gezielten Vergleich bei schwierigen Scans. Größerer Betriebsaufwand; standardmäßig Elasticsearch statt schlanker SQLite-Basis. |
| Docling | Dokumentparser mit strukturiertem Dokumentmodell, OCR und Herkunfts-/Layoutinformationen | Fertiger Extraktionsbaustein für die vorgeschlagene Pipeline, keine vollständige Rechercheanwendung. Kein Markdown-Zwang. |

Offizielle Grundlagen und Grenzen:

- AnythingLLM verwendet standardmäßig [lokale LanceDB für Vektoren](https://docs.anythingllm.com/features/vector-databases).
  Die [Desktop-Speicherübersicht](https://docs.anythingllm.com/installation-desktop/storage)
  unterscheidet SQLite-Anwendungsdaten, Vektorbestand und verarbeitete Dokumente.
  API-Zugriff ist laut [Desktop-Übersicht](https://docs.anythingllm.com/installation-desktop/overview)
  möglich; Eignung als Belegwerkzeug für externe Agenten gesondert testen.
- Open WebUI dokumentiert [Wissenssammlungen](https://docs.openwebui.com/features/workspace/knowledge/),
  [Hybrid-Suche und Quellenmetadaten](https://docs.openwebui.com/features/chat-conversations/rag/)
  sowie [API-Endpunkte](https://docs.openwebui.com/reference/api-endpoints/).
  Eine Quellenmarkierung allein garantiert keine korrekte Originalseitenzuordnung.
- RAGFlow nennt im [Quickstart](https://ragflow.io/docs) als empfohlene Ausgangsbasis
  4 CPU-Kerne, 16 GB RAM und 50 GB freien Speicher. Diese Basis ist keine
  Größenempfehlung für unsere gesamte Sammlung. Die [Engine-Dokumentation](https://ragflow.io/docs/v1.0.0/switch_doc_engine)
  beschreibt Elasticsearch als Standard und Infinity als Alternative.
- Docling beschreibt [unterstützte Formate](https://github.com/docling-project/docling/blob/main/docs/usage/supported_formats.md)
  und [OCR](https://github.com/docling-project/docling/blob/main/docs/concepts/OCR.md).
  Im Pilot strukturierte Ausgabe und Seitenbezug prüfen, statt pauschal Markdown
  als dauerhaftes Zwischenformat zu erzeugen.

**Praktische Auswahl:** Zuerst AnythingLLM gegen die vorhandene txtai-Basis mit
demselben kleinen Beleg-/Fragensatz vergleichen. Open WebUI bevorzugen, wenn die
allgemeine lokale Chat-Oberfläche selbst ein Ziel ist. RAGFlow nur dann zusätzlich
testen, wenn schwierige Dokumentlayouts/OCR die anderen Ansätze klar begrenzen.
Docling als Extraktionsadapter unabhängig von der endgültigen Oberfläche prüfen.

Für keine dieser Anwendungen ist die Eignung für die gesamte Observations-Sammlung
hier nachgewiesen. Vollständigkeitsstatus, `.php`-Formaterkennung, Archive,
Herkunftsmanifest und Mehrfachfassungen bleiben projektspezifische Importaufgaben.
Wichtiges Pilotkriterium für die Zusammenarbeit mit einer externen KI: Die API
muss rohe Belegtexte mit stabilen IDs und Quellen liefern können; ein fertiger
Chat-Antwortendpunkt allein reicht dafür nicht. Keine dieser Anwendungen wurde
installiert, gestartet oder mit Rohdaten beschickt.

### Suchbasis ohne fertige Oberfläche

| Variante | Bewertung für Observations |
| --- | --- |
| txtai + SQLite + Faiss | Bevorzugt: vorhandenes Know-how, Hybrid-Suche, kein Datenbankserver; Index ist ein Verzeichnis mit mehreren Dateien |
| SQLite FTS5 + sqlite-vec + Sentence Transformers | Gute Alternative bei Priorität auf einer DB-Datei; Fusion, Import und Recherche-API selbst bauen; Vektorsuche auf Zielgröße messen |
| Eigener Vektorserver | Für den Start zusätzliche Betriebsarbeit ohne nachgewiesenen Bedarf |

SQLite allein erzeugt keine Embeddings. FTS5 bietet lexikalische Suche, eine
Vektorerweiterung ergänzt Ähnlichkeitssuche. `sqlite-vec` unterstützt Python und
Metadatenfilter/Partitionen, arbeitet bei `vec0` aber mit vollständigen
Vektorvergleichen innerhalb der ausgewählten Daten. Daraus folgt keine feste
maximale Bestandsgröße; Latenz hängt von Vektorzahl, Dimension, Filtern und Hardware
ab. Nicht auf einen kleinen Pilotbenchmark allein verlassen, sondern auch die
hochgerechnete Zielgröße testen.

Die relevante Größenordnung sind **Chunks, nicht Rohdaten-GB**. Rechenbeispiel:
1 Mio. Vektoren × 768 Dimensionen × 4 Byte ergeben 3,072 GB reine float32-Vektoren;
5 Mio. ergeben 15,36 GB. Texte, Suchstrukturen, Metadaten, Modelle und temporäre
Daten kommen hinzu. Das ist eine Szenariorechnung, keine gemessene Bestandsprognose.

## Vorgeschlagener Datenfluss

```text
Bestehende Manifeste + lokale Originale (nur lesen)
    → dokumentierte Auswahl vollständiger Materialien
    → Formaterkennung / begrenzte Archivverarbeitung
    → Text pro Seite/Abschnitt; OCR nur bei Bedarf
    → SQLite: Dokumente, Herkunft, Texte, Jobs, Qualität
    → tokenbegrenzte Chunks → mehrsprachige Embeddings + Wortindex
    → Hybrid-Suche → Kontext/Originalseite → KI-Antwort mit Belegen
```

1. **Auswahl und Herkunft:** Mastermanifest zeilenweise verarbeiten, historische
   Ergebnisse/Korrekturen nach den bestehenden Statusregeln auflösen; nicht einfach
   jede jemals erfolgreiche Zeile importieren. Erfolgreiche, vorhandene, vollständige
   Dateien zulassen. Unklare Widersprüche dokumentieren. Kataloge und Begleitmetadaten
   getrennt führen und standardmäßig aus inhaltlichen Belegen ausschließen.
2. **Typen:** Signatur/Inhalt, Originalname und URL gemeinsam berücksichtigen.
   LRHmaterials-`.php` kann beispielsweise PDF oder ZIP sein. Archive als Container
   mit einzelnen Mitgliedern erfassen. Keine ungeprüfte Gesamtextraktion:
   Pfadschutz, Größen-/Tiefenlimits und Fehlerzustände vorsehen; alles Abgeleitete
   außerhalb von `raw-data/` speichern.
3. **Extraktion:** PDF seitenweise, HTML als bereinigten Haupttext, Text/DOCX direkt;
   ältere Officeformate mit passendem Adapter. Erst vorhandene Textschicht nutzen.
   Gemischte PDFs seitenweise auf OCR-Bedarf prüfen. Tesseract/OCR-Werkzeuge erst
   nach Qualitätsprobe auswählen. Originale nie mit OCR-Versionen überschreiben.
   Audio/Video ohne Transkript als inhaltlich noch nicht erschlossen ausweisen.
4. **Qualität:** Originalextrakt und normalisierte Suchfassung unterscheiden.
   Silbentrennung, Kopfzeilen und OCR-Störungen behutsam behandeln. Kurze Definitionen
   und Überschriften nicht durch einen pauschalen 100-Zeichen-Filter verlieren.
   Timeouts und Speicherlimits pro Datei; Fehler sollen den Gesamtjob nicht stoppen.
5. **Chunking/Modell:** Als Pilotkandidat `intfloat/multilingual-e5-base` gegen das
   vorhandene MPNet testen. E5 verlangt `query: ` / `passage: ` auch bei deutschen
   Texten und hat 512 Tokens Grenze. Startwert für E5: ca. 300–400 Tokens je Chunk,
   40–60 Tokens Überlappung, Präfix/Titel im Budget berücksichtigen. Absatzgrenzen
   bevorzugen, Seitenbezug erhalten. Für MPNet kleinere modellgerechte Chunks nutzen.
   Modell, Tokenizer, Revision, Dimension und Chunkversion im Index festhalten.
   Modellwechsel erzeugt eine neue Indexgeneration.
6. **Mehrfachfassungen:** Exakte Hashgleichheit zur Einsparung von Extraktion und
   Embeddings verwenden, aber sämtliche Quellenzuordnungen behalten. Ähnliche Titel
   sind keine Dubletten. Andere Scans, Übersetzungen und Ausgaben bleiben getrennt;
   mögliche Werkgruppen sind zusätzliche, mit Unsicherheit versehene Metadaten.
7. **Indexkonsistenz:** Nur begrenzte Batches verarbeiten. Jobs mit Checkpoints und
   Fehlertexten führen; Suchgeneration erst veröffentlichen, wenn Text- und
   Vektorbestand zusammenpassen. Wiederholungen müssen idempotent sein. Fehlender
   Mount führt zum Abbruch, nicht zur automatischen Entfernung von Indexeinträgen.

## Ablage und Datenmodell

Vorschlag für die spätere Implementierung; die genannten Laufzeitverzeichnisse
und Module sind noch nicht angelegt:

```text
search/                         # Code, Konfiguration und Dokumentation in Git
  README.md
  knowledge-query.sh            # Bereits vorhandenes, rein lesendes API-Beispiel
  ...                          # Später: Import, Extraktion, Indexierung, Suche
search-data/                    # Lokal, später vor Erstellung in .gitignore ergänzen
  catalog.sqlite               # Herkunft, Seiten, Chunks, Jobs, Qualität
  index/<generation>/          # txtai SQLite-Inhalt + Vektor-/Wortindex
  cache/                       # Nur nötige Extraktions-/OCR-Zwischenergebnisse
```

Der Katalog ist die dauerhafte Grundlage; der Suchindex ist daraus wiederaufbaubar.
Im txtai-Inhaltsspeicher liegen die für Suche nötigen Chunktexte und Metadaten
zusätzlich. Diese bewusste Redundanz vermeidet Extraktion bei Modellwechseln.
Backups müssen konsistente DB-/Indexgenerationen sichern, nicht nur `state.db`.

| Entität | Wesentliche Inhalte |
| --- | --- |
| Dateien/Container | Relative Originalpfade, SHA-256, Typ, Größe, historischer Downloadstatus |
| Herkunft | Quellen-ID, Abruf-/Fund-URL, Originalname, Manifestbezug; mehrere je Inhalt |
| Dokumente | Datei-/Archivmitgliedbezug, Titel, Sprache, Autor, Dokumentdatum mit Herkunft/Unsicherheit |
| Seiten/Abschnitte | PDF-Seitenindex (1-basiert), ggf. gedruckte Seitenbezeichnung, extrahierter Text, Methode/Qualität |
| Chunks | Stabile ID aus Inhalts-/Extraktions-/Chunkversion und Position, Text, Tokenzahl, Seiten/Offsets |
| Jobs/Generationen | Status, Versuche, Fehler, Konfigurations-/Modellversion, Fortschritt, Veröffentlichungsstand |

Bei DOCX/HTML ohne feste Paginierung Abschnitt und Textposition zitieren; keine
Seitenzahlen erfinden. Datum des Werkes, Uploaddatum und Abrufdatum getrennt halten.
Autoren-/Werkszuordnung nicht aus einem Quellenordner als gesicherte Tatsache ableiten.

## LRH-Letters: Dokumentstruktur als Teil des Indexes

Ergänzung vom 10.11.2026: Für HCO Policy Letters und HCO Bulletins soll die
fachliche Dokumentstruktur ausdrücklich berücksichtigt werden. Der typische
Zusammenhang grün/HCO PL und rot/HCOB ist beispielsweise in der archivierten
[Wiedergabe des HCO PL vom 13.03.1966](https://saentowiki.com/en/hcopls/orders-precedence-of-personnel-titles-of-div1.dep2.hcob-pl-ed-p660313)
beschrieben. Typ aus dem Dokumentkopf erkennen; Farbe und Bandzugehörigkeit sind
nur zusätzliche Hinweise. Schwarzweißscans und gemischte Sammelbände müssen funktionieren.

**Suchbare Haupteinheit ist der einzelne Letter in einer bestimmten Fassung.**
Eine PDF-Datei kann viele Letters enthalten, ein Letter mehrere Seiten. Daraus
ergibt sich die Hierarchie Datei/Band → Letter-Fassung → Abschnitt → Chunk.
Eine mögliche gemeinsame Werkidentität verbindet Fassungen; weitere Scans oder
Abdrucke derselben Fassung sind eigene Quellenbelege. Diese Zuordnungen benötigen
Nachweise und dürfen nicht allein aus Titel oder Datum entstehen.

| Feld | Nutzen |
| --- | --- |
| Dokumenttyp | HCO PL / HCOB sowie andere erkannte Typen getrennt filtern; keine automatische LRH-Autorenzuweisung |
| Originaldatum | Datum des ursprünglichen Issues, getrennt von Revision und Sammelbanddatum |
| Issue-Kennung | Beispielsweise Issue I/II, soweit vorhanden; Typ + Datum allein identifizieren einen Letter nicht eindeutig |
| Revisionsangaben | Originale Kennung wie R/RA/RB sowie ausdrücklich angegebene Revision-/Neufassungs-/Wiederveröffentlichungsdaten |
| Titel und Serie | Originaltitel, ggf. Übersetzung, Serienname und Seriennummer als durchsuchbare Felder |
| Verteiler | Adressaten/Verteilerzeilen als eigene Metadaten statt Vermischung mit dem eigentlichen Inhalt |
| Verfasser-/Freigabeangaben | Namens-/Signatur-/Redaktionsangaben so erfassen, wie sie in dieser Fassung vorliegen |
| Verweise und Änderungen | Referenzen auf andere Issues; ausdrückliche Aussagen zu Änderung, Ersetzung oder Aufhebung mit Belegstelle |
| Fundstelle | Ausgabe/Band, Originaldatei, PDF-Seitenindex, gedruckte Seite, Abschnitt; Extraktionssicherheit |

Warum Datumsfelder getrennt nötig sind: Die archivierte Fassung von
[Financial Planning](https://saentowiki.com/en/hcopls/financial-planning-fin-40-p651126r82)
führt ein ursprüngliches Datum von 1965 und eine Neufassung von 1982, außerdem
eine Serienzuordnung und Referenzen auf andere Letters. Ein Filter auf das
Originaldatum allein würde diese spätere Textfassung fälschlich als historischen
Wortlaut von 1965 behandeln. Die Archivwiedergabe ist ein Strukturbeispiel, kein
Nachweis, welche Ausgabe im lokalen Bestand vorhanden ist oder authentisch ist.

Vorgehen für Extraktion und Suche:

1. **Letter-Grenzen erkennen:** Dokumentköpfe, Typ-/Datumszeilen, Titel und Layout
   gemeinsam auswerten. Wiederholte Fortsetzungsköpfe und Inhaltsverzeichnisse nicht
   als neue Letters behandeln; bloße Erwähnungen anderer HCOBs im Fließtext ebenfalls
   nicht. Unklare Segmentierungen behalten Status/Begründung und Originalseitenbezug.
2. **Abschnitte erhalten:** Nach Überschriften, Absätzen und nummerierten Regeln
   unterteilen. Chunks überschreiten keine Letter-/Fassungsgrenze. Lange Abschnitte
   tokenbegrenzt teilen; kurze Regeln im Kontext halten.
3. **Kontext anreichern:** Für Embeddings einen kurzen, belegten Kontext aus Typ,
   Titel, Datum, Serie und Abschnitt voranstellen; im Tokenbudget mitzählen.
   Exakte Felder zusätzlich in SQLite und im Wortindex führen. Wiederkehrende
   Büro-/Verteilerköpfe nicht in jedem Chunk als Hauptinhalt wiederholen.
4. **Referenzen verbinden:** Originale Referenzzeichenfolge, normalisierten
   Zielkandidaten, Relationstyp und Beleg-Chunk in SQLite speichern. Mehrdeutige oder
   fehlende Ziele ungelöst lassen. Einfache Relationstabellen reichen; keine
   Graphdatenbank erforderlich.
5. **Fassungen sichtbar halten:** Standardmäßig alle verfügbaren Fassungen
   recherchierbar lassen und verwandte Treffer gruppieren. Neueste vorhandene Fassung,
   historischer Wortlaut und im Dokument behauptete Geltung sind verschiedene Dinge.
   Weder allein das jüngste Datum noch ein Revisionssuffix beweist aktuelle Gültigkeit.
   Historische Stichtagssuchen ohne passende Fassung als unsicher kennzeichnen.
6. **Gezielt prüfen:** Pilotfälle mit mehreren Letters am selben Datum, Revisionen,
   Übersetzungen, Fortsetzungsseiten, Zitaten fremder Letters und Inhaltsverzeichnissen
   aufnehmen. Feldextraktion und Letter-Grenzen neben der Suchqualität bewerten.

Damit werden Fragen wie „Welche HCO PLs behandeln das Thema?“, „Was steht in
Serie X, Nummer Y?“, „Welche Fassung liegt hier vor?“ und „Welche Dokumente
verweisen auf diesen Letter?“ direkt beantwortbar. Bei ausreichenden Belegen
können auch Änderungen zwischen Fassungen verglichen werden. Für sonstige Dokumente
bleibt eine allgemeine Abschnittssuche als Rückfall erhalten.

## Wie die KI recherchieren soll

Hybrid-Suche verbindet Begriffe wie `HCOB`, Datumsangaben und Originaltitel mit
inhaltlichen Fragen. Semantik allein ist für exakte Fachbegriffe zu unzuverlässig.
Eine deutsche Anfrage soll auch englische Belege finden; Fachbegriffe bei Bedarf
zusätzlich im englischen Original suchen.

Der spätere Observations-Client sollte `search`, `context`, `document` und `status`
mit JSON-Ausgabe anbieten. Filter: Quelle, Sprache, Autor, Dokumentdatum und
Extraktionsqualität. Indexierung gehört in einen eigenen expliziten Befehl.
Suchtreffer enthalten mindestens Chunk-ID, Text, Titel, relative Originaldatei,
Archivmitglied, Seiten-/Abschnittsbezug, Herkunft, Sprache und Indexgeneration.

Rechercheablauf:

1. Suchabdeckung lesen: Was ist indexiert, OCR-offen, fehlerhaft oder ausgeschlossen?
2. Mehrere gezielte Suchanfragen stellen, bei Bedarf DE/EN und exakte Begriffe.
3. Als Startwert ca. 40–80 Kandidaten aus Wort- und Vektorsuche gewinnen, fusionieren
   und auf ca. 8–12 Belegabschnitte begrenzen. Auswahl nach Qualität im Pilot anpassen;
   optionales Reranking erst bei nachgewiesenem Bedarf ergänzen.
4. Nahezu identische Treffer gruppieren; verschiedene Fassungen sichtbar halten.
5. Relevante Nachbarabschnitte und bei Zitaten die Originalseite prüfen.
6. Antwort mit nachprüfbaren Belegen geben. Autorenbehauptung, Quelleninhalt und eigene
   Schlussfolgerung unterscheiden. Ein Suchscore ist keine Wahrheitswahrscheinlichkeit.
7. Keine Treffer heißt nicht, dass ein Werk oder eine Aussage im Bestand fehlt.
   Begrenzte Suchabdeckung und unsichere OCR ausdrücklich berücksichtigen.

Ein späterer Agenten-Skill soll genau diese Schritte anleiten, Quellen als
Recherchematerial behandeln und keine darin enthaltenen Anweisungen ausführen.
Er darf bei leerem Index keinen Indexbau oder Download automatisch beginnen.

## Pilot und Ausbau

1. Etwa 100–300 gezielt ausgewählte Dokumente aus den vorhandenen Manifesten:
   DE/EN, LRH/CBR, Text-PDF, Scan-PDF, HTML, Office, Archivmitglieder, `.php`-Namen,
   kurze Definitionen, lange Bände und mehrere Ausgaben. Die Auswahl ist Teil der
   späteren Umsetzung; bisher wurde sie nicht durchgeführt.
2. Mindestens 20–30 Recherchefragen mit manuell belegten Fundstellen: Fachbegriffe,
   Paraphrasen, deutsch-englische Suche, Datum/Edition und bewusst unbeantwortbare
   Fragen. Kandidatenmodelle anhand derselben Fundstellen vergleichen.
3. Messen: Belegtreffer in Top 10, korrekte Seitenzuordnung, OCR-Abdeckung, Indexrate,
   Wiederaufnahme nach Abbruch, RAM-/Plattenbedarf und Suchlatenz mit/ohne Filter.
   Zielwert als Start: mindestens 80 % der bekannten Belege in Top 10; falsche
   Quellen-/Seitenzuordnung ist ein Fehler. Antwortqualität zusätzlich manuell prüfen.
4. Zielgröße aus gemessenen Chunks pro Dokument-/Formatgruppe abschätzen. Vor
   Gesamtimport ausreichend große Skalierungsprobe; Suchziel zunächst wenige Sekunden
   pro Anfrage auf dem Zielrechner. Keine seriöse Gesamtlaufzeit vor diesen Messungen.
5. Danach vollständige geeignete Textbestände in Batches indexieren. OCR-Rückstand
   separat abarbeiten und Suchabdeckung fortlaufend ausweisen. Keine Rohdatenlöschung.

## Bash-Beispiel für die bereits vorhandene knowledge-API

`knowledge-query.sh` demonstriert heute verfügbare Lese-Endpunkte. Es erstellt
keinen Observations-Index, startet keinen Dienst und indexiert keine Dateien.
Eine bereits laufende, passende knowledge-Instanz muss explizit angegeben werden.
Port 8000 ist der dokumentierte Port von `~/apps/knowledge`; daraus folgt nicht,
dass dort Observations-Daten liegen. Weder Verfügbarkeit noch Indexinhalt wurden
in dieser Analyse per API geprüft.

```bash
# Vorhandenen Dienst prüfen; die Antworten beziehen sich auf dessen Bestand.
export KNOWLEDGE_API_URL=http://127.0.0.1:8000
bash search/knowledge-query.sh count
bash search/knowledge-query.sh topics
bash search/knowledge-query.sh search 'Wie wird Verantwortung definiert?' 8

# Die ID aus einem echten Treffer unverändert übernehmen:
bash search/knowledge-query.sh neighbours '/knowledge/beispiel.pdf::31' 2
```

Die Beispiel-ID ist ein Platzhalter. Dieser Client nutzt bewusst keinen
Quellenfilter; die oben dokumentierten SQL-Probleme im bestehenden Server müssen
vor einer robusten Übernahme gelöst werden. Ein späterer Observations-Client muss
zusätzlich die reicheren Belegmetadaten und den Abdeckungsstatus liefern.

## Externe technische Grundlagen

- [txtai-Konfiguration](https://neuml.github.io/txtai/embeddings/configuration/): SQLite-Inhaltsspeicher, standardmäßig Faiss für Vektoren.
- [txtai-Indexformat](https://neuml.github.io/txtai/embeddings/format/): mehrere lokale Speicherkomponenten.
- [txtai-Hybrid-Suche](https://neuml.github.io/txtai/embeddings/query/): Kombination dichter und lexikalischer Suche.
- [sqlite-vec](https://alexgarcia.xyz/sqlite-vec/) und [vec0-Metadaten/Partitionen](https://alexgarcia.xyz/sqlite-vec/features/vec0.html).
- [MPNet-Modellkarte](https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2): 768 Dimensionen, Standardkonfiguration mit 128 Tokens.
- [Multilingual-E5-Modellkarte](https://huggingface.co/intfloat/multilingual-e5-base): Präfixe und 512-Token-Grenze.
- [pypdf-Textextraktion](https://pypdf.readthedocs.io/en/stable/user/extract-text.html): seitenweise Extraktion, Grenzen bei Bildscans und Speicherbedarf.
