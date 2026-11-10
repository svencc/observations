# Observations

Observations sammelt englische und deutsche Materialien von **L. Ron Hubbard (LRH)** und **Captain Bill Robertson (CBR)** aus verschiedenen Onlinearchiven. Originaldateien, gespeicherte Webseiten und Herkunftsnachweise werden lokal nach Bezugsquelle abgelegt.

Die **Datensammlung gilt seit dem 09.11.2026 auf Nutzerwunsch vorerst als abgeschlossen**. Der letzte Lauf einschließlich Abschlussprüfung ist beendet; weitere Downloads werden nicht automatisch gestartet. Inhaltliche Sortierung, OCR, Markdown-Konvertierung, Dublettenbereinigung und eine Suchanwendung sind noch nicht umgesetzt.

Am **10.11.2026** wurde die Analyse einer lokalen semantischen Suche/RAG-Recherche beauftragt. Der [Architekturvorschlag in search/README.md](search/README.md) bewertet den vorhandenen txtai-Dienst unter `~/apps/knowledge`, SQLite-Alternativen, Textextraktion, Belegstellen und einen Pilotbetrieb. Ein [rein lesender Bash-Client](search/knowledge-query.sh) demonstriert die bestehende knowledge-API. Ein Observations-Suchindex wurde noch nicht aufgebaut; eine Verarbeitung des Gesamtbestands wurde nicht gestartet.

## Einstieg und aktueller Stand

Die nächste Phase ist in zwei zunächst konzeptionelle Teilprojekte gegliedert:

- [0-search-engine/GOAL.MD](1-search-engine/GOAL.MD): lokale semantische Suchdatenbank und Recherche-API für die KI.
- [1-prepare-data/GOAL.MD](2-prepare-data/GOAL.MD): Texte, Struktur und Metadaten erschließen; beschreibende Markdown-Dateien beziehungsweise Volltext-Markdown mit Header prüfen, insbesondere für LRH-Letters.

Der festgehaltene Abschlussstand steht in [get-data/STATUS.md](get-data/STATUS.md), die Vorgaben für weitere Agenten in [AGENTS.md](AGENTS.md). Der Abschluss ist eine Entscheidung über die Projektphase, kein Nachweis einer bibliografisch vollständigen LRH-/CBR-Sammlung.

Der Fortsetzungslauf endete am **09.11.2026 um 03:21 Uhr (Europe/Berlin)** regulär. Insgesamt sind rund **555,4 GB** erfolgreich protokolliert, davon **368,4 GB** im letzten Lauf hinzugekommen. Die lokale Abschlussvalidierung erfasste **91.731 Dateien** mit zwei bekannten Archivwarnungen. Rund **1,30 TiB** bleiben frei. Datei- und Abrufzahlen sind keine Anzahl eindeutiger Werke.

Die ursprüngliche offene LRHmaterials-Dateiliste ist zu **99,7 % erfolgreich geladen**: 20.006 Erfolge, 60 Fehler und 6 unversuchte Text-/Scanpakete. Google Drive bleibt mit **19.978 fehlenden inventarisierten Dateien** offen. Die [Überschneidungsanalyse](get-data/overlap-assessment/README.md) identifiziert 3.557 mögliche Namensüberschneidungen, aber keine bewiesenen Dubletten der fehlenden Dateien. Diese Restpunkte sind bewusst zurückgestellt.

| Dokument | Inhalt |
| --- | --- |
| [Abschlussstand](get-data/STATUS.md) | Beschlossener Abschluss, Bestandszahlen, Prüfungen und zurückgestellte Restpunkte vom 09.11.2026 |
| [Agentenvorgaben](AGENTS.md) | Keine automatische weitere Beschaffung oder Verarbeitung |
| [Übergabe](raw-data/ÜBERGABE.MD) | Gesicherter Übergabestand, Umzug, Fortsetzung und bekannte Stolperstellen; nur mit lokalem Rohdatenbestand verfügbar |
| [Downloadbericht](get-data/downloaded.md) | Ergebnisse je Quelle, erfolgreiche Dateien, Fehler und Teilübertragungen |
| [Laufstatus](get-data/run-state.json) | Zuletzt protokollierter Prozessstatus und Abschlussprüfungen |
| [Fortsetzungsstatus](get-data/continuation-state.json) | Phase der Fortsetzung: Kopierprüfung, Downloads oder Abschluss |
| [Offene Blocker](get-data/manual-blockers.json) | Technische Hindernisse und nächste Schritte |
| [Zugangsfragen](get-data/privat-data.md) | Offene Anmeldungen und manuelle Nachprüfungen, ohne Zugangsdaten |
| [Beschaffungsplan](get-data/plan1.md) | Quellen, Ablageregeln und Kriterien für die Beschaffung |
| [Ursprüngliche Recherche](get-data/goal1.md) | Ausgangspunkt und historische Quellenbewertung |
| [Skriptübersicht](get-data/README.md) | Dokumentation des Beschaffungslaufs |

Der Übergabestand vom **7. November 2026** dokumentiert rund **187 GB / 174,2 GiB erfolgreich protokollierte Daten**. Der damalige Lauf wurde bei Unterschreiten der 20-GiB-Speicherreserve angehalten. Diese Zahl ist ein historischer Stand und kein Maß für die Größe einer vollständigen Werksammlung. Rohdaten, unvollständige Transfers und zusätzliche Kopien können mehr Speicher belegen.

Am **8.–9. November 2026** wurde der Bestand auf dem größeren Laufwerk geprüft und erweitert. `continuation-state.json` zeigt den abgeschlossenen Ablauf. Der Supervisorstatus `finished_with_incomplete_queue` dokumentiert technisch offen gebliebene Quellen und bleibt unverändert; er ist kein Auftrag zum Neustart. Der Übergabesnapshot vom 07.11.2026 bleibt historisch und umfasst nicht den heutigen Gesamtbestand.

**Ein erfolgreicher Download ist kein Nachweis für eine vollständige Sammlung.** Katalogseiten, Archive und einzelne Werke werden getrennt betrachtet. Mehrere Quellen können denselben Inhalt enthalten; ein ZIP kann viele Dokumente oder auch Audiodateien umfassen. Ältere Rechercheangaben können durch spätere Abrufe überholt sein.

## Aufbau

```text
Observations/
├── README.md
├── get-data/                         # Skripte, Planung und Laufberichte
│   ├── download-manifest.jsonl       # Zentrales Herkunfts- und Ergebnisprotokoll
│   ├── downloaded.md                # Daraus erzeugter lesbarer Bericht
│   ├── run-state.json
│   ├── continuation-state.json       # Status des Fortsetzungsablaufs
│   ├── manual-blockers.json
│   └── *.py
└── raw-data/                         # Lokale Rohdaten; nicht in Git
    ├── ÜBERGABE.MD
    ├── _handover/                    # Übergabesnapshot und Kopierinventar
    ├── _provenance/                  # Übergreifende Laufprotokolle
    └── <quelle>/
        ├── ...                      # Originaldateien und ggf. Torrent-Nutzdaten
        └── _provenance/
            ├── manifest.jsonl       # Herkunftsprotokoll dieser Quelle
            └── catalog/             # Gesicherte Kataloge und Inventare
```

Der Ordner heißt im Repository tatsächlich `get-data/`. Die Skripte bestimmen die Projektwurzel relativ zu ihrem Speicherort. `get-data/` und `raw-data/` müssen deshalb Geschwister bleiben.

**Ein Git-Clone enthält die Rohdaten nicht.** `raw-data/` ist in [.gitignore](.gitignore) ausgeschlossen und muss separat übertragen werden. Auch vorhandene Kataloge und Inventare sind für viele Skripte Voraussetzung; die Sammlung lässt sich nicht durch einen einzigen Installationsbefehl aus einem frischen Clone wiederherstellen.

## Quellen

| Quellenordner | Erfasste Materialien bzw. Abrufweg |
| --- | --- |
| `stss` | Englische und deutsche Bücher, Scans, Bände, Kurse und CBR-Dokumente aus dem STSS-Katalog |
| `lrhmaterials` | Öffentliche Dokumentverzeichnisse und Archivpakete |
| `freezone-de`, `freezone-org` | Deutsche und englische CBR-Texte, Seminartranskripte und verlinkte Dokumente |
| `project-avalon` | Dateien des Scientology-Bibliotheksbereichs, einschließlich ergänzender Autoren |
| `saentowiki` | Englische HTML-Texte und Kataloge; Scanarchiv weiterhin offen |
| `sptv-drive` | Öffentlich verlinkte Google-Drive-Ordner, Dateiinventare und Downloads |
| `scientolipedia`, `galac-patra` | Verlinkte Archivcontainer, Torrent-Metadaten und teilweise vollständige Nutzdaten |
| `ronsorg`, `esmb` | Ergänzende Webseiten, CBR-Werkkatalog und Anhänge |
| `aogp` | PDFs aus dem kostenlosen Bücherkatalog |
| `sciento` | Zugang und Katalog geprüft; vollständiges Bibliotheksinventar offen |

Konkrete Einstiegsadressen stehen im [Plan](get-data/plan1.md), tatsächlich verwendete Abrufadressen im [Manifest](get-data/download-manifest.jsonl).

## Einrichtung

### Git LFS für das Herkunftsmanifest

`get-data/download-manifest.jsonl` wird über Git LFS versioniert. Git speichert dafür einen kleinen Verweis; der vollständige Inhalt wird beim Push im LFS-Speicher des GitHub-Repositorys abgelegt. Die Zuordnung steht in [.gitattributes](.gitattributes). Der lokale Dateipfad und die Nutzung durch Python bleiben gleich. Die Rohdatensammlung unter `raw-data/` bleibt separat und wird dadurch nicht zu GitHub hochgeladen.

Auf einem neuen Rechner zuerst Git LFS installieren (unter macOS mit Homebrew: `brew install git-lfs`). Danach im geklonten Repository:

```sh
git lfs install --local
git lfs pull
```

Vor dem Lesen des Manifests muss der vollständige Inhalt vorliegen; ein LFS-Verweis ist kein JSONL-Manifest. `.gitattributes` zusammen mit der Manifeständerung committen. Weitere Hinweise: [GitHub-Dokumentation zu Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/configuring-git-large-file-storage).

### Python-Umgebung

Voraussetzungen sind **Python 3.9 oder neuer**, ausreichend Speicher auf dem Ziellaufwerk und für HTTP-Downloads das Paket `requests`. Die folgenden Beispiele gelten für macOS/Linux und werden aus der Projektwurzel ausgeführt:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install requests
```

Unter Windows entsprechend `.venv\Scripts\python.exe` statt `.venv/bin/python` verwenden. Die virtuelle Umgebung bleibt lokal und gehört nicht in einen Commit.

Für die Drive-Skripte wird zusätzlich `gdown`, für Torrent-Downloads und Torrent-Prüfungen `libtorrent` benötigt. Im bisherigen Lauf wurden diese Versionen verwendet:

```sh
.venv/bin/python -m pip install gdown==5.2.2 libtorrent==2.1.1
```

Die Verfügbarkeit von `libtorrent` hängt von Betriebssystem und Python-Version ab. Einige Skripte durchsuchen zusätzlich den historischen Pfad `/tmp/observations-download-deps`; regulär in der virtuellen Umgebung installierte Pakete funktionieren ohne diesen Ordner.

Für den unten beschriebenen überwachten Fortsetzungsablauf werden `requests` und `libtorrent` benötigt, weil dessen Abschlussroutine auch Torrent-Dateien prüft. `gdown` ist dafür nicht erforderlich. `resume_acquisition.py` verwendet `fcntl` und ist wie der Supervisor für macOS/Linux ausgelegt; unter Windows reicht ein Austausch des Python-Pfads für diesen Ablauf nicht aus.

## Historische Abrufwege — nur bei neuem Beschaffungsauftrag

**Die folgenden Befehle sind Dokumentation, keine aktuelle Arbeitsanweisung.** Die Beschaffung bleibt abgeschlossen. Erst bei einem neuen ausdrücklichen Nutzerauftrag für weitere Daten diese Abläufe wieder verwenden.

Vor einem Neustart den jüngsten Laufstatus und die Blocker lesen und sicherstellen, dass dieselbe Quelle nicht bereits von einem anderen Prozess bearbeitet wird. Das bestehende Masterprotokoll und die Kataloge bleiben erhalten.

Für die Fortsetzung eines **übernommenen Bestands** ist dieser Ablauf vorgesehen:

```sh
.venv/bin/python get-data/resume_acquisition.py --detach
```

Ohne `--detach` läuft derselbe Ablauf im Vordergrund. Er benötigt das vorhandene Inventar `raw-data/_handover/copy-verification.jsonl` und den übernommenen Rohdatenbestand. Zuerst werden die inventarisierten erfolgreichen Dateien auf Größe und SHA-256 geprüft. Nur bei erfolgreicher Prüfung und mindestens 20 GiB freiem Speicher startet er `extra_sources.py` für **LRHmaterials, Ron's Org und ESMB** sowie den Supervisor mit der neu ermittelten Prozess-ID. Google Drive wird dabei nicht erneut abgerufen.

Eine Prozesssperre verhindert mehrere gleichzeitige Aufrufe dieses Fortsetzungsablaufs. Sie schützt nicht vor separat gestarteten Downloadskripten; solche Läufe vorher selbst ausschließen. Bei einer fehlgeschlagenen Kopierprüfung bleibt der Ablauf mit `blocked_migration_verification` stehen. Abweichungen im Prüfbericht klären, bevor die Beschaffung erneut gestartet wird.

| Datei | Zweck |
| --- | --- |
| `get-data/continuation-state.json` | Aktuelle Phase und neue Prozess-IDs des Ablaufs |
| `raw-data/_provenance/continuation.log` | Ablaufprotokoll beim Start mit `--detach` |
| `raw-data/_handover/migration-verification.log` | Fortschritt der Kopierprüfung |
| `raw-data/_handover/migration-verification.json` | Abschließendes Ergebnis der Kopierprüfung |
| `raw-data/_provenance/extra-sources-continuation.log` | Downloadfortschritt und Abruffehler |
| `raw-data/_provenance/supervisor.log` | Protokoll separat mit `supervise_downloads.py --detach` gestarteter Supervisorläufe; im Fortsetzungsablauf steht dessen Ausgabe im Ablaufprotokoll |

`extra_sources.py` reiht gespeicherte unterbrochene Dokumentlinks und die offene LRHmaterials-Warteschlange vor den Katalogeinstiegen ein. Es liest vorhandene Erfolge aus dem Manifest, durchsucht gespeicherte HTML-Kataloge erneut und überspringt erfolgreiche Dateien, wenn Pfad und Größe passen. Dieses Überspringen ersetzt keine erneute SHA-256-Prüfung. Unterbrochene HTTP-Downloads dieses Abrufwegs werden von vorn geladen.

Reine Audio-ZIP-Pakete im Bereich `02-AUDIO_Materials` werden standardmäßig zurückgestellt; erkennbare Transkript-/Textpakete und einzelne Dokumente bleiben zugelassen. Der am 09.11.2026 korrigierte Filter schließt den gemischten Ordner `Audios-Videos-PDFs_and_Docs` nicht mehr pauschal aus; die sechs zuvor zurückgestellten Pakete wurden dennoch nicht nachgeladen. Für einen ausdrücklich beauftragten separaten Direktlauf erlaubt `extra_sources.py --include-audio-archives` auch Audio-ZIPs. Vorhandene Rohdaten bleiben erhalten. Das Skript prüft vor jeder Abrufgruppe die 20-GiB-Reserve; laufende Übertragungen können den freien Speicher dennoch weiter verringern.

### Prozessüberwachung

Der Supervisor kann bereits gestartete Downloadprozesse unter macOS/Linux überwachen. Er aktualisiert den Bericht etwa alle 30 Sekunden und sendet bei weniger als 20 GiB freiem Speicher ein Beendigungssignal an die überwachten Prozesse.

Für separate Direktläufe lässt sich die Überwachung auch manuell starten. Dieses Beispiel ersetzt den obigen Fortsetzungsablauf und führt selbst keine vorgeschaltete Kopierprüfung durch:

```sh
mkdir -p raw-data/_provenance
.venv/bin/python get-data/extra_sources.py > raw-data/_provenance/extra-sources.log 2>&1 &
download_pid=$!
.venv/bin/python get-data/supervise_downloads.py --detach "LRHmaterials=$download_pid"
```

Dabei immer die **neu ermittelte PID** verwenden. Prozess-IDs aus alten Berichten gelten nur für den damaligen Lauf. Der Supervisor verwendet `ps`; unter Windows ist eine Anpassung erforderlich.

Die Speicherprüfung bezieht sich auf das Dateisystem der **Projektwurzel**. Bei Arbeit auf einem externen Laufwerk gehört daher das gesamte Projekt dorthin. Nach Prozessende startet der Supervisor die Torrent- und lokale Bestandsprüfung; für diese Abschlussroutine wird auch `libtorrent` benötigt. Deren Exitcodes stehen in `run-state.json`. Ein beendeter Prozess oder ein erfolgreicher Prüflauf bedeutet nicht, dass alle Quellen vollständig beschafft wurden.

### Weitere Abrufwerkzeuge

Diese Skripte sind einzelne Werkzeuge des bisherigen Laufs und setzen teilweise vorhandene Kataloge, Inventare oder Probeberichte voraus. Inventarisierungsskripte können zugleich Downloads starten.

| Skript in `get-data/` | Aufgabe |
| --- | --- |
| `resume_acquisition.py` | Übernommenen Bestand prüfen und anschließend Zusatzquellen mit Supervisor fortsetzen; `--detach` startet im Hintergrund |
| `extra_sources.py` | LRHmaterials, Ron's Org und ESMB fortsetzen; Audio-ZIPs standardmäßig zurückstellen |
| `inspect_sources.py` | Öffentliche Einstiegskataloge und Links speichern |
| `download_sources.py` | STSS, Freezone, Avalon und SaentoWiki anhand gespeicherter Kataloge abrufen; STSS benötigt zusätzlich `materials.json` im Katalogordner |
| `download_aogp.py` | PDFs aus dem aktuellen kostenlosen AOGP-Katalog laden |
| `probe_archives.py` | Drive-/Cloud-Links prüfen und verlinkte Galac-Patra-Container abrufen |
| `cloud_sources.py` | Öffentliche Cloudbestände untersuchen und Drive-Dateien laden; `--drive-only` beschränkt den Lauf auf Drive |
| `drive_pagination.py` | Abgeschnittene öffentliche Drive-Listen ergänzen und zusätzliche Dateien herunterladen |
| `drive_transfer.py` | Beide gespeicherten Drive-Inventare zusammenführen und ausstehende Dateien über die anonyme API laden |
| `probe_drive_pagination.py`, `probe_drive_media.py`, `probe_drive_ranges.py` | Gezielte Netzwerktests zu Drive-Listen und Downloads |
| `torrent_sources.py` | Veröffentlichte Magnets und Torrents aus Galac-Patra-ZIPs laden; begrenzter Test mit `--magnets-only --seconds 300` |

Drive wurde im dokumentierten Lauf nach einer HTTP-403-„Sorry“-Seite gestoppt. Vor einem erneuten Massentransfer den Zugang nach einer Wartezeit im Browser prüfen; die Antwort belegt keine allgemeine Loginpflicht. Sciento verwendet einen E-Mail-Code-Login. Weitere offene Punkte stehen in [privat-data.md](get-data/privat-data.md).

## Herkunft und Prüfung

Das zentrale [download-manifest.jsonl](get-data/download-manifest.jsonl) enthält einen JSON-Datensatz je protokolliertem Vorgang. Weitere Zeilen können frühere Ergebnisse ergänzen oder korrigieren. Die Zeilenzahl ist daher keine Dateizahl; bei Torrents können mehrere Einzeldateien dieselbe Magnet-URL haben.

Protokolliert werden unter anderem Quelle, Fundstelle, Abruf-URL, relativer Dateipfad, Originalname, Sprache, Abrufzeit, Status, Größe und SHA-256 sowie verfügbare HTTP- und Fehlerdetails. Je Quelle liegt zusätzlich ein Manifest unter `_provenance/`.

Sprachangaben können aus dem jeweiligen Katalog oder Abrufweg stammen und sind keine vollständige Inhaltsprüfung. Neben `en` und `de` kommen `mixed` und `unknown` vor; unteilbare Pakete können weitere Sprachen enthalten.

| Status | Bedeutung |
| --- | --- |
| `successful` | Erfolgreich gespeicherter bzw. bestätigter Abruf; Art und Umfang der Prüfung hängen vom Abrufweg ab |
| `failed` | Abruf oder Formatprüfung fehlgeschlagen |
| `partial` | Unvollständige Übertragung; kein fertiger Dokumentbestand |

Ein erfolgreicher HTML-Katalog bestätigt nicht den Download seiner verlinkten Dokumente. Bei LRHmaterials können lokale Dateien `materials__<URL-Hash>.php` heißen und trotzdem PDF-, Word- oder ZIP-Inhalte enthalten. Für den Dateityp Originalnamen, URL und Inhaltsprüfung heranziehen.

Vorhandene Daten lassen sich lokal prüfen und Berichte neu erzeugen. Diese Prüfungen wurden bereits ausgeführt. Nicht allein für ein Statusupdate erneut starten: Sie können das Manifest und Berichte verändern.

```sh
.venv/bin/python get-data/verify_torrent_files.py
.venv/bin/python get-data/validate_downloads.py
.venv/bin/python get-data/write_download_report.py
```

Die Torrent-Prüfung arbeitet ohne Peer-Verbindungen und bestätigt vollständige ausgewählte Einzeldateien anhand der Torrent-Stücke. Die lokale Validierung prüft Existenz, Größe, PDF-Signaturen und ZIP-Inhalte und kann korrigierende Manifestzeilen schreiben. ZIP-Prüfungen können lange dauern. Hinweise stehen in [validation.json](get-data/validation.json); sie sind trotz Exitcode 0 zu beachten. Diese Prüfung ersetzt keine vollständige SHA-256-Kontrolle oder inhaltliche Prüfung. `write_download_report.py` erneuert `downloaded.md` und erhält eine bereits vorhandene `privat-data.md`.

## Umzug und Sicherung

1. Einen abgeschlossenen, konsistenten Laufstand abwarten. Bei Kopien während laufender Downloads anschließend erneut abgleichen.
2. **Ganz `raw-data/` und `get-data/` kopieren**, einschließlich `_provenance/`, `_handover/`, `.part`-Dateien, Torrent-Metadaten und unvollständiger Nutzdaten. Ein Git-Clone allein genügt nicht.
3. Falls nur die Rohdaten übertragen wurden, den gesicherten Ordner `raw-data/_handover/get-data/` als `get-data/` neben `raw-data/` wiederherstellen. Der Snapshot kann älter als der aktuelle Arbeitsstand sein.
4. Die Kopie auf dem Zielrechner anhand des mitkopierten Inventars prüfen:

   ```sh
   python3 get-data/verify_migrated_copy.py
   ```

Die Prüfung benötigt nur die Python-Standardbibliothek und vergleicht Größe und SHA-256 der im Übergabeinventar erfassten erfolgreichen Dateien. Das Ergebnis landet in `raw-data/_handover/migration-verification.json`; bei Abweichungen endet das Skript mit Exitcode 1. `--size-only` ist ein schneller Vorabcheck und ersetzt den Prüfsummenvergleich nicht. Unfertige Transfers werden dadurch nicht als vollständig bestätigt.

**Das vorhandene Übergabeinventar stammt vom 07.11.2026 und deckt die späteren Downloads nicht ab.** Es genügt deshalb nicht zur Prüfung einer künftigen Kopie des gesamten aktuellen Bestands. Bei einem späteren Umzug ist ein aktuelles vollständiges Inventar erforderlich.

`write_handover.py --final` kann nach einem abgeschlossenen Lauf die Übergabe und den Dokumentationssnapshot erneuern. Es überschreibt dabei Übergabeartefakte und kann rekonstruierte Teilübertragungen im Manifest ergänzen. Einzelheiten zum gesicherten Bestand stehen in der [Übergabe](raw-data/ÜBERGABE.MD).

Torrent-Resume-Dateien können alte absolute Pfade enthalten. Auf dem Zielsystem den Speicherpfad ausdrücklich neu setzen und vorhandene Stücke prüfen lassen. Originale und Teilbestände bis zur bestätigten Übernahme erhalten; keine automatische Umbenennung, Löschung oder Dublettenbereinigung vornehmen.
