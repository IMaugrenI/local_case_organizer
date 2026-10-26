"""Focused UI experience layer for the established local browser interface.

B02: keep all original nodes, callbacks and local-only data paths intact.
No second UI or external dependency.
"""
EXPERIENCE_CSS = r'''<style>
[hidden]{display:none!important}
/* B02 usability correction: keep the original backend, HTML, handlers and theme. */
html{font-size:16px;scroll-behavior:smooth}
body{font-size:1rem!important;line-height:1.55}
body .wrap{max-width:1380px!important;padding:22px clamp(16px,3vw,44px) 65px!important}
body .hero{padding:15px 0 26px!important}
body .hero h1{font-size:clamp(2.1rem,4vw,4.2rem)!important;line-height:1.1!important}
body .hero .lead{font-size:1.07rem!important;line-height:1.65!important}
body .hero .note{font-size:.95rem!important}
body .lco-brandbar{margin-bottom:20px!important}
body .next-step{padding:18px 22px!important;margin-top:18px!important}
body .lco-process{margin:22px 0!important}
body .lco-process-step{padding:11px!important}
.lco-workspace-nav{position:sticky;top:0;z-index:20;display:flex;gap:8px;align-items:center;overflow-x:auto;padding:11px;margin:18px 0 24px;background:var(--lco-bg,#0d0d0c);border:1px solid var(--lco-border,rgba(244,240,232,.13));border-radius:16px;box-shadow:0 8px 28px rgba(0,0,0,.13)}
.lco-workspace-nav button{flex:0 0 auto;white-space:nowrap;font-size:.99rem!important;min-height:44px!important;padding:11px 16px!important;background:transparent!important;color:var(--lco-muted,#aaa49a)!important;border:1px solid transparent!important}
.lco-workspace-nav button[aria-current=page]{background:var(--lco-gold,#c69a52)!important;color:#1b160e!important}
.lco-workspace-nav button:hover:not([aria-current=page]){color:var(--lco-text,#f4f0e8)!important;background:var(--lco-surface,#181612)!important}
[hidden].lco-hidden-by-view{display:none!important}
.wrap{min-height:250px}
.wrap .section-title{font-size:clamp(1.4rem,2.2vw,1.85rem)!important;margin-top:28px!important;margin-bottom:12px!important}
.wrap>.editor,.wrap>.file-list,.wrap>.upload-box,.wrap>.actions,.wrap>.grid,.wrap>.lco-tech-details{margin-bottom:24px!important}
.wrap .editor,.wrap .upload-box{padding:clamp(17px,2vw,28px)!important}
.wrap .hint,.wrap .note{font-size:.96rem!important;line-height:1.65!important;color:#c5beb3!important}
.wrap p{line-height:1.65}
.wrap .editor-actions,.wrap .upload-row{gap:12px!important;align-items:flex-end;margin-bottom:15px}
.wrap .editor-actions>label{display:flex;flex:1 1 205px;min-width:180px;flex-direction:column;gap:8px;font-size:.98rem}
.wrap .editor-actions>label:has(input[type=checkbox]){flex:0 0 auto;min-width:unset;flex-direction:row;align-items:center}
.wrap input[type=text],.wrap input[type=date],.wrap input[type=number],.wrap textarea,.wrap select{box-sizing:border-box;min-height:44px;max-width:100%;padding:10px 12px;font-size:1rem!important}
.wrap input[type=checkbox]{width:18px;height:18px;accent-color:var(--lco-gold,#c69a52)}
.wrap textarea{min-height:100px;margin:9px 0 15px}
.wrap button{font-size:.96rem!important;padding:12px 16px!important}
.wrap .actions{grid-template-columns:repeat(auto-fit,minmax(215px,1fr))!important}
.wrap .grid{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))!important}
.wrap table{font-size:.93rem}
.wrap table th{font-size:.88rem!important}
.wrap td.readonly{font-size:.87rem!important}
.wrap [aria-live=polite]{overflow-wrap:anywhere}
body.lco-light .lco-workspace-nav{background:#f6f1e8}
body.lco-light .lco-workspace-nav button{color:#645746!important}
body.lco-light .lco-workspace-nav button[aria-current=page]{background:#9b7135!important;color:white!important}
body.lco-light .wrap .hint,body.lco-light .wrap .note{color:#544d44!important}
@media(max-width:680px){.lco-workspace-nav{margin:12px -4px 18px;padding:7px}.wrap .editor-actions>label{min-width:100%}.wrap .actions{grid-template-columns:1fr!important}body .lco-process{display:none}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}


/* B02 contrast patch: foreground/background pairs validated against WCAG 2.x AA.
   Regular text >=4.5:1, interactive boundaries >=3:1.
   Use opaque form surfaces: native date inputs, selects and dropdowns must never
   render light text on the browser's default light widget background. */
body{
  --lco-control-bg:#201e1a;
  --lco-control-fg:#f4f0e8;
  --lco-control-placeholder:#bdb4a7;
  --lco-control-border:#8d806e;
  --lco-contrast-primary-bg:#c69a52;
  --lco-contrast-primary-fg:#17120d;
  color-scheme:dark;
}
body.lco-light{
  --lco-control-bg:#fbf8f2;
  --lco-control-fg:#211d18;
  --lco-control-placeholder:#665b4f;
  --lco-control-border:#8b8070;
  --lco-contrast-primary-bg:#80571b;
  --lco-contrast-primary-fg:#ffffff;
  color-scheme:light;
}
body input[type=text],
body input[type=number],
body input[type=date],
body input[type=email],
body input[type=search],
body input[type=file],
body select,
body textarea{
  background:var(--lco-control-bg)!important;
  color:var(--lco-control-fg)!important;
  border:1px solid var(--lco-control-border)!important;
}
body input::placeholder,
body textarea::placeholder{
  color:var(--lco-control-placeholder)!important;
  opacity:1!important;
}
body select option{
  background:var(--lco-control-bg)!important;
  color:var(--lco-control-fg)!important;
}
body input[type=file]::file-selector-button{
  border:1px solid var(--lco-control-border);
  border-radius:9px;
  background:var(--lco-control-bg);
  color:var(--lco-control-fg);
  padding:9px 12px;
  cursor:pointer;
}
body button:not(.ghost):not(.light):not(.secondary):not(.lco-theme-toggle){
  background:var(--lco-contrast-primary-bg)!important;
  color:var(--lco-contrast-primary-fg)!important;
}
body .lco-workspace-nav button:not(.ghost):not(.light):not(.secondary):not(.lco-theme-toggle){
  background:transparent!important;
  color:var(--lco-muted)!important;
}
body .lco-workspace-nav button:hover:not([aria-current=page]):not(.ghost):not(.light):not(.secondary):not(.lco-theme-toggle){
  background:var(--lco-surface)!important;
  color:var(--lco-text)!important;
}
body .lco-workspace-nav button[aria-current=page]:not(.ghost):not(.light):not(.secondary):not(.lco-theme-toggle){
  background:var(--lco-contrast-primary-bg)!important;
  color:var(--lco-contrast-primary-fg)!important;
}
body.lco-light .next-step{
  color:#544d44!important;
  background:#fbf8f2!important;
}
body.lco-light .next-step::before,
body.lco-light .lco-process-step span,
body.lco-light .lco-tech-details>summary::after,
body.lco-light .lco-tech-label{
  color:#80571b!important;
}
body.lco-light .lco-feedback.ok{
  color:#256145!important;
  background:#eef7f0!important;
}
body.lco-light .lco-feedback.attention{
  color:#81530d!important;
  background:#fff4df!important;
}
body.lco-light .lco-skip-link{
  background:#80571b!important;
  color:#fff!important;
}
body.lco-light .wrap .hint,
body.lco-light .wrap .note{
  color:#544d44!important;
}
body .lco-workspace-nav button:focus-visible,
body .wrap button:focus-visible,
body .wrap input:focus-visible,
body .wrap select:focus-visible,
body .wrap textarea:focus-visible{
  outline:3px solid var(--lco-gold-bright)!important;
  outline-offset:3px;
}

/* Explicit readable light-mode foregrounds on every existing card/control. */
body.lco-light .hero,
body.lco-light .card,
body.lco-light .editor,
body.lco-light .upload-box,
body.lco-light .file-list,
body.lco-light .lco-tech-details{
 color:#211d18!important;
}
body.lco-light :is(.editor,.upload-box,.file-list,.card) :is(p,li,blockquote,label),
body.lco-light .hero :is(h1,.lead,.note){
 color:#211d18!important;
}
body.lco-light :is(.editor,.upload-box,.file-list,.card) :is(.hint,.note,.readonly){
 color:#4d463e!important;
}
body.lco-light .lco-feedback:not(.ok):not(.attention){
 color:#211d18!important;
 background:#fbf8f2!important;
}
body.lco-light button.ghost,
body.lco-light button.light,
body.lco-light button.secondary,
body.lco-light #lang-toggle,
body.lco-light .lco-theme-toggle{
 background:#ece4d9!important;
 color:#211d18!important;
 border-color:#8b8070!important;
}
body.lco-light #lco-workspace-nav button:not([aria-current=page]){
 background:transparent!important;
 color:#302920!important;
}
body.lco-light #lco-workspace-nav button[aria-current=page]{
 background:#80571b!important;
 color:#ffffff!important;
}
body.lco-light a:not(.lco-skip-link){color:#16497b}
body.lco-light table :is(th,td){color:#211d18!important}
body.lco-light table th{background:#e5ddd1!important}
body.lco-light td.readonly{color:#4d463e!important}
body.lco-light .chip{color:#664515!important;background:#f7eddc!important}
body.lco-light .lco-brand-name,
body.lco-light .lco-product-name{color:#211d18!important}
body.lco-light .lco-brand-mark{color:#80571b}

/* Unified card rhythm and readable help text without changing the workflow. */
body .editor,body .upload-box,body .file-list{
  padding:clamp(22px,2.5vw,32px)!important;
  box-sizing:border-box;
}
body #cards .card{padding:19px 20px!important;min-width:0;box-sizing:border-box;}
body #cards .card>div:first-child{font-size:.92rem!important;line-height:1.5;}
body .editor-actions>label,body .editor>label{line-height:1.55;}
body .lco-feedback{padding:16px 20px!important;line-height:1.55;}
body .hero .lang-state,body .hero .lang-status{font-size:.92rem!important;}
body .lco-process-step strong{font-size:.94rem!important;line-height:1.45;}
body.lco-light .hero .lang-state,body.lco-light .hero .lang-status{color:#3a332b!important;}

/* Global controls: fixed in the top brand row, never inside a hidden work area. */
body .wrap #lco-brandbar{
  position:sticky;
  top:0;
  z-index:35;
  min-height:64px;
  margin:0 0 14px!important;
  padding:8px 0;
  box-sizing:border-box;
  background:var(--lco-bg,#0d0d0c)!important;
  border-bottom:1px solid var(--lco-border,rgba(244,240,232,.10));
  display:flex;
  flex-wrap:wrap;
  justify-content:space-between;
  align-items:center;
  gap:12px 22px;
}
body .wrap #lco-workspace-nav{
  top:var(--lco-brandbar-height,64px);
  margin-top:0!important;
}
body .wrap #lco-brandbar .lco-top-toggles{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  align-items:center;
  /* A small right-hand inset shifts both switches left as a group. */
  margin:0 clamp(18px,3vw,36px) 0 auto;
  padding:0;
}
body #lco-brandbar #lang-toggle,
body #lco-brandbar #theme-toggle,
body #lco-brandbar .lco-header-control{
  min-height:40px!important;
  min-width:82px;
  font-size:.88rem!important;
  font-weight:700;
  padding:8px 12px!important;
  border-radius:9px!important;
  border:1px solid #81715b!important;
  background:#211e18!important;
  color:#f4f0e8!important;
}
body.lco-light .wrap #lco-brandbar{background:#efe9df!important}
body.lco-light #lco-brandbar #lang-toggle,
body.lco-light #lco-brandbar #theme-toggle,
body.lco-light #lco-brandbar .lco-header-control{
  background:#ece4d9!important;
  color:#211d18!important;
  border-color:#8b8070!important;
}
body #lco-brandbar .lco-header-control:focus-visible{
  outline:3px solid var(--lco-gold-bright,#e1b969)!important;
  outline-offset:3px;
}
.lco-screen-reader-only{
  position:absolute!important;
  width:1px;height:1px;
  padding:0;margin:-1px;
  overflow:hidden;
  clip:rect(0,0,0,0);
  white-space:nowrap;
  border:0;
}
/* No card effect on the introduction: the page background shines through. */
body .wrap .hero,
body.lco-light .wrap .hero{
  background:transparent!important;
  background-image:none!important;
  box-shadow:none!important;
  border:0!important;
  border-bottom:1px solid var(--lco-border,rgba(244,240,232,.10))!important;
  padding:18px 0 24px!important;
  border-radius:0!important;
}
body .wrap .hero .hero-top,
body .wrap .hero .hero-copy{background:transparent!important;box-shadow:none!important}
@media(max-width:640px){
  body .wrap #lco-brandbar{min-height:0;}
  body .wrap #lco-brandbar .lco-top-toggles{width:100%;justify-content:flex-end;margin-right:0}
  body #lco-brandbar #lang-toggle,body #lco-brandbar #theme-toggle{min-width:0}
}

/* Compact, single-line desktop navigation; smaller type only in the tabs. */
body .wrap #lco-workspace-nav{
 gap:4px!important;
 padding:8px!important;
 flex-wrap:nowrap!important;
 overflow-x:auto;
}
body .wrap #lco-workspace-nav button{
 font-size:.84rem!important;
 font-weight:680!important;
 letter-spacing:0!important;
 min-height:39px!important;
 padding:8px 10px!important;
 line-height:1.15!important;
 white-space:nowrap;
 flex:0 0 auto;
}
@media (min-width:1080px){
 body .wrap #lco-workspace-nav{justify-content:space-between}
}
</style>'''
EXPERIENCE_SCRIPT = r'''<script>
(() => {
'use strict';
// Progressive enhancement of existing elements: no additional runtime.
const VIEWS=[
{id:'overview',de:'Überblick',en:'Overview',refs:['case-selector','cards']},
{id:'documents',de:'Dokumente',en:'Documents',refs:['fileInput','_main','register-editor','recent-files','integrity-history','text-index-status']},
{id:'timeline',de:'Zeitlinie',en:'Timeline',refs:['timeline-editor','timeline-candidates']},
{id:'relations',de:'Beziehungen',en:'Relationships',refs:['entity-editor','evidence-graph','claim-results','claim-comparisons']},
{id:'tasks',de:'Aufgaben',en:'Tasks',refs:['task-board']},
{id:'ai',de:'KI-Austausch',en:'AI exchange',refs:['ai-review-result']},
{id:'export',de:'Übergabe',en:'Export',refs:['dossier-preview','export-history']},
{id:'system',de:'System',en:'System',refs:['case-audit','lco-tech-details']}
];
const TRANSLATIONS={
'case-selector':['Fall auswählen','Choose your case'],
'cards':['Aktueller Status','Current status'],
'fileInput':['Dateien hinzufügen','Add files'],
'_main':['Hauptaktionen','Main actions'],
'register-editor':['Dokumente prüfen','Document register'],
'recent-files':['Neue Dateien im Eingangsordner','Recent inbox files'],
'integrity-history':['Originale überprüfen','Integrity checks'],
'text-index-status':['Lokale Textsuche und OCR','Private PDF / OCR text index'],
'timeline-editor':['Zeitlinie bearbeiten','Timeline'],
'timeline-candidates':['Datumsangaben vorschlagen','Suggested timeline dates (manual review)'],
'entity-editor':['Personen und Organisationen','Entities / people / institutions'],
'evidence-graph':['Quellenverknüpfungen','Verified links / Evidence map'],
'claim-results':['Quellengebundene Aussagen','Source-linked claims'],
'claim-comparisons':['Angaben vergleichen','Claim comparisons – possible discrepancies'],
'task-board':['Aufgaben und Wiedervorlagen','Tasks and operator-entered reminders'],
'ai-review-result':['Optionaler Offline-KI-Austausch','Optional offline AI review exchange'],
'export-history':['Übergabehistorie','Export history'],
'case-audit':['Änderungsjournal','Metadata change history']
};
const ACTIONS={
'openSelectedCase()':['Fall öffnen','Open selected case'],
'loadCaseHub()':['Fallliste aktualisieren','Refresh case list'],
'createCaseFromUI()':['Neuen Fall anlegen','Create a separate case'],
'loadTimelineCandidates()':['Datumsangaben suchen','Find date mentions in imported text'],
'loadEvidenceGraph()':['Quellenverknüpfungen anzeigen','Refresh evidence map'],
"runAction('verify-integrity')":['Originaldateien prüfen','Verify original files now'],
'loadIntegrityHistory()':['Prüfhistorie anzeigen','Show verification history'],
'indexSelectedDocument()':['Dokument indizieren','Index selected document'],
'searchIndexedDocuments()':['Text durchsuchen','Search local text'],
'saveSourcedClaim()':['Aussage als Entwurf erfassen','Add draft claim'],
'loadSourcedClaims()':['Aussagen aktualisieren','Refresh claims'],
'addClaimComparison()':['Wert zuordnen','Link claim value'],
'loadClaimComparisons()':['Unterschiede anzeigen','Find differences'],
'loadCaseAudit()':['Änderungen anzeigen','Refresh change history'],
'createCaseTask()':['Aufgabe hinzufügen','Add reminder'],
'loadCaseTasks()':['Aufgaben anzeigen','Refresh task list'],
'prepareAiHandoff()':['Privates Kontextpaket erstellen','Prepare private handoff'],
'loadAiSuggestions()':['Vorschläge prüfen','Review suggestions'],
'importAiResponse()':['Vorschläge ungeprüft importieren','Import as untrusted suggestions'],
'showDossierPreview()':['Dossier-Vorschau anzeigen','Preview dossier contents']
};
const LABELS={
'case-selector':['Fall','Case'],'new-case-id':['Neue Fallkennung','New case ID'],
'new-case-title':['Anzeigename','Display title'],'text-file-id':['Dokumentkennung','Document ID'],
'text-use-ocr':['Lokale OCR aktivieren','Enable offline OCR'],'text-query':['Dokumente durchsuchen','Search indexed documents'],
'claim-file-id':['Dokumentkennung','Document ID'],'claim-page':['Seite','Page'],
'claim-quote':['Wörtliches Quellenzitat','Verbatim source passage'],
'claim-statement':['Aussage / Interpretation (ungeprüft)','Claim / interpretation (not a verified fact)'],
'compare-claim-id':['Aussagekennung','Claim ID'],'compare-topic':['Vergleichsthema','Topic'],
'compare-kind':['Art','Kind'],'compare-value':['Wert','Value'],
'task-title':['Aufgabe','Task'],'task-date':['Fällig am','Due date'],
'task-priority':['Priorität','Priority'],'task-files':['Verknüpfte Dokumente','Linked documents'],
'ai-source-ids':['Indizierte Dokumentkennungen','Indexed document IDs'],
'ai-response-json':['JSON-Vorschläge manuell einfügen (keine Übertragung)','Paste JSON suggestions (no automatic transmission)']
};
const HINTS={
'case-selector':['Jeder Fall besitzt einen getrennten lokalen Arbeitsbereich. Änderungen vor dem Wechsel speichern.','Each case has its own workspace. Save before switching.'],
'timeline-candidates':['Nur überprüfte lokale Textquellen. Datumsangaben sind Vorschläge, keine bestätigten Ereignisse.','Dates from verified text are suggestions, not confirmed events.'],
'evidence-graph':['Nur explizit verknüpfte Quellen; keine automatische Wahrheitsprüfung.','Only entered links are shown, no automated truth judgment.'],
'integrity-history':['Manuelle SHA-256-Prüfung mit lokalem Prüfjournal.','Manual SHA-256 verification with local journal.'],
'text-index-status':['Lokale Textextraktion. OCR nur nach ausdrücklicher Auswahl mit installierten Offline-Werkzeugen. Originale bleiben unverändert.','Manual local text extraction; OCR opt-in; originals unchanged.'],
'claim-results':['Aussagen bleiben auch nach einer Prüfung menschliche Bewertungen. Ein exaktes Quellenzitat ist erforderlich.','Claims are human assertions even after review. An exact quote is required.'],
'claim-comparisons':['Abweichende Angaben sind Prüfhinweise, keine bestätigten Widersprüche.','Different values need review, not proven contradictions.'],
'case-audit':['Änderungsjournal ohne Dokumentinhalte oder bestätigte Benutzeridentität.','Metadata-only change journal, no authenticated users.'],
'task-board':['Manuelle Termine; keine automatische Fristberechnung oder Benachrichtigung.','Manual dates; no automatic deadlines or notifications.'],
'ai-review-result':['Keine KI-Modellverbindung. Private Auszüge werden nur manuell weitergegeben; Vorschläge sind ungeprüft.','No model connection; handoff is manual and suggestions untrusted.'],
'export-history':['Erstellte Pakete, ZIP-Dateien und Manifeste.','Created packages, ZIP archives and manifests.']
};
let selected='overview';
const isDe=()=>String(localStorage.getItem('local_case_organizer_ui_lang')||'de').toLowerCase().startsWith('de');
function source(ref){
 if(ref==='_main')return [...document.querySelectorAll('button[onclick]')].find(x=>x.getAttribute('onclick')==="runAction('setup')")?.closest('.actions')||null;
 const el=document.getElementById(ref);if(!el)return null;
 if(['cards','dossier-preview','lco-tech-details'].includes(ref))return el;
 let node=el.closest('.editor,.upload-box,.file-list,.paths,.log')||el;
 if(node.parentElement?.parentElement?.classList.contains('two-col'))node=node.parentElement;
 return node;
}
const grouped = new Map();
function groupNode(node,view){
 if(!node || !node.parentNode) return;
 const old = grouped.get(node);
 if(old && old !== view) return; // Preserve one predictable section assignment.
 grouped.set(node,view);
 const heading = node.previousElementSibling;
 if(heading?.matches('h2.section-title') && !heading.classList.contains('lco-hidden-heading')) {
  grouped.set(heading,view);
 }
}
function groupView(ref,view) {
 groupNode(source(ref),view);
}
function activate(id,focus=false){
 selected=VIEWS.some(v=>v.id===id)?id:'overview';
 try{sessionStorage.setItem('lco_view_v3',selected)}catch{}
 for(const [node,view] of grouped) {
  node.hidden=(selected!==view);
 }
 // Preserve the original two-column wrappers; do not move register/timeline
 // elements because the upstream translation layer uses sibling positions.
 for(const wrapper of document.querySelectorAll('.two-col')) {
  const children=[...wrapper.children];
  if(children.some(child=>grouped.has(child))) {
   wrapper.hidden=!children.some(child=>!child.hidden);
   wrapper.style.gridTemplateColumns='minmax(0,1fr)';
  }
 }
 const nav=document.getElementById('lco-workspace-nav');
 for(const view of VIEWS){
  const tab=document.getElementById('lco-tab-'+view.id);
  if(!tab)continue;
  if(view.id===selected)tab.setAttribute('aria-current','page');
  else tab.removeAttribute('aria-current');
 }
 if(focus)document.getElementById('lco-tab-'+selected)?.focus();
}
function build(){
 if(document.getElementById('lco-workspace-nav'))return;
 const wrap=document.querySelector('.wrap');
 if(!wrap)return;
 const nav=document.createElement('nav');nav.id='lco-workspace-nav';
 nav.className='lco-workspace-nav';nav.setAttribute('aria-label','Arbeitsbereiche');
 const brand=document.getElementById('lco-brandbar');
 if(brand?.parentElement===wrap)brand.insertAdjacentElement('afterend',nav);
 else wrap.insertBefore(nav,wrap.firstChild);

 for(const view of VIEWS){
  const button=document.createElement('button');
  button.type='button';button.id='lco-tab-'+view.id;
  button.addEventListener('click',()=>activate(view.id));
  nav.appendChild(button);
  for(const ref of view.refs)groupView(ref,view.id);
 }
 // Hero, next-step and progress belong to overview; the live feedback box
 // stays visible so users can see errors even after switching areas.
 for(const id of ['next-step','lco-process']){
  const node=document.getElementById(id);if(node)groupNode(node,'overview');
 }
 const hero=wrap.querySelector('.hero');if(hero)groupNode(hero,'overview');

 nav.addEventListener('keydown',e=>{
  if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;
  e.preventDefault();const i=VIEWS.findIndex(v=>v.id===selected);
  const next=e.key==='Home'?0:e.key==='End'?VIEWS.length-1:(i+(e.key==='ArrowRight'?1:-1)+VIEWS.length)%VIEWS.length;
  activate(VIEWS[next].id,true);
 });
 let remembered='overview';try{remembered=sessionStorage.getItem('lco_view_v3')||remembered}catch{}
 activate(remembered);
}
function copy(){
 const i=isDe()?0:1;
 const nav=document.getElementById('lco-workspace-nav');if(nav)nav.setAttribute('aria-label',isDe()?'Arbeitsbereiche':'Work areas');
 for(const view of VIEWS){const button=document.getElementById('lco-tab-'+view.id);if(button)button.textContent=isDe()?view.de:view.en;}
 for(const [ref,words]of Object.entries(TRANSLATIONS)){
  const node=source(ref);if(!node)continue;
  const h=node.querySelector(':scope > h2.section-title')||(node.previousElementSibling?.matches('h2.section-title')?node.previousElementSibling:null);
  if(h)h.textContent=words[i];
 }
 for(const button of document.querySelectorAll('button[onclick]')){const t=ACTIONS[button.getAttribute('onclick')];if(t)button.textContent=t[i];}
 for(const [id,words]of Object.entries(LABELS)){
  const label=document.getElementById(id)?.closest('label');if(!label)continue;
  const nodes=[...label.childNodes].filter(n=>n.nodeType===Node.TEXT_NODE);
  if(nodes.length){nodes[0].nodeValue=words[i]+' ';nodes.slice(1).forEach(n=>n.nodeValue='');}
 }
 for(const [ref,words]of Object.entries(HINTS)){
  const node=source(ref);const hint=node?.querySelector(':scope > p.hint,:scope > .hint');
  if(hint&&!hint.querySelector('table'))hint.textContent=words[i];
 }
 const opts={date:['Datum','Date'],amount:['Betrag','Amount'],text:['Text','Text'],high:['Hoch','High'],low:['Niedrig','Low']};
 for(const option of document.querySelectorAll('#compare-kind option,#task-priority option')){if(opts[option.value])option.textContent=opts[option.value][i];}
 const legacy=document.querySelector('#case-selector option[value=legacy-default]');if(legacy)legacy.textContent=(isDe()?'Standard-Arbeitsbereich':'Legacy workspace')+' (legacy-default)';
}
// The human-copy layer owns the single post-render translation pass.
window.LCOApplyExtraCopy=copy;
document.addEventListener('DOMContentLoaded',()=>{
 build();
 copy();
});
window.addEventListener('load',copy);
})();
</script>'''
