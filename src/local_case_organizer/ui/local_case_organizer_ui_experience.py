"""Focused UI experience layer for the established local browser interface.

B02: keep all original nodes, callbacks and local-only data paths intact.
No second UI or external dependency.
"""
EXPERIENCE_CSS = r'''<style>
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
.lco-workspace-nav button[aria-selected=true]{background:var(--lco-gold,#c69a52)!important;color:#1b160e!important}
.lco-workspace-nav button:hover:not([aria-selected=true]){color:var(--lco-text,#f4f0e8)!important;background:var(--lco-surface,#181612)!important}
.lco-workspace-view[hidden]{display:none!important}
.lco-workspace-view{min-height:250px}
.lco-workspace-view .section-title{font-size:clamp(1.4rem,2.2vw,1.85rem)!important;margin-top:28px!important;margin-bottom:12px!important}
.lco-workspace-view>.editor,.lco-workspace-view>.file-list,.lco-workspace-view>.upload-box,.lco-workspace-view>.actions,.lco-workspace-view>.grid,.lco-workspace-view>.lco-tech-details{margin-bottom:24px!important}
.lco-workspace-view .editor,.lco-workspace-view .upload-box{padding:clamp(17px,2vw,28px)!important}
.lco-workspace-view .hint,.lco-workspace-view .note{font-size:.96rem!important;line-height:1.65!important;color:#c5beb3!important}
.lco-workspace-view p{line-height:1.65}
.lco-workspace-view .editor-actions,.lco-workspace-view .upload-row{gap:12px!important;align-items:flex-end;margin-bottom:15px}
.lco-workspace-view .editor-actions>label{display:flex;flex:1 1 205px;min-width:180px;flex-direction:column;gap:8px;font-size:.98rem}
.lco-workspace-view .editor-actions>label:has(input[type=checkbox]){flex:0 0 auto;min-width:unset;flex-direction:row;align-items:center}
.lco-workspace-view input[type=text],.lco-workspace-view input[type=date],.lco-workspace-view input[type=number],.lco-workspace-view textarea,.lco-workspace-view select{box-sizing:border-box;min-height:44px;max-width:100%;padding:10px 12px;font-size:1rem!important}
.lco-workspace-view input[type=checkbox]{width:18px;height:18px;accent-color:var(--lco-gold,#c69a52)}
.lco-workspace-view textarea{min-height:100px;margin:9px 0 15px}
.lco-workspace-view button{font-size:.96rem!important;padding:12px 16px!important}
.lco-workspace-view .actions{grid-template-columns:repeat(auto-fit,minmax(215px,1fr))!important}
.lco-workspace-view .grid{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))!important}
.lco-workspace-view table{font-size:.93rem}
.lco-workspace-view table th{font-size:.88rem!important}
.lco-workspace-view td.readonly{font-size:.87rem!important}
.lco-workspace-view [aria-live=polite]{overflow-wrap:anywhere}
body.lco-light .lco-workspace-nav{background:#f6f1e8}
body.lco-light .lco-workspace-nav button{color:#645746!important}
body.lco-light .lco-workspace-nav button[aria-selected=true]{background:#9b7135!important;color:white!important}
body.lco-light .lco-workspace-view .hint,body.lco-light .lco-workspace-view .note{color:#544d44!important}
@media(max-width:680px){.lco-workspace-nav{margin:12px -4px 18px;padding:7px}.lco-workspace-view .editor-actions>label{min-width:100%}.lco-workspace-view .actions{grid-template-columns:1fr!important}body .lco-process{display:none}}
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
body .lco-workspace-nav button:hover:not([aria-selected=true]):not(.ghost):not(.light):not(.secondary):not(.lco-theme-toggle){
  background:var(--lco-surface)!important;
  color:var(--lco-text)!important;
}
body .lco-workspace-nav button[aria-selected=true]:not(.ghost):not(.light):not(.secondary):not(.lco-theme-toggle){
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
body.lco-light .lco-workspace-view .hint,
body.lco-light .lco-workspace-view .note{
  color:#544d44!important;
}
body .lco-workspace-nav button:focus-visible,
body .lco-workspace-view button:focus-visible,
body .lco-workspace-view input:focus-visible,
body .lco-workspace-view select:focus-visible,
body .lco-workspace-view textarea:focus-visible{
  outline:3px solid var(--lco-gold-bright)!important;
  outline-offset:3px;
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
const isDe=()=>String(localStorage.getItem('local_case_organizer_ui_lang')||document.documentElement.lang||'en').toLowerCase().startsWith('de');
function source(ref){
 if(ref==='_main')return [...document.querySelectorAll('button[onclick]')].find(x=>x.getAttribute('onclick')==="runAction('setup')")?.closest('.actions')||null;
 const el=document.getElementById(ref);if(!el)return null;
 if(['cards','dossier-preview','lco-tech-details'].includes(ref))return el;
 let node=el.closest('.editor,.upload-box,.file-list,.paths,.log')||el;
 if(node.parentElement?.parentElement?.classList.contains('two-col'))node=node.parentElement;
 return node;
}
function move(ref,target){
 const node=source(ref);if(!node||!node.parentNode||node.parentElement===target)return;
 const prev=node.previousElementSibling;
 if(prev?.matches('h2.section-title')&&!prev.classList.contains('lco-hidden-heading'))target.appendChild(prev);
 target.appendChild(node);
}
function activate(id,focus=false){
 selected=VIEWS.some(v=>v.id===id)?id:'overview';
 try{sessionStorage.setItem('lco_view_v2',selected)}catch{}
 for(const view of VIEWS){
  const panel=document.getElementById('lco-panel-'+view.id),tab=document.getElementById('lco-tab-'+view.id);
  if(panel)panel.hidden=view.id!==selected;
  if(tab){tab.setAttribute('aria-selected',String(view.id===selected));tab.tabIndex=view.id===selected?0:-1}
 }
 if(focus)document.getElementById('lco-tab-'+selected)?.focus();
}
function build(){
 if(document.getElementById('lco-workspace-nav'))return;
 const wrap=document.querySelector('.wrap');
 const anchor=document.getElementById('lco-process')||document.getElementById('next-step');
 if(!wrap||!anchor||anchor.parentElement!==wrap)return;
 const nav=document.createElement('nav');nav.id='lco-workspace-nav';nav.className='lco-workspace-nav';nav.setAttribute('role','tablist');
 const container=document.createElement('div');container.id='lco-workspace-views';
 anchor.insertAdjacentElement('afterend',nav);nav.insertAdjacentElement('afterend',container);
 for(const view of VIEWS){
  const button=document.createElement('button');button.type='button';button.id='lco-tab-'+view.id;button.setAttribute('role','tab');button.setAttribute('aria-controls','lco-panel-'+view.id);
  button.addEventListener('click',()=>activate(view.id));nav.appendChild(button);
  const panel=document.createElement('section');panel.id='lco-panel-'+view.id;panel.className='lco-workspace-view';panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby',button.id);panel.tabIndex=-1;container.appendChild(panel);
  view.refs.forEach(ref=>move(ref,panel));
 }
 for(const columns of wrap.querySelectorAll('.two-col'))if(!columns.children.length)columns.remove();
 nav.addEventListener('keydown',e=>{
  if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;
  e.preventDefault();const i=VIEWS.findIndex(v=>v.id===selected);
  const next=e.key==='Home'?0:e.key==='End'?VIEWS.length-1:(i+(e.key==='ArrowRight'?1:-1)+VIEWS.length)%VIEWS.length;
  activate(VIEWS[next].id,true);
 });
 let remembered='overview';try{remembered=sessionStorage.getItem('lco_view_v2')||remembered}catch{}
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
document.addEventListener('DOMContentLoaded',()=>{
 build();copy();
 document.getElementById('lang-toggle')?.addEventListener('click',()=>{setTimeout(copy,120);setTimeout(copy,500)});
 document.addEventListener('click',()=>setTimeout(copy,250),true);
});
})();
</script>'''
