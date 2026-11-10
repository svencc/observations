# Zugänge und Punkte zur gemeinsamen Nachprüfung

Hier stehen nur Zugangsvoraussetzungen und offene Fragen, keine Passwörter, Codes oder Cookies. Technische Abruffehler und Einzelstatus stehen in [downloaded.md](downloaded.md).

**Endstand des bisherigen Rechners:** Der öffentliche Downloadlauf wurde am 07.11.2026 wegen der 20-GiB-Speicherreserve angehalten. Fortsetzung auf größerem externen Speicher / anderem Rechner ist vom Nutzer vorgesehen. Maßgeblich dafür: `raw-data/ÜBERGABE.MD` und der Dokumentationssnapshot unter `raw-data/_handover/`. Der Speicherstopp erfordert keine Zugangsdaten.

## Tatsächlich privater Zugang erforderlich

| Quelle | Was fehlt | Vorgehen |
| --- | --- | --- |
| [Sciento.org](https://sciento.org/login?next=%2Fsearch%2F) | Vom Nutzer kontrollierte E-Mail-Adresse bzw. angemeldete Sitzung. Die Bibliothek verwendet einen per E-Mail versandten Login-Code. | Nutzer übernimmt die Anmeldung oder stellt eine geeignete Sitzung bereit. Es wurde kein Code angefordert und kein Konto angelegt. Ohne Login kein vollständiges Bibliotheksinventar möglich. |

## Nachprüfen; privater Zugang bislang nicht als nötig belegt

- **SPTV / Google Drive:** Sieben der neun direkt verlinkten Ordner liefern HTTP 404. Das kann ein veralteter Link oder eine beschränkte Freigabe sein; daraus lässt sich keine sichere Loginpflicht ableiten. Zwei Ordner sind anonym lesbar, und deren aktuelle Unterordner werden erfasst. Bei fehlenden Beständen aktuelle Links beim Eigentümer erfragen oder mit eigenem Google-Konto prüfen. Bisher keine Freigabeanfrage gestellt.
- **Drive-Downloadlimits:** Falls eine Datei trotz öffentlicher Liste nicht herunterladbar ist, Fehlermeldung im Downloadprotokoll prüfen. Ein eigenes Konto hilft nicht zwangsläufig bei Quoten oder gesperrten Downloads. Betroffene Dateien werden nicht als erfolgreich markiert.
- **Drive aktuell blockiert:** Nach erfolgreichen anonymen Downloads lieferte Google HTTP 403 mit einer HTML-Seite „Sorry“. Der automatische Drive-Abruf wurde deshalb gestoppt. Nach einer Wartezeit einen öffentlichen Ordner im normalen Browser prüfen und feststellen, ob eine Browserprüfung, eine Downloadquote oder eine Kontofreigabe betroffen ist. Eine Loginpflicht ist weiterhin nicht belegt. Das vollständige ermittelte Inventar umfasst 20.436 Dateien; ausstehende Einträge sind im Laufstatus gezählt und können später erneut versucht werden.
- **Drive-Listenbegrenzung gelöst:** Die 50-Einträge-Grenze lässt sich für die öffentlichen Ordner durch anonyme API-Paginierung überwinden. Dafür sind keine privaten Zugangsdaten nötig. Zusätzlich zum ursprünglichen Inventar wurden über 10.000 weitere Dateiverweise ermittelt. Der direkte anonyme API-Download funktioniert auch für getestete Dateien, bei denen die Download-Webseite zuvor scheiterte.
- **Mail.ru / Yandex:** Öffentliche Metadaten sind ohne Login erreichbar. Downloadversuche und etwaige Fehler stehen im Downloadprotokoll. Nicht pauschal ein Konto anlegen; zuerst den konkreten Fehler prüfen.
- **SaentoWiki-Scanarchiv:** Der verlinkte Cloudbestand entspricht nach aktuell sichtbarer Struktur nicht dem angekündigten englischen Großarchiv. Einen aktuellen EN-/DE-Scanlink suchen oder beim Betreiber erfragen. Ein Login ist dafür bislang nicht als Lösung belegt.
- **ESMB:** Der Thread ist öffentlich lesbar. Fehlende Anhänge mit 404 können gelöscht sein; ein Forenkonto ist nicht automatisch die Lösung. Gültige Ersatzlinks suchen, bei einer ausdrücklichen Loginmeldung eigenes Konto prüfen.
- **AOGP:** Der alte Bücherpfad liefert 404; der aktuelle kostenlose Katalog wurde gefunden: <https://www.ao-gp.org/scientology-free-books-pdfs-by-l-ron-hubbard>. Dessen 19 PDFs sind ohne Login heruntergeladen. Für diese Bücher sind keine privaten Daten nötig. Eine kostenpflichtige Mitgliedschaft für weitere Angebote wurde nicht abgeschlossen.
- **Torrents:** Bei fehlenden Peers/Metadaten ist kein Passwort erforderlich. Später erneut versuchen oder einen aktiven Spiegel suchen. Die kleinen Galac-Patra-ZIPs sind nur Metadatencontainer, nicht die Materialbibliotheken selbst.
- **CBR-Paket inzwischen verfügbar:** Der Scientolipedia-Torrent `Non-Confidential_RO_CBR_Excal` ließ sich mit der vollständigen veröffentlichten Trackerliste laden. Seine 60 ausgewählten Textdateien wurden per Torrent-Prüfsummen vollständig bestätigt. Zusätzlich wurden 108 vollständige Einzeldateien aus dem größeren Galac-Patra-CBR-Torrent bestätigt. Die großen LRH-RARs bleiben unvollständig; der 9-GB-Scientolipedia-Magnet lieferte in den bisherigen Versuchen keine Metadaten.

## Falls wir Betreiber kontaktieren wollen

- STSS / Ron's Org: `theta@ronsorg.ch` — aktueller Index oder Spiegel.
- Freezone.de: <https://www.freezone.de/kontakt/> — fehlende CBR-Texte oder Transkripte.
- Galac-Patra / Timecops: `timecops@mail.ru` — aktive EN-/DE-Spiegel oder Seeds.
- Historische Excal-Kontaktadresse aus goal1.md: `Independent_scientologist@hotmail.com` — unbestätigte Altspur; keine Anfrage verschickt.

Es wurden keine Nachrichten versandt, Registrierungen durchgeführt oder privaten Zugangsdaten gesucht. Die öffentlichen Downloads wurden bis zum Speicherstopp unabhängig von diesen Zugangsthemen ausgeführt und sind jetzt angehalten.
