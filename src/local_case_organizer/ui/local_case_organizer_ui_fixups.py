from __future__ import annotations

FIXUP_CSS = r'''
<style>
  .lco-brandbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:20px;
    margin: 2px 0 42px;
  }
  .lco-brand {
    display:inline-flex;
    align-items:center;
    gap:13px;
  }
  .lco-brand-mark { width:38px; height:38px; }
  .lco-brand-mark svg { width:100%; height:100%; display:block; }
  .lco-brand-copy { display:flex; flex-direction:column; gap:2px; }
  .lco-brand-name { font-size:.83rem; letter-spacing:.19em; font-weight:800; }
  .lco-product-name { color:var(--lco-muted,#aaa49a); font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; }

  .hero {
    padding: 30px 0 46px !important;
    box-shadow:none !important;
    border-radius:0 !important;
    border:0 !important;
    border-bottom:1px solid var(--lco-border,rgba(244,240,232,.10)) !important;
    background:transparent !important;
  }
  .hero h1 {
    max-width:850px;
    margin-bottom:18px;
    font-size:clamp(2.8rem,5.5vw,5.4rem);
    line-height:.98;
    letter-spacing:-.045em;
  }
  .hero .lead { max-width:820px; font-size:1.08rem; line-height:1.7; }
  .hero .note { max-width:760px; }

  .next-step {
    position:relative;
    margin-top:38px !important;
    padding:24px 26px !important;
    border-radius:20px !important;
    border:1px solid var(--lco-border-strong,rgba(198,154,82,.34)) !important;
    border-left:2px solid var(--lco-gold,#c69a52) !important;
    font-size:1rem;
    line-height:1.65;
  }
  .next-step::before {
    content:"NÄCHSTER SCHRITT";
    display:block;
    margin-bottom:7px;
    color:var(--lco-gold,#c69a52);
    font-size:.72rem;
    letter-spacing:.15em;
    font-weight:800;
  }

  .lco-process {
    display:grid;
    grid-template-columns:repeat(6,minmax(0,1fr));
    gap:0;
    margin:32px 0 44px;
    border-top:1px solid var(--lco-border,rgba(244,240,232,.10));
    border-bottom:1px solid var(--lco-border,rgba(244,240,232,.10));
  }
  .lco-process-step {
    min-width:0;
    padding:16px 12px;
    border-right:1px solid var(--lco-border,rgba(244,240,232,.10));
  }
  .lco-process-step:last-child { border-right:0; }
  .lco-process-step span {
    display:block;
    margin-bottom:5px;
    color:var(--lco-gold,#c69a52);
    font-size:.71rem;
    letter-spacing:.11em;
    font-weight:800;
  }
  .lco-process-step strong { display:block; font-size:.88rem; line-height:1.35; }

  .section-title {
    margin-top:38px !important;
    margin-bottom:12px !important;
    font-size:clamp(1.45rem,2.5vw,2.15rem);
    letter-spacing:-.025em;
  }
  .editor, .upload-box, .file-list, .paths, .log {
    border-radius:18px !important;
  }
  .editor, .upload-box, .file-list {
    border:1px solid var(--lco-border,rgba(244,240,232,.10)) !important;
  }

  #cards {
    grid-template-columns:repeat(auto-fit,minmax(165px,1fr)) !important;
    gap:12px !important;
  }
  #cards .card {
    min-height:94px;
    box-shadow:none !important;
    border:1px solid var(--lco-border,rgba(244,240,232,.10)) !important;
  }
  #cards .card > div:first-child { color:var(--lco-muted,#aaa49a) !important; font-size:.85rem; }
  #cards .value { font-size:2rem; }

  .actions { gap:10px !important; }
  .upload-row, .editor-actions { gap:10px !important; }
  .hint { line-height:1.55; }

  .lco-tech-details {
    margin-top:38px;
    border:1px solid var(--lco-border,rgba(244,240,232,.10));
    border-radius:18px;
    overflow:hidden;
  }
  .lco-tech-details > summary {
    cursor:pointer;
    list-style:none;
    padding:17px 19px;
    font-weight:750;
  }
  .lco-tech-details > summary::-webkit-details-marker { display:none; }
  .lco-tech-details > summary::after {
    content:"+";
    float:right;
    color:var(--lco-gold,#c69a52);
    font-size:1.2rem;
  }
  .lco-tech-details[open] > summary::after { content:"−"; }
  .lco-tech-body {
    padding:18px;
    border-top:1px solid var(--lco-border,rgba(244,240,232,.10));
  }
  .lco-tech-body .actions { margin-top:0 !important; }
  .lco-tech-label {
    margin:22px 0 8px;
    color:var(--lco-muted,#aaa49a);
    font-size:.82rem;
  }

  .lco-hidden-heading { display:none !important; }

  table th { font-size:.78rem; line-height:1.3; }
  td.readonly { font-size:.78rem !important; }

  @media (max-width:900px) {
    .lco-process { grid-template-columns:repeat(3,1fr); }
    .lco-process-step:nth-child(3) { border-right:0; }
    .lco-process-step:nth-child(-n+3) { border-bottom:1px solid var(--lco-border,rgba(244,240,232,.10)); }
  }
  @media (max-width:620px) {
    .lco-process { grid-template-columns:1fr; }
    .lco-process-step { border-right:0; border-bottom:1px solid var(--lco-border,rgba(244,240,232,.10)); }
    .lco-process-step:last-child { border-bottom:0; }
    .lco-brandbar { margin-bottom:24px; }
  }
</style>
'''

FIXUP_SCRIPT = r'''
<script>
(function () {
  const COPY = {
    de: {
      heroTitle: 'Deine Unterlagen. Klar geordnet.',
      heroLead: 'Sammle Dokumente an einem Ort, ordne sie, baue eine verständliche Zeitlinie auf und erstelle daraus ein sauberes Übergabepaket.',
      heroNote: 'Alles bleibt lokal auf diesem Computer. Deine Originaldateien werden beim Import nachvollziehbar übernommen.',
      statusTitle: 'Auf einen Blick',
      addTitle: '1. Dokumente hinzufügen',
      mainTitle: '2. Unterlagen ordnen',
      registerTitle: '3. Dokumente prüfen',
      timelineTitle: '4. Zeitlinie aufbauen',
      entitiesTitle: '5. Personen & Organisationen',
      exportTitle: '6. Übergabe vorbereiten',
      recentTitle: 'Dateien, die noch warten',
      upload: 'Ausgewählte Dateien hinzufügen',
      openInbox: 'Ordner für neue Dateien öffnen',
      uploadHint: 'Du kannst Dateien hier auswählen oder sie direkt in den Ordner für neue Unterlagen legen.',
      setup: 'Arbeitsbereich vorbereiten',
      importFiles: 'Wartende Dateien übernehmen',
      buildRegister: 'Dokumentenübersicht erstellen',
      buildTimeline: 'Zeitlinie erstellen',
      buildExport: 'Übergabepaket erstellen',
      openRegister: 'Ordner mit Arbeitslisten öffnen',
      openExports: 'Ordner mit Übergaben öffnen',
      doctor: 'Probleme prüfen',
      refresh: 'Ansicht aktualisieren',
      loadRegister: 'Dokumentenübersicht laden',
      saveRegister: 'Änderungen speichern',
      loadTimeline: 'Zeitlinie laden',
      addTimeline: 'Ereignis hinzufügen',
      saveTimeline: 'Zeitlinie speichern',
      loadEntities: 'Einträge laden',
      addEntity: 'Person oder Organisation hinzufügen',
      saveEntities: 'Änderungen speichern',
      loadExports: 'Übergaben aktualisieren',
      techSummary: 'Weitere Optionen & technische Details',
      localPaths: 'Lokale Speicherorte',
      log: 'Technisches Protokoll',
      process: ['Dokumente hinzufügen','Unterlagen übernehmen','Dokumente prüfen','Zeitlinie','Personen & Organisationen','Übergabe'],
      next_step_add_files: 'Füge zuerst die Dokumente hinzu, die du für diesen Fall ordnen möchtest.',
      next_step_import_waiting: 'Die neuen Dateien sind bereit. Übernimm sie jetzt in diesen Fall.',
      next_step_build_register: 'Erstelle jetzt die Dokumentenübersicht, damit du die Unterlagen prüfen und ordnen kannst.',
      next_step_select_export: 'Wähle in der Dokumentenübersicht aus, welche Unterlagen später in die Übergabe gehören.',
      next_step_first_export: 'Alles ist vorbereitet. Erstelle jetzt dein erstes Übergabepaket.',
      next_step_workspace_ready: 'Dein Fall ist bereits aufgebaut. Prüfe oder ergänze die Bereiche unten.',
      next_step_use_buttons: 'Wähle den nächsten passenden Schritt unten.',
      registerHint: 'Hier prüfst du Dokumente, gruppierst sie, markierst sie für die spätere Übergabe und ergänzt Notizen.',
      timelineHint: 'Ordne Ereignissen die passenden Dokumente zu. Die bekannten Dokumente werden darunter angezeigt.',
      timelineKnown: 'Bekannte Dokumente erscheinen hier, sobald die Dokumentenübersicht geladen wurde.',
      timelineEmpty: 'Noch keine Ereignisse vorhanden. Erstelle zuerst die Zeitlinie oder füge ein Ereignis hinzu.',
      entitiesHint: 'Verbinde Personen, Institutionen oder Firmen mit den Dokumenten, in denen sie eine Rolle spielen.',
      entitiesKnown: 'Bekannte Dokumente erscheinen hier, sobald die Dokumentenübersicht geladen wurde.',
      entitiesEmpty: 'Noch keine Personen oder Organisationen eingetragen.',
      exportHint: 'Hier siehst du bereits erstellte Übergabepakete und wie viele Originaldokumente sie enthalten.',
      exportEmpty: 'Noch kein Übergabepaket erstellt.',
      waitingNone: 'Aktuell warten keine neuen Dateien auf die Übernahme.',
      table: {
        file_id:'Datei-ID', original_name:'Dateiname', relative_path:'Datei',
        review_status:'Prüfung', document_group:'Gruppe', selected_for_export:'Für Übergabe',
        linked_timeline_event_ids:'In Zeitlinie', linked_entity_ids:'Verknüpft mit', note:'Notiz',
        event_id:'Ereignis-ID', date:'Datum', title:'Ereignis', description:'Beschreibung',
        linked_file_ids:'Zugehörige Dokumente', entity_id:'Eintrag-ID', entity_type:'Art',
        name:'Name', role:'Rolle', aliases:'Weitere Namen',
        export_dir:'Paket', zip_name:'ZIP-Datei', manifest_name:'Begleitdatei',
        selected_originals_count:'Originale enthalten'
      }
    },
    en: {
      heroTitle: 'Your documents. Clearly organized.',
      heroLead: 'Bring documents together, organize them, build a clear timeline and create a clean handoff package.',
      heroNote: 'Everything stays local on this computer. Imported originals remain traceable.',
      statusTitle: 'At a glance',
      addTitle: '1. Add documents',
      mainTitle: '2. Organize your files',
      registerTitle: '3. Review documents',
      timelineTitle: '4. Build the timeline',
      entitiesTitle: '5. People & organizations',
      exportTitle: '6. Prepare the handoff',
      recentTitle: 'Files still waiting',
      upload: 'Add selected files',
      openInbox: 'Open folder for new files',
      uploadHint: 'Choose files here or place them directly in the folder for new documents.',
      setup: 'Prepare workspace',
      importFiles: 'Add waiting files to this case',
      buildRegister: 'Create document overview',
      buildTimeline: 'Create timeline',
      buildExport: 'Create handoff package',
      openRegister: 'Open working-list folder',
      openExports: 'Open handoff folder',
      doctor: 'Check for problems',
      refresh: 'Refresh view',
      loadRegister: 'Load document overview',
      saveRegister: 'Save changes',
      loadTimeline: 'Load timeline',
      addTimeline: 'Add event',
      saveTimeline: 'Save timeline',
      loadEntities: 'Load entries',
      addEntity: 'Add person or organization',
      saveEntities: 'Save changes',
      loadExports: 'Refresh handoffs',
      techSummary: 'More options & technical details',
      localPaths: 'Local storage locations',
      log: 'Technical log',
      process: ['Add documents','Bring files in','Review documents','Timeline','People & organizations','Handoff'],
      next_step_add_files: 'First add the documents you want to organize for this case.',
      next_step_import_waiting: 'The new files are ready. Add them to this case now.',
      next_step_build_register: 'Create the document overview so you can review and organize the files.',
      next_step_select_export: 'Choose in the document overview which files should later be included in the handoff.',
      next_step_first_export: 'Everything is prepared. Create your first handoff package.',
      next_step_workspace_ready: 'Your case is already set up. Review or update the sections below.',
      next_step_use_buttons: 'Choose the next useful step below.',
      registerHint: 'Review documents here, group them, mark them for the handoff and add notes.',
      timelineHint: 'Connect events with the documents that belong to them. Known documents are shown below.',
      timelineKnown: 'Known documents appear here once the document overview is loaded.',
      timelineEmpty: 'No events yet. Create the timeline first or add an event.',
      entitiesHint: 'Connect people, institutions or companies with the documents in which they appear.',
      entitiesKnown: 'Known documents appear here once the document overview is loaded.',
      entitiesEmpty: 'No people or organizations added yet.',
      exportHint: 'See previously created handoff packages and how many original documents they contain.',
      exportEmpty: 'No handoff package created yet.',
      waitingNone: 'No new files are waiting to be added.',
      table: {
        file_id:'File ID', original_name:'Filename', relative_path:'File',
        review_status:'Review', document_group:'Group', selected_for_export:'Include in handoff',
        linked_timeline_event_ids:'Used in timeline', linked_entity_ids:'Linked to', note:'Note',
        event_id:'Event ID', date:'Date', title:'Event', description:'Description',
        linked_file_ids:'Related documents', entity_id:'Entry ID', entity_type:'Type',
        name:'Name', role:'Role', aliases:'Other names',
        export_dir:'Package', zip_name:'ZIP file', manifest_name:'Companion file',
        selected_originals_count:'Originals included'
      }
    }
  };

  const RAW_NEXT = {
    "Next step: add files through the upload area or open the inbox folder and place files there.": 'next_step_add_files',
    "Next step: use 'Import inbox files' to move your waiting files into a tracked import batch.": 'next_step_import_waiting',
    "Next step: use 'Build register' to create your document register.": 'next_step_build_register',
    "Next step: mark the important register rows with 'selected_for_export = yes' so the handoff package knows what to include.": 'next_step_select_export',
    "Next step: create your first export package.": 'next_step_first_export',
    "Your workspace already has imports, working tables, and exports. Use the browser tables to keep the dossier current.": 'next_step_workspace_ready',
    "Use the main action buttons below.": 'next_step_use_buttons'
  };

  function currentLang() {
    const value = localStorage.getItem('local_case_organizer_ui_lang') || document.documentElement.lang || 'en';
    return String(value).toLowerCase().startsWith('de') ? 'de' : 'en';
  }

  function copy() { return COPY[currentLang()]; }

  function textButton(selector, value) {
    const el = document.querySelector(selector);
    if (el) el.textContent = value;
  }

  function headingBefore(element) {
    if (!element) return null;
    let node = element.previousElementSibling;
    while (node && !node.matches('h2.section-title')) node = node.previousElementSibling;
    return node;
  }

  function sectionHeadingForInner(id) {
    const el = document.getElementById(id);
    if (!el) return null;
    const box = el.closest('.editor, .upload-box, .file-list, .paths, .log');
    return box ? headingBefore(box) : null;
  }

  function ensureBrand() {
    const wrap = document.querySelector('.wrap');
    if (!wrap || document.getElementById('lco-brandbar')) return;
    const bar = document.createElement('div');
    bar.id = 'lco-brandbar';
    bar.className = 'lco-brandbar';
    bar.innerHTML = `
      <div class="lco-brand">
        <span class="lco-brand-mark" aria-hidden="true">
          <svg viewBox="0 0 64 64" fill="none">
            <g stroke="#e1b969" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round">
              <path d="M32 5.5C25.8 13.3 25.5 22.7 32 30.8C38.5 22.7 38.2 13.3 32 5.5Z"/>
              <path d="M31.6 30.1C23.1 20.8 12.4 22.4 5.8 31.8C13.4 40.5 23.7 41.2 31.8 32.5"/>
              <path d="M32.4 30.1C40.9 20.8 51.6 22.4 58.2 31.8C50.6 40.5 40.3 41.2 32.2 32.5"/>
              <path d="M32 33.2C25.7 41.4 26 50.8 32 58.5C38 50.8 38.3 41.4 32 33.2Z"/>
              <path d="M32 24.8L39.2 32L32 39.2L24.8 32L32 24.8Z"/>
              <path d="M19.7 29.1L15.2 33.2L23.2 39.1"/>
              <path d="M44.3 29.1L48.8 33.2L40.8 39.1"/>
            </g>
          </svg>
        </span>
        <span class="lco-brand-copy">
          <span class="lco-brand-name">TOF SYSTEMS</span>
          <span class="lco-product-name">Case Organizer</span>
        </span>
      </div>`;
    wrap.insertBefore(bar, wrap.firstChild);
  }

  function ensureProcess() {
    const next = document.getElementById('next-step');
    if (!next) return;
    let root = document.getElementById('lco-process');
    if (!root) {
      root = document.createElement('div');
      root.id = 'lco-process';
      root.className = 'lco-process';
      next.insertAdjacentElement('afterend', root);
    }
    root.innerHTML = copy().process.map((label,index) =>
      `<div class="lco-process-step"><span>0${index+1}</span><strong>${label}</strong></div>`
    ).join('');
  }

  function humanizeTables() {
    const labels = copy().table;
    document.querySelectorAll('table th').forEach(th => {
      const key = th.textContent.trim();
      if (labels[key]) th.textContent = labels[key];
    });
  }

  function humanizeCards() {
    const cards = Array.from(document.querySelectorAll('#cards .card'));
    const labels = currentLang() === 'de'
      ? ['Wartende Dateien','Dokumente im Fall',null,null,'Übergabepakete','Für Übergabe ausgewählt','Personen & Organisationen']
      : ['Waiting files','Documents in case',null,null,'Handoff packages','Selected for handoff','People & organizations'];
    cards.forEach((card,index) => {
      if (labels[index] === null) {
        card.style.display = 'none';
        return;
      }
      card.style.display = '';
      const label = card.querySelector('div');
      if (label && labels[index]) label.textContent = labels[index];
    });
  }

  function humanizeNextStep(value) {
    const raw = String(value || '').trim();
    const key = raw.startsWith('next_step_') ? raw : (RAW_NEXT[raw] || 'next_step_use_buttons');
    return copy()[key] || copy().next_step_use_buttons;
  }

  function moveTechnicalSections() {
    if (document.getElementById('lco-tech-details')) return;

    const openRegister = document.querySelector('button[onclick*="open-register"]');
    const helpfulActions = openRegister ? openRegister.closest('.actions') : null;
    const helpfulHeading = helpfulActions ? headingBefore(helpfulActions) : null;

    const paths = document.getElementById('paths')?.closest('.paths');
    const pathsHeading = paths ? headingBefore(paths) : null;
    const log = document.getElementById('log')?.closest('.log');
    const logHeading = log ? headingBefore(log) : null;

    const anchor = log || paths || helpfulActions;
    if (!anchor || !anchor.parentNode) return;

    const details = document.createElement('details');
    details.id = 'lco-tech-details';
    details.className = 'lco-tech-details';
    const summary = document.createElement('summary');
    summary.textContent = copy().techSummary;
    const body = document.createElement('div');
    body.className = 'lco-tech-body';
    details.append(summary, body);

    if (helpfulActions) body.appendChild(helpfulActions);
    if (paths) {
      const label = document.createElement('div');
      label.className = 'lco-tech-label';
      label.dataset.role = 'paths-label';
      label.textContent = copy().localPaths;
      body.append(label, paths);
    }
    if (log) {
      const label = document.createElement('div');
      label.className = 'lco-tech-label';
      label.dataset.role = 'log-label';
      label.textContent = copy().log;
      body.append(label, log);
    }

    [helpfulHeading, pathsHeading, logHeading].forEach(el => {
      if (el) el.classList.add('lco-hidden-heading');
    });

    anchor.parentNode.appendChild(details);
  }

  function applyHumanCopy() {
    ensureBrand();
    ensureProcess();
    moveTechnicalSections();

    const t = copy();
    const hero = document.querySelector('.hero');
    if (hero) {
      const h1 = hero.querySelector('h1');
      const lead = hero.querySelector('.lead');
      const note = hero.querySelector('.note');
      if (h1) h1.textContent = t.heroTitle;
      if (lead) lead.textContent = t.heroLead;
      if (note) note.textContent = t.heroNote;
    }

    const cards = document.getElementById('cards');
    const statusHeading = cards ? headingBefore(cards) : null;
    if (statusHeading) statusHeading.textContent = t.statusTitle;

    const upload = document.getElementById('fileInput')?.closest('.upload-box');
    const uploadHeading = upload ? headingBefore(upload) : null;
    if (uploadHeading) uploadHeading.textContent = t.addTitle;
    if (upload) {
      const hint = upload.querySelector('.hint');
      if (hint) hint.textContent = t.uploadHint;
    }

    const setupButton = document.querySelector('button[onclick*="runAction(\'setup\')"]');
    const mainActions = setupButton ? setupButton.closest('.actions') : null;
    const mainHeading = mainActions ? headingBefore(mainActions) : null;
    if (mainHeading) mainHeading.textContent = t.mainTitle;

    const registerHeading = sectionHeadingForInner('register-editor');
    const timelineHeading = sectionHeadingForInner('timeline-editor');
    const entityHeading = sectionHeadingForInner('entity-editor');
    const exportHeading = sectionHeadingForInner('export-history');
    const recentHeading = sectionHeadingForInner('recent-files');
    if (registerHeading) registerHeading.textContent = t.registerTitle;
    if (timelineHeading) timelineHeading.textContent = t.timelineTitle;
    if (entityHeading) entityHeading.textContent = t.entitiesTitle;
    if (exportHeading) exportHeading.textContent = t.exportTitle;
    if (recentHeading) recentHeading.textContent = t.recentTitle;

    textButton('button[onclick="uploadFiles()"]', t.upload);
    textButton('button[onclick*="open-inbox"]', t.openInbox);
    textButton('button[onclick*="runAction(\'setup\')"]', t.setup);
    textButton('button[onclick*="runAction(\'import\')"]', t.importFiles);
    textButton('button[onclick*="runAction(\'build-register\')"]', t.buildRegister);
    textButton('button[onclick*="runAction(\'build-timeline\')"]', t.buildTimeline);
    textButton('button[onclick*="runAction(\'export-package\')"]', t.buildExport);
    textButton('button[onclick*="open-register"]', t.openRegister);
    textButton('button[onclick*="open-exports"]', t.openExports);
    textButton('button[onclick*="doctor"]', t.doctor);
    textButton('button[onclick="refreshAll()"]', t.refresh);
    textButton('button[onclick="loadRegister()"]', t.loadRegister);
    textButton('button[onclick="saveRegister()"]', t.saveRegister);
    textButton('button[onclick="loadTimeline()"]', t.loadTimeline);
    textButton('button[onclick="addTimelineRow()"]', t.addTimeline);
    textButton('button[onclick="saveTimeline()"]', t.saveTimeline);
    textButton('button[onclick="loadEntities()"]', t.loadEntities);
    textButton('button[onclick="addEntityRow()"]', t.addEntity);
    textButton('button[onclick="saveEntities()"]', t.saveEntities);
    textButton('button[onclick="loadExportHistory()"]', t.loadExports);

    const registerEditor = document.getElementById('register-editor')?.closest('.editor');
    if (registerEditor) {
      const hint = registerEditor.querySelector('.hint');
      if (hint) hint.textContent = t.registerHint;
    }
    const timelineEditor = document.getElementById('timeline-editor')?.closest('.editor');
    if (timelineEditor) {
      const hints = timelineEditor.querySelectorAll('.hint');
      if (hints[0]) hints[0].textContent = t.timelineHint;
      if (hints[1] && !hints[1].querySelector('.chip-list')) hints[1].textContent = t.timelineKnown;
      if (hints[2] && !hints[2].querySelector('table')) hints[2].textContent = t.timelineEmpty;
    }
    const entityEditor = document.getElementById('entity-editor')?.closest('.editor');
    if (entityEditor) {
      const hints = entityEditor.querySelectorAll('.hint');
      if (hints[0]) hints[0].textContent = t.entitiesHint;
      if (hints[1] && !hints[1].querySelector('.chip-list')) hints[1].textContent = t.entitiesKnown;
      if (hints[2] && !hints[2].querySelector('table')) hints[2].textContent = t.entitiesEmpty;
    }
    const exportEditor = document.getElementById('export-history')?.closest('.editor');
    if (exportEditor) {
      const hints = exportEditor.querySelectorAll('.hint');
      if (hints[0]) hints[0].textContent = t.exportHint;
      if (hints[1] && !hints[1].querySelector('table')) hints[1].textContent = t.exportEmpty;
    }

    const recent = document.getElementById('recent-files');
    if (recent && /No files are currently waiting|Keine Dateien/i.test(recent.textContent)) {
      recent.textContent = t.waitingNone;
    }

    const next = document.getElementById('next-step');
    if (next) next.textContent = humanizeNextStep(next.textContent);

    const tech = document.getElementById('lco-tech-details');
    if (tech) {
      const summary = tech.querySelector(':scope > summary');
      if (summary) summary.textContent = t.techSummary;
      const pathsLabel = tech.querySelector('[data-role="paths-label"]');
      const logLabel = tech.querySelector('[data-role="log-label"]');
      if (pathsLabel) pathsLabel.textContent = t.localPaths;
      if (logLabel) logLabel.textContent = t.log;
    }

    humanizeCards();
    humanizeTables();
  }

  const originalRenderNextStep = window.renderNextStep;
  if (typeof originalRenderNextStep === 'function') {
    window.renderNextStep = function(value) {
      return originalRenderNextStep.call(this, humanizeNextStep(value));
    };
  }

  ['buildRegisterTable','buildTimelineTable','buildEntityTable','renderExportHistory'].forEach(name => {
    const original = window[name];
    if (typeof original === 'function') {
      window[name] = function() {
        const result = original.apply(this, arguments);
        setTimeout(() => { humanizeTables(); applyHumanCopy(); }, 0);
        return result;
      };
    }
  });

  const originalRefreshAll = window.refreshAll;
  if (typeof originalRefreshAll === 'function') {
    window.refreshAll = async function() {
      const result = await originalRefreshAll.apply(this, arguments);
      setTimeout(applyHumanCopy, 0);
      return result;
    };
  }

  const originalRefreshStatus = window.refreshStatus;
  if (typeof originalRefreshStatus === 'function') {
    window.refreshStatus = async function() {
      const result = await originalRefreshStatus.apply(this, arguments);
      setTimeout(applyHumanCopy, 0);
      return result;
    };
  }

  const originalToggleLanguage = window.toggleLanguage;
  if (typeof originalToggleLanguage === 'function') {
    window.toggleLanguage = function() {
      const result = originalToggleLanguage.apply(this, arguments);
      setTimeout(applyHumanCopy, 0);
      setTimeout(applyHumanCopy, 80);
      return result;
    };
  }

  const originalApplyLanguage = window.applyLanguage;
  if (typeof originalApplyLanguage === 'function') {
    window.applyLanguage = function() {
      const result = originalApplyLanguage.apply(this, arguments);
      setTimeout(applyHumanCopy, 0);
      return result;
    };
  }

  document.addEventListener('DOMContentLoaded', () => {
    applyHumanCopy();
    setTimeout(applyHumanCopy, 250);
    setTimeout(applyHumanCopy, 900);
  });
})();
</script>
'''
