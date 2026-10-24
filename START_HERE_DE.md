# Hier starten

Das ist der kürzeste Einstieg für neue Nutzer.

> English version: [START_HERE.md](START_HERE.md)

## Was dieses Tool macht

`local_case_organizer` hilft dir, sensible lokale Dateien zu strukturieren in:

1. importierte Originale mit Provenienz
2. ein Dokumentregister
3. eine bearbeitbare Timeline
4. ein neutrales Exportpaket

Das Tool arbeitet local-first und benötigt keinen Cloud-Dienst.

Es ist **keine** Rechtsberatung und entscheidet nicht, ob ein Dokument rechtlich korrekt oder wichtig ist.

## Voraussetzungen

- Python 3.11+ (unter Windows über `py` oder `python` erreichbar)
- ein lokaler Browser für die UI
- genügend lokaler Speicherplatz für kopierte Originale und Exporte

## Erster Start

### Linux

```bash
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
bash scripts/linux/start_here.sh
```

### Windows PowerShell

```powershell
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
pwsh ./scripts/windows/start_here.ps1
```

### macOS

```bash
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
./scripts/macos/start_here.command
```

Der Launcher bereitet den lokalen Workspace vor und startet die Browser-UI.

Die UI läuft lokal. Das Terminal bzw. der Prozess muss während der Nutzung laufen; beendet wird mit `Ctrl+C`.

## Normaler Ablauf

### 1. Dateien ablegen

Lege Dateien hier ab:

```text
data/inbox/
```

oder wähle eine Quelle über den unterstützten Importweg.

### 2. Importieren

```bash
python run.py import
```

Der Import erzeugt einen eindeutigen Batch, kopiert Originale nach `data/originals/`, berechnet SHA-256 und schreibt Provenienz.

### 3. Register bauen

```bash
python run.py build-register
```

### 4. Timeline bauen

```bash
python run.py build-timeline
```

### 5. Exportieren

```bash
python run.py export-package
```

Exporte landen unter `exports/`.

Die weitergebbare Export-Provenienz enthält bewusst keine absoluten lokalen Quellpfade. Ausgewählte Originale werden vor dem Export gegen ihren gespeicherten SHA-256 geprüft.

## Nützliche Prüfungen

```bash
python run.py status
python run.py check
python run.py doctor
```

## Grenze für private Daten

Diese lokalen Laufzeitordner werden von Git ignoriert:

- `data/`
- `exports/`
- `logs/`
- `workspace/`
- private Profile und Archive

Keine echten Fallakten, Exporte, Screenshots mit privaten Daten oder absoluten privaten Pfade in öffentliche GitHub-Issues stellen.

Vor echten sensiblen Daten: [SECURITY.md](SECURITY.md).

## Mehr Details

- [Einsteiger-Guide](docs/guides/beginner_quickstart.md)
- [Installation und erster Test](docs/guides/install_and_first_test.md)
- [Befehle](docs/reference/commands.md)
- [Release-Checkliste](docs/release/release_checklist.md)
