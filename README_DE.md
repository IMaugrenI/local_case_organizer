# local_case_organizer

<p align="center">
  <img src="https://raw.githubusercontent.com/IMaugrenI/IMaugrenI/main/assets/banner/local_case_organizer_banner_v3_spaced.png" alt="local_case_organizer banner" width="100%" />
</p>

> Die englische Hauptfassung liegt in `README.md`.

**Sensible Fallakten lokal in saubere Dossiers strukturieren**

Ein lokales, cloud-freies Werkzeug, um unübersichtliche Dokumentensammlungen in strukturierte Register, Zeitleisten und Exportpakete zu überführen.

Lokale Dossier- und Organisationsschicht für sensible Fallakten.

Diese Ablage ist der neutrale öffentliche Kern für lokale Fallorganisation. Sie ist für Menschen gedacht, die sensible Unterlagen ohne Cloud-Workflow in eine sauberere, prüfbare Dossier-Struktur bringen wollen.

## Was dieses Repo ist

Dieses Repository ist das öffentliche **Structure**-Repo in der Produktlinie.

## Für wen es gedacht ist

Dieses Repo ist für Menschen, die sensible lokale Dokumente ohne cloud-first Workflow in ein saubereres, prüfbares Dossier überführen wollen.

## Was es nicht ist

Dieses Repo ist keine Kanzleisoftware, kein Gerichtstool, keine Rechtsberatungs-Engine und kein versteckter Cloud-Dienst.

## Wohin du als Nächstes gehen kannst

- `tof-showcase` — öffentlicher Architektur- und Produktlinien-Einstieg
- `tof_local_knowledge` — Evidenz suchen und extrahieren, bevor du strukturierst
- `tof_local_builder` — geprüfte Ausgaben erzeugen, bevor du sie ordnest

## Warum dieses Repo existiert

Dieses Repo existiert, um Originale geschützt zu halten, stabile Dokument-IDs zu vergeben, eine prüfbare Struktur aufzubauen, Timeline-Arbeit zu unterstützen und saubere Exportpakete vorzubereiten, ohne sensibles Material in einen Cloud-Workflow zu schieben.

## Rolle in der öffentlichen Produktlinie

Struktur (Organisation und Export)

### Funktioniert allein
Ja.

### Kann kombiniert werden mit
- `tof_local_builder` zur Strukturierung erzeugter Ausgaben
- `tof_local_knowledge` zur Ordnung extrahierter Evidenz

### Nicht gedacht für
- Generierungsprozesse auszulösen
- als Knowledge-Retrieval-System zu dienen

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
4. private Dateien in `data/inbox/` ablegen oder den Inbox-Button aus der UI nutzen
5. die großen UI-Buttons für Import, Register, Timeline und Export verwenden

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
