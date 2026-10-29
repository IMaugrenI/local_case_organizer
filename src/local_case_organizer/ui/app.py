from __future__ import annotations

import html
import json
import os
import platform
import subprocess
import sys
import webbrowser
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from local_case_organizer.cases import create_case, get_active_case, list_cases, using_case
from local_case_organizer.ui.case_selection import requested_case
from local_case_organizer.ui.ui_security import allow_local_post, allowed_ui_host
from local_case_organizer.ui.multipart_upload import parse_multipart_files
from local_case_organizer.ui.quick_intake import quick_organize_inbox
from local_case_organizer.ui.autopilot import autopilot_status, process_autopilot
from local_case_organizer.ui.case_briefing import case_briefing
from local_case_organizer.ui.simple_actions import update_document, add_manual_event, add_manual_entity, prepare_local_search, bulk_export_selection
from local_case_organizer.document_text import index_document, search_text
from local_case_organizer.claims import add_claim, read_claims, set_review_status
from local_case_organizer.comparison import add_comparison, comparison_report
from local_case_organizer.audit import recent_changes
from local_case_organizer.tasks import add_task, update_task, task_board
from local_case_organizer.ai_exchange import (prepare_ai_packet, import_ai_suggestions,
                                               read_ai_suggestions, review_ai_suggestion)
from local_case_organizer.graph import evidence_graph
from local_case_organizer.integrity import recent_integrity_runs, verify_integrity
from local_case_organizer.entities.store import ENTITY_FIELDS, read_entity_rows, write_entity_rows
from local_case_organizer.export.builder import build_export_package
from local_case_organizer.export.dossier import dossier_preview
from local_case_organizer.export.history import read_export_history
from local_case_organizer.imports.ingest import import_sources
from local_case_organizer.paths import create_local_workspace, describe_workspace, get_repo_root, get_workspace_paths
from local_case_organizer.register.generator import build_document_register
from local_case_organizer.register.store import REGISTER_FIELDS, read_register_rows, write_register_rows
from local_case_organizer.timeline.suggestions import accept_candidate, propose_events
from local_case_organizer.timeline.generator import build_timeline_template
from local_case_organizer.timeline.store import TIMELINE_FIELDS, read_timeline_rows, write_timeline_rows


HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>local_case_organizer</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #f5f7fb; color: #18212f; }
    .wrap { max-width: 1280px; margin: 0 auto; padding: 24px; }
    .hero, .panel, .upload-box, .file-list, .paths, .log, .editor { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
    .hero { padding: 24px; }
    h1, h2, h3 { margin-top: 0; }
    .lead { color: #4b5563; line-height: 1.5; }
    .note { font-size: 14px; color: #6b7280; }
    .section-title { margin-top: 28px; margin-bottom: 10px; }
    .next-step { margin-top: 18px; background: #ecfeff; border: 1px solid #a5f3fc; color: #164e63; border-radius: 14px; padding: 16px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-top: 20px; }
    .card { background: white; border-radius: 14px; padding: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
    .value { font-size: 28px; font-weight: bold; margin-top: 8px; }
    .actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-top: 20px; }
    .upload-row, .editor-actions { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
    button { border: 0; border-radius: 12px; padding: 14px 16px; font-size: 15px; cursor: pointer; background: #1f6feb; color: white; }
    button.secondary { background: #0f766e; }
    button.light { background: #475569; }
    button.ghost { background: #e5e7eb; color: #111827; }
    input[type=file] { max-width: 100%; }
    .hint { margin-top: 12px; color: #6b7280; font-size: 14px; }
    .paths, .log { margin-top: 18px; }
    .paths { background: #0f172a; color: #e2e8f0; overflow: auto; }
    .log { background: #111827; color: #d1fae5; min-height: 180px; }
    pre { margin: 0; white-space: pre-wrap; word-break: break-word; }
    ul { margin: 8px 0 0 18px; padding: 0; }
    .editor { overflow: auto; }
    table { width: 100%; border-collapse: collapse; min-width: 980px; }
    th, td { text-align: left; border-bottom: 1px solid #e5e7eb; padding: 10px; vertical-align: top; }
    th { background: #f8fafc; position: sticky; top: 0; }
    td.readonly { color: #475569; font-size: 13px; }
    input[type=text], textarea, select { width: 100%; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px; font: inherit; background: white; }
    textarea { min-height: 72px; resize: vertical; }
    .two-col { display: grid; grid-template-columns: 1fr; gap: 20px; }
    .chip-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
    .chip { background: #eef2ff; color: #3730a3; border: 1px solid #c7d2fe; border-radius: 999px; padding: 4px 10px; font-size: 12px; }
    @media (min-width: 1100px) { .two-col { grid-template-columns: 1fr 1fr; } }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"hero\">
      <h1>local_case_organizer</h1>
      <p class=\"lead\">A simple local front door for building a clean case dossier. Add files, import them, build a register, edit the working tables, and export a handoff package.</p>
      <p class=\"note\">This UI is local-only. Your private files stay on your machine.</p>
    </div>

    <div class=\"next-step\" id=\"next-step\">Loading next step...</div>

    <h2 class=\"section-title\">Choose your case</h2>
    <div class=\"editor\">
      <p class=\"hint\">Each case has its own private local workspace. Switching cases reloads the browser; save any unsaved changes first.</p>
      <div class=\"editor-actions\">
        <label>Case <select id=\"case-selector\"></select></label>
        <button type=\"button\" class=\"secondary\" onclick=\"openSelectedCase()\">Open selected case</button>
        <button type=\"button\" class=\"ghost\" onclick=\"loadCaseHub()\">Refresh case list</button>
      </div>
      <div class=\"editor-actions\">
        <label>New case ID <input id=\"new-case-id\" type=\"text\" placeholder=\"my-case\" maxlength=\"48\"></label>
        <label>Display title <input id=\"new-case-title\" type=\"text\" placeholder=\"Optional private title\" maxlength=\"120\"></label>
        <button type=\"button\" onclick=\"createCaseFromUI()\">Create a separate case</button>
      </div>
      <div id=\"case-hub-result\" class=\"hint\" aria-live=\"polite\"></div>
    </div>

    <h2 class=\"section-title\">Current status</h2>
    <div class=\"grid\" id=\"cards\"></div>

    <h2 class=\"section-title\">Add files</h2>
    <div class=\"upload-box\">
      <div class=\"upload-row\">
        <input id=\"fileInput\" type=\"file\" multiple>
        <button class=\"secondary\" onclick=\"uploadFiles()\">Upload selected files to inbox</button>
        <button class=\"ghost\" onclick=\"runAction('open-inbox')\">Open inbox folder</button>
      </div>
      <div class=\"hint\">You can either upload files here or open the inbox folder and place files there yourself.</div>
    </div>

    <h2 class=\"section-title\">Main actions</h2>
    <div class=\"actions\">
      <button onclick=\"runAction('setup')\">1. Prepare workspace</button>
      <button class=\"secondary\" onclick=\"runAction('import')\">2. Import inbox files</button>
      <button onclick=\"runAction('build-register')\">3. Build register</button>
      <button onclick=\"runAction('build-timeline')\">4. Build timeline</button>
      <button class=\"secondary\" onclick=\"runAction('export-package')\">5. Build export package</button>
      <button class=\"ghost\" onclick=\"showDossierPreview()\">Preview dossier contents</button>
    </div>

    <div id=\"dossier-preview\" class=\"hint\" aria-live=\"polite\"></div>

    <h2 class=\"section-title\">Helpful actions</h2>
    <div class=\"actions\">
      <button class=\"ghost\" onclick=\"runAction('open-register')\">Open register folder</button>
      <button class=\"ghost\" onclick=\"runAction('open-exports')\">Open exports folder</button>
      <button class=\"light\" onclick=\"runAction('doctor')\">Run doctor</button>
      <button class=\"light\" onclick=\"refreshAll()\">Refresh all</button>
    </div>

    <div class=\"two-col\">
      <div>
        <h2 class=\"section-title\">Document register</h2>
        <div class=\"editor\">
          <div class=\"editor-actions\">
            <button onclick=\"loadRegister()\">Load register</button>
            <button class=\"secondary\" onclick=\"saveRegister()\">Save register changes</button>
          </div>
          <div class=\"hint\">Editable fields are review status, document group, export selection, and note. The right-hand columns show where a file already appears in the timeline or entities table.</div>
          <div id=\"register-editor\" class=\"hint\">Register will appear here.</div>
        </div>
      </div>
      <div>
        <h2 class=\"section-title\">Timeline</h2>
        <div class=\"editor\">
          <div class=\"editor-actions\">
            <button onclick=\"loadTimeline()\">Load timeline</button>
            <button onclick=\"addTimelineRow()\">Add timeline row</button>
            <button class=\"secondary\" onclick=\"saveTimeline()\">Save timeline changes</button>
          </div>
          <div class=\"hint\">Use <code>linked_file_ids</code> to connect timeline events to file IDs from the register.</div>
          <div id=\"timeline-file-hints\" class=\"hint\">Known file IDs will appear here after the register is loaded.</div>
          <div id=\"timeline-editor\" class=\"hint\">Timeline will appear here.</div>
        </div>
      </div>
    </div>

    <h2 class=\"section-title\">Suggested timeline dates (manual review)</h2>
    <div class=\"editor\">
      <div class=\"editor-actions\">
        <button type=\"button\" onclick=\"loadTimelineCandidates()\">Find date mentions in imported text</button>
      </div>
      <p class=\"hint\">Only verified UTF-8 TXT, MD, CSV and EML originals; no OCR or cloud.
      Suggestions are NOT verified events. Click Add draft for each item you choose.</p>
      <div id=\"timeline-candidates\" aria-live=\"polite\">No suggestions requested.</div>
    </div>

    <h2 class=\"section-title\">Entities / people / institutions</h2>
    <div class=\"editor\">
      <div class=\"editor-actions\">
        <button onclick=\"loadEntities()\">Load entities</button>
        <button onclick=\"addEntityRow()\">Add entity row</button>
        <button class=\"secondary\" onclick=\"saveEntities()\">Save entity changes</button>
      </div>
      <div class=\"hint\">Use <code>linked_file_ids</code> to connect people, institutions, or companies to file IDs from the register.</div>
      <div id=\"entity-file-hints\" class=\"hint\">Known file IDs will appear here after the register is loaded.</div>
      <div id=\"entity-editor\" class=\"hint\">Entities will appear here.</div>
    </div>

    <h2 class=\"section-title\">Verified links / Evidence map</h2>
    <div class=\"editor\">
      <div class=\"editor-actions\"><button onclick=\"loadEvidenceGraph()\">Refresh evidence map</button></div>
      <p class=\"hint\">Only explicitly entered relationships are shown. Links are not judgments of factual or legal truth.</p>
      <div id=\"evidence-graph\" aria-live=\"polite\"></div>
    </div>

    <h2 class=\"section-title\">Integrity checks</h2>
    <div class=\"editor\">
      <div class=\"editor-actions\">
        <button onclick=\"runAction(\'verify-integrity\')\">Verify original files now</button>
        <button class=\"secondary\" onclick=\"loadIntegrityHistory()\">Show verification history</button>
      </div>
      <p class=\"hint\">Manual, read-only hash verification. Results are recorded in a local append-only journal.</p>
      <div id=\"integrity-history\" class=\"hint\"></div>
    </div>

    <h2 class=\"section-title\">Private PDF / OCR text index</h2>
    <div class=\"editor\">
      <p class=\"hint\">Manual offline extraction from an imported, hash-verified document. OCR runs only when explicitly selected and the optional local tools are installed. Indexed text stays in the private working folder, never inside original evidence files.</p>
      <div class=\"editor-actions\">
        <label>Document ID <input id=\"text-file-id\" type=\"text\" placeholder=\"DOC-...\"></label>
        <label><input id=\"text-use-ocr\" type=\"checkbox\"> Enable offline OCR</label>
        <button type=\"button\" onclick=\"indexSelectedDocument()\">Index selected document</button>
      </div>
      <div class=\"editor-actions\" style=\"margin-top:16px\">
        <label>Search indexed documents <input id=\"text-query\" type=\"text\" placeholder=\"Search term\"></label>
        <button type=\"button\" class=\"secondary\" onclick=\"searchIndexedDocuments()\">Search local text</button>
      </div>
      <div id=\"text-index-status\" class=\"hint\" aria-live=\"polite\"></div>
      <div id=\"text-search-results\" class=\"hint\"></div>
    </div>

    <h2 class=\"section-title\">Source-linked claims</h2>
    <div class=\"editor\">
      <p class=\"hint\">Claims remain user assertions, even after review. Paste an exact quote from an indexed page. Every new claim starts as a draft; review is a separate manual step.</p>
      <div class=\"editor-actions\">
        <label>Document ID <input type=\"text\" id=\"claim-file-id\" placeholder=\"DOC-...\"></label>
        <label>Page <input type=\"number\" id=\"claim-page\" min=\"1\" max=\"100\" value=\"1\" style=\"width:100px\"></label>
      </div>
      <label>Verbatim source passage<textarea id=\"claim-quote\" maxlength=\"500\"></textarea></label>
      <label>Claim / interpretation (not a verified fact)<textarea id=\"claim-statement\" maxlength=\"800\"></textarea></label>
      <div class=\"editor-actions\">
        <button type=\"button\" onclick=\"saveSourcedClaim()\">Add draft claim</button>
        <button type=\"button\" class=\"secondary\" onclick=\"loadSourcedClaims()\">Refresh claims</button>
      </div>
      <div id=\"claim-results\" aria-live=\"polite\"></div>
    </div>

    <h2 class=\"section-title\">Claim comparisons – possible discrepancies</h2>
    <div class=\"editor\">
      <p class=\"hint\">Manually assign a shared topic and an exact value to distinct source-linked claims.
      Different values flag a review candidate, not a proven contradiction.</p>
      <div class=\"editor-actions\">
        <label>Claim ID <input id=\"compare-claim-id\" type=\"text\" placeholder=\"CLM-...\"></label>
        <label>Topic <input id=\"compare-topic\" type=\"text\" placeholder=\"invoice-amount\"></label>
        <label>Kind <select id=\"compare-kind\"><option value=\"date\">Date</option><option value=\"amount\">Amount</option><option value=\"text\">Text</option></select></label>
        <label>Value <input id=\"compare-value\" type=\"text\" placeholder=\"1250,00\"></label>
        <button type=\"button\" onclick=\"addClaimComparison()\">Link claim value</button>
        <button type=\"button\" class=\"secondary\" onclick=\"loadClaimComparisons()\">Find differences</button>
      </div>
      <div id=\"claim-comparisons\" aria-live=\"polite\"></div>
    </div>

    <h2 class=\"section-title\">Metadata change history</h2>
    <div class=\"editor\">
      <div class=\"editor-actions\"><button onclick=\"loadCaseAudit()\">Refresh change history</button></div>
      <p class=\"hint\">Local, metadata-only record of saved edits. No document contents or verified
      operator identity; incomplete transactions are not presented as committed.</p>
      <div id=\"case-audit\" aria-live=\"polite\"></div>
    </div>

    <h2 class=\"section-title\">Tasks and operator-entered reminders</h2>
    <div class=\"editor\">
      <p class=\"hint\">Manual organizational dates only. Not calculated legal deadlines.
      No background notifications or automatic actions.</p>
      <div class=\"editor-actions\">
        <label>Task <input id=\"task-title\" type=\"text\" maxlength=\"180\" placeholder=\"Review document\"></label>
        <label>Due date <input id=\"task-date\" type=\"date\"></label>
        <label>Priority <select id=\"task-priority\"><option value=\"normal\">Normal</option><option value=\"high\">High</option><option value=\"low\">Low</option></select></label>
        <label>Linked documents <input id=\"task-files\" type=\"text\" placeholder=\"DOC-1,DOC-2\"></label>
        <button type=\"button\" onclick=\"createCaseTask()\">Add reminder</button>
        <button type=\"button\" class=\"secondary\" onclick=\"loadCaseTasks()\">Refresh task list</button>
      </div>
      <div id=\"task-board\" aria-live=\"polite\"></div>
    </div>

    <h2 class=\"section-title\">Optional offline AI review exchange</h2>
    <div class=\"editor\">
      <p class=\"hint\">This app does not run or contact an LLM. An explicit packet may contain
      private excerpts. Hand it to a trusted local assistant yourself. Returned suggestions
      are untrusted; only an individual manual action can create a draft claim.</p>
      <div class=\"editor-actions\">
        <label>Indexed document IDs <input id=\"ai-source-ids\" type=\"text\" placeholder=\"DOC-1,DOC-2\"></label>
        <button type=\"button\" onclick=\"prepareAiHandoff()\">Prepare private handoff</button>
        <button type=\"button\" class=\"secondary\" onclick=\"loadAiSuggestions()\">Review suggestions</button>
      </div>
      <label>Paste JSON suggestions from your trusted local assistant (no automatic transmission)
        <textarea id=\"ai-response-json\" maxlength=\"110000\" placeholder='{"suggestions":[{"file_id":"DOC-1","page":1,"source_quote":"Exact quote","statement":"Draft statement"}]}'></textarea>
      </label>
      <button type=\"button\" onclick=\"importAiResponse()\">Import as untrusted suggestions</button>
      <div id=\"ai-review-result\" aria-live=\"polite\"></div>
    </div>

    <h2 class=\"section-title\">Export history</h2>
    <div class=\"editor\">
      <div class=\"editor-actions\">
        <button onclick=\"loadExportHistory()\">Load export history</button>
      </div>
      <div class=\"hint\">Recent export packages, matching ZIP archives, and manifest files are shown here.</div>
      <div id=\"export-history\" class=\"hint\">Export history will appear here.</div>
    </div>

    <h2 class=\"section-title\">Recent inbox files</h2>
    <div class=\"file-list\"><div id=\"recent-files\">Loading recent files...</div></div>

    <h2 class=\"section-title\">Local paths</h2>
    <div class=\"paths\"><pre id=\"paths\">Loading paths...</pre></div>

    <h2 class=\"section-title\">Activity log</h2>
    <div class=\"log\"><pre id=\"log\">Starting local_case_organizer UI...</pre></div>
  </div>

  <script>
    const originalCaseFetch = window.fetch.bind(window);
    const CASE_CHOICE_KEY = 'lco_active_case_tab';
    // UI messages are keyed, not inferred from document contents or API data.
    const UI_MESSAGES = {
      caseCurrent: ["Aktueller Fall: ", "Current case: "],
      switchStart: ["Ungespeicherte Änderungen vor dem Wechsel zu ", "Save unsaved changes before switching to "],
      switchEnd: [" speichern. Wirklich fortfahren?", "? Continue?"],
      caseCreated: ["Fall ", "Created case "],
      caseCreatedEnd: [" erstellt. Wähle ihn oben aus, um ihn zu öffnen.", " created. Select it above to open."],
      caseCreateError: ["Fall konnte nicht erstellt werden", "Case could not be created"],
      noRecent: ["Keine neuen Dateien im Eingangsordner.", "No files are currently waiting in the inbox."],
      noPackages: ["Noch keine Übergabepakete vorhanden.", "No export packages found yet."],
      noRegister: ["Noch kein Dokumentenregister vorhanden. Erstelle zuerst eines.", "No register rows available yet. Build the register first."],
      noTimeline: ["Noch keine Zeitlinie vorhanden. Erstelle zuerst eine.", "No timeline rows available yet. Build the timeline first."],
      noEntities: ["Noch keine Einträge vorhanden.", "No entity rows available yet. Add your first row."],
      noHints: ["Bekannte Dokumente erscheinen nach dem Laden des Registers.", "Known file IDs will appear here after the register is loaded."],
      preview: ["Dossier-Vorschau: ", "Dossier preview: "],
      selectedDocuments: [" ausgewählte Dokumente, ", " selected documents, "],
      timelineEntries: [" Zeitlinieneinträge, ", " timeline entries, "],
      linkedClaims: [" zugehörige Aussagen. ", " linked claims. "],
      scanning: ["Lokale geprüfte Textquellen werden durchsucht …", "Scanning verified local text originals ..."],
      dateFound: [" Datumsangaben gefunden; ", " date mentions found; "],
      sourceWarnings: [" Quellenwarnungen; ", " source warnings; "],
      duplicates: [" Gruppen mit doppelten Inhalten.", " duplicate-content groups."],
      skippedSources: ["Übersprungene Quellen: ", "Skipped sources: "],
      line: ["Zeile ", "line "],
      addDraft: ["Entwurf hinzufügen", "Add draft"],
      alreadyAdded: ["Bereits hinzugefügt", "Already added"],
      draftAdded: ["Entwurf hinzugefügt", "Draft added"],
      searching: ["Suche läuft …", "Searching ..."],
      matchingPages: [" passende Seiten aus ", " matching pages from "],
      verifiedIndexed: [" geprüften indizierten Dokumenten.", " verified indexed documents."],
      page: ["Seite ", "page "],
      useSource: ["Quelle für Aussage verwenden", "Use source for claim"],
      noClaims: ["Noch keine quellengebundenen Aussagen vorhanden.", "No source-linked claims yet."],
      quote: ["Zitat: ", "Quote: "],
      statement: ["Aussage: ", "Statement: "],
      updateReview: ["Prüfstatus aktualisieren", "Update review status"],
      status_draft: ["Entwurf", "Draft"],
      status_needs_review: ["Prüfung erforderlich", "Needs review"],
      status_reviewed: ["Geprüft", "Reviewed"],
      status_unreviewed: ["Ungeprüft", "Unreviewed"],
      status_flagged: ["Markiert", "Flagged"],
      status_selected_for_export: ["Für Übergabe markiert", "Selected for export"],
      status_yes: ["Ja", "Yes"],
      status_no: ["Nein", "No"],
      status_open: ["Offen", "Open"],
      status_in_progress: ["In Bearbeitung", "In progress"],
      status_done: ["Erledigt", "Done"],
      status_cancelled: ["Abgebrochen", "Cancelled"],
      priority_normal: ["Normal", "Normal"],
      priority_high: ["Hoch", "High"],
      priority_low: ["Niedrig", "Low"],
      noDate: ["Kein Datum", "No date"],
      update: ["Aktualisieren", "Update"],
      noReminders: ["Keine Wiedervorlagen in diesem Fall.", "No reminders in this case."],
      aiConfirm: ["Private Textauszüge werden im Arbeitsbereich dieses Falls gespeichert. Fortfahren?", "Private text excerpts will be written to the selected case working folder. Continue?"],
      savedPacket: ["Lokales Paket gespeichert: ", "Saved local packet: "],
      savedPacketEnd: [". Es wurden keine Daten versendet. Private Quellen sorgfältig behandeln.", ". Nothing transmitted. Handle private source excerpts carefully."],
      proposalsPending: [" Vorschläge warten auf manuelle Prüfung.", " proposals awaiting manual review."],
      exactQuote: [" · Quellenzitat: ", " · exact quote: "],
      draft: [" · Entwurf: ", " · draft: "],
      reject: ["Ablehnen", "Reject"],
      createDraftClaim: ["Aussagenentwurf erstellen", "Create draft claim"],
      noAI: ["Keine KI-Vorschläge importiert.", "No AI suggestions imported."],
      noAudits: ["Noch keine gespeicherten Änderungen vorhanden.", "No saved edits recorded yet."],
      rows: [" Zeilen · ", " rows · "],
      registeredComparisons: [" erfasste Vergleiche · ", " registered comparisons · "],
      possibleDiscrepancies: [" mögliche Abweichungen.", " possible discrepancies."],
      reviewSuggested: ["): Prüfung empfohlen", "): review suggested"],
      noGraph: ["Noch keine Quellenverknüpfungen vorhanden.", "No linked evidence registered yet."],
      unresolved: [" · ungeklärt: ", " · unresolved: "],
      truncated: [" · gekürzte Darstellung", " · showing a limited view"],
      noIntegrity: ["Noch keine Integritätsprüfungen protokolliert.", "No verification runs recorded yet."],
      checked: [" geprüft · ", " checked · "],
      graphAria: ["Beziehungsübersicht für Dokumente, Ereignisse und Einträge", "Document, event and entity relationship map"],
      loadExport: ["Übergabeverlauf geladen.", "Export history loaded."],
      actionFailed: ["Aktion fehlgeschlagen", "Action failed"],
      saveFailed: ["Speichern fehlgeschlagen", "Save failed"],
      emptyTaskNote: ["Manuelle Termine; keine automatische Fristberechnung.", "Manual dates only; no automatically calculated deadlines."],
      status_pending_review: ["Prüfung ausstehend", "Pending review"],
      status_rejected: ["Abgelehnt", "Rejected"],
      status_created_draft_claim: ["Als Entwurf übernommen", "Created draft claim"],
      date_closed: ["Abgeschlossen", "Closed"],
      date_unscheduled: ["Ohne Termin", "Unscheduled"],
      date_overdue: ["Überfällig", "Overdue"],
      date_due_today: ["Heute fällig", "Due today"],
      date_upcoming: ["Anstehend", "Upcoming"],
      date_invalid_manual_date: ["Ungültiges manuelles Datum", "Invalid manual date"],
      indexing: ["Geprüftes Original wird lokal indiziert …", "Indexing the selected verified original locally ..."],
      pages: [" Seiten, ", " pages, "],
      characters: [" Zeichen lokal indiziert.", " characters indexed privately."],
      taskNote: ["Termine werden manuell eingegeben. Angaben dienen nur der Organisation, nicht der rechtlichen Fristberechnung oder externen Benachrichtigungen.", "Dates are entered manually. Indicators are organizational only, not legally calculated deadlines or external notifications."],
      kind_amount: ["Betrag", "Amount"],
      kind_date: ["Datum", "Date"],
      kind_text: ["Text", "Text"],
      createdClaim: ["Aussagenentwurf erstellt: ", "Created draft claim "],
      noTaskDate: ["Kein Datum", "No date"],
      tableNo: ["Nein", "No"],
      tableYes: ["Ja", "Yes"],
      indexFailed: ["Dokument konnte nicht indiziert werden", "Could not index document"],
      editSaved: ["Änderungen gespeichert", "Changes saved"],
    };
    function uiText(key) {
      const localized = UI_MESSAGES[key];
      return localized ? localized[(localStorage.getItem('local_case_organizer_ui_lang') || 'de').startsWith('de') ? 0 : 1] : key;
    }
    function localizedEnum(prefix, value) {
      const id = prefix + '_' + value;
      return Object.prototype.hasOwnProperty.call(UI_MESSAGES,id) ? uiText(id) : value;
    }
    window.fetch = (url, opts = {}) => {
      if (typeof url !== 'string' || !url.startsWith('/api/')) {
        return originalCaseFetch(url, opts);
      }
      const headers = new Headers(opts.headers || {});
      const selected = sessionStorage.getItem(CASE_CHOICE_KEY);
      if (selected) headers.set('X-LCO-Case', selected);
      if ((opts.method || 'GET').toUpperCase() === 'POST') headers.set('X-LCO-UI', 'same-origin-ui');
      return originalCaseFetch(url, {...opts, headers});
    };

    async function loadCaseHub() {
      const response = await fetch('/api/cases');
      const data = await response.json();
      const select = document.getElementById('case-selector');
      const previous = sessionStorage.getItem(CASE_CHOICE_KEY) || data.selected_case;
      select.replaceChildren();
      for (const item of [{case_id:'legacy-default',title:'Legacy default workspace'}, ...(data.cases || [])]) {
        const option = document.createElement('option');
        option.value = item.case_id;
        option.textContent = item.title + ' (' + item.case_id + ')';
        option.selected = item.case_id === previous;
        select.appendChild(option);
      }
      document.getElementById('case-hub-result').textContent = uiText('caseCurrent') + previous;
    }

    function openSelectedCase() {
      const selected = document.getElementById('case-selector').value;
      if (!selected) return;
      if (!window.confirm(uiText('switchStart') + selected + uiText('switchEnd'))) return;
      sessionStorage.setItem(CASE_CHOICE_KEY, selected);
      window.location.reload();
    }

    async function createCaseFromUI() {
      const box = document.getElementById('case-hub-result');
      try {
        const case_id = document.getElementById('new-case-id').value.trim();
        const title = document.getElementById('new-case-title').value.trim();
        const response = await fetch('/api/create-case', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body:JSON.stringify({case_id, title}),
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || uiText('caseCreateError'));
        await loadCaseHub();
        box.textContent = uiText('caseCreated') + result.case_id + uiText('caseCreatedEnd');
      } catch(error) { box.textContent = String(error); }
    }

    let registerRows = [];
    let registerFields = [];
    let timelineRows = [];
    let timelineFields = [];
    let entityRows = [];
    let entityFields = [];

    function appendLog(text) {
      const log = document.getElementById('log');
      log.textContent = `[${new Date().toLocaleTimeString()}] ${text}\n\n` + log.textContent;
    }

    function renderCards(data) {
      const cards = document.getElementById('cards');
      cards.innerHTML = '';
      const items = [
        ['Inbox files', data.inbox_file_count ?? 0],
        ['Imported originals', data.original_file_count ?? 0],
        ['Import batches', data.import_batches ?? 0],
        ['Register files', data.register_files ?? 0],
        ['Export packages', data.export_packages ?? 0],
        ['Selected for export', data.selected_export_count ?? 0],
        ['Entities', data.entity_count ?? 0],
      ];
      for (const [label, value] of items) {
        const el = document.createElement('div');
        el.className = 'card';
        el.innerHTML = `<div>${label}</div><div class=\"value\">${value}</div>`;
        cards.appendChild(el);
      }
    }

    function renderRecentFiles(items) {
      const root = document.getElementById('recent-files');
      if (!items || items.length === 0) {
        root.textContent = uiText('noRecent');
        return;
      }
      const html = ['<ul>'];
      for (const item of items) {
        html.push(`<li>${item}</li>`);
      }
      html.push('</ul>');
      root.innerHTML = html.join('');
    }

    function renderNextStep(text) {
      document.getElementById('next-step').textContent = text;
    }

    function renderKnownFileHints() {
      const labels = registerRows.map(row => `${row.file_id || ''} — ${row.original_name || ''}`).filter(Boolean);
      const html = labels.length
        ? `<div class=\"chip-list\">${labels.map(label => `<span class=\"chip\">${escapeHtml(label)}</span>`).join('')}</div>`
        : uiText('noHints');
      document.getElementById('timeline-file-hints').innerHTML = html;
      document.getElementById('entity-file-hints').innerHTML = html;
    }

    function renderExportHistory(items) {
      const root = document.getElementById('export-history');
      if (!items || items.length === 0) {
        root.textContent = uiText('noPackages');
        return;
      }
      let html = '<table><thead><tr><th>export_dir</th><th>zip_name</th><th>manifest_name</th><th>selected_originals_count</th></tr></thead><tbody>';
      for (const item of items) {
        html += `<tr><td>${escapeHtml(item.export_dir || '')}</td><td>${escapeHtml(item.zip_name || '')}</td><td>${escapeHtml(item.manifest_name || '')}</td><td>${escapeHtml(item.selected_originals_count || '')}</td></tr>`;
      }
      html += '</tbody></table>';
      root.innerHTML = html;
    }

    function buildRegisterTable() {
      const root = document.getElementById('register-editor');
      if (!registerRows.length) {
        root.textContent = uiText('noRegister');
        renderKnownFileHints();
        return;
      }
      const html = ['<table><thead><tr>'];
      const visibleFields = ['file_id','original_name','relative_path','review_status','document_group','selected_for_export','linked_timeline_event_ids','linked_entity_ids','note'];
      for (const field of visibleFields) {
        html.push(`<th>${field}</th>`);
      }
      html.push('</tr></thead><tbody>');
      registerRows.forEach((row, index) => {
        html.push('<tr>');
        html.push(`<td class=\"readonly\">${row.file_id || ''}</td>`);
        html.push(`<td class=\"readonly\">${row.original_name || ''}</td>`);
        html.push(`<td class=\"readonly\">${row.relative_path || ''}</td>`);
        html.push(`<td><select data-register-row=\"${index}\" data-field=\"review_status\">` +
          ['unreviewed','reviewed','flagged','selected_for_export'].map(v => `<option value=\"${v}\" ${row.review_status === v ? 'selected' : ''}>${localizedEnum('status',v)}</option>`).join('') +
          '</select></td>');
        html.push(`<td><input type=\"text\" data-register-row=\"${index}\" data-field=\"document_group\" value=\"${escapeHtml(row.document_group || '')}\"></td>`);
        html.push(`<td><select data-register-row=\"${index}\" data-field=\"selected_for_export\">` +
          ['no','yes'].map(v => `<option value=\"${v}\" ${row.selected_for_export === v ? 'selected' : ''}>${localizedEnum('table',v)}</option>`).join('') +
          '</select></td>');
        html.push(`<td class=\"readonly\">${escapeHtml(row.linked_timeline_event_ids || '')}</td>`);
        html.push(`<td class=\"readonly\">${escapeHtml(row.linked_entity_ids || '')}</td>`);
        html.push(`<td><textarea data-register-row=\"${index}\" data-field=\"note\">${escapeHtml(row.note || '')}</textarea></td>`);
        html.push('</tr>');
      });
      html.push('</tbody></table>');
      root.innerHTML = html.join('');
      renderKnownFileHints();
    }

    function buildTimelineTable() {
      const root = document.getElementById('timeline-editor');
      if (!timelineRows.length) {
        root.textContent = uiText('noTimeline');
        return;
      }
      const html = ['<table><thead><tr>'];
      for (const field of timelineFields) {
        html.push(`<th>${field}</th>`);
      }
      html.push('</tr></thead><tbody>');
      timelineRows.forEach((row, index) => {
        html.push('<tr>');
        timelineFields.forEach(field => {
          const value = row[field] || '';
          if (field === 'summary') {
            html.push(`<td><textarea data-timeline-row=\"${index}\" data-field=\"${field}\">${escapeHtml(value)}</textarea></td>`);
          } else {
            html.push(`<td><input type=\"text\" data-timeline-row=\"${index}\" data-field=\"${field}\" value=\"${escapeHtml(value)}\"></td>`);
          }
        });
        html.push('</tr>');
      });
      html.push('</tbody></table>');
      root.innerHTML = html.join('');
    }

    function buildEntityTable() {
      const root = document.getElementById('entity-editor');
      if (!entityRows.length) {
        root.textContent = uiText('noEntities');
        return;
      }
      const html = ['<table><thead><tr>'];
      for (const field of entityFields) {
        html.push(`<th>${field}</th>`);
      }
      html.push('</tr></thead><tbody>');
      entityRows.forEach((row, index) => {
        html.push('<tr>');
        entityFields.forEach(field => {
          const value = row[field] || '';
          if (field === 'notes') {
            html.push(`<td><textarea data-entity-row=\"${index}\" data-field=\"${field}\">${escapeHtml(value)}</textarea></td>`);
          } else {
            html.push(`<td><input type=\"text\" data-entity-row=\"${index}\" data-field=\"${field}\" value=\"${escapeHtml(value)}\"></td>`);
          }
        });
        html.push('</tr>');
      });
      html.push('</tbody></table>');
      root.innerHTML = html.join('');
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;');
    }

    function syncRegisterFromInputs() {
      document.querySelectorAll('[data-register-row]').forEach(el => {
        const rowIndex = Number(el.getAttribute('data-register-row'));
        const field = el.getAttribute('data-field');
        registerRows[rowIndex][field] = el.value;
      });
    }

    function syncTimelineFromInputs() {
      document.querySelectorAll('[data-timeline-row]').forEach(el => {
        const rowIndex = Number(el.getAttribute('data-timeline-row'));
        const field = el.getAttribute('data-field');
        timelineRows[rowIndex][field] = el.value;
      });
    }

    function syncEntitiesFromInputs() {
      document.querySelectorAll('[data-entity-row]').forEach(el => {
        const rowIndex = Number(el.getAttribute('data-entity-row'));
        const field = el.getAttribute('data-field');
        entityRows[rowIndex][field] = el.value;
      });
    }

    async function showDossierPreview() {
      const target = document.getElementById('dossier-preview');
      try {
        const response = await fetch('/api/dossier-preview');
        const data = await response.json();
        target.textContent = uiText('preview') + data.selected_documents +
          uiText('selectedDocuments') + data.entered_timeline_rows +
          uiText('timelineEntries') + data.claims_in_selection + uiText('linkedClaims') + data.note;
      } catch (error) { target.textContent = String(error); }
    }

    async function loadRegister() {
      const response = await fetch('/api/register-data');
      const data = await response.json();
      registerFields = data.fields || [];
      registerRows = data.rows || [];
      buildRegisterTable();
      appendLog('Register loaded.');
    }

    async function saveRegister() {
      syncRegisterFromInputs();
      const response = await fetch('/api/save-register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: registerRows }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Save failed (HTTP ' + response.status + ')');
      appendLog(JSON.stringify(data, null, 2));
      await loadRegister();
      await refreshStatus();
    }

    async function loadTimeline() {
      const response = await fetch('/api/timeline-data');
      const data = await response.json();
      timelineFields = data.fields || [];
      timelineRows = data.rows || [];
      buildTimelineTable();
      appendLog('Timeline loaded.');
    }

    function addTimelineRow() {
      if (!timelineFields.length) {
        timelineFields = ['event_id','event_date','event_title','linked_file_ids','people_or_entities','summary','status'];
      }
      const nextId = `EV-${String(timelineRows.length + 1).padStart(6, '0')}`;
      const row = {
        event_id: nextId,
        event_date: '',
        event_title: '',
        linked_file_ids: '',
        people_or_entities: '',
        summary: '',
        status: 'draft',
      };
      timelineRows.push(row);
      buildTimelineTable();
      appendLog(`Added timeline row ${nextId}.`);
    }

    async function saveTimeline() {
      syncTimelineFromInputs();
      const response = await fetch('/api/save-timeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: timelineRows }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Save failed (HTTP ' + response.status + ')');
      appendLog(JSON.stringify(data, null, 2));
      await loadTimeline();
      await refreshStatus();
    }

    async function loadEntities() {
      const response = await fetch('/api/entity-data');
      const data = await response.json();
      entityFields = data.fields || [];
      entityRows = data.rows || [];
      buildEntityTable();
      appendLog('Entities loaded.');
    }

    function addEntityRow() {
      if (!entityFields.length) {
        entityFields = ['entity_id','entity_name','entity_type','linked_file_ids','notes'];
      }
      const nextId = `ENT-${String(entityRows.length + 1).padStart(6, '0')}`;
      entityRows.push({
        entity_id: nextId,
        entity_name: '',
        entity_type: '',
        linked_file_ids: '',
        notes: '',
      });
      buildEntityTable();
      appendLog(`Added entity row ${nextId}.`);
    }

    async function saveEntities() {
      syncEntitiesFromInputs();
      const response = await fetch('/api/save-entities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: entityRows }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Save failed (HTTP ' + response.status + ')');
      appendLog(JSON.stringify(data, null, 2));
      await loadEntities();
      await refreshStatus();
    }

    async function loadTimelineCandidates() {
      const area = document.getElementById('timeline-candidates');
      area.textContent = uiText('scanning');
      try {
        const response = await fetch('/api/propose-events', {method:'POST'});
        const report = await response.json();
        if (!response.ok) throw new Error(report.error || 'Could not build suggestions');
        area.replaceChildren();
        const note = document.createElement('p');
        note.textContent = (report.candidates || []).length + uiText('dateFound') +
          (report.warnings || []).length + uiText('sourceWarnings') +
          (report.duplicate_content || []).length + uiText('duplicates');
        area.appendChild(note);
        if ((report.warnings || []).length) {
          const w = document.createElement('p');
          w.textContent = uiText('skippedSources') + (report.warnings || []).map(x => x.file_id + ' (' + x.reason + ')').join(', ');
          area.appendChild(w);
        }
        for (const item of report.candidates || []) {
          const row = document.createElement('div');
          row.style.cssText = 'padding:12px;border-bottom:1px solid #7774;display:flex;gap:12px;align-items:center;flex-wrap:wrap';
          const description = document.createElement('span');
          description.textContent = item.date + ' · ' + item.original_name + ' · ' + uiText('line') + item.line +
            ' · ' + item.excerpt;
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'secondary';
          button.textContent = uiText('addDraft');
          button.addEventListener('click', async () => {
            button.disabled = true;
            try {
              const response = await fetch('/api/accept-candidate', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body:JSON.stringify({candidate_id:item.candidate_id}),
              });
              const data = await response.json();
              if (!response.ok) throw new Error(data.error || 'Could not add draft');
              button.textContent = data.status === 'already_recorded' ? uiText('alreadyAdded') : uiText('draftAdded');
              await loadTimeline();
              await loadEvidenceGraph();
            } catch (error) {
              button.disabled = false;
              appendLog(String(error));
            }
          });
          row.appendChild(description);row.appendChild(button);area.appendChild(row);
        }
      } catch (error) {
        area.textContent = String(error);
      }
    }

    async function casePost(url, payload) {
      const response = await fetch(url, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload || {}),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Local action failed');
      return data;
    }

    async function indexSelectedDocument() {
      const area = document.getElementById('text-index-status');
      area.textContent = uiText('indexing');
      try {
        const result = await casePost('/api/index-document', {
          file_id: document.getElementById('text-file-id').value.trim(),
          use_ocr: document.getElementById('text-use-ocr').checked
        });
        area.textContent = result.file_id + ': ' + result.method + ', ' +
          result.pages + uiText('pages') + result.characters + uiText('characters');
      } catch (error) { area.textContent = String(error); }
    }

    async function searchIndexedDocuments() {
      const area = document.getElementById('text-search-results');
      area.textContent = uiText('searching');
      try {
        const data = await casePost('/api/search-text', {
          query: document.getElementById('text-query').value.trim(),
        });
        area.replaceChildren();
        const info = document.createElement('p');
        info.textContent = (data.matches || []).length + uiText('matchingPages') +
          data.indexed_files + uiText('verifiedIndexed');
        area.appendChild(info);
        for (const hit of data.matches || []) {
          const row = document.createElement('div');
          row.style.cssText = 'padding:10px;border-bottom:1px solid #7774';
          const description = document.createElement('p');
          description.textContent = hit.file_id + ' · ' + hit.original_name +
            ' · ' + uiText('page') + hit.page + ': ' + hit.excerpt;
          const selected = document.createElement('button');
          selected.type = 'button';
          selected.className = 'ghost';
          selected.textContent = uiText('useSource');
          selected.addEventListener('click', () => {
            document.getElementById('claim-file-id').value = hit.file_id;
            document.getElementById('claim-page').value = hit.page;
            document.getElementById('claim-quote').value = hit.excerpt.trim().slice(0,500);
            document.getElementById('claim-statement').focus();
          });
          row.appendChild(description); row.appendChild(selected); area.appendChild(row);
        }
      } catch (error) { area.textContent = String(error); }
    }

    async function saveSourcedClaim() {
      const area = document.getElementById('claim-results');
      try {
        const row = await casePost('/api/add-claim', {
          file_id: document.getElementById('claim-file-id').value.trim(),
          page: Number(document.getElementById('claim-page').value),
          quote: document.getElementById('claim-quote').value,
          statement: document.getElementById('claim-statement').value,
        });
        appendLog(uiText('createdClaim') + row.claim_id);
        await loadSourcedClaims();
        await loadEvidenceGraph();
      } catch (error) { area.textContent = String(error); }
    }

    async function loadSourcedClaims() {
      const area = document.getElementById('claim-results');
      try {
        const response = await fetch('/api/claims');
        const data = await response.json();
        area.replaceChildren();
        if (!(data.claims || []).length) {
          area.textContent = uiText('noClaims');
          return;
        }
        for (const claim of data.claims || []) {
          const item = document.createElement('div');
          item.style.cssText = 'padding:12px;border-bottom:1px solid #7774';
          const description = document.createElement('p');
          description.textContent = claim.claim_id + ' · ' + claim.file_id +
            ' ' + uiText('page') + claim.source_page + ' · ' + localizedEnum('status',claim.review_status) +
            '\\n' + uiText('quote') + claim.source_quote + '\\n' + uiText('statement') + claim.statement;
          description.style.whiteSpace = 'pre-wrap';
          item.appendChild(description);
          const status = document.createElement('select');
          for (const s of ['draft','needs_review','reviewed']) {
            const option = document.createElement('option');
            option.value = s; option.textContent = localizedEnum('status',s);
            option.selected = s === claim.review_status;
            status.appendChild(option);
          }
          const save = document.createElement('button');
          save.type = 'button'; save.className = 'secondary';
          save.textContent = uiText('updateReview');
          save.addEventListener('click', async () => {
            try {
              await casePost('/api/review-claim', {claim_id:claim.claim_id, status:status.value});
              await loadSourcedClaims();
            } catch (error) { appendLog(String(error)); }
          });
          item.appendChild(status);item.appendChild(save);area.appendChild(item);
        }
      } catch (error) { area.textContent = String(error); }
    }

    async function addClaimComparison() {
      const area = document.getElementById('claim-comparisons');
      try {
        await casePost('/api/add-comparison', {
          claim_id: document.getElementById('compare-claim-id').value.trim(),
          topic: document.getElementById('compare-topic').value.trim(),
          kind: document.getElementById('compare-kind').value,
          value: document.getElementById('compare-value').value.trim()
        });
        await loadClaimComparisons();
      await loadCaseAudit();
      await loadCaseTasks();
      } catch (error) { area.textContent = String(error); }
    }

    async function createCaseTask() {
      const area = document.getElementById('task-board');
      try {
        await casePost('/api/add-task', {
          title: document.getElementById('task-title').value.trim(),
          due_date: document.getElementById('task-date').value,
          priority: document.getElementById('task-priority').value,
          linked_file_ids: document.getElementById('task-files').value.trim()
        });
        document.getElementById('task-title').value = '';
        await loadCaseTasks();
      } catch(error) { area.textContent = String(error); }
    }

    async function loadCaseTasks() {
      const area = document.getElementById('task-board');
      try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Tasks unavailable');
        area.replaceChildren();
        const note = document.createElement('p');
        note.textContent = data.as_of + ' · ' + uiText('taskNote');
        area.appendChild(note);
        for (const task of data.tasks || []) {
          const row = document.createElement('div');
          row.style.cssText = 'display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:10px;border-bottom:1px solid #7774';
          const label = document.createElement('span');
          label.textContent = task.title + ' · ' + (task.due_date || uiText('noDate')) +
            ' · ' + localizedEnum('date',task.date_indicator) + ' · ' + localizedEnum('priority',task.priority) +
            (task.linked_file_ids ? ' · ' + task.linked_file_ids : '');
          const select = document.createElement('select');
          select.style.maxWidth = '155px';
          for (const status of ['open','in_progress','done','cancelled']) {
            const choice = document.createElement('option');
            choice.value = status; choice.textContent = localizedEnum('status',status);
            choice.selected = task.status === status; select.appendChild(choice);
          }
          const save = document.createElement('button');
          save.type = 'button'; save.className = 'secondary'; save.textContent = uiText('update');
          save.addEventListener('click', async () => {
            try {
              await casePost('/api/update-task', {task_id: task.task_id, status:select.value});
              await loadCaseTasks();
            } catch(error) { area.textContent = String(error); }
          });
          row.appendChild(label);row.appendChild(select);row.appendChild(save);area.appendChild(row);
        }
        if (!(data.tasks || []).length) {
          const empty = document.createElement('p');
          empty.textContent = uiText('noReminders');
          area.appendChild(empty);
        }
      } catch(error) { area.textContent = String(error); }
    }

    async function prepareAiHandoff() {
      const area = document.getElementById('ai-review-result');
      const raw = document.getElementById('ai-source-ids').value.trim();
      const files = raw.split(',').map(x => x.trim()).filter(Boolean);
      if (!window.confirm(uiText('aiConfirm'))) return;
      try {
        const output = await casePost('/api/prepare-ai-review', {file_ids:files});
        area.textContent = uiText('savedPacket') + output.path +
          uiText('savedPacketEnd');
      } catch(error) { area.textContent = String(error); }
    }

    async function importAiResponse() {
      const area = document.getElementById('ai-review-result');
      try {
        const parsed = JSON.parse(document.getElementById('ai-response-json').value);
        const outcome = await casePost('/api/import-ai-review', parsed);
        area.textContent = outcome.accepted_as_pending + uiText('proposalsPending');
        await loadAiSuggestions();
      } catch(error) { area.textContent = String(error); }
    }

    async function loadAiSuggestions() {
      const area = document.getElementById('ai-review-result');
      try {
        const response = await fetch('/api/ai-suggestions');
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Suggestions unavailable');
        area.replaceChildren();
        for (const entry of data.suggestions || []) {
          const card = document.createElement('div');
          card.style.cssText = 'border-bottom:1px solid #7774;padding:12px';
          const line = document.createElement('p');
          line.textContent = entry.file_id + ' · ' + uiText('page') + entry.page + ' · ' + localizedEnum('status',entry.status) +
            uiText('exactQuote') + entry.source_quote + uiText('draft') + entry.statement;
          card.appendChild(line);
          if (entry.status === 'pending_review') {
            for (const choice of [
              {decision:'reject',label:uiText('reject')},
              {decision:'create_draft_claim',label:uiText('createDraftClaim')}
            ]) {
              const button = document.createElement('button');
              button.type='button'; button.className='secondary';button.textContent=choice.label;
              button.addEventListener('click', async () => {
                try {
                  await casePost('/api/review-ai-suggestion', {
                    suggestion_id:entry.suggestion_id, decision:choice.decision
                  });
                  await loadAiSuggestions(); await loadSourcedClaims();
                } catch(error) { area.textContent = String(error); }
              });
              card.appendChild(button);
            }
          }
          area.appendChild(card);
        }
        if (!(data.suggestions || []).length) area.textContent = uiText('noAI');
      } catch(error) { area.textContent = String(error); }
    }

    async function loadCaseAudit() {
      const root = document.getElementById('case-audit');
      try {
        const response = await fetch('/api/audit-history');
        const data = await response.json();
        root.replaceChildren();
        for (const item of data.changes || []) {
          const line = document.createElement('p');
          line.textContent = item.at + ' · ' + item.area + ' · ' +
            item.row_count + uiText('rows') + item.change_id;
          root.appendChild(line);
        }
        if (!(data.changes || []).length) root.textContent = uiText('noAudits');
      } catch(error) { root.textContent = String(error); }
    }

    async function loadClaimComparisons() {
      const area = document.getElementById('claim-comparisons');
      try {
        const response = await fetch('/api/claim-comparisons');
        const data = await response.json();
        area.replaceChildren();
        const intro = document.createElement('p');
        intro.textContent = (data.records || []).length + uiText('registeredComparisons') +
          (data.review_candidates || []).length + uiText('possibleDiscrepancies');
        area.appendChild(intro);
        for (const group of data.review_candidates || []) {
          const div = document.createElement('div');
          div.style.cssText = 'padding:12px;border-bottom:1px solid #7774';
          const title = document.createElement('strong');
          title.textContent = group.topic + ' (' + localizedEnum('kind',group.kind) + uiText('reviewSuggested');
          div.appendChild(title);
          for (const source of group.sources || []) {
            const line = document.createElement('p');
            line.textContent = source.claim_id + ' / ' + source.file_id +
              ': ' + source.value + ' [' + source.claim_review_status + ']';
            div.appendChild(line);
          }
          area.appendChild(div);
        }
      } catch (error) { area.textContent = String(error); }
    }

    async function loadEvidenceGraph() {
      const response = await fetch('/api/evidence-graph');
      const data = await response.json();
      const root = document.getElementById('evidence-graph');
      root.replaceChildren();
      const nodes = (data.nodes || []).slice(0, 60);
      const edges = data.edges || [];
      if (!nodes.length) {
        root.textContent = uiText('noGraph');
        return;
      }
      const ns = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(ns, 'svg');
      svg.setAttribute('viewBox', '0 0 760 420');
      svg.setAttribute('role', 'img');
      svg.setAttribute('aria-label', uiText('graphAria'));
      svg.style.cssText = 'width:100%;min-width:540px;height:auto;max-height:560px';
      const columns = {document: 105, event: 380, entity: 655};
      const counts = {document:0, event:0, entity:0};
      const points = {};
      for (const node of nodes) {
        const n = counts[node.kind]++;
        const x = columns[node.kind] || 380;
        const y = 28 + (n % 10) * 38;
        points[node.id] = [x, y];
      }
      for (const edge of edges) {
        const a = points[edge.source], b = points[edge.target];
        if (!a || !b) continue;
        const line = document.createElementNS(ns, 'line');
        for (const [key, value] of Object.entries({x1:a[0],y1:a[1],x2:b[0],y2:b[1]})) line.setAttribute(key, value);
        line.setAttribute('stroke', '#b89a65');
        line.setAttribute('stroke-opacity', '0.5');
        line.setAttribute('stroke-width', '1.5');
        svg.appendChild(line);
      }
      for (const node of nodes) {
        const [x,y] = points[node.id];
        const circle = document.createElementNS(ns, 'circle');
        circle.setAttribute('cx',x);circle.setAttribute('cy',y);circle.setAttribute('r','7');
        circle.setAttribute('fill', node.kind === 'document' ? '#93c5fd' : node.kind === 'event' ? '#fbbf24' : '#86efac');
        const title = document.createElementNS(ns, 'title');
        title.textContent = node.kind + ': ' + node.label;
        circle.appendChild(title);svg.appendChild(circle);
        const label = document.createElementNS(ns, 'text');
        label.setAttribute('x', x + 11); label.setAttribute('y', y + 4);
        label.setAttribute('fill', 'currentColor'); label.setAttribute('font-size', '11');
        label.textContent = String(node.label || node.id).slice(0,22);
        svg.appendChild(label);
      }
      root.appendChild(svg);
      const note = document.createElement('p');
      note.textContent = 'Links: ' + edges.length + uiText('unresolved') + (data.unresolved || []).length +
        ((data.truncated || data.total_nodes > nodes.length) ? uiText('truncated') : '');
      root.appendChild(note);
    }

    async function loadIntegrityHistory() {
      const response = await fetch('/api/integrity-history');
      const data = await response.json();
      const root = document.getElementById('integrity-history');
      root.textContent = (data.runs || []).length
        ? (data.runs || []).map(row => row.at + ' · ' + row.checked + uiText('checked') + JSON.stringify(row.counts)).join('\\n')
        : uiText('noIntegrity');
      root.style.whiteSpace = 'pre-wrap';
    }

    async function loadExportHistory() {
      const response = await fetch('/api/export-history');
      const data = await response.json();
      renderExportHistory(data.rows || []);
      appendLog(uiText('loadExport'));
    }

    async function refreshStatus() {
      const response = await fetch('/api/status');
      const data = await response.json();
      renderCards(data.summary);
      renderRecentFiles(data.recent_inbox_files || []);
      renderNextStep(data.next_step || 'Use the main action buttons below.');
      document.getElementById('paths').textContent = JSON.stringify(data.paths, null, 2);
      appendLog('Status refreshed.');
    }

    async function runAction(action) {
      appendLog(`Running ${action} ...`);
      const response = await fetch(`/api/${action}`, { method: 'POST' });
      const data = await response.json();
      if (!response.ok) {
        appendLog('Action ' + action + ' failed: ' + (data.error || response.status));
        throw new Error(data.error || 'Action failed (HTTP ' + response.status + ')');
      }
      appendLog(JSON.stringify(data, null, 2));
      await refreshAll();
    }

    async function uploadFiles() {
      const input = document.getElementById('fileInput');
      if (!input.files || input.files.length === 0) {
        appendLog('No files selected for upload.');
        return;
      }
      const form = new FormData();
      for (const file of input.files) {
        form.append('files', file, file.name);
      }
      appendLog(`Uploading ${input.files.length} file(s) to inbox ...`);
      const response = await fetch('/api/upload', { method: 'POST', body: form });
      const data = await response.json();
      if (!response.ok) {
        appendLog('Upload failed: ' + (data.error || response.status));
        throw new Error(data.error || 'Upload failed (HTTP ' + response.status + ')');
      }
      appendLog(JSON.stringify(data, null, 2));
      input.value = '';
      await refreshStatus();
    }

    async function refreshAll() {
      await refreshStatus();
      await loadRegister();
      await loadTimeline();
      await loadEntities();
      await loadExportHistory();
      await loadEvidenceGraph();
      await loadIntegrityHistory();
      await loadClaimComparisons();
      await loadSourcedClaims();
    }

    loadCaseHub();
    refreshAll();
  </script>
</body>
</html>
"""


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())



def _count_directories(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.iterdir() if item.is_dir())



def _check_writable(path: Path) -> bool:
    path.mkdir(parents=True, exist_ok=True)
    probe = path / ".write_probe"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False



def _next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1



def _recent_inbox_files(inbox_dir: Path, limit: int = 8) -> list[str]:
    files = [path for path in inbox_dir.rglob("*") if path.is_file()]
    files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return [str(path.relative_to(inbox_dir)) for path in files[:limit]]



def _selected_export_count() -> int:
    rows = read_register_rows()
    return sum(1 for row in rows if str(row.get("selected_for_export", "")).lower() == "yes")



def _split_link_values(value: str) -> list[str]:
    return [item.strip() for item in str(value).split(',') if item.strip()]



def _register_link_maps() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    timeline_map: dict[str, list[str]] = {}
    entity_map: dict[str, list[str]] = {}

    for row in read_timeline_rows():
        event_id = str(row.get("event_id", "")).strip()
        for file_id in _split_link_values(str(row.get("linked_file_ids", ""))):
            timeline_map.setdefault(file_id, []).append(event_id)

    for row in read_entity_rows():
        entity_id = str(row.get("entity_id", "")).strip()
        for file_id in _split_link_values(str(row.get("linked_file_ids", ""))):
            entity_map.setdefault(file_id, []).append(entity_id)

    return timeline_map, entity_map



def _next_step_message() -> str:
    workspace_paths = get_workspace_paths()
    inbox_files = _count_files(workspace_paths.inbox_dir)
    import_batches = _count_directories(workspace_paths.originals_dir)
    register_rows = len(read_register_rows())
    selected_for_export = _selected_export_count()
    export_packages = _count_directories(workspace_paths.exports_dir)
    if inbox_files > 0:
        return "Next step: use 'Import inbox files' to move your waiting files into a tracked import batch."
    if import_batches == 0:
        return "Next step: add files through the upload area or open the inbox folder and place files there."
    if register_rows == 0:
        return "Next step: use 'Build register' to create your document register."
    if selected_for_export == 0:
        return "Next step: mark the important register rows with 'selected_for_export = yes' so the handoff package knows what to include."
    if export_packages == 0:
        return "Next step: create your first export package."
    return "Your workspace already has imports, working tables, and exports. Use the browser tables to keep the dossier current."



def _status_payload() -> dict[str, object]:
    paths = get_workspace_paths()
    return {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "summary": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "inbox_file_count": _count_files(paths.inbox_dir),
            "original_file_count": _count_files(paths.originals_dir),
            "import_batches": _count_directories(paths.originals_dir),
            "register_files": _count_files(paths.register_dir),
            "selected_export_count": _selected_export_count(),
            "entity_count": len(read_entity_rows()),
            "export_packages": _count_directories(paths.exports_dir),
        },
        "paths": describe_workspace(paths),
        "recent_inbox_files": _recent_inbox_files(paths.inbox_dir),
        "next_step": _next_step_message(),
    }



def _doctor_payload() -> dict[str, object]:
    paths = create_local_workspace()
    return {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "checks": {
            "repo_root_exists": paths.repo_root.exists(),
            "run_py_exists": (paths.repo_root / "run.py").exists(),
            "src_package_exists": (paths.repo_root / "src" / "local_case_organizer").exists(),
            "data_dir_writable": _check_writable(paths.data_dir),
            "inbox_dir_writable": _check_writable(paths.inbox_dir),
            "originals_dir_writable": _check_writable(paths.originals_dir),
            "register_dir_writable": _check_writable(paths.register_dir),
            "exports_dir_writable": _check_writable(paths.exports_dir),
            "logs_dir_writable": _check_writable(paths.logs_dir),
        },
    }



def _open_path_in_file_manager(path: Path) -> dict[str, object]:
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
        return {"opened": str(path)}
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}



def _save_uploaded_files(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    # Validate the entire bounded request before modifying the selected case.
    uploads = parse_multipart_files(handler)
    paths = create_local_workspace()
    if paths.inbox_dir.is_symlink():
        raise ValueError("Inbox must not be a symlink")
    saved: list[str] = []
    written: list[Path] = []
    try:
        for filename, content in uploads:
            target = _next_available_path(paths.inbox_dir / filename)
            # Exclusive creation prevents overwriting originals or racing uploads.
            with target.open("xb") as handle:
                written.append(target)
                handle.write(content)
            saved.append(str(target.relative_to(paths.inbox_dir)))
    except Exception:
        for target in written:
            target.unlink(missing_ok=True)
        raise
    return {
        "uploaded_files": saved,
        "inbox_dir": str(paths.inbox_dir),
        "message": f"Saved {len(saved)} file(s) to the inbox.",
    }



def _read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length > 0 else b"{}"
    return json.loads(raw.decode("utf-8")) if raw else {}



def _register_data_payload() -> dict[str, object]:
    timeline_map, entity_map = _register_link_maps()
    rows: list[dict[str, str]] = []
    for row in read_register_rows():
        file_id = str(row.get("file_id", "")).strip()
        enriched = dict(row)
        enriched["linked_timeline_event_ids"] = ", ".join(timeline_map.get(file_id, []))
        enriched["linked_entity_ids"] = ", ".join(entity_map.get(file_id, []))
        rows.append(enriched)
    return {"fields": REGISTER_FIELDS + ["linked_timeline_event_ids", "linked_entity_ids"], "rows": rows}



def _timeline_data_payload() -> dict[str, object]:
    build_timeline_template()
    return {"fields": TIMELINE_FIELDS, "rows": read_timeline_rows()}



def _entity_data_payload() -> dict[str, object]:
    return {"fields": ENTITY_FIELDS, "rows": read_entity_rows()}



def _export_history_payload() -> dict[str, object]:
    return {"rows": read_export_history()}



def _save_register_payload(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    body = _read_json_body(handler)
    rows = body.get("rows", [])
    if not isinstance(rows, list):
        rows = []
    path = write_register_rows(rows)
    return {"saved_register_path": str(path), "saved_rows": len(rows)}



def _save_timeline_payload(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    body = _read_json_body(handler)
    rows = body.get("rows", [])
    if not isinstance(rows, list):
        rows = []
    path = write_timeline_rows(rows)
    return {"saved_timeline_path": str(path), "saved_rows": len(rows)}



def _save_entities_payload(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    body = _read_json_body(handler)
    rows = body.get("rows", [])
    if not isinstance(rows, list):
        rows = []
    path = write_entity_rows(rows)
    return {"saved_entities_path": str(path), "saved_rows": len(rows)}



def _json_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, indent=2).encode("utf-8")



def run_ui(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> int:
    if not allowed_ui_host(host):
        raise ValueError("The private case UI may only bind to localhost; no authentication is implemented")
    create_local_workspace()

    active_case = get_active_case()

    class Handler(BaseHTTPRequestHandler):
        def __init__(self, *args: object, **kwargs: object) -> None:
            # ThreadingHTTPServer creates new threads; explicitly rebind selected case.
            with using_case(active_case):
                super().__init__(*args, **kwargs)

        def _send(self, code: int, content_type: str, body: bytes) -> None:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            try:
                chosen = requested_case(self.headers.get("X-LCO-Case"), active_case, get_repo_root())
            except (ValueError, OSError) as exc:
                self._send(400, "application/json; charset=utf-8", _json_bytes({"error": str(exc)}))
                return
            with using_case(chosen):
                self._handle_get()

        def _handle_get(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                label = html.escape(get_active_case() or "legacy-default", quote=True)
                page = HTML.replace("</h1>", "</h1><p class='note'>Active case: " + label + "</p>", 1)
                self._send(200, "text/html; charset=utf-8", page.encode("utf-8"))
                return
            if parsed.path == "/api/cases":
                self._send(200, "application/json; charset=utf-8",
                           _json_bytes({"selected_case": get_active_case() or "legacy-default",
                                        "cases": list_cases(get_repo_root())}))
                return
            if parsed.path == "/api/status":
                self._send(200, "application/json; charset=utf-8", _json_bytes(_status_payload()))
                return
            if parsed.path == "/api/autopilot-status":
                self._send(200, "application/json; charset=utf-8", _json_bytes(autopilot_status()))
                return
            if parsed.path == "/api/case-briefing":
                self._send(200, "application/json; charset=utf-8", _json_bytes(case_briefing()))
                return
            if parsed.path == "/api/register-data":
                self._send(200, "application/json; charset=utf-8", _json_bytes(_register_data_payload()))
                return
            if parsed.path == "/api/timeline-data":
                self._send(200, "application/json; charset=utf-8", _json_bytes(_timeline_data_payload()))
                return
            if parsed.path == "/api/entity-data":
                self._send(200, "application/json; charset=utf-8", _json_bytes(_entity_data_payload()))
                return
            if parsed.path == "/api/evidence-graph":
                self._send(200, "application/json; charset=utf-8", _json_bytes(evidence_graph()))
                return
            if parsed.path == "/api/integrity-history":
                self._send(200, "application/json; charset=utf-8", _json_bytes({"runs": recent_integrity_runs()}))
                return
            if parsed.path == "/api/ai-suggestions":
                self._send(200, "application/json; charset=utf-8",
                           _json_bytes({"suggestions": read_ai_suggestions()}))
                return
            if parsed.path == "/api/tasks":
                self._send(200, "application/json; charset=utf-8", _json_bytes(task_board()))
                return
            if parsed.path == "/api/audit-history":
                self._send(200, "application/json; charset=utf-8", _json_bytes({"changes": recent_changes()}))
                return
            if parsed.path == "/api/claim-comparisons":
                self._send(200, "application/json; charset=utf-8", _json_bytes(comparison_report()))
                return
            if parsed.path == "/api/claims":
                self._send(200, "application/json; charset=utf-8", _json_bytes({"claims": read_claims()}))
                return
            if parsed.path == "/api/dossier-preview":
                self._send(200, "application/json; charset=utf-8", _json_bytes(dossier_preview()))
                return
            if parsed.path == "/api/export-history":
                self._send(200, "application/json; charset=utf-8", _json_bytes(_export_history_payload()))
                return
            self._send(404, "application/json; charset=utf-8", _json_bytes({"error": "not found"}))

        def do_POST(self) -> None:
            if not allow_local_post(self.headers):
                self._send(403, "application/json; charset=utf-8",
                           _json_bytes({"error": "Same-origin local UI request required"}))
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = -1
            if length < 0 or length > 32 * 1024 * 1024:
                self._send(413, "application/json; charset=utf-8",
                           _json_bytes({"error": "Request exceeds local size limit"}))
                return
            try:
                chosen = requested_case(self.headers.get("X-LCO-Case"), active_case, get_repo_root())
            except (ValueError, OSError) as exc:
                self._send(400, "application/json; charset=utf-8", _json_bytes({"error": str(exc)}))
                return
            with using_case(chosen):
                try:
                    self._handle_post()
                except (ValueError, TypeError, OSError) as exc:
                    # Invalid user input (including an empty inbox) is an API
                    # response, not a broken connection or thread traceback.
                    self._send(400, "application/json; charset=utf-8",
                               _json_bytes({"error": str(exc)}))

        def _handle_post(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/api/create-case":
                try:
                    body = _read_json_body(self)
                    payload = create_case(get_repo_root(), str(body.get("case_id", "")),
                                          str(body.get("title", "")))
                except (ValueError, OSError, FileExistsError, TypeError) as exc:
                    self._send(400, "application/json; charset=utf-8", _json_bytes({"error": str(exc)}))
                    return
            elif parsed.path == "/api/quick-update-document":
                payload = update_document(_read_json_body(self))
            elif parsed.path == "/api/quick-bulk-export":
                body = _read_json_body(self)
                payload = bulk_export_selection(str(body.get("mode", "")))
            elif parsed.path == "/api/quick-add-event":
                payload = add_manual_event(_read_json_body(self))
            elif parsed.path == "/api/quick-add-entity":
                payload = add_manual_entity(_read_json_body(self))
            elif parsed.path == "/api/quick-prepare-search":
                body = _read_json_body(self)
                payload = prepare_local_search(include_pdf=body.get("include_pdf") is True)
            elif parsed.path == "/api/autopilot-process":
                body = _read_json_body(self)
                payload = process_autopilot(
                    use_ocr=body.get("use_ocr") is True,
                    retry_failed=body.get("retry_failed") is True,
                )
            elif parsed.path == "/api/setup":
                payload = {"created": describe_workspace(create_local_workspace())}
            elif parsed.path == "/api/upload":
                payload = _save_uploaded_files(self)
            elif parsed.path == "/api/import":
                payload = import_sources(None)
            elif parsed.path == "/api/quick-organize":
                body = _read_json_body(self)
                files = body.get("files")
                payload = quick_organize_inbox(files)
            elif parsed.path == "/api/build-register":
                payload = {"register_path": str(build_document_register())}
            elif parsed.path == "/api/build-timeline":
                payload = {"timeline_path": str(build_timeline_template())}
            elif parsed.path == "/api/save-register":
                payload = _save_register_payload(self)
            elif parsed.path == "/api/save-timeline":
                payload = _save_timeline_payload(self)
            elif parsed.path == "/api/save-entities":
                payload = _save_entities_payload(self)
            elif parsed.path == "/api/verify-integrity":
                payload = verify_integrity()
            elif parsed.path == "/api/propose-events":
                payload = propose_events()
            elif parsed.path == "/api/accept-candidate":
                body = _read_json_body(self)
                try:
                    payload = accept_candidate(str(body.get("candidate_id", "")))
                except ValueError as exc:
                    self._send(400, "application/json; charset=utf-8", _json_bytes({"error": str(exc)}))
                    return
            elif parsed.path in {"/api/index-document", "/api/search-text", "/api/add-claim", "/api/review-claim", "/api/add-comparison", "/api/add-task", "/api/update-task", "/api/prepare-ai-review", "/api/import-ai-review", "/api/review-ai-suggestion"}:
                try:
                    body = _read_json_body(self)
                    if parsed.path == "/api/prepare-ai-review":
                        payload = prepare_ai_packet(body.get("file_ids", []))
                    elif parsed.path == "/api/import-ai-review":
                        payload = import_ai_suggestions(body)
                    elif parsed.path == "/api/review-ai-suggestion":
                        payload = review_ai_suggestion(str(body.get("suggestion_id", "")),
                                                       str(body.get("decision", "")))
                    elif parsed.path == "/api/add-task":
                        payload = add_task(str(body.get("title", "")), str(body.get("due_date", "")),
                                           str(body.get("priority", "normal")),
                                           str(body.get("linked_file_ids", "")),
                                           str(body.get("note", "")))
                    elif parsed.path == "/api/update-task":
                        payload = update_task(str(body.get("task_id", "")),
                                              str(body.get("status", "")))
                    elif parsed.path == "/api/add-comparison":
                        payload = add_comparison(str(body.get("claim_id", "")),
                                                 str(body.get("topic", "")),
                                                 str(body.get("kind", "")),
                                                 str(body.get("value", "")))
                    elif parsed.path == "/api/index-document":
                        payload = index_document(str(body.get("file_id", "")),
                                                 use_ocr=body.get("use_ocr") is True)
                    elif parsed.path == "/api/search-text":
                        payload = search_text(str(body.get("query", "")))
                    elif parsed.path == "/api/add-claim":
                        payload = add_claim(
                            str(body.get("file_id", "")), body.get("page"),
                            body.get("quote", ""), body.get("statement", "")
                        )
                    else:
                        payload = set_review_status(str(body.get("claim_id", "")),
                                                    str(body.get("status", "")))
                except (ValueError, TypeError, OSError) as exc:
                    self._send(400, "application/json; charset=utf-8",
                               _json_bytes({"error": str(exc)}))
                    return
            elif parsed.path == "/api/export-package":
                export_dir = build_export_package()
                payload = {
                    "export_dir": str(export_dir),
                    "zip_path": str(export_dir.with_suffix('.zip')),
                    "manifest_path": str(export_dir / 'export_manifest.json'),
                }
            elif parsed.path == "/api/open-inbox":
                payload = _open_path_in_file_manager(get_workspace_paths().inbox_dir)
            elif parsed.path == "/api/open-register":
                payload = _open_path_in_file_manager(get_workspace_paths().register_dir)
            elif parsed.path == "/api/open-exports":
                payload = _open_path_in_file_manager(get_workspace_paths().exports_dir)
            elif parsed.path == "/api/doctor":
                payload = _doctor_payload()
            else:
                self._send(404, "application/json; charset=utf-8", _json_bytes({"error": "not found"}))
                return

            self._send(200, "application/json; charset=utf-8", _json_bytes(payload))

        def log_message(self, fmt: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}"
    print(json.dumps({"ui_url": url, "message": "local_case_organizer UI is running"}, indent=2))
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
