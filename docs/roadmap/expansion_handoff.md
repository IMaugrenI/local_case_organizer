# Local Case Organizer – Entwicklungsausbau A1–A10

Stand: 2026-10-25. Entwicklungs-PR #3; diese Funktionen sind nicht
als freigegebener main-Release zu behandeln.

## Funktionspakete

| Paket | Im Entwicklungsbranch |
| --- | --- |
| A1 | Explizite isolierte Fälle, Hash-Originalprüfung und Quellenverknüpfung |
| A2 | Manuell übernommene Datums-/Timeline-Vorschläge mit Quellenbezug |
| A3 | Optionale lokale PDF-/OCR-Textextraktion und Indizierung |
| A4 | Verbatim-quellengebundene Claims und menschlicher Reviewstatus |
| A5 | Operatorgruppierte Datums-/Betrags-/Textabweichungen als Prüfhinweis |
| A6 | Lokales metadatenbasiertes Änderungsjournal |
| A7 | Lokale Browser-Fallauswahl und -Erstellung mit isolierten Daten |
| A8 | Neutrale ZIP-Dossiers mit Verzeichnis und ausgewählten Originalen |
| A9 | Fallgebundene Aufgaben und manuell eingegebene Wiedervorlagen |
| A10 | Offline-KI-Kontext- und JSON-Vorschlagsaustausch mit Einzelentscheidung |

## System- und Schutzgrenzen

- Bestehende Starter, Python-CLI, CSV, Browser-UI und privates Workspace-Modell.
- Keine LLM-/Cloud-Verbindung, automatische Bewertung, Rechtsberatung
  oder ungeprüfte Überführung von AI-Vorschlägen in bestätigtes Wissen.
- Quellen-Zitate werden gegen den Hash der Originaldatei und die
  indizierte Textstelle geprüft; Reviewstatus bescheinigt keine Wahrheit.
- Fallakten und Exporte sind privat. AI-Kontextpakete enthalten private
  Textauszüge und dürfen nicht ohne bewusste Betreiberhandlung weitergegeben werden.
- Case-Browser bindet nur an Loopback und schützt POSTs gegen einfache
  browserbasierte Cross-Origin-Aufrufe; **keine** Benutzer-Authentifizierung.
- Termine werden vom Benutzer eingetragen, nicht rechtlich berechnet.
- Das Audit-Journal enthält keine Dokumentinhalte oder authentifizierte
  Benutzernamen. Es ist nicht kryptografisch manipulationssicher.

## Nachweislage und Restbedarf

- Bestehende GitHub-CI enthält gezielte Entwicklungstests der neuen Funktionen.
- **Keine** Prüfung privater Echtdaten, Nutzergeräte, OCR-Tool-Installation,
  vollständige Cross-Platform-Runtime oder Gesamt-Abnahme.
- P2/Betreiberentscheidungen: tatsächlicher LLM-Adapter mit separatem
  Datenzugriffsmandat, Weitergabe-/Freigabefluss und Datenschutzzustimmung;
  OCR-Abhängigkeiten sowie plattformspezifische Starter;
  mögliche robuste Mehrprozess-Transaktionen/Audit-Härtung;
  externe Frist-/Kalender-Benachrichtigungen nur nach Zustimmung.
- Falls Berechtigungen für mehrere Benutzer erforderlich werden, muss
  das Mandats- und Authentifizierungskonzept separat entschieden werden.
- Gesamt-Abnahme und GO/NO-GO werden nach dem Ausbau durch DOM gemäß
  zentraler verbindlicher Abnahmeliste entschieden.

Bis dahin: Draft-PR offen, keine automatische Freigabe oder Merge nach main.
