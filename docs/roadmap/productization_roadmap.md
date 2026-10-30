# Productization roadmap

This file is the preferred sorted mirror of `docs/02_productization_roadmap.md`.

## Goal

Turn `local_case_organizer` from a good repository into a local end-user product that normal people can operate without living in the terminal.

## Product target

A user should be able to:

1. download the project
2. run the starter path
3. see a browser UI
4. add files
5. import them
6. build a register
7. build a timeline
8. export a handoff package

## Phase 1 — front door and basic workflow

Status: already started.

Target:

- local browser UI as the main front door
- setup through `start_here`
- inbox upload in the browser
- import button
- register button
- timeline button
- export button
- simple status cards
- next-step guidance

## Phase 2 — dossier editing layer

Target:

- editable register fields in the browser
- editable timeline rows in the browser
- visible document-group assignment
- visible export selection state
- file-to-event linking
- entities / people / institutions layer

## Phase 3 — export polish

Target:

- export only selected records
- export manifest
- zipped handoff package
- clearer delivery summary
- visible export history

## Phase 4 — cross-platform polish

Target:

- same behavior on Windows, Linux, and macOS
- clearer path-opening behavior
- better file-upload feedback
- friendlier error messages
- release-ready starter paths

## Phase 5 — release mode

Target:

- GitHub releases
- simple download package
- starter files per operating system
- short offline user guide inside the release package


## CASE-A1 (development branch) – case workspaces, provenance and links

- Legacy single-case workspace remains the default without migration.
- Explicit create-case/list-cases and --case select private, isolated workspaces.
- UI runs for one selected case per process; it does not silently switch scopes.
- Verify-integrity is manual only; source originals are never modified.
- A local append-only journal records verification results by file ID (no file contents).
- Evidence map displays only manually entered document-event-entity links.
- These are development features, not an operator acceptance or legal assessment.


## CASE-A2 (development branch) – provenance-based timeline suggestions

- Explicit \`python run.py [--case ID] propose-events\` and browser button.
- Reads only verified, registered, imported originals (.txt/.md/.csv/.eml, UTF-8)
  under a strict per-file byte limit; does not OCR, invoke an LLM or use the network.
- Extracts unverified YYYY-MM-DD and DD.MM.YYYY date mentions with source file ID,
  line number, excerpt, and deterministic suggestion ID.
- A user must **explicitly accept** a suggestion to append a draft timeline row.
  Before writing, the exact source is read and hash-checked again.
- Detects identical-content hashes across imported, scanned text items as
  a review hint. No automatic claims about truth, legality or completeness.
- Existing timelines, original files, imports, exports and legacy workspace
  remain in place; accepted events use the existing timeline CSV format.
- No private files, proposal excerpts or original source paths are committed
  to GitHub. This package is not the final acceptance.


## CASE-A3/A4 (development branch) – Local PDF/OCR index and sourced claims

- Extraction is **explicit**, opt-in, and scoped to a case's verified imported
  original: \`python run.py --case <id> index-document <DOC-ID> [--ocr]\`.
  The default legacy workspace remains available without \`--case\`.
- Supported local plaintext: UTF-8 TXT/MD/CSV/EML. PDFs use installed
  \`pdftotext\` (preferred) or optional Python \`pypdf\`.
  OCR requires explicit \`--ocr\` and preinstalled \`tesseract\`; scanned
  PDFs also require \`pdftoppm\`. No tool installs or network calls occur.
- The indexed derivative is a bounded JSON document under the existing ignored
  \`data/working/text_index/\` scoped to the selected case. The raw original is
  never altered or committed. Per-file size, page count, text and execution
  duration are bounded. Search verifies the original hash and excludes stale
  indexes: \`python run.py --case <id> search-text "needle"\`.
- Source-linked claims contain file ID, exact quote, page reference, a separate
  human-entered statement, and manual review status.
  Creating/reviewing a claim verifies the original source and matches the
  quote to the indexed page verbatim. Reviewed means a human reviewed the
  record; it does **not** certify truth or legal conclusions.
- Claims appear in the evidence graph and, when a user explicitly builds
  a handoff export, in \`claims.csv\`; private text-index derivatives are
  never included in exports by default.
- No server beyond the existing local browser UI, no forced dependencies,
  no cloud LLM, no automatic legal evaluation, no production installation.


## CASE-A5 (development) – manually grouped claim comparison

- Each comparison links an existing claim ID, operator-supplied topic key,
  explicitly selected date / decimal amount / plain text kind and value.
- Cross-document differences are flagged only for **two or more different
  source documents** and distinct normalized values under the same topic.
- No claims are automatically edited or pronounced false.
- Adding a link checks that the claim's original hash and exact quote still
  match the existing indexed source. No OCR/LLM or external services are called.
- Comparison data are kept in the selected local case register directory,
  never in GitHub. \`python run.py [--case ID] compare-claims\` is read-only.
- Existing case, source register, claim and export data remain undisturbed.


## CASE-A6 (development) – metadata-only local edit journal

- Atomic CSV replacements with two-phase \`prepared\` / \`committed\` journal
  entries for the existing register, timeline, entities, claims and comparison
  work areas. Routine generation of the register/timeline uses the same writer.
- Only timestamps, table area, affected row count and SHA-256 digests are
  stored; personal text, source originals and credentials are not copied.
- \`python run.py [--case ID] audit-history\` and a read-only UI panel show
  completed changes. No local username is asserted (there is no login system).
- A prepared-only record may remain after a power failure; it is **not** reported
  as committed.
- The journal has a size limit and never deletes entries automatically.
- This is *not* a signed or tamper-proof compliance trail and does not store
  earlier full document versions. Multi-process serialization is not guaranteed.
  Final acceptance remains separate at the end of expansion.

## CASE-A7/A8 – Browser-Fallverwaltung und neutraler Dossier-Export (Entwicklung)

- Im bestehenden lokalen Browser können separate Fälle erstellt, aufgelistet und bewusst
  ausgewählt werden. Pro Tab wird die Fall-ID in Session Storage gehalten; sie wird
  als Header an die vorhandenen lokalen API-Routen weitergereicht. Jeder Request
  validiert die Fall-ID erneut, bevor auf fallbezogene Daten zugegriffen wird.
- Auswahl des Legacy-Standard-Arbeitsbereichs bleibt möglich. Nicht gespeicherte
  Änderungen werden beim Wechsel nicht automatisch übertragen.
- Die bestehende Export-Funktion ergänzt DOSSIER.md und EVIDENCE_INDEX.csv im
  bisherigen ZIP, Manifest und SHA-256-Checksumme. Nur explizit für den Export
  ausgewählte Originale werden als Anlage kopiert und vorher hash-verifiziert.
- Dossier: Belegverzeichnis, Timeline-Einträge, quellenbezogene Aussagen und deren
  Review-Status. Ein Reviewstatus ist keine Tatsachenbestätigung. Keine
  juristische Bewertung und keine ungeprüften oder automatisch getroffenen Aussagen.
- Die Browser-Vorschau zählt ausgewählte Unterlagen, Timeline-Einträge und
  verknüpfte Aussagen, führt aber selbst keine Originalkopie durch.
- Datenschutz: Die Fallinhalte bleiben lokal; auf GitHub liegen nur Programmcode
  und synthetische Tests. Der vorhandene Startweg bleibt verbindlich.
- Abnahme weiterhin gesammelt nach dem Ausbau. Keine Runtime-Prüfung oder
  Installation auf Betreibergeräten.


## CASE-A9 – Aufgaben und manuelle Wiedervorlagen (Entwicklung)

- Bedienerseitig eingegebene Aufgaben mit Datum, Priorität, Status und Links
  auf im jeweiligen Fall bekannte Datei-IDs.

- Statusanzeige für eingegebene Termine: bevorstehend/heute/vergangen;
  **keine** automatische Berechnung juristischer Fristen.
- Browser und bestehende CLI (`tasks`, `add-task`, `update-task`).
- Fallgebundene Aufgaben unter `data/register/tasks.csv` mit dem bestehenden
  metadatenbasierten Audit-Journal.
- Keine Hintergrunddienste, Timer, E-Mail, externe Kalender oder Cloud.


## CASE-A10 – optionale lokale KI-Review-Schnittstelle (Entwicklung)

- \`prepare-ai-review\` legt auf ausdrücklichen Wunsch ein begrenztes Paket
  aus **zuvor indizierten und noch hash-geprüften** Originalen lokal unter
  \`data/working/ai_exchange/outbox/\` ab. Es kann private Textauszüge
  enthalten. Es erfolgt **keine** automatische Übertragung oder LLM-Abfrage.
- Ein vertrauenswürdiges, vom Betreiber separat kontrolliertes lokales LLM
  kann eine JSON-Liste mit Dokument-ID, Seite, exakt belegtem Zitat und
  vorgeschlagener Interpretation erzeugen.
- \`import-ai-review\` (lokales Inbox-JSON) bzw. der Browser-Import (eingefügtes
  JSON) validieren jede Quellenstelle erneut. Ergebnisse bleiben zunächst
  untrusted \`pending_review\` im fallgebundenen Register.
- Nur ein ausdrücklicher Einzelentscheid \`review-ai-suggestion\` kann einen
  Vorschlag verwerfen oder als normalen \`draft\`-Claim erzeugen. Eine
  Quelle beweist nicht die Interpretation, ein AI-Draft ist **niemals**
  automatisch Review- oder Wissensstand.
- Vorhandenes Claim-/Audit-System wird wiederverwendet; keine neue Datenbank,
  kein zweiter Browser, keine API-Schlüssel oder automatische OS-/Netz-Aktionen.
- Dieses Paket ist eine **Integrationsnaht**, kein eingebautes generatives
  Modell und keine installierte Drittanbieter-KI. Die vollständige KI-Integration
  bleibt bei Bedarf eine gesonderte Entscheidung im bestehenden ToF-Ökosystem.


## Sicherheitsnachbesserung vor Feature-Freeze – lokales Browser-Gateway

- Der Browser-Startweg verweigert jetzt Nicht-Loopback-Adressen. Keine
  direkte öffentliche HTTP-Freigabe; keine Nutzerverwaltung vorhanden.
- Browser-POST-Requests müssen einen spezifischen, same-origin gesetzten
  HTTP-Header besitzen. Cross-site Navigations-/Formular-POSTs werden
  abgewiesen; vorhandene Browser-UI setzt den Header automatisch.
- Origin und Sec-Fetch-Site werden geprüft, soweit vorhanden, und die
  HTTP-Anfragegröße begrenzt. Dies ist **kein** Authentifizierungs- oder
  Berechtigungssystem für andere lokale Prozesse.
- Reservierte Kennung \`legacy-default\` kann nicht als zusätzliche Fallakte
  erzeugt werden, um die Legacy-Auswahl nicht zu überlagern.
- Betriebs-/Gesamtabnahme wie vereinbart erst nach dem Ausbaumodus.

## A11 – Kontrollierte organisatorische Dokumentverknüpfungen (Entwicklungsbranch)

- Reuse of exact, type-separated, hash-verified reference groups in the existing
  `case_connections` and `case_narrative` modules.
- Explicit local review: `pending_review`,
  `accepted_as_organizational_link`, `dismissed`, or
  `recheck_required` after source-quote or membership change.
- Source-set signature is checked again server-side before a review decision;
  operator confirmation never certifies document truth, legal status, an event,
  or an AI interpretation.
- Review metadata is stored only within the selected case using the established
  audited CSV writer. No copies of raw text or original documents are made.
- Existing single-page narrative shows the proof references, state and deliberate
  accept/dismiss buttons. The same browser remains local-loopback only.
- Selected-only handoffs show a review status only for the exact selected source
  set. Partial selections cannot inherit a full-case acceptance and show a
  neutral `pending_review` label instead of revealing that out-of-scope
  members exist. Excluded file names, citations and IDs remain private.
- No cloud service, new database, background worker, second browser, or alternate
  start path. Review metadata is not a cryptographically tamper-proof audit.
- Current scope is development; GitHub CI is not end-device/operator acceptance.

## A12 – Fallbezogenes Quellen-Prüf-Cockpit (Entwicklungsbranch)

- Die bereits vorhandene Fallübersicht bietet ein zusammengeführtes, lesendes
  Prüfcockpit für Dokumente mit offenem Prüfstatus, quellengebundene Claims und
  organisatorische Dokumentverbindungen aus A11.
- Claims werden für die Anzeige erneut gegen das gehashte Original und das
  exakte Seitenzitat geprüft. Ist ein Nachweis ungültig, werden weder Aussage
  noch Zitat in der Prüfliste angezeigt; der Eintrag wird nur als
  `recheck_required` geführt. Frühere Review-Metadaten werden nicht heimlich
  verändert.
- Die einzige direkte Entscheidung ist eine ausdrücklich bestätigte manuelle
  Claim-Prüfung über den bereits vorhandenen, serverseitig nochmals
  quellenprüfenden `/api/review-claim`-Pfad. Andere Aktionen navigieren zu den
  vorhandenen Dokument- und Verknüpfungsdialogen.
- Die Prüfliste ist auf zwanzig Beispiele je Bereich begrenzt. Zähler und
  Unvollständigkeits-Hinweis machen die Anzeigegrenzen sichtbar.
- Keine zweite Datenhaltung, automatische Tatsachen- oder Rechtsfeststellung,
  unbemerkte Exportfreigabe, neue Runtime, Cloud-Dienste oder neuen Startweg.
- CI-Nachweis ist eine Entwicklungsprüfung, nicht die Betreiberabnahme.

## A13 – Lokale Quellenabdeckung und organisatorische Lücken (Entwicklungsbranch)

- Der vorhandene lokale Browser zeigt nach ausdrücklichem Öffnen des Panels
  einen **nur lesenden**, fallbezogenen Abdeckungsbericht. Keine Hintergrund-
  Verarbeitung, OCR, LLM-Abfrage oder neue Runtime.
- Ausschließlich registrierte Originale werden mit vorhandenen Provenienzdaten
  abgeglichen. Für begrenzt große Dateien wird SHA-256 erneut geprüft.
  Ein Textindex zählt nur dann als verfügbar, wenn er zum gehashten Original
  passt und durchsuchbaren Text enthält.
- Getrennte Befunde: Quelle fehlt/verändert, Provenienz unzureichend,
  Quelle zu groß oder Textformat nicht unterstützt, Index fehlt oder
  enthält keinen durchsuchbaren Text. **Index fehlt ≠ Original fehlt.**
- Manuelle Timeline-, Beteiligten-, Aufgaben- und Claim-Einträge werden auf
  fehlende oder unbekannte Dokument-ID-Verknüpfungen geprüft. Diese Hinweise
  sind organisatorisch und keine Aussagen über ein tatsächlich fehlendes
  Beweismittel.
- Der Bericht begrenzt den Scan auf 120 registrierte Quellen und die Anzeige
  auf 40 Beispiele; nicht gescannte Quellen und Anzeigegrenzen werden offen
  ausgewiesen. Ungeprüfte Quellen werden nicht als verifiziert gezählt.
- Der Bediener gelangt zu den bestehenden Dokument-, Such- und Integritäts-
  Ansichten. Alle Folgeaktionen bleiben separat und ausdrücklich.
- Die Aktenvollständigkeit außerhalb des registrierten lokalen Bestands ist
  **nicht ermittelbar**; keine Tatsachenbewertung, Rechtsberatung,
  selbstständige Freigabe oder Modifikation des Dossier-Exports.
- Entwicklungsnachweise sind von Zielsystem-/Betreiberabnahme zu trennen.

## A14 – Prüfaufgaben mit Quellen- und Fragenbezug (Entwicklungsbranch)

- Im vorhandenen lokalen Browser können aus **aktuell angebotenen** offenen
  Dokument-, Claim- und Verknüpfungsprüfungen sowie fallbezogenen offenen
  Organisationsfragen **nach ausdrücklicher Bestätigung** Aufgaben erstellt
  werden. Die Anzeige ist begrenzt; Nichtanzeige beweist keine Erledigung.
- Der bestehende Aufgaben-Store `data/register/tasks.csv` und sein
  metadatenbasiertes Änderungsjournal bleiben die alleinige Datenhaltung.
  Drei optionale Spalten (`review_kind`, `review_ref`, `review_token`)
  verknüpfen Aufgaben mit ihrem ursprünglichen Prüfkontext. Bestehende
  Aufgaben-CSV-Dateien bleiben lesbar und werden beim nächsten regulären
  Schreiben ohne Verlust vorhandener Einträge erweitert.
- Der Server validiert Typ, Referenz und aktuellen SHA-256-Kontext erneut.
  Doppelte offene Aufgaben für denselben Prüfpunkt werden vermieden.
  Bereits geschlossene Aufgaben dürfen durch ausdrückliche Bedienhandlung
  neu erstellt werden.
- Dokumentaufgaben berücksichtigen die gegen das Original geprüfte
  Abdeckungsstufe und die registrierte SHA-256. Geänderte oder nicht mehr
  sichtbare Prüfkontexte erscheinen als Hinweis zur erneuten manuellen
  Betrachtung; Status oder Aufgabentext werden nicht stillschweigend geändert.
- Die Umsetzung erstellt **keine** Termine, Erinnerungen, Rechtsfristen,
  fachlichen Aussagen, Quellenfreigaben oder Exporte. Eine auf `done`
  gestellte Aufgabe führt ausdrücklich zu keiner Review-Zustandsänderung.
- Das Fall-Scope bleibt verbindlich. Andere Fälle, unabhängige Aufgaben,
  Originale, KI-Vorschläge und die externe Anwalt-Übergabe werden nicht verändert.
- GitHub-Tests sind Entwicklungsnachweise, keine Betreiber-/Runtime-Abnahme.
