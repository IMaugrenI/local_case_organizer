from __future__ import annotations

FIXUP_CSS = """
<style>
  .hero { padding: 20px 22px !important; }
  .hero .lead { max-width: 980px; }
  .next-step { padding: 14px 16px !important; font-weight: 500; }
  .section-title { margin-top: 24px !important; margin-bottom: 10px !important; }
  .editor, .upload-box, .file-list, .paths, .log { border-radius: 18px !important; }
  #cards .card { min-height: 86px; }
  #cards .card > div:first-child { color: #334155; }
  .hint { line-height: 1.45; }
  .lco-log-toolbar { display: flex; justify-content: flex-end; margin-bottom: 10px; }
  .lco-log-toggle {
    border: 0;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 13px;
    cursor: pointer;
    background: #334155;
    color: white;
  }
  .log.lco-collapsed {
    max-height: 220px;
    overflow: auto;
  }
</style>
"""

FIXUP_SCRIPT = r"""
<script>
(function () {
  const NEXT_STEP_TEXT = {
    en: {
      next_step_add_files: 'Next step: add files through the upload area or open the inbox folder and place files there.',
      next_step_import_waiting: "Next step: use 'Import inbox files' to move your waiting files into a tracked import batch.",
      next_step_build_register: "Next step: use 'Build register' to create your document register.",
      next_step_select_export: "Next step: mark the important register rows with 'selected_for_export = yes' so the export package knows what to include.",
      next_step_first_export: 'Next step: create your first export package.',
      next_step_workspace_ready: 'Your workspace already has imports, working tables, and exports. Use the browser tables to keep the dossier current.',
      next_step_use_buttons: 'Use the main action buttons below.'
    },
    de: {
      next_step_add_files: 'Nächster Schritt: Dateien über den Upload-Bereich hinzufügen oder den Inbox-Ordner öffnen und dort Dateien hineinlegen.',
      next_step_import_waiting: "Nächster Schritt: 'Inbox-Dateien importieren' nutzen, damit wartende Dateien in einen verfolgten Import-Batch übernommen werden.",
      next_step_build_register: "Nächster Schritt: 'Register bauen' nutzen, um dein Dokumentenregister zu erstellen.",
      next_step_select_export: "Nächster Schritt: wichtige Register-Zeilen mit 'selected_for_export = yes' markieren, damit das Exportpaket weiß, was enthalten sein soll.",
      next_step_first_export: 'Nächster Schritt: dein erstes Exportpaket erstellen.',
      next_step_workspace_ready: 'Dein Arbeitsbereich hat bereits Importe, Arbeitstabellen und Exporte. Nutze die Browser-Tabellen, um das Dossier aktuell zu halten.',
      next_step_use_buttons: 'Nutze die Hauptaktions-Buttons unten.'
    }
  };

  const NEXT_STEP_TEXT_TO_KEY = {
    "Next step: add files through the upload area or open the inbox folder and place files there.": 'next_step_add_files',
    "Next step: use 'Import inbox files' to move your waiting files into a tracked import batch.": 'next_step_import_waiting',
    "Next step: use 'Build register' to create your document register.": 'next_step_build_register',
    "Next step: mark the important register rows with 'selected_for_export = yes' so the export package knows what to include.": 'next_step_select_export',
    'Next step: create your first export package.': 'next_step_first_export',
    'Your workspace already has imports, working tables, and exports. Use the browser tables to keep the dossier current.': 'next_step_workspace_ready',
    'Use the main action buttons below.': 'next_step_use_buttons',
    'Nächster Schritt: Dateien über den Upload-Bereich hinzufügen oder den Inbox-Ordner öffnen und dort Dateien hineinlegen.': 'next_step_add_files',
    "Nächster Schritt: 'Inbox-Dateien importieren' nutzen, damit wartende Dateien in einen verfolgten Import-Batch übernommen werden.": 'next_step_import_waiting',
    "Nächster Schritt: 'Register bauen' nutzen, um dein Dokumentenregister zu erstellen.": 'next_step_build_register',
    "Nächster Schritt: wichtige Register-Zeilen mit 'selected_for_export = yes' markieren, damit das Exportpaket weiß, was enthalten sein soll.": 'next_step_select_export',
    'Nächster Schritt: dein erstes Exportpaket erstellen.': 'next_step_first_export',
    'Dein Arbeitsbereich hat bereits Importe, Arbeitstabellen und Exporte. Nutze die Browser-Tabellen, um das Dossier aktuell zu halten.': 'next_step_workspace_ready',
    'Nutze die Hauptaktions-Buttons unten.': 'next_step_use_buttons'
  };

  function currentLang() {
    const value = localStorage.getItem('local_case_organizer_ui_lang') || document.documentElement.lang || 'en';
    return String(value).toLowerCase().startsWith('de') ? 'de' : 'en';
  }

  function normalizeNextStepValue(value) {
    if (!value) return NEXT_STEP_TEXT[currentLang()].next_step_use_buttons;
    const raw = String(value).trim();
    const key = raw.startsWith('next_step_') ? raw : (NEXT_STEP_TEXT_TO_KEY[raw] || null);
    if (key && NEXT_STEP_TEXT[currentLang()][key]) {
      return NEXT_STEP_TEXT[currentLang()][key];
    }
    return raw;
  }

  function sectionEditorFor(id) {
    const el = document.getElementById(id);
    return el ? el.closest('.editor') : null;
  }

  function applyTextFixes() {
    const lang = currentLang();

    const nextStep = document.getElementById('next-step');
    if (nextStep) {
      nextStep.textContent = normalizeNextStepValue(nextStep.textContent);
    }

    const registerEditor = sectionEditorFor('register-editor');
    if (registerEditor) {
      const hints = registerEditor.querySelectorAll('.hint');
      if (hints[0]) {
        hints[0].textContent = lang === 'de'
          ? 'Bearbeitbar sind Prüfstatus, Dokumentgruppe, Exportmarkierung und Notiz. Die rechten Spalten zeigen, wo eine Datei bereits in Zeitlinie oder Einträgen vorkommt.'
          : 'Editable fields are review status, document group, export selection, and note. The right-hand columns show where a file already appears in the timeline or entities table.';
      }
    }

    const timelineEditor = sectionEditorFor('timeline-editor');
    if (timelineEditor) {
      const hints = timelineEditor.querySelectorAll('.hint');
      if (hints[0]) {
        hints[0].innerHTML = lang === 'de'
          ? 'Nutze <code>linked_file_ids</code>, um Zeitlinien-Ereignisse mit Datei-IDs aus dem Register zu verbinden.'
          : 'Use <code>linked_file_ids</code> to connect timeline events to file IDs from the register.';
      }
      if (hints[1] && !hints[1].querySelector('.chip-list')) {
        hints[1].textContent = lang === 'de'
          ? 'Bekannte Datei-IDs erscheinen hier, sobald das Register geladen wurde.'
          : 'Known file IDs will appear here after the register is loaded.';
      }
      if (hints[2] && !hints[2].querySelector('table')) {
        hints[2].textContent = lang === 'de'
          ? 'Noch keine Zeitlinien-Zeilen vorhanden. Baue zuerst die Zeitlinie.'
          : 'No timeline rows available yet. Build the timeline first.';
      }
    }

    const entityEditor = sectionEditorFor('entity-editor');
    if (entityEditor) {
      const hints = entityEditor.querySelectorAll('.hint');
      if (hints[0]) {
        hints[0].innerHTML = lang === 'de'
          ? 'Nutze <code>linked_file_ids</code>, um Personen, Institutionen oder Firmen mit Datei-IDs aus dem Register zu verbinden.'
          : 'Use <code>linked_file_ids</code> to connect people, institutions, or companies to file IDs from the register.';
      }
      if (hints[1] && !hints[1].querySelector('.chip-list')) {
        hints[1].textContent = lang === 'de'
          ? 'Bekannte Datei-IDs erscheinen hier, sobald das Register geladen wurde.'
          : 'Known file IDs will appear here after the register is loaded.';
      }
      if (hints[2] && !hints[2].querySelector('table')) {
        hints[2].textContent = lang === 'de'
          ? 'Noch keine Einträge vorhanden. Füge deine erste Zeile hinzu.'
          : 'No entity rows available yet. Add your first row.';
      }
    }

    const exportEditor = sectionEditorFor('export-history');
    if (exportEditor) {
      const hints = exportEditor.querySelectorAll('.hint');
      if (hints[0]) {
        hints[0].textContent = lang === 'de'
          ? 'Hier werden die letzten Exportpakete, passende ZIP-Dateien und Manifest-Dateien angezeigt.'
          : 'Recent export packages, matching ZIP archives, and manifest files are shown here.';
      }
      if (hints[1] && !hints[1].querySelector('table')) {
        hints[1].textContent = lang === 'de'
          ? 'Noch keine Exportpakete gefunden.'
          : 'No export packages found yet.';
      }
    }
  }

  function applyCardFixes() {
    const lang = currentLang();
    document.querySelectorAll('#cards .card').forEach((card) => {
      const label = card.querySelector('div');
      if (!label) return;
      const text = label.textContent.trim();
      if (text === 'Register-Dateien' || text === 'Register files' || text === 'Files in register folder' || text === 'Dateien im Register-Ordner') {
        label.textContent = lang === 'de' ? 'Dateien im Register-Ordner' : 'Files in register folder';
      }
      if (text === 'Für Export markiert' || text === 'Selected for export' || text === 'Marked for export') {
        label.textContent = lang === 'de' ? 'Für Export markiert' : 'Marked for export';
      }
    });
  }

  function ensureLogToggle() {
    const logPanel = document.querySelector('.log');
    if (!logPanel) return;

    let toolbar = document.querySelector('.lco-log-toolbar');
    let button = toolbar ? toolbar.querySelector('.lco-log-toggle') : null;

    if (!toolbar) {
      toolbar = document.createElement('div');
      toolbar.className = 'lco-log-toolbar';
      button = document.createElement('button');
      button.className = 'lco-log-toggle';
      button.type = 'button';
      button.addEventListener('click', () => {
        logPanel.classList.toggle('lco-collapsed');
        updateLogToggleLabel();
      });
      toolbar.appendChild(button);
      logPanel.parentNode.insertBefore(toolbar, logPanel);
    }

    if (!logPanel.classList.contains('lco-collapsed') && !logPanel.dataset.lcoExpandedOnce) {
      logPanel.classList.add('lco-collapsed');
    }

    function updateLogToggleLabel() {
      if (!button) return;
      button.textContent = logPanel.classList.contains('lco-collapsed')
        ? (currentLang() === 'de' ? 'Log erweitern' : 'Expand log')
        : (currentLang() === 'de' ? 'Log einklappen' : 'Collapse log');
    }

    updateLogToggleLabel();
    logPanel.dataset.lcoToggleReady = '1';
  }

  function applyAllFixes() {
    applyTextFixes();
    applyCardFixes();
    ensureLogToggle();
  }

  const originalRenderNextStep = window.renderNextStep;
  if (typeof originalRenderNextStep === 'function') {
    window.renderNextStep = function (value) {
      return originalRenderNextStep.call(this, normalizeNextStepValue(value));
    };
  }

  const originalRefreshAll = window.refreshAll;
  if (typeof originalRefreshAll === 'function') {
    window.refreshAll = async function () {
      const result = await originalRefreshAll.apply(this, arguments);
      setTimeout(applyAllFixes, 0);
      return result;
    };
  }

  const originalRefreshStatus = window.refreshStatus;
  if (typeof originalRefreshStatus === 'function') {
    window.refreshStatus = async function () {
      const result = await originalRefreshStatus.apply(this, arguments);
      setTimeout(applyAllFixes, 0);
      return result;
    };
  }

  const originalToggleLanguage = window.toggleLanguage;
  if (typeof originalToggleLanguage === 'function') {
    window.toggleLanguage = function () {
      const result = originalToggleLanguage.apply(this, arguments);
      setTimeout(applyAllFixes, 0);
      setTimeout(applyAllFixes, 50);
      return result;
    };
  }

  const originalApplyLanguage = window.applyLanguage;
  if (typeof originalApplyLanguage === 'function') {
    window.applyLanguage = function () {
      const result = originalApplyLanguage.apply(this, arguments);
      setTimeout(applyAllFixes, 0);
      return result;
    };
  }

  document.addEventListener('DOMContentLoaded', () => {
    applyAllFixes();
    setTimeout(applyAllFixes, 250);
    setTimeout(applyAllFixes, 1000);
  });
})();
</script>
"""
