# local_case_organizer

> Die englische Hauptfassung liegt in `README.md`.

Lokales Tool zur Organisation sensibler Fallakten in saubere Dossiers.

Ein lokales, cloudfreies System, um chaotische Dokumentensammlungen in strukturierte Register, Zeitlinien und Exportpakete zu überführen.

Dieses Repository ist ein neutraler öffentlicher Kern für lokale Fallorganisationsarbeit. Es ist für Menschen gedacht, die aus ungeordneten Dokumentenbeständen ein prüfbares Dossier erstellen wollen, ohne Daten in eine Cloud zu geben.

## Schnellstart (sicherster Einstieg)

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
2. lokale Browser-Oberfläche

## Einordnung

`local_case_organizer` ist kein Kanzleisystem, kein Gerichtstool und keine Rechtsberatungsmaschine.

Es ist eine lokale Dossier- und Organisationsschicht.

Ziel ist:

1. Originale schützen
2. stabile Dokument-IDs vergeben
3. ein prüfbares Register aufbauen
4. Timeline-Arbeit ermöglichen
5. saubere Exportpakete für Dritte (z. B. Anwälte) vorbereiten

## Zielgruppe

- Privatpersonen mit chaotischen Fallakten
- Beratungs- und Unterstützungsumfelder
- Anwälte als Empfänger strukturierter Dossiers

## Runtime-Wahrheit

Primärer Einstieg:

```bash
python run.py setup
python run.py ui
python run.py check
```

Weitere Befehle:

```bash
python run.py status
python run.py doctor
python run.py import
python run.py build-register
python run.py build-timeline
python run.py export-package
```

## Plattform-Starter

Die unterstützte Runtime bleibt `python run.py ...`.

Komfortstarter existieren für:

- Linux
- Windows
- macOS

## Grenzen

Dieses Repository behauptet nicht:

- garantierte rechtliche Korrektheit
- automatische Rechtsbewertung
- Cloud-Verarbeitung als Standard

Es bleibt technisch ehrlich:

- local-first
- cloudfrei
- datenschutzfreundlich
- evidenz- und herkunftsbewusst

## Status

Früher V1-Stand mit funktionierendem Python-CLI, lokaler UI und sauberer Plattformstruktur.
