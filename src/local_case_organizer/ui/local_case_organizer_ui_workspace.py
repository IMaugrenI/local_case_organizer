"""One-page progressive workspace; composes existing API actions without a new runtime.

All user text is rendered with textContent. Technical/irreversible decisions
remain explicit. The historical advanced view stays available.
"""

WORKSPACE_CSS = r'''<style>
#lco-easy-home #lco-simple-list{display:none}
#lco-easy-home .lco-ws-panel{border:1px solid var(--lco-border,#857a70);border-radius:14px;margin:14px 0;background:var(--lco-panel,#171615);overflow:hidden}
#lco-easy-home .lco-ws-panel>summary{padding:19px 21px;font-size:1.08rem;font-weight:750;cursor:pointer;list-style-position:inside}
#lco-easy-home .lco-ws-panel[open]>summary{border-bottom:1px solid var(--lco-border,#857a70)}
#lco-easy-home .lco-ws-body{padding:18px 21px}
#lco-easy-home .lco-ws-body>p:first-child{margin-top:0;line-height:1.6;opacity:.85}
#lco-easy-home .lco-ws-grid{display:flex;gap:12px;flex-wrap:wrap;align-items:end;margin:12px 0}
#lco-easy-home .lco-ws-grid>label{display:flex;flex:1 1 170px;gap:7px;flex-direction:column}
#lco-easy-home .lco-ws-grid>label>input,#lco-easy-home .lco-ws-grid>label>select{width:100%;min-height:43px;max-width:100%;box-sizing:border-box}
#lco-easy-home input:not([type=checkbox]):not([type=file]),#lco-easy-home textarea,#lco-easy-home select{background:var(--lco-control-bg,#292622);color:var(--lco-control-fg,#f4f0e8);border:1px solid var(--lco-control-border,#837565);border-radius:8px;padding:9px}
#lco-easy-home textarea{width:100%;min-height:65px;box-sizing:border-box}
#lco-easy-home input[type=checkbox]{width:18px;height:18px;accent-color:#b99454}
#lco-easy-home .lco-ws-check{display:flex;gap:9px;align-items:center;font-size:.95rem}
#lco-easy-home .lco-ws-btns{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:12px 0}
#lco-easy-home .lco-ws-btns>button{padding:10px 14px}
#lco-easy-home button:disabled{opacity:.55;cursor:progress}
#lco-easy-home .lco-ws-list{list-style:none;margin:8px 0 4px;padding:0}
#lco-easy-home .lco-ws-list>li{padding:16px 0;border-bottom:1px solid var(--lco-border,#857a70);overflow-wrap:anywhere}
#lco-easy-home .lco-ws-list>li:last-child{border:0}
#lco-easy-home .lco-ws-list small{opacity:.76;display:block;margin:6px 0}
#lco-easy-home .lco-ws-note{width:100%;display:block}
#lco-easy-home .lco-ws-feedback{min-height:22px;line-height:1.5;margin:9px 0;font-size:.95rem}
#lco-easy-home .lco-ws-feedback[data-kind=error]{color:#e6a692}
#lco-easy-home .lco-ws-feedback[data-kind=ok]{color:#e1b969}
#lco-easy-home .lco-ws-inline{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
#lco-easy-home .lco-ws-inline>label{display:flex;align-items:center;gap:7px}
#lco-easy-home .lco-ws-document-title{font-weight:750;font-size:1.04rem}
#lco-easy-home .lco-ws-doc-controls{display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin:10px 0}
#lco-easy-home .lco-ws-doc-controls select{max-width:210px}
#lco-easy-home .lco-ws-doc-fields{display:grid;grid-template-columns:minmax(120px,1fr) minmax(210px,2fr);gap:10px;align-items:end}
#lco-easy-home .lco-ws-doc-fields>label{display:block}
#lco-easy-home .lco-ws-doc-fields input,#lco-easy-home .lco-ws-doc-fields textarea{display:block;width:100%;margin-top:6px;box-sizing:border-box}
#lco-easy-home .lco-ws-doc-fields textarea{min-height:46px}
#lco-easy-home .lco-ws-subtle{font-size:.88rem;opacity:.73}
body.lco-light #lco-easy-home .lco-ws-panel{background:#fbf8f2}
body.lco-light #lco-easy-home .lco-ws-feedback[data-kind=error]{color:#8c3223}
body.lco-light #lco-easy-home .lco-ws-feedback[data-kind=ok]{color:#80571b}
@media(max-width:650px){#lco-easy-home .lco-ws-body{padding:14px}#lco-easy-home .lco-ws-panel>summary{padding:15px}#lco-easy-home .lco-ws-doc-fields{grid-template-columns:1fr}}
</style>'''

WORKSPACE_SCRIPT = r'''<script>
(function(){
"use strict";
const de={
 documents:"Dokumente bearbeiten",docHelp:"Ordne Dokumente ein, ergänze Notizen und wähle bewusst aus, was später in eine Übergabe darf.",
 documentEmpty:"Noch keine Dokumente im Register.",
 docFilter:"Dokumentname, ID, Gruppe oder Notiz filtern",docPaging:"{shown} von {matched} Treffern auf Seite {page}/{pages} · {total} Dokumente insgesamt",docPrevious:"Zurück",docNext:"Weiter",docNoMatch:"Keine passenden Dokumente im Register. Filter ändern oder löschen.",
 selectAll:"Alle Dokumente markieren",selectNone:"Auswahl aufheben",
 confirmAll:"Alle {n} Dokumente für eine mögliche Übergabe markieren? Enthaltene sensible Daten vor dem Export einzeln prüfen. Es wird noch nichts versendet.",
 confirmNone:"Alle ausgewählten Dokumente für die Übergabe abwählen?",
 selectionDone:"Auswahl aktualisiert. Die Übergabe muss weiterhin ausdrücklich bestätigt werden.",
 review:"Prüfstatus",group:"Kategorie",note:"Notiz",save:"Notiz und Kategorie speichern",include:"Für Übergabe auswählen",
 unreviewed:"Ungeprüft",reviewed:"Geprüft",flagged:"Markiert",selected_for_export:"Für Übergabe markiert",
 yes:"Ja",no:"Nein",updated:"Änderung gespeichert.",failed:"Aktion fehlgeschlagen. Vorhandene Daten bleiben bestehen.",
 search:"Dokumente durchsuchen",searchHelp:"Die Suche läuft lokal. PDF-Text benötigt gegebenenfalls ein installiertes Offline-Werkzeug; Bilder werden nicht automatisch per OCR gelesen.",
 query:"Suchbegriff",prepare:"Suche vorbereiten",includePdf:"PDF-Texte ebenfalls vorbereiten (ohne OCR)",
 searchNow:"Suchen",searchEmpty:"Keine passenden Fundstellen. Gegebenenfalls zuerst die Suche vorbereiten.",
 searching:"Suche wird vorbereitet …",prepared:"{n} Dokument(e) neu für die lokale Suche vorbereitet. {left} weitere warten auf einen erneuten Durchlauf.",
 page:"Seite",timeline:"Zeitlinie",timelineHelp:"Datumsangaben sind Hinweise, keine bestätigten Tatsachen. Neue Einträge bleiben zunächst Entwürfe.",
 eventTitle:"Ereignis / Kurzbeschreibung",eventDate:"Datum",eventSummary:"Erläuterung (optional)",source:"Quelldokument (optional)",
 addEvent:"Entwurf hinzufügen",showDates:"Datumsangaben vorschlagen",addedEvent:"Zeitlinieneintrag als Entwurf gespeichert.",
 noTimeline:"Noch keine selbst erfassten Ereignisse.",suggested:"Vorschlag – erst prüfen",accept:"Als Entwurf übernehmen",
 tasks:"Aufgaben und Termine",tasksHelp:"Nur selbst eingegebene Termine. Keine automatische rechtliche Fristberechnung oder Benachrichtigung.",
 taskTitle:"Aufgabe",due:"Datum (optional)",priority:"Priorität",normal:"Normal",low:"Niedrig",high:"Hoch",createTask:"Aufgabe hinzufügen",
 taskAdded:"Aufgabe eingetragen.",noTasks:"Noch keine Aufgaben.",state:"Status",open:"Offen",in_progress:"In Arbeit",done:"Erledigt",cancelled:"Abgebrochen",apply:"Aktualisieren",
 entities:"Personen und Beziehungen",entityHelp:"Nur selbst eingetragene Angaben und Quellenverknüpfungen; keine automatische Schlussfolgerung.",
 entityName:"Name",entityType:"Art / Rolle (optional)",entityNotes:"Notizen",addEntity:"Eintrag hinzufügen",entityAdded:"Eintrag gespeichert.",noEntities:"Noch keine Personen oder Organisationen.",
 handoff:"Übergabe erstellen",handoffHelp:"Nur bewusst ausgewählte Unterlagen kommen in das Übergabepaket. Die Erstellung und jede spätere Weitergabe bleiben deine Entscheidung.",
 exportPreview:"Ausgewählte Dokumente: {n}",buildExport:"Übergabepaket lokal erstellen",openExports:"Exportordner öffnen",
 qualityCheck:"Übergabe vorab prüfen",qualityIntro:"Lokale Vorschau: nur ausgewählte Originale und deren Arbeitsdaten. Keine Aussage zur vollständigen Akte oder rechtlichen Beweiskraft.",
 qualityStats:"{verified} von {inspected} Originalen hashgeprüft · {unscanned} nicht gescannt · {pending} offene Dokumentprüfungen · {claims} nicht quellengeprüfte Aussagen ausgeschlossen",
 qualityWarning:"Prüfhinweise ({n}):",qualityNone:"Keine Warnhinweise im geprüften Ausschnitt. Das beweist keine Vollständigkeit.",
 qualityBlocked:"Ein ausgewähltes Original ist nicht sicher lesbar oder verändert. Export nicht starten.",
 qualityApprove:"Es gibt {n} organisatorische Prüfhinsweise. Trotzdem ein Paket mit den geprüften Auswahlgrenzen erstellen? Es wird nichts versendet.",
 qualityLoadError:"Übergabeprüfung konnte nicht geladen werden.",
 qualityCode_verified:"Original unverändert",qualityCode_missing_original:"Ausgewähltes Original fehlt",
 qualityCode_missing_provenance:"Quellennachweis fehlt",qualityCode_hash_mismatch:"Ausgewähltes Original verändert",
 qualityCode_unsafe_original:"Originalpfad nicht sicher prüfbar",
 qualityCode_unsupported_selected_claims:"Aussagen ohne aktuellen Quellenbeleg werden ausgeschlossen",
 qualityCode_selected_document_reviews_pending:"Ausgewählte Dokumente noch nicht manuell geprüft",
 qualityCode_preview_not_all_sources_scanned:"Vorschau hat nicht alle ausgewählten Quellen geprüft",
 exportConfirm:"Lokales Übergabepaket aus {n} ausgewählten Dokumenten erstellen? Es wird nichts versendet.",
 exportNone:"Bitte zuerst im Abschnitt „Dokumente bearbeiten“ mindestens ein Dokument markieren.",
 exportDone:"Übergabepaket erstellt. Keine externe Übertragung.",
 integrity:"Sicherheit und Kontrolle",integrityHelp:"Prüfe Originale auf unveränderte Inhalte. Keine Änderungen an den Originaldateien.",
 verify:"Originale überprüfen",verified:"Integritätsprüfung durchgeführt. Ergebnisse stehen im Prüfprotokoll.",
 technical:"Weitere Spezialfunktionen",technicalHelp:"Quellengebundene Aussagen, Vergleichshinweise und der optionale manuelle KI-Austausch bleiben über die Expertenansicht erreichbar.",
 advanced:"Expertenansicht öffnen",
 choose:"Kein Quelldokument",load:"Aktualisieren",loading:"Lade Daten …",
 error:"Vorgang fehlgeschlagen. Bitte Details prüfen.",none:"Keine Einträge."
};
const en={
 documents:"Manage documents",docHelp:"Organize documents, add notes and explicitly select files for a handoff.",
 documentEmpty:"No registered documents yet.",
 docFilter:"Filter filename, ID, group or note",docPaging:"{shown} of {matched} matches on page {page}/{pages} · {total} documents total",docPrevious:"Previous",docNext:"Next",docNoMatch:"No matching registered documents. Change or clear the filter.",
 selectAll:"Select all documents",selectNone:"Clear selection",
 confirmAll:"Mark all {n} documents for possible handoff? Review sensitive material individually before export. Nothing is transmitted now.",
 confirmNone:"Clear all selected handoff documents?",
 selectionDone:"Selection updated. Handoff still requires explicit confirmation.",
 review:"Review status",group:"Category",note:"Note",save:"Save category and note",include:"Include in handoff",
 unreviewed:"Unreviewed",reviewed:"Reviewed",flagged:"Flagged",selected_for_export:"Marked for export",
 yes:"Yes",no:"No",updated:"Change saved.",failed:"Action failed. Existing files were not changed.",
 search:"Search documents",searchHelp:"Search runs locally. PDF extraction may require an installed offline tool; image OCR never runs automatically.",
 query:"Search term",prepare:"Prepare search",includePdf:"Also prepare PDF text (no OCR)",
 searchNow:"Search",searchEmpty:"No matching passages. You may need to prepare the search first.",
 searching:"Preparing local search …",prepared:"{n} document(s) indexed locally. {left} more await another batch.",
 page:"Page",timeline:"Timeline",timelineHelp:"Date mentions are suggestions, not proven events. New entries start as drafts.",
 eventTitle:"Event / short title",eventDate:"Date",eventSummary:"Notes (optional)",source:"Source document (optional)",
 addEvent:"Add draft",showDates:"Suggest date mentions",addedEvent:"Timeline event saved as draft.",
 noTimeline:"No manually recorded events yet.",suggested:"Suggestion – review first",accept:"Accept as draft",
 tasks:"Tasks and dates",tasksHelp:"Operator-entered dates only. No calculated legal deadlines or background notifications.",
 taskTitle:"Task",due:"Date (optional)",priority:"Priority",normal:"Normal",low:"Low",high:"High",createTask:"Add task",
 taskAdded:"Task recorded.",noTasks:"No tasks yet.",state:"Status",open:"Open",in_progress:"In progress",done:"Done",cancelled:"Cancelled",apply:"Update",
 entities:"People and relationships",entityHelp:"Only operator-entered information and explicit source links; no inferred facts.",
 entityName:"Name",entityType:"Type / role (optional)",entityNotes:"Notes",addEntity:"Add entry",entityAdded:"Entry saved.",noEntities:"No people or institutions yet.",
 handoff:"Prepare handoff",handoffHelp:"Only manually selected originals are added to a handoff package. Creating or sharing it requires your decision.",
 exportPreview:"Selected documents: {n}",buildExport:"Create local handoff package",openExports:"Open export folder",
 qualityCheck:"Check handoff before creating",qualityIntro:"Local preview: selected originals and related working data only. Not a full-case or legal proof assessment.",
 qualityStats:"{verified} of {inspected} originals hash-checked · {unscanned} not scanned · {pending} documents awaiting review · {claims} unsupported claims excluded",
 qualityWarning:"Review notices ({n}):",qualityNone:"No notices in the checked sample. This does not prove completeness.",
 qualityBlocked:"A selected original is changed or unavailable. Export cannot proceed.",
 qualityApprove:"There are {n} organizational review notices. Still create the locally selected package? Nothing is sent.",
 qualityLoadError:"Unable to read handoff quality preview.",
 qualityCode_verified:"Original unchanged",qualityCode_missing_original:"Selected original is missing",
 qualityCode_missing_provenance:"Source provenance missing",qualityCode_hash_mismatch:"Selected original changed",
 qualityCode_unsafe_original:"Original path cannot be verified safely",
 qualityCode_unsupported_selected_claims:"Unverifiable claims will be excluded",
 qualityCode_selected_document_reviews_pending:"Selected documents still await manual review",
 qualityCode_preview_not_all_sources_scanned:"Not every selected source was checked in the preview",
 exportConfirm:"Create a local handoff package from {n} selected documents? Nothing is transmitted.",
 exportNone:"Please select at least one document in Manage documents first.",
 exportDone:"Handoff package created; nothing transmitted.",
 integrity:"Safety and controls",integrityHelp:"Check original files for modifications without changing them.",
 verify:"Verify originals",verified:"Integrity check completed. Details are in the verification journal.",
 technical:"Other specialized tools",technicalHelp:"Source-linked claims, comparison reviews and optional manual AI exchange remain available in Advanced view.",
 advanced:"Open advanced view",
 choose:"No source document",load:"Refresh",loading:"Loading data …",
 error:"Operation failed. Please check details.",none:"No entries."
};
const el=id=>document.getElementById(id);
const t=key=>(String(localStorage.getItem("local_case_organizer_ui_lang")||"de").startsWith("de")?de:en)[key]||key;
const fmt=(key,vars={})=>Object.entries(vars).reduce((text,[name,value])=>text.replace("{"+name+"}",String(value)),t(key));
let cachedDocs=[],timelineRows=[],taskRows=[],entityRows=[],suggestions=[];
const DOCS_PER_PAGE=40;
let docPage=0,docQuery="";
const docDrafts=new Map();
function newNode(tag,content,cls){
 const item=document.createElement(tag);if(cls)item.className=cls;
 if(content!==undefined&&content!==null)item.textContent=String(content);
 return item;
}
function localize(root=document){
 root.querySelectorAll("[data-ws-copy]").forEach(item=>{item.textContent=t(item.dataset.wsCopy)});
 root.querySelectorAll("[data-ws-placeholder]").forEach(item=>{item.placeholder=t(item.dataset.wsPlaceholder)});
}
function message(id,key,kind="ok",vars){
 const node=el(id);if(!node)return;
 node.dataset.kind=kind;node.dataset.msgKey=key;node.dataset.msgVars=JSON.stringify(vars||{});
 node.textContent=fmt(key,vars);
}
function resetMessageTranslations(){
 document.querySelectorAll("#lco-easy-home .lco-ws-feedback[data-msg-key]").forEach(item=>{
  let vars={};try{vars=JSON.parse(item.dataset.msgVars||"{}")}catch{}
  item.textContent=fmt(item.dataset.msgKey,vars);
 });
}
async function request(url,data){
 const options=data===undefined?{}:{
  method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)
 };
 const response=await fetch(url,options);
 let body={};try{body=await response.json()}catch{}
 if(!response.ok)throw new Error(body.error||("HTTP "+response.status));
 return body;
}
function bindButton(id,handler){
 const btn=el(id);if(!btn)return;
 btn.addEventListener("click",async ()=>{
  if(btn.disabled)return;btn.disabled=true;
  try{await handler()}catch(error){console.warn("One-page action failed",error);message("lco-ws-general","error","error")}
  finally{btn.disabled=false}
 });
}
function populateDocSelect(nodeId,keepValue=""){
 const select=el(nodeId);if(!select)return;
 const old=keepValue||select.value;
 select.replaceChildren();
 const empty=newNode("option",t("choose"));empty.value="";select.append(empty);
 for(const row of cachedDocs){
  const option=newNode("option",row.original_name||row.file_id);option.value=row.file_id;select.append(option);
 }
 select.value=cachedDocs.some(row=>row.file_id===old)?old:"";
}
function renderDocs(){
 const list=el("lco-ws-doc-list");if(!list)return;
 list.replaceChildren();
 const filtered=cachedDocs.filter(row=>[row.original_name,row.file_id,row.document_group,row.note]
   .some(value=>String(value||"").toLocaleLowerCase().includes(docQuery)));
 const pages=Math.max(1,Math.ceil(filtered.length/DOCS_PER_PAGE));
 docPage=Math.min(docPage,pages-1);
 const shown=filtered.slice(docPage*DOCS_PER_PAGE,(docPage+1)*DOCS_PER_PAGE);
 const info=el("lco-ws-doc-page-info");
 if(info)info.textContent=fmt("docPaging",{
  shown:shown.length,matched:filtered.length,page:docPage+1,pages,total:cachedDocs.length
 });
 const prev=el("lco-ws-doc-prev"),next=el("lco-ws-doc-next");
 if(prev)prev.disabled=docPage===0;
 if(next)next.disabled=docPage>=pages-1;
 if(!cachedDocs.length){list.append(newNode("li",t("documentEmpty")));return;}
 if(!filtered.length){list.append(newNode("li",t("docNoMatch")));return;}
 for(const row of shown){
  const li=newNode("li"),name=newNode("strong",row.original_name||row.file_id,"lco-ws-document-title");
  const small=newNode("small",row.file_id+" · "+(row.suffix||""));
  li.append(name,small);
  const controls=newNode("div",null,"lco-ws-doc-controls");
  const cbLabel=newNode("label",null,"lco-ws-check");
  const check=newNode("input");check.type="checkbox";check.checked=row.selected_for_export==="yes";
  const cbText=newNode("span",null);cbText.dataset.wsCopy="include";
  cbLabel.append(check,cbText);
  const reviewLabel=newNode("label",null,"lco-ws-check");
  const reviewText=newNode("span");reviewText.dataset.wsCopy="review";
  const status=newNode("select");
  for(const value of ["unreviewed","reviewed","flagged","selected_for_export"]){
   const option=newNode("option",t(value));option.value=value;option.selected=row.review_status===value;
   option.dataset.wsCopy=value;status.append(option);
  }
  reviewLabel.append(reviewText,status);controls.append(cbLabel,reviewLabel);
  const fields=newNode("div",null,"lco-ws-doc-fields");
  const groupLabel=newNode("label"),groupText=newNode("span");groupText.dataset.wsCopy="group";
  const group=newNode("input");group.type="text";group.maxLength=120;
  const draft=docDrafts.get(row.file_id)||{};
  group.value=draft.group!==undefined?draft.group:row.document_group||"";
  groupLabel.append(groupText,group);
  const noteLabel=newNode("label"),noteText=newNode("span");noteText.dataset.wsCopy="note";
  const note=newNode("textarea");note.maxLength=1200;
  note.value=draft.note!==undefined?draft.note:row.note||"";
  group.addEventListener("input",()=>docDrafts.set(row.file_id,{group:group.value,note:note.value}));
  note.addEventListener("input",()=>docDrafts.set(row.file_id,{group:group.value,note:note.value}));
  noteLabel.append(noteText,note);fields.append(groupLabel,noteLabel);
  const save=newNode("button",t("save"),"secondary");save.type="button";save.dataset.wsCopy="save";
  const feedback=newNode("p",null,"lco-ws-feedback");
  const change=async(field,value,restore)=>{
   check.disabled=true;status.disabled=true;save.disabled=true;
   try{
    await request("/api/quick-update-document",{file_id:row.file_id,field,value});
    row[field]=value;feedback.textContent=t("updated");feedback.dataset.kind="ok";
    refreshExportPreview();
   }catch(error){console.warn("Document update failed",error);feedback.textContent=t("failed")+": "+error.message;feedback.dataset.kind="error";restore?.()}
   finally{check.disabled=false;status.disabled=false;save.disabled=false}
  };
  check.addEventListener("change",()=>change("selected_for_export",check.checked?"yes":"no",()=>{check.checked=row.selected_for_export==="yes"}));
  status.addEventListener("change",()=>change("review_status",status.value,()=>{status.value=row.review_status}));
  save.addEventListener("click",async()=>{
   if(group.value!==row.document_group)await change("document_group",group.value);
   if(note.value!==row.note)await change("note",note.value);
   if(group.value===row.document_group && note.value===row.note)docDrafts.delete(row.file_id);
  });
  li.append(controls,fields,save,feedback);list.append(li);
 }
 localize(list);
 for(const id of ["lco-ws-event-file","lco-ws-task-file","lco-ws-entity-file"])populateDocSelect(id);
}
async function loadDocs(){
 const result=await request("/api/register-data");
 cachedDocs=Array.isArray(result.rows)?result.rows:[];
 renderDocs();refreshExportPreview();
}
function addListItem(root,textValue,subtext){
 const li=newNode("li"),heading=newNode("strong",textValue);li.append(heading);
 if(subtext)li.append(newNode("small",subtext));
 root.append(li);return li;
}
function renderTimeline(){
 const root=el("lco-ws-events");root.replaceChildren();
 const rows=timelineRows.filter(row=>row.event_date||row.event_title);
 if(!rows.length){root.append(newNode("li",t("noTimeline")));return;}
 for(const row of rows.slice(-70).reverse()){
  addListItem(root,(row.event_date||"—")+" · "+(row.event_title||""),
   (row.linked_file_ids||"")+" · "+(row.summary||"")+" · "+(row.status||"draft"));
 }
}
async function loadTimeline(){
 const result=await request("/api/timeline-data");
 timelineRows=Array.isArray(result.rows)?result.rows:[];
 renderTimeline();
}
async function loadTasks(){
 const result=await request("/api/tasks");taskRows=Array.isArray(result.tasks)?result.tasks:[];
 const root=el("lco-ws-task-list");root.replaceChildren();
 if(!taskRows.length){root.append(newNode("li",t("noTasks")));return;}
 for(const item of taskRows.slice(0,90)){
  const li=addListItem(root,item.title,(item.due_date||"—")+" · "+(item.priority||"")+" · "+item.date_indicator);
  const select=newNode("select");
  for(const status of ["open","in_progress","done","cancelled"]){
   const option=newNode("option",t(status));option.dataset.wsCopy=status;
   option.value=status;option.selected=status===item.status;select.append(option);
  }
  const button=newNode("button",t("apply"),"secondary");button.dataset.wsCopy="apply";button.type="button";
  const feedback=newNode("span",null,"lco-ws-feedback");
  button.addEventListener("click",async()=>{
   button.disabled=true;
   try{await request("/api/update-task",{task_id:item.task_id,status:select.value});await loadTasks()}
   catch(error){feedback.textContent=t("failed");console.warn(error);button.disabled=false}
  });
  li.append(select,button,feedback);
 }
 localize(root);
}
async function loadEntities(){
 const result=await request("/api/entity-data");entityRows=Array.isArray(result.rows)?result.rows:[];
 const root=el("lco-ws-entity-list");root.replaceChildren();
 if(!entityRows.length){root.append(newNode("li",t("noEntities")));return;}
 for(const row of entityRows.slice(-70).reverse()){
  addListItem(root,row.entity_name||"—",
   (row.entity_type||"")+" · "+(row.linked_file_ids||"")+" · "+(row.notes||""));
 }
}
function refreshExportPreview(){
 const root=el("lco-ws-export-count");
 if(root)root.textContent=fmt("exportPreview",{n:cachedDocs.filter(row=>row.selected_for_export==="yes").length});
}
async function loadHandoffQuality(){
 const report=await request("/api/dossier-preview");
 const summary=el("lco-ws-quality-summary");
 const list=el("lco-ws-quality-warnings");
 if(!summary||!list)return report;
 summary.textContent=fmt("qualityStats",{
  verified:report.verified_originals||0,inspected:report.inspected_originals||0,
  unscanned:report.not_scanned||0,pending:report.manual_review_pending_in_scan||0,
  claims:report.claims_excluded_unverifiable||0
 });
 list.replaceChildren();
 for(const warning of (report.warnings||[]).slice(0,30)){
  const li=newNode("li",t("qualityCode_"+String(warning.code||""))+(" · "+String(warning.file_id||""))+
   (warning.count?" · "+String(warning.count):""));
  list.append(li);
 }
 if(!list.children.length)list.append(newNode("li",t("qualityNone")));
 return report;
}
function renderSuggestions(){
 const root=el("lco-ws-suggestions");root.replaceChildren();
 if(!suggestions.length){root.append(newNode("li",t("none")));return;}
 for(const item of suggestions.slice(0,30)){
  const li=addListItem(root,item.date+" · "+item.original_name,
    item.file_id+" · "+item.excerpt);
  const warn=newNode("small",t("suggested"));warn.dataset.wsCopy="suggested";
  const btn=newNode("button",t("accept"),"secondary");btn.type="button";btn.dataset.wsCopy="accept";
  btn.addEventListener("click",async()=>{
   btn.disabled=true;
   try{await request("/api/accept-candidate",{candidate_id:item.candidate_id});
    suggestions=suggestions.filter(x=>x.candidate_id!==item.candidate_id);
    renderSuggestions();await loadTimeline();message("lco-ws-timeline-msg","addedEvent","ok");
   }catch(error){console.warn(error);btn.disabled=false;message("lco-ws-timeline-msg","failed","error")}
  });li.append(warn,btn);
 }
}
function resetText(id){const node=el(id);if(node)node.value=""}
function openPanel(id){const node=el(id);if(node){node.open=true;node.scrollIntoView({block:"start",behavior:"smooth"})}}
function bind(){
 el("lco-ws-doc-reload").addEventListener("click",()=>loadDocs().catch(console.warn));
 el("lco-ws-doc-filter").addEventListener("input",event=>{
  docQuery=String(event.target.value||"").trim().toLocaleLowerCase();docPage=0;renderDocs();
 });
 el("lco-ws-doc-prev").addEventListener("click",()=>{if(docPage>0){docPage--;renderDocs()}});
 el("lco-ws-doc-next").addEventListener("click",()=>{docPage++;renderDocs()});
 for(const [buttonId,mode] of [["lco-ws-select-all","all"],["lco-ws-select-none","none"]]){
  bindButton(buttonId,async()=>{
   const count=cachedDocs.length;
   if(!window.confirm(mode==="all"?fmt("confirmAll",{n:count}):t("confirmNone")))return;
   await request("/api/quick-bulk-export",{mode});
   message("lco-ws-selection-msg","selectionDone","ok");
   await loadDocs();
  });
 }
 el("lco-ws-search-form").addEventListener("submit",async event=>{
  event.preventDefault();const root=el("lco-ws-search-results");root.replaceChildren();
  try{
   const result=await request("/api/search-text",{query:el("lco-ws-query").value.trim()});
   if(!result.matches?.length){root.append(newNode("li",t("searchEmpty")));return}
   for(const hit of result.matches.slice(0,35))addListItem(root,hit.original_name+" · "+t("page")+" "+hit.page,hit.excerpt);
  }catch(error){root.append(newNode("li",t("error")+": "+error.message))}
 });
 bindButton("lco-ws-prepare",async()=>{
  message("lco-ws-search-msg","searching","ok");
  try{
   const result=await request("/api/quick-prepare-search",{include_pdf:el("lco-ws-pdf").checked});
   message("lco-ws-search-msg","prepared","ok",{n:result.indexed||0,left:result.remaining||0});
  }catch(error){message("lco-ws-search-msg","error","error");console.warn(error)}
 });
 el("lco-ws-timeline-form").addEventListener("submit",async event=>{
  event.preventDefault();const button=el("lco-ws-event-submit");button.disabled=true;
  try{
   await request("/api/quick-add-event",{
    title:el("lco-ws-event-title").value.trim(),date:el("lco-ws-event-date").value,
    summary:el("lco-ws-event-summary").value,file_id:el("lco-ws-event-file").value,
   });
   message("lco-ws-timeline-msg","addedEvent","ok");
   resetText("lco-ws-event-title");resetText("lco-ws-event-summary");await loadTimeline();
  }catch(error){message("lco-ws-timeline-msg","error","error");console.warn(error)}
  finally{button.disabled=false}
 });
 bindButton("lco-ws-proposals",async()=>{
  const result=await request("/api/propose-events",{});
  suggestions=Array.isArray(result.candidates)?result.candidates:[];
  renderSuggestions();
 });
 el("lco-ws-task-form").addEventListener("submit",async event=>{
  event.preventDefault();const button=el("lco-ws-task-submit");button.disabled=true;
  try{
   await request("/api/add-task",{title:el("lco-ws-task-title").value.trim(),
    due_date:el("lco-ws-task-date").value,
    priority:el("lco-ws-task-priority").value,linked_file_ids:el("lco-ws-task-file").value});
   resetText("lco-ws-task-title");message("lco-ws-task-msg","taskAdded","ok");await loadTasks();
  }catch(error){console.warn(error);message("lco-ws-task-msg","error","error")}
  finally{button.disabled=false}
 });
 el("lco-ws-entity-form").addEventListener("submit",async event=>{
  event.preventDefault();const button=el("lco-ws-entity-submit");button.disabled=true;
  try{
   await request("/api/quick-add-entity",{name:el("lco-ws-entity-name").value.trim(),
    kind:el("lco-ws-entity-kind").value.trim(),notes:el("lco-ws-entity-notes").value,
    file_id:el("lco-ws-entity-file").value});
   resetText("lco-ws-entity-name");resetText("lco-ws-entity-notes");
   message("lco-ws-entity-msg","entityAdded","ok");await loadEntities();
  }catch(error){console.warn(error);message("lco-ws-entity-msg","error","error")}
  finally{button.disabled=false}
 });
 bindButton("lco-ws-quality-check",async()=>{
  try{await loadHandoffQuality()}
  catch(error){console.warn(error);el("lco-ws-quality-summary").textContent=t("qualityLoadError")}
 });
 bindButton("lco-ws-export",async()=>{
  try{
   // Re-read selected sources and integrity immediately before user confirmation.
   const quality=await loadHandoffQuality();
   const selected=Number(quality.selected_documents||0);
   if(!selected){message("lco-ws-export-msg","exportNone","error");return}
   if(quality.export_blocked_in_scanned_sources){
    message("lco-ws-export-msg","qualityBlocked","error");return;
   }
   if(!window.confirm(fmt("exportConfirm",{n:selected})))return;
   if((quality.warnings||[]).length &&
      !window.confirm(fmt("qualityApprove",{n:(quality.warnings||[]).length})))return;
   await request("/api/export-package",{});
   message("lco-ws-export-msg","exportDone","ok");
  }catch(error){console.warn(error);message("lco-ws-export-msg","error","error")}
 });
 bindButton("lco-ws-open-exports",async()=>{
  try{
   const result=await request("/api/open-exports",{});
   if(result.error)throw new Error(result.error);
  }catch(error){console.warn(error);message("lco-ws-export-msg","error","error")}
 });
 bindButton("lco-ws-verify",async()=>{
  try{await request("/api/verify-integrity",{});message("lco-ws-security-msg","verified","ok")}
  catch(error){console.warn(error);message("lco-ws-security-msg","error","error")}
 });
 el("lco-ws-advanced").addEventListener("click",()=>el("lco-simple-advanced")?.click());
 // Shortcut buttons are connected by the existing simple layer; they call
 // this function instead of activating another navigation tab.
 window.LCOOpenSimplePanel=openPanel;
 for(const [panel,loader] of [
  ["lco-ws-documents",loadDocs],["lco-ws-timeline",loadTimeline],
  ["lco-ws-tasks",loadTasks],["lco-ws-entities",loadEntities]
 ]){
  el(panel).addEventListener("toggle",()=>{
   if(el(panel).open)loader().catch(error=>console.warn(error));
  });
 }
}
function init(){
 const home=el("lco-easy-home");if(!home||el("lco-ws-documents"))return;
 const layout=[
 '<details class="lco-ws-panel" id="lco-ws-documents"><summary data-ws-copy="documents"></summary><div class="lco-ws-body">',
 '<p data-ws-copy="docHelp"></p><div class="lco-ws-btns"><button type="button" id="lco-ws-doc-reload" data-ws-copy="load"></button>',
 '<button type="button" id="lco-ws-select-all" class="secondary" data-ws-copy="selectAll"></button>',
 '<button type="button" id="lco-ws-select-none" class="ghost" data-ws-copy="selectNone"></button></div>',
 '<p id="lco-ws-selection-msg" class="lco-ws-feedback" role="status" aria-live="polite"></p>',
 '<label><span data-ws-copy="docFilter"></span><input type="search" id="lco-ws-doc-filter" maxlength="160" autocomplete="off" style="width:100%;max-width:540px"></label>',
 '<p id="lco-ws-doc-page-info" aria-live="polite"></p>',
 '<ul class="lco-ws-list" id="lco-ws-doc-list"></ul>',
 '<div class="lco-ws-btns"><button type="button" id="lco-ws-doc-prev" class="secondary" data-ws-copy="docPrevious"></button>',
 '<button type="button" id="lco-ws-doc-next" class="secondary" data-ws-copy="docNext"></button></div></div></details>',
 '<details class="lco-ws-panel" id="lco-ws-search"><summary data-ws-copy="search"></summary><div class="lco-ws-body">',
 '<p data-ws-copy="searchHelp"></p><form id="lco-ws-search-form"><div class="lco-ws-grid">',
 '<label><span data-ws-copy="query"></span><input id="lco-ws-query" type="text" minlength="2" maxlength="100" required></label>',
 '</div><div class="lco-ws-btns"><button type="submit" data-ws-copy="searchNow"></button>',
 '<button type="button" id="lco-ws-prepare" class="secondary" data-ws-copy="prepare"></button>',
 '<label class="lco-ws-check"><input type="checkbox" id="lco-ws-pdf"><span data-ws-copy="includePdf"></span></label></div></form>',
 '<p class="lco-ws-feedback" id="lco-ws-search-msg" aria-live="polite"></p>',
 '<ul class="lco-ws-list" id="lco-ws-search-results"></ul></div></details>',
 '<details class="lco-ws-panel" id="lco-ws-timeline"><summary data-ws-copy="timeline"></summary><div class="lco-ws-body">',
 '<p data-ws-copy="timelineHelp"></p><form id="lco-ws-timeline-form"><div class="lco-ws-grid">',
 '<label><span data-ws-copy="eventTitle"></span><input type="text" id="lco-ws-event-title" maxlength="160" minlength="3" required></label>',
 '<label><span data-ws-copy="eventDate"></span><input type="date" id="lco-ws-event-date" required></label>',
 '<label><span data-ws-copy="source"></span><select id="lco-ws-event-file"></select></label></div>',
 '<label><span data-ws-copy="eventSummary"></span><textarea id="lco-ws-event-summary" maxlength="800"></textarea></label>',
 '<div class="lco-ws-btns"><button type="submit" id="lco-ws-event-submit" data-ws-copy="addEvent"></button>',
 '<button type="button" class="secondary" id="lco-ws-proposals" data-ws-copy="showDates"></button></div></form>',
 '<p id="lco-ws-timeline-msg" class="lco-ws-feedback" aria-live="polite"></p>',
 '<ul id="lco-ws-suggestions" class="lco-ws-list"></ul><ul id="lco-ws-events" class="lco-ws-list"></ul></div></details>',
 '<details class="lco-ws-panel" id="lco-ws-tasks"><summary data-ws-copy="tasks"></summary><div class="lco-ws-body">',
 '<p data-ws-copy="tasksHelp"></p><form id="lco-ws-task-form"><div class="lco-ws-grid">',
 '<label><span data-ws-copy="taskTitle"></span><input id="lco-ws-task-title" type="text" minlength="3" maxlength="180" required></label>',
 '<label><span data-ws-copy="due"></span><input type="date" id="lco-ws-task-date"></label>',
 '<label><span data-ws-copy="priority"></span><select id="lco-ws-task-priority">',
 '<option value="normal" data-ws-copy="normal"></option><option value="high" data-ws-copy="high"></option><option value="low" data-ws-copy="low"></option></select></label>',
 '<label><span data-ws-copy="source"></span><select id="lco-ws-task-file"></select></label></div>',
 '<button type="submit" id="lco-ws-task-submit" data-ws-copy="createTask"></button></form>',
 '<p id="lco-ws-task-msg" class="lco-ws-feedback" aria-live="polite"></p>',
 '<ul class="lco-ws-list" id="lco-ws-task-list"></ul></div></details>',
 '<details class="lco-ws-panel" id="lco-ws-entities"><summary data-ws-copy="entities"></summary><div class="lco-ws-body">',
 '<p data-ws-copy="entityHelp"></p><form id="lco-ws-entity-form"><div class="lco-ws-grid">',
 '<label><span data-ws-copy="entityName"></span><input id="lco-ws-entity-name" type="text" minlength="2" maxlength="160" required></label>',
 '<label><span data-ws-copy="entityType"></span><input id="lco-ws-entity-kind" type="text" maxlength="80"></label>',
 '<label><span data-ws-copy="source"></span><select id="lco-ws-entity-file"></select></label></div>',
 '<label><span data-ws-copy="entityNotes"></span><textarea id="lco-ws-entity-notes" maxlength="1200"></textarea></label>',
 '<button type="submit" id="lco-ws-entity-submit" data-ws-copy="addEntity"></button></form>',
 '<p id="lco-ws-entity-msg" class="lco-ws-feedback" aria-live="polite"></p>',
 '<ul class="lco-ws-list" id="lco-ws-entity-list"></ul></div></details>',
 '<details class="lco-ws-panel" id="lco-ws-handoff"><summary data-ws-copy="handoff"></summary><div class="lco-ws-body">',
 '<p data-ws-copy="handoffHelp"></p><p id="lco-ws-export-count"></p>',
 '<p data-ws-copy="qualityIntro"></p>',
 '<button type="button" class="secondary" id="lco-ws-quality-check" data-ws-copy="qualityCheck"></button>',
 '<p id="lco-ws-quality-summary" role="status" aria-live="polite"></p>',
 '<ul id="lco-ws-quality-warnings" class="lco-ws-list"></ul>',
 '<div class="lco-ws-btns"><button type="button" id="lco-ws-export" data-ws-copy="buildExport"></button>',
 '<button type="button" id="lco-ws-open-exports" class="secondary" data-ws-copy="openExports"></button></div>',
 '<p class="lco-ws-feedback" id="lco-ws-export-msg" aria-live="polite"></p></div></details>',
 '<details class="lco-ws-panel" id="lco-ws-integrity"><summary data-ws-copy="integrity"></summary><div class="lco-ws-body">',
 '<p data-ws-copy="integrityHelp"></p><button type="button" id="lco-ws-verify" data-ws-copy="verify"></button>',
 '<p class="lco-ws-feedback" id="lco-ws-security-msg" aria-live="polite"></p></div></details>',
 '<details class="lco-ws-panel" id="lco-ws-technical"><summary data-ws-copy="technical"></summary><div class="lco-ws-body">',
 '<p data-ws-copy="technicalHelp"></p><button type="button" id="lco-ws-advanced" data-ws-copy="advanced"></button></div></details>',
 '<p id="lco-ws-general" class="lco-ws-feedback" aria-live="polite"></p>'
 ].join("");
 home.insertAdjacentHTML("beforeend",layout);
 localize(home);bind();
 window.LCORefreshWorkspace=loadDocs;
 loadDocs().catch(error=>console.warn("Document overview unavailable",error));
 // Reuse the existing language toggle; never replace or add another switch.
 const prior=window.LCOApplyExtraCopy;
 window.LCOApplyExtraCopy=function(){if(typeof prior==="function")prior();localize(home);resetMessageTranslations();refreshExportPreview()};
}
document.addEventListener("DOMContentLoaded",init);
})();
</script>'''
