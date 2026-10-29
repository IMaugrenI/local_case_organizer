# local_case_organizer

<p align="center">
  <img src="https://raw.githubusercontent.com/IMaugrenI/IMaugrenI/main/assets/banner/local_case_organizer_banner_v3_spaced.png" alt="local_case_organizer banner" width="100%" />
</p>

**Unübersichtliche lokale Dokumente in eine geordnete, prüfbare Fallakte überführen.**

Local Case Organizer unterstützt beim Import von Dateien, bei stabilen Dokumentreferenzen, beim Aufbau eines Registers und einer Zeitachse sowie bei der Vorbereitung von Exportpaketen. Die Verarbeitung bleibt standardmäßig lokal und ist für Menschen mit **unstrukturierten oder sensiblen Dokumentensammlungen** gedacht.

**Einstieg:** [Schnellstart](START_HERE_DE.md) · [English README](README.md) · [ToF Systems Übersicht](https://github.com/IMaugrenI/tof-showcase)

**Ablauf:** **Import → Register → Timeline → Export**. Jeder Schritt macht das Dossier leichter nachvollziehbar, besprechbar und übergebbar. Das Repository ist das eigenständige **Structure**-Werkzeug. Eine optionale Anbindung an ein bereits lokal laufendes Ollama-Modell kann ungeprüfte, quellengebundene Vorschläge liefern; standardmäßig erfolgt keine Modellanfrage.

**Grenze:** Dieses Organisationswerkzeug ist weder Rechtsberatung noch Gerichtssystem noch Garantie rechtlicher oder regulatorischer Konformität. Sensible Inhalte müssen vor der Weitergabe eines Exportpakets geprüft werden.

## Rolle in der öffentlichen Produktlinie

Struktur (Organisation und Export)

### Funktioniert allein
Ja.

### Kann kombiniert werden mit
- `tof_local_builder` zur Strukturierung erzeugter Ausgaben
- `tof_local_knowledge` zur Ordnung extrahierter Evidenz

### Nicht gedacht für
- unbeaufsichtigte KI-Feststellungen, rechtliche Schlussfolgerungen oder automatische Datenweitergabe
- als eigenständige Cloud- oder Knowledge-Retrieval-Plattform zu dienen

## Einfachster sicherer Einstieg

### Linux

```bash
bash scripts/linux/start_here.sh
```

### Windows PowerShell

```powershell
pwsh ./scripts/windows/start_here.ps1
```

### macOS

```bash
./scripts/macos/start_here.command
```

Dieser Pfad führt aus:

1. setup
2. lokale Browser-UI

## Zielgruppen

- Privatpersonen mit chaotischen Fallakten
- Beratungs- und Unterstützungskontexte
- Anwältinnen und Anwälte als nachgelagerte Empfänger saubererer Dossier-Exporte

## Empfohlene Dokumentationsreihenfolge

- `docs/guides/beginner_quickstart.md`
- `docs/guides/install_and_first_test.md`
- `docs/reference/commands.md`
- `docs/reference/python_cli_runtime.md`
- `docs/platform/linux.md`
- `docs/platform/windows.md`
- `docs/platform/macos.md`
- `docs/roadmap/productization_roadmap.md`
- `docs/roadmap/roadmap_v1.md`
- `docs/release/release_checklist.md`

Eine Doku-Übersicht liegt in `docs/README.md`.

## Grenzen

Dieses Repository beansprucht **nicht**:

- garantierte rechtliche Korrektheit
- garantierte DSGVO-Konformität in jeder Bereitstellung
- automatische rechtliche Bewertung
- Cloud-Verarbeitung als Standardpfad

Dieses Repository soll technisch ehrlich bleiben:

- local-first
- cloud-free per Default
- privacy-friendly by design
- evidenz- und provenienzbewusst
- neutral genug für unterschiedliche Falltypen

## Runtime-Wahrheit

Primärer Runtime-Einstieg:

```bash
python run.py setup
python run.py ui
python run.py check
python run.py status
python run.py doctor
python run.py import
python run.py import --source /pfad/zu/dateien
python run.py build-register
python run.py build-timeline
python run.py export-package
```

## Sortierte Launcher-Struktur

Dünne OS-Starter liegen unter:

- `scripts/linux/`
- `scripts/windows/`
- `scripts/macos/`

Gemeinsame Starter in diesen Ordnern:

- `setup`
- `ui`
- `check`
- `status`
- `doctor`
- `import`
- `build-register`
- `build-timeline`
- `export-package`
- `start_here`

## Was die Befehle tun

- `setup` bereitet ignorierte lokale Ordner wie `data/`, `exports/` und `logs/` vor
- `ui` startet die lokale Browser-Oberfläche
- `check` prüft Repo- und lokalen Workspace-Status
- `status` zeigt eine kompakte Übersicht über lokale Dateien, Import-Batches und Exportpakete
- `doctor` führt lokale Runtime- und Schreibbarkeitsprüfungen aus
- `import` übernimmt Dateien aus `data/inbox/` oder einem gewählten Quellpfad und schreibt Import-Manifeste
- `build-register` scannt importierte Originale und erstellt `data/register/document_register.csv`
- `build-timeline` erstellt `data/register/timeline.csv`
- `export-package` erstellt ein neutrales, zeitgestempeltes Exportpaket unter `exports/`

## Lokaler Testfluss

1. Repository lokal klonen
2. den passenden `start_here`-Starter für dein Betriebssystem ausführen
3. die Browser-UI öffnet sich lokal
4. in der **einfachen Ansicht** einen Fall auswählen oder anlegen
5. bis zu 160 Dateien (insgesamt höchstens 150 MiB) auswählen oder ins Feld ziehen; der Organizer teilt die Auswahl in begrenzte Teilpakete, importiert sie und setzt die lokale Text-/PDF-Vorbereitung mit sichtbarem Fortschritt fort
6. auf **derselben einfachen Seite** Dokumente markieren und kommentieren, lokale Suche, Zeitlinie, Aufgaben, Personen und Quellenhinweise verwenden sowie nach ausdrücklicher Bestätigung ein Übergabepaket erstellen. Zusätzliche Fachfunktionen wie quellengebundene Aussagen, Vergleichshinweise, manuelles KI-Übergabepaket und ausdrücklich aktiviertes Offline-OCR liegen unter **„Weitere Spezialfunktionen“** (standardmäßig zugeklappt).

Der Knopf **Bereits abgelegte Inbox-Dateien einordnen** verarbeitet schon vorhandene Inbox-Dateien. Identische Dateiinhalte werden übersprungen; Eingangsdateien und Originalkopien bleiben erhalten.

**Aktenautopilot:** Die Verarbeitung erfolgt nach einer bewussten Dateiablage schrittweise und fallbezogen. Der private Fortschritt liegt unter `data/working/autopilot_state.json` im ausgewählten Fall; **„Weiterverarbeiten“** setzt einen unterbrochenen Durchlauf fort. Textdateien und PDFs werden lokal für die Suche aufbereitet, soweit vorhandene Werkzeuge und Ressourcenlimits das erlauben. Ungeeignete und nicht lesbare Dateien erscheinen als Prüfbedarf. Die Checkbox **„Lokale OCR ... zulassen“** ist standardmäßig ausgeschaltet: Sie erlaubt ausschließlich nach bewusster Auswahl die lokal installierten OCR-Werkzeuge; es werden keine Programme automatisch nachinstalliert. Die automatische Aktenvorbereitung ruft weder Cloud noch LLM auf, gibt keine Quellen frei und versendet nichts. Eine **separat und ausdrücklich gestartete lokale Ollama-Analyse** ist unten beschrieben.

Die Fallübersicht schlägt aus Dateinamen oder verifizierten lokalen Textstellen **mögliche Dokumentarten** vor. Datumsstellen aus geeigneten Textdateien und indizierten PDFs bleiben unbestätigte, quellenbezogene Hinweise. Die Anwalts-Lesehilfe berücksichtigt diese Vorschläge ausschließlich für bewusst zum Export ausgewählte Unterlagen. Über **„Alle Dokumente markieren“** kann die Auswahl nach ausdrücklicher Warnung in einem Schritt gesetzt werden; die eigentliche Übergabe benötigt weiterhin eine weitere Bestätigung.

## Optionale lokale KI-Analyse (Ollama)

In der bestehenden einfachen Seite unter **Weitere Spezialfunktionen → Optionaler KI-Austausch** können lokal installierte Ollama-Modelle erkannt und für ein bewusst ausgewähltes Dokument genutzt werden. Erforderlich ist eine bereits laufende Ollama-Instanz unter `127.0.0.1:11434`; der Organizer installiert und startet weder Ollama noch ein Modell und wählt keinen fremden Netzwerkendpunkt.

Ein ausdrücklicher Klick mit Bestätigung erlaubt die Übertragung von höchstens **zwei hash-geprüften, gekürzten Textstellen** des gewählten Dokuments an **diesen lokalen Dienst**. Die Antworten müssen wörtliche Quellenstellen, Dokument-ID und Seite enthalten. Nicht belegbare Modellbehauptungen werden verworfen; gültige Vorschläge bleiben **ungeprüft** und werden niemals automatisch zu bestätigten Aussagen, Zeitlinieneinträgen oder exportierten Fakten. Bereits bekannte Vorschläge werden nicht doppelt gespeichert. Die Fallübersicht zeigt nur Hinweise, deren Originalquelle noch zur Zitatstelle passt.

**Wichtige Grenze:** Der Organizer kann nur die Verbindung zum Loopback-Dienst kontrollieren. Die tatsächliche Konfiguration und Vertrauenswürdigkeit der lokal betriebenen Ollama-Instanz liegt beim Betreiber. Ohne Ollama funktioniert die Aktenorganisation weiterhin vollständig; die manuelle KI-Austauschfunktion bleibt verfügbar. Keine KI-Analyse läuft unbeaufsichtigt nach Import oder Seitenaufruf.

## Aktenübersicht und anwaltstaugliche Übergabe

Die einfache Seite enthält einen **quellenbezogenen Fallüberblick** mit Anzahl der
Unterlagen, offenen manuellen Prüfungen, Datums-Hinweisen und möglichen nächsten
Arbeitsschritten. Es werden keine Verfahrensstände oder rechtliche Fristen
berechnet oder behauptet. Text-Hinweise sind ausdrücklich unbestätigte Vorschläge.

Beim bewusst ausgelösten lokalen Export wird zusätzlich
`ANWALT_START_HERE.md` erzeugt. Die Datei erklärt die Lesereihenfolge, verweist
auf die Anlagen-IDs und benennt Punkte, die Betreiber und Anwalt noch prüfen müssen.

**Exportgrenze:** Nur ausdrücklich ausgewählte Originaldateien und mit diesen
Auswahlen verknüpfte Register-, Ereignis-, Personen-, Aufgaben-, Aussagen- und
Provenienzzeilen werden ausgegeben. Unverknüpfte Zeilen werden nicht automatisch
mitgegeben. Freitextangaben können dennoch sensible Informationen enthalten
und müssen vor jeder tatsächlichen Weitergabe geprüft werden.

## Was Import zusätzlich bringt

Der Import-Schritt ist der Provenienz-Anker für V1.

Jeder Import erzeugt:

- ein zeitgestempeltes Batch unter `data/originals/`
- ein batch-spezifisches `import_manifest_*.csv`
- ein aggregiertes `provenance.csv`

Dadurch können spätere Dokumentregister stabile Datei-IDs behalten, statt sie bei jedem Lauf blind neu zu erzeugen.

## Erfolgszustand

Ein erfolgreicher erster Lauf bedeutet:

- dein lokaler Workspace existiert
- die lokale Browser-UI öffnet sich
- `data/inbox/` ist für abgelegte Dateien bereit
- die UI kann den lokalen Status sauber lesen
- spätere Importe erzeugen stabile Batch- und Provenienz-Daten

## Aktuelle Repository-Form

```text
run.py
src/local_case_organizer/
docs/
scripts/
examples/demo_case/
profiles/default/
```

## Status

Frühes V1-Scaffold mit funktionierendem Python-first Befehlsweg, lokaler Browser-UI, sortierten Doku-Ordnern und sortierter Cross-Platform-Launcher-Struktur.


## Ausbaustand A1–A10 auf dem Entwicklungsbranch

Der Entwurfs-PR #3 ergänzt die Fallakten um isolierte Arbeitsbereiche,
Hash-Integrität, Belegverknüpfungen, optionale PDF-/OCR-Indizierung,
lokale Suche, quellengebundene Aussagen, Vergleichshinweise, Audit-Journal,
Fallauswahl im Browser, Dossier-Export und manuelle Wiedervorlagen.

**Optionale KI-Integration:** Eine lokale Übergabeschnittstelle erstellt
auf Wunsch begrenzte Kontextpakete aus indizierten, noch überprüften
Quellen. Externe lokale KI-Vorschläge müssen bewusst importiert und
einzeln als Entwurf bestätigt werden. **Kein eingebauter Modellaufruf**
und keine automatisch akzeptierten Erkenntnisse.

Die vorhandenen Python- und Betriebssystem-Starter bleiben verbindlich.
Originaldokumente bleiben unverändert; private Arbeitsdateien werden
nicht auf GitHub hochgeladen. OCR setzt vorhandene optionale lokale
Werkzeuge voraus und wird nicht automatisch installiert.

Siehe [Ausbau-Übergabe](docs/roadmap/expansion_handoff.md).

**Entwicklungsvorschau, nicht in main und keine Gesamtfreigabe.**
