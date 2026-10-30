# Verbindliche Gutachten- und Abnahmeliste – local_case_organizer A1–A16

**Fassung:** 1.0 – Vorabnahme / Prüfvertrag, 30.10.2026  
**Status:** ABNAHME NOCH NICHT GESTARTET · **GO/NO-GO: OFFEN**  
**Einzige maßgebliche Liste:** Diese Datei. Kein paralleler Prüfkatalog, kein fortlaufend wachsender Forderungsbestand.  
**Kandidatenbasis:** [Draft-PR #4](https://github.com/IMaugrenI/local_case_organizer/pull/4), Code-Stand `afd1f5cb175b15ea7e11d120acea0bb4b90b6484` (A11–A16); A1–A10 sind in `main`. Die Dokumentation dieser Liste ist ein nachfolgender Commit, keine Produktfreigabe.

## 1. Zweck, Prüfgrenzen und Rollen

**Prüfgegenstand:** Das im bestehenden Repository implementierte, lokale, fallisolierte Organisationswerkzeug mit Python-`run.py`, vorhandener Browser-UI und den vorhandenen Betriebssystem-Startern. Gegenstand sind die **realisierten A1–A16-Funktionsverträge**: Fallverwaltung, unveränderte Originale und SHA-256-Provenienz, ausdrücklich gestarteter Import, Register, Zeitlinie, Beteiligte, Aufgaben, auditierte Änderungen, quellengebundene Prüfung und lokale Suche, optionales Offline-PDF/OCR und optional freigegebene lokale KI, kontrollierte ausgewählte Dossierübergabe, Benutzerführung sowie Plattformstarter.

**Keine stillschweigenden Zusagen:** Keine juristische Richtigkeits- oder Vollständigkeitsprüfung, keine automatische Übertragung, keine systemweite Multiuser-Authentifizierung, keine verpflichtende Verschlüsselung, kein Malware-Scanning, kein nativer MSI-/DMG-/AppImage-Installer und keine garantierte Unterstützung nicht geprüfter Zielgeräte. Sicherheits- und Produktgrenzen aus `SECURITY.md` und bestehendem Code bleiben verbindlich. Keine zusätzlichen Funktionen während der Abnahme, außer zwingender P0/P1-Sicherheitskorrektur.

**Rollen:**
- **DOM:** Prüfgegenstand, Zielbetriebssystem, optionale Funktionen und Lieferform festlegen; die nötigen Zielsystemprüfungen ausführen; Betreiberentscheidungen, Befundprioritäten und finales GO/NO-GO zeichnen.
- **ChatGPT:** Diese eine Liste fortschreiben, Review-Bündel/Nachweise bewerten, bereits bestandene Prüfungen übernehmen, fehlende Nachweise oder konkrete Korrekturprompts benennen; keine behauptete eigene Zielsystemausführung.
- **Lokale KI (nur wo DOM sie einsetzt):** Entwicklungsrepository prüfen, vorhandene Ergebnisse wiederverwenden, gegebenenfalls begrenzte isolierte Nachweise liefern; während der Abnahme keine eigenständigen Funktionsänderungen.
- **GitHub-Repository:** Bei diesem Projekt erfolgt der konkrete bestehende Repository-Ausbau direkt dort. Der Draft-PR wird nicht eigenmächtig gemergt oder veröffentlicht.

## 2. Endliche Prüfliste – exakt 18 IDs

**Statuswerte:** `BESTANDEN-DEV` (nachgewiesene Entwicklung, kein Runtimebeleg), `BESTANDEN-RUNTIME`, `OFFEN-NACHWEIS`, `OFFEN-ENTSCHEIDUNG`, `NICHT-BESTANDEN`, `ENTFÄLLT (begründet + DOM)`. Ein bereits nachgewiesener DEV-Punkt wird nicht routinemäßig wiederholt.

| ID | Verbindlicher Prüfpunkt / eindeutiges Bestehenskriterium | Nachweisart und konkrete Grenze | Status vor Abnahmestart |
| --- | --- | --- | --- |
| **D01** | Architektur stimmt mit dem Produktvertrag überein: vorhandenes `run.py`, `src/local_case_organizer/`, OS-Starter und lokaler Workspace; keine zweite Runtime oder konkurrierender Startweg. A1–A16 liegen auf dem vorgesehenen Entwicklungsstand. | Repository- und Roadmap-Abgleich, PR #4. **Nur Quell-/Architekturnachweis.** | BESTANDEN-DEV |
| **D02** | Python-Code, CLI, Daten-/Sicherheitsgrenzen und gezielte synthetische Tests bestehen auf dem dokumentierten Code-Stand. | GitHub-CI `Python smoke checks`, **169 bestanden**; Python 3.14 **nur gezielte Kompatibilität**. [Lauf 41027903511](https://github.com/IMaugrenI/local_case_organizer/actions/runs/41027903511). | BESTANDEN-DEV |
| **D03** | Vorhandene Windows- und macOS-Starter für Setup, Doctor und CLI-Hilfe funktionieren in CI; Linux-CLI-Startweg bleibt bestehen. | [Windows/macOS/Ubuntu-GitHub-CI](https://github.com/IMaugrenI/local_case_organizer/actions/runs/41027903511); **keine echte GUI-/Geräteabnahme**. | BESTANDEN-DEV |
| **R01** | Auf **DOMs freigegebenem Zielsystem** startet der vorhandene Plattformstarter mit Python ≥3.11; `doctor` meldet `ready: true` und Exitcode 0. | Zielsystem: OS, Version, Starter, Doctor-Auszug/Exitcode. Kein paralleler Startmechanismus. | OFFEN-NACHWEIS |
| **R02** | Bestehende Browser-UI ist am lokalen Host bedienbar; Schreiben wird nur über die freigegebenen lokalen UI-Grenzen ausgelöst. Kein öffentlicher Listener, Proxy oder automatische Fernübertragung. | Ein gezielter Zielsystem-UI-/Loopback-Nachweis mit zulässigem und unzulässigem Anfragebeispiel; keine echten Akten. | OFFEN-NACHWEIS |
| **R03** | Fall auswählen/anlegen und wechseln isoliert Register, Originale, Prüfungen und Aufgaben. Bereits vorhandene Fallstände bleiben nach regulärem Neustart erhalten. | Zwei synthetische Fallkontexte; Eingabe in A darf in B nicht erscheinen; kontrollierter Neustart. | OFFEN-NACHWEIS |
| **R04** | Bewusste Aufnahme führt zu nachvollziehbarer Dokument-ID, Batch und SHA-256-Provenienz ohne Änderung des Originals. Begrenzte/bereits importierte Arbeitslisten lassen sich ohne ungewollte Dubletten fortsetzen. | Kleine synthetische Einfuhr inkl. Wiederholung/ggf. `Weiterverarbeiten`; Originalhash/Registerbezug. | OFFEN-NACHWEIS |
| **R05** | Dokumentregister zeigt, filtert und verwaltet Dateien einschließlich Positionen jenseits 200; Seitenwechsel verliert keine ungespeicherten Entwürfe. Prüfstatus/Exportauswahl ändert sich nur bewusst. | Gezielte synthetische Registeransicht mit über 200 Zeilen; Filter, Seite, Entwurf, Speichern, Status. | OFFEN-NACHWEIS |
| **R06** | Zeitlinie, Beteiligte, Aufgaben, manuelle Termine und Audit-Journal funktionieren fallgebunden; keine automatisch berechneten Rechtsfristen; Aufgabenerledigung bestätigt keine Tatsachen. | Wenige synthetische manuelle Einträge und eine Statusänderung; Nachweis bestehender CSV-/Audit-Struktur. | OFFEN-NACHWEIS |
| **R07** | Datums-/Quellenhinweise sind erkennbar ungeprüft; Claim-Zitat muss Original und Seite entsprechen; Vergleichshinweise erzeugen keine bewiesenen Widersprüche. | Eine vorhandene oder synthetische Quellenfundstelle, ein bewusst bestätigter Entwurf, ein abgewiesenes falsches Zitat. | OFFEN-NACHWEIS |
| **R08** | A11–A14: Dokumentbezüge, Quellen-Prüf-Cockpit, Quellenabdeckung und explizite Prüfaufgaben zeigen aktuellen Kontext und manuelle Zustände; geänderte Quelle erfordert erneute Prüfung. Keine stillschweigende Freigabe. | Ein zusammenhängender Test mit zwei passenden Quellen, Reviewaktion, Quellendrift-Hinweis und Aufgabenbezug. | OFFEN-NACHWEIS |
| **R09** | Lokale Textsuche verarbeitet zulässige Textquellen und respektiert fehlende/ungültige Indizes. PDF-Extraktion/OCR wird **nur falls von DOM in den Release-Scope aufgenommen** mit vorhandenen Offline-Werkzeugen geprüft. | Zielsystem: gezielter Textsuchbeleg; PDF/OCR bei Nichtfreigabe ausdrücklich `ENTFÄLLT` im Zusatzvermerk. | OFFEN-NACHWEIS |
| **R10** | KI-Vorschläge/Modellverarbeitung werden nicht automatisch versendet oder als Wahrheit übernommen. **Nur bei DOM-Freigabe lokaler KI**: ausdrücklicher lokaler Aufruf, begrenzte Quelle, manuelle Review-Grenze. | Ohne lokale KI: Nachweis deaktivierten Standardpfads und `ENTFÄLLT` für aktive Modellprobe; sonst eine isolierte lokale Einwilligungsprobe. | OFFEN-ENTSCHEIDUNG |
| **R11** | Ausdrücklich ausgewählte Originale erzeugen lokal ZIP, Manifest und SHA-256, Anlagenindex, Anwalt-Einstieg, Sachverhalts-/Dossier-Arbeitsstand sowie `UEBERGABE_PRUEFPUNKTE.md`. Keine automatische Weitergabe. | Ein synthetischer lokaler Handoff; ZIP-Inhalt, Hash, Freigabeschritte und ausgewählte Dateimenge prüfen. | OFFEN-NACHWEIS |
| **R12** | A15-Datenschutz-/Integritätsgrenze: ausgeschlossene Originale und gemischt verknüpfte Freitexteinträge bleiben draußen; nicht belegbare Claims werden zurückgehalten; fehlendes oder geändertes ausgewähltes Original blockiert den Export und hinterlässt kein unfertiges Paket. | **Ausschließlich isolierte synthetische Negativprobe** oder belegter Entwicklungsnachweis plus minimaler Zielsystemnachweis; niemals produktive Originale verändern. | OFFEN-NACHWEIS |
| **R13** | Regelmäßiges Beenden und Wiederöffnen bewahrt lokale Falldaten; DOM dokumentiert Aufbewahrung/Backup/Restore-Verantwortung und einen risikoarmen Wiederherstellungsweg. Keine Behauptung einer nicht vorhandenen automatischen Backupfunktion. | Kontrollierter Neustart; Betreibervermerk zum Sicherungskonzept. Gefährliche Restore-Probe nur isoliert, falls nötig. | OFFEN-NACHWEIS |
| **O01** | **Scope-Freeze vor Zielsystemprüfung:** DOM legt Ziel-OS/Gerät, Quellstand, Lieferform (bestehendes Repo/Starter), optionale PDF/OCR-/KI-Grenzen, private Datenhaltung und bekannte Ausschlüsse schriftlich fest. | Einmalige DOM-Entscheidung mit Datum; keine nachträgliche Pflicht zur Universal-OS-/Installer-Abnahme. | OFFEN-ENTSCHEIDUNG |
| **O02** | **Schlussgutachten:** Alle 17 vorstehenden IDs bewertet; P0/P1 geschlossen oder NO-GO, P2 entschieden, fehlende Nachweise und Abweichungen klassifiziert; DOM dokumentiert endgültiges GO/NO-GO einschließlich Release-/Merge-Entscheidung. | Unterschriebener/ausdrücklich bestätigter Schlussvermerk mit Begründung, Datum, geprüfter SHA und ggf. Restbefundliste. | OFFEN-ENTSCHEIDUNG |

**Umfang:** D01–D03 = 3 bereits dokumentierte Entwicklungsnachweise; R01–R13 = 13 gebündelte Zielsystem-/Funktionspunkte; O01–O02 = 2 Betreiberentscheidungen. **Summe: 18, keine versteckte Unterliste mit weiteren Muss-Punkten.** Ein einzelner zusammenhängender synthetischer Browser-Durchlauf darf mehrere R-IDs abdecken.

## 3. Nachweisprotokoll – eine Zeile je ID, kein neues Prüfregister

Für jede der 18 IDs werden in **dieser** Liste die Felder geführt:

`ID | endgültiger Status | Datum | Prüfumgebung (DEV / Zielsystem) | konkreter Nachweis (Link, Logauszug oder Lauf-ID) | Befundklasse / Priorität | Restbedarf / DOM-Entscheidung`

Solange noch nicht durchgeführt, bleiben die R- und O-IDs explizit `OFFEN`. Der Nachweis eines CI-Erfolgs wird nicht als Beleg für eine reale Browser-/Geräteprüfung umetikettiert. Nachweise dürfen sich über mehrere IDs erstrecken. Quellmaterial bleibt privat; Screenshots und Protokolle mit echten Falldaten gehören nicht in öffentliche GitHub-Kommentare.

**Befundklassen:** `PRODUKTFEHLER`, `UMGEBUNG`, `NACHWEIS_FEHLT`, `BETREIBERENTSCHEID`. Zusätzlich `P0`, `P1`, `P2` bei tatsächlichem Produktfehler, sonst keine künstliche Fehlerpriorität. Bereits bestandene Tests werden wiederverwendet. Abweichungen werden gesammelt; kein fortlaufendes Nacharbeiten einzelner P2 während der Prüfphase.

## 4. Feste Reihenfolge und Stop-Regeln

1. **Freigabe der Liste und O01:** DOM bestimmt Zielgerät und Funktionsscope. Ab dann gilt die Liste als **eingefroren**. Abnahmestart, nicht Produktneubau.
2. **Nachweise übernehmen:** D01–D03 sind für den genannten Quellstand bereits DEV-belegt; nur ein tatsächlicher relevanter Codewechsel kann einen **betroffenen** Nachweis erneuern.
3. **Zielsystem in einem gebündelten Durchlauf:** R01–R13 gezielt mit synthetischen Daten; bereits nachgewiesene Schritte überspringen. Keine ungeplanten Neuinstallationen, Neustarts, Zweitinstanzen oder Veränderungen realer Produktivdaten.
4. **Befunde gesammelt schließen:** P0/P1 sofort vor abhängigem Weiterprüfen behandeln; P2 spätestens vor Feature-Freeze entscheiden. Nach Korrekturen **nur betroffene IDs** erneut prüfen. Keine pauschale Regressionsrunde ohne begründeten konkreten Einfluss.
5. **O02 Schlussgutachten:** Jeder Punkt hat einen finalen Status, Nachweis bzw. dokumentierte Unmöglichkeit und ggf. Restbedarf. DOM entscheidet GO oder NO-GO; danach wird diese Abnahme als **ABGESCHLOSSEN** markiert.

## 5. Harte, endliche Abschlussdefinition

- **GO:** Alle für den in O01 festgelegten Scope obligatorischen IDs sind `BESTANDEN` (DEV beziehungsweise Runtime, je nach ID). `ENTFÄLLT` gilt ausschließlich für zuvor ausdrücklich ausgeklammerte optionale Funktionen und braucht DOM-Begründung. Keine offenen P0/P1, P2 dokumentiert und entschieden, Sicherheits- und Datenschutzgrenzen eingehalten, O02 unterzeichnet.
- **NO-GO:** Jeder verbleibende Muss-Punkt `NICHT-BESTANDEN` oder `OFFEN`, fehlende verbindliche Betreiberentscheidung, ungeklärter P0/P1 oder nicht nachgewiesene zentrale Sicherheitsgrenze führt zur **abgeschlossenen** Entscheidung NO-GO mit konkret begrenzter Mängelliste.
- **Kein endloses Offenhalten:** Fehlende Nachweise werden nicht durch immer neue Prüfpunkte ersetzt. NO-GO schließt den Prüfprozess ab; ein späterer neuer Kandidat benötigt **nur einen neuen Freigabeentscheid und gezielte Wiederprüfung der betroffenen IDs**, nicht die stillschweigende Wiederholung aller 18 Punkte.
- **Änderungsgrenze:** Nach Scope-Freeze keine neuen Muss-Anforderungen ohne vorhandenen Blueprint-/Produktvertrag oder zwingenden P0/P1-Sicherheitsbefund und ausdrückliche DOM-Freigabe. Neue Produktideen gehören in einen separaten Ausbauzyklus, **nicht** in diese Abnahme.
- **Release:** Der Draft-PR bleibt bis zu DOMs ausdrücklicher Entscheidung ungemergt. Keine automatische Veröffentlichung, kein Release-Tag und keine behauptete Vollfreigabe durch CI.

## 6. Schlussvermerk (wird erst am Ende ausgefüllt)

| Feld | Eintrag |
| --- | --- |
| Prüfstand / Commit-SHA | OFFEN – von DOM in O01 zu bestimmen |
| Zielsystem / Betriebssystem | OFFEN – O01 |
| Optionale PDF-/OCR-Freigabe | OFFEN – O01 |
| Optionale lokale KI | OFFEN – O01 |
| Entwicklungsläufe | GitHub CI 41027903511; Python 169/169, Python 3.14 gezielt, Windows/macOS Launcher erfolgreich |
| R01–R13 Nachweise / Restbedarf | OFFEN – Abnahme noch nicht gestartet |
| P0/P1 und P2 Bewertung | OFFEN – zum Schlussgutachten |
| Endentscheidung | **NOCH KEIN GO/NO-GO** |
| DOM-Bestätigung / Datum | OFFEN |
| Prozessstatus | **VORBEREITET, NICHT GESTARTET** |
