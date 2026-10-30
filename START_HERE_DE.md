# Hier starten

Das ist der kürzeste Weg vom frischen Klon bis zu einem geordneten lokalen Fall und einem sauberen Übergabepaket.

> English version: [START_HERE.md](START_HERE.md)

## Wofür dieses Produkt gedacht ist

Bringe eine chaotische Sammlung lokaler Dokumente in einen verständlichen Fall:

1. Dokumente hinzufügen
2. Unterlagen in den Fall übernehmen
3. Dokumente prüfen und ordnen
4. eine Zeitlinie aufbauen
5. Personen und Organisationen verbinden
6. ein Übergabepaket erstellen

Alles ist für lokale Nutzung gedacht. Das Tool ordnet Material; es entscheidet **nicht**, was rechtlich richtig, wichtig oder verwertbar ist.

## Was du brauchst

- Python 3.11+ (unter Windows über `py` oder `python`)
- einen lokalen Browser
- genügend Speicherplatz für kopierte Originale und Übergabepakete

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
.\scripts\windows\start_here.ps1
```

### macOS

```bash
git clone https://github.com/IMaugrenI/local_case_organizer.git
cd local_case_organizer
./scripts/macos/start_here.command
```

Die lokale Browserseite öffnet sich und zeigt dir den nächsten sinnvollen Schritt.

Windows: Die Befehle laufen in einer geöffneten Windows-PowerShell. PowerShell 7 (`pwsh`) ist für die bestehenden `.ps1`-Skripte nicht erforderlich. Wenn die Skriptausführung durch eine Unternehmensrichtlinie gesperrt ist, die Richtlinie nicht stillschweigend umgehen.

Der Starter verlangt Python 3.11 oder neuer. Auf macOS müssen die vorhandenen `.command`-Dateien ausführbar sein; bei einem Release werden sie mit ausführbarem Git-Dateimodus bereitgestellt.


## Dein erstes sinnvolles Ergebnis

Für einen sicheren Test nutze synthetische Demo-Unterlagen statt echter sensibler Daten.

Ein normaler erster Ablauf:

1. **Dokumente hinzufügen**
2. **Wartende Dateien übernehmen**
3. **Dokumentenübersicht erstellen**
4. Unterlagen prüfen und die gewünschten Dateien für die Übergabe markieren
5. **Zeitlinie erstellen** und bei Bedarf mindestens ein Ereignis ergänzen
6. bei Bedarf Personen oder Organisationen ergänzen
7. **Übergabepaket erstellen**

**Erfolgreiches Ergebnis:** Du hast ein lokales Paket mit den ausgewählten Unterlagen, während die Arbeitsstruktur und Nachvollziehbarkeit im Organizer erhalten bleiben.

## Wenn etwas nicht funktioniert

Die Browserseite zeigt eine verständliche Meldung. Technische Details bleiben unter **Weitere Optionen & technische Details**.

Wähle dort **Probleme prüfen**.

Im Terminal:

```bash
python run.py doctor
```

Wenn eine Datei nach dem Import verändert wurde, kann der Export stoppen, statt still eine veränderte Datei weiterzugeben. Das ist ein Integritätsschutz.

## Datenschutz und Vertrauen

Echte Fallunterlagen können sensibel sein.

Veröffentliche keine echten Fallakten, Übergabepakete, Screenshots mit persönlichen Informationen oder privaten lokalen Pfade in öffentlichen GitHub-Issues.

Lies vor echten sensiblen Daten [SECURITY.md](SECURITY.md).

## Stoppen und später weitermachen

Die Browseroberfläche läuft im Terminalprozess. Beenden mit `Ctrl+C`.

Später denselben `start_here`-Starter erneut nutzen oder:

```bash
python run.py ui
```

Deine lokalen Falldateien bleiben im ignorierten lokalen Arbeitsbereich erhalten.

## Beispiel aus echter Nutzung

[docs/guides/USER_JOURNEY_DE.md](docs/guides/USER_JOURNEY_DE.md) zeigt einen kompletten Fall-bis-Übergabe-Ablauf und einen typischen Integritätsfehler.

## Mehr Details

- [Einsteiger-Guide](docs/guides/beginner_quickstart.md)
- [Installation und erster Test](docs/guides/install_and_first_test.md)
- [Befehle](docs/reference/commands.md)
- [Release-Checkliste](docs/release/release_checklist.md)
