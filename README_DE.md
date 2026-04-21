# tof_container_pulse

Lokaler Docker-Host-Status auf einen Blick

Erzeugt eine einfache statische Statusseite aus Docker-CLI-Daten — read-only, lokal, keine Datenbank, keine Cloud.

> Die englische Hauptfassung liegt in README.md.

---

Ein Host. Eine Seite. Ein Blick.

tof_container_pulse ist ein kleines lokales Dashboard für Docker-Hosts.  
Es erzeugt eine statische pulse.html, damit du eine Frage sofort beantworten kannst:

> Läuft gerade alles sauber?

---

## Rolle in der öffentlichen Produktlinie

Beobachten (Systemzustand sichtbar machen)

### Funktioniert allein
Ja.

### Integration
Keine (bewusst nur Beobachtung)

### Nicht gedacht für
- andere Tools zu steuern  
- automatisierte Prozesse auszulösen  
- Teil einer Verarbeitungskette zu werden  

---

## Funktionen

- Linux, macOS, Windows  
- read-only Zugriff über Docker CLI  
- kein Docker SDK notwendig  
- konfigurierbare Warnschwellen  
- optionaler Watch-Modus  
- optionaler Multi-Host-Modus (Docker Contexts)  
- statische HTML-Ausgabe  
- keine Datenbank  
- keine Cloud  

---

## Voraussetzungen

- Python 3.9+  
- Docker CLI im PATH  
- laufender Docker-Daemon oder Docker Desktop  

---

## Schnellstart

bash python3 run.py --once 

Erzeugt die HTML-Datei und öffnet sie automatisch im Browser.

---

## Kernprinzipien

- read-only  
- kein Eingriff in Container  
- keine Historie  
- keine versteckte Logik  

---

## Statusmodell

- ok = läuft und innerhalb der Grenzwerte  
- warn = läuft, aber über Grenzwerten  
- critical = nicht gesund  
- unknown = Zustand nicht sauber bestimmbar