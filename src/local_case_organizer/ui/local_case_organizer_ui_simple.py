"""Simple on-demand document intake above the existing advanced workspace.

The original work-area navigation and all expert capabilities remain intact.
"""
SIMPLE_CSS = r'''<style>
body.lco-simple-mode .wrap > :not(#lco-brandbar):not(#lco-easy-home){display:none!important}
body:not(.lco-simple-mode) #lco-easy-home{display:none!important}
#lco-easy-home{max-width:1040px;margin:0 auto 35px;padding:12px 0 34px;color:var(--lco-fg,inherit)}
#lco-easy-home .lco-easy-intro{padding:16px 0 24px}
#lco-easy-home h1{font-size:clamp(1.8rem,3.5vw,2.65rem);margin-bottom:8px;line-height:1.2}
#lco-easy-home .lco-easy-intro p{max-width:650px;color:var(--lco-muted,#c9c2b7);line-height:1.6}
#lco-easy-home .lco-easy-card{border:1px solid var(--lco-border,#7775);border-radius:15px;padding:22px;margin:0 0 16px;background:var(--lco-panel,#171615)}
#lco-easy-home .lco-easy-case{display:flex;flex-wrap:wrap;gap:14px;align-items:end}
#lco-easy-home .lco-easy-field{flex:1 1 260px;max-width:450px}
#lco-easy-home .lco-easy-field label{display:block;margin-bottom:8px;font-weight:650}
#lco-easy-home select,#lco-easy-home input[type=text]{background:var(--lco-control-bg,#292622);color:var(--lco-control-fg,#f4f0e8);border:1px solid var(--lco-control-border,#837565);border-radius:9px;min-height:42px;width:100%}
#lco-easy-home .lco-easy-new{margin-top:16px;max-width:480px}
#lco-easy-home .lco-easy-new button{margin-top:10px}
#lco-easy-home .lco-easy-new[hidden]{display:none!important}
#lco-easy-home .lco-easy-drop{border:2px dashed #b39460;border-radius:15px;padding:34px 20px;text-align:center;background:rgba(179,148,96,.06);transition:background .15s}
#lco-easy-home .lco-easy-drop.dragging{background:rgba(179,148,96,.2);border-color:#e1b969}
#lco-easy-home .lco-easy-drop h2{font-size:1.4rem;margin:0 0 8px}
#lco-easy-home .lco-easy-drop p,#lco-easy-home .lco-easy-help{line-height:1.6;color:var(--lco-muted,#c9c2b7)}
#lco-easy-home .lco-easy-drop button{margin-top:12px}
#lco-easy-home button:disabled{opacity:.55;cursor:progress}
#lco-easy-home .lco-easy-result{min-height:26px;margin:14px 0 4px;line-height:1.55}
#lco-easy-home .lco-easy-result[data-kind=error]{color:#e6a692}
#lco-easy-home .lco-easy-result[data-kind=ok]{color:var(--lco-gold-bright,#e1b969)}
#lco-easy-home .lco-easy-secondary{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:14px}
#lco-easy-home .lco-easy-secondary button{font-size:.9rem;padding:10px 14px}
#lco-easy-home .lco-easy-documents{margin:0;padding:0;list-style:none}
#lco-easy-home .lco-easy-documents li{padding:12px 0;border-bottom:1px solid var(--lco-border,#7775);overflow-wrap:anywhere}
#lco-easy-home .lco-easy-documents li:last-child{border:0}
#lco-easy-home .lco-easy-documents small{display:block;opacity:.75;margin-top:4px}
#lco-easy-home .lco-easy-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
#lco-easy-home .lco-easy-actions button{padding:11px 14px}
.lco-quick-export{padding:8px 0 16px;border-bottom:1px solid var(--lco-border,#7775);margin-bottom:14px}
.lco-quick-export p{line-height:1.55;max-width:700px}
.lco-quick-export .lco-quick-export-actions{display:flex;gap:10px;flex-wrap:wrap}
.lco-quick-export button{font-size:.92rem}
.lco-quick-export-result{min-height:26px;padding:10px 0}
.lco-quick-export-result[data-kind=error]{color:#e6a692}
body.lco-light .lco-quick-export-result[data-kind=error]{color:#8c3223}
body.lco-light #lco-easy-home .lco-easy-card{background:#fbf8f2}
body.lco-light #lco-easy-home .lco-easy-intro p,
body.lco-light #lco-easy-home .lco-easy-drop p,
body.lco-light #lco-easy-home .lco-easy-help{color:#544d44}
body.lco-light #lco-easy-home .lco-easy-drop{background:#f5f0e7}
body.lco-light #lco-easy-home .lco-easy-drop.dragging{background:#ebdfc9}
body.lco-light #lco-easy-home .lco-easy-result[data-kind=error]{color:#8c3223}
body.lco-light #lco-easy-home .lco-easy-result[data-kind=ok]{color:#80571b}
body:not(.lco-simple-mode) #lco-simple-return{display:inline-flex}
#lco-simple-return{font-size:.84rem!important;padding:8px 12px!important;white-space:nowrap}
@media(max-width:650px){#lco-easy-home .lco-easy-card{padding:16px}#lco-easy-home .lco-easy-drop{padding:24px 12px}}
</style>'''

SIMPLE_SCRIPT = r'''<script>
(function(){
"use strict";
const STORAGE_MODE="lco_view_mode_v1";
const CASE_KEY="lco_active_case_tab";
const L={
 de:{
  headline:"Deine Fallakte. Ganz einfach.",lead:"Fall wählen, Dokumente hinzufügen und direkt mit einer geordneten Übersicht arbeiten.",
  caseTitle:"1. Fall auswählen",caseLabel:"Aktueller Fall",newCase:"Neuen Fall anlegen",
  newLabel:"Wie soll der neue Fall heißen?",create:"Fall erstellen und öffnen",
  filesTitle:"2. Dateien hinzufügen",drop:"Dateien hier ablegen oder über den Knopf auswählen.",
  gate:"Das Ablegen oder Auswählen startet die lokale Übernahme und das Dokumentenregister. Keine KI-Auswertung und keine Weitergabe.",
  pick:"Dateien auswählen",existing:"Bereits abgelegte Inbox-Dateien einordnen",
  limits:"Auch große Auswahlen werden automatisch in sichere Teilpakete aufgeteilt (bis 160 Dateien / 150 MB). Originale bleiben unverändert.",
  listTitle:"3. Deine Dokumente",empty:"Noch keine Dokumente in diesem Fall.",
  openDocuments:"Register bearbeiten",openTimeline:"Zeitlinie bearbeiten",openExport:"Übergabe vorbereiten",
  advanced:"Erweiterte Ansicht",basic:"Einfache Ansicht",
  exportHelp:"Markiere zuerst im Dokumentenregister die gewünschten Unterlagen für die Übergabe. Ein Export startet erst nach deiner Bestätigung.",
  chooseExport:"Dokumente für Übergabe auswählen",exportNow:"Übergabepaket erstellen",
  exportConfirm:"Jetzt ein neues lokales Übergabepaket aus den markierten Dokumenten erstellen?",
  exportNothing:"Noch keine Dokumente für die Übergabe markiert. Bitte zuerst im Register auswählen.",
  exportDone:"Übergabepaket lokal erstellt. Es wurde nichts versendet.",
  exportFailed:"Übergabepaket konnte nicht erstellt werden. Bitte Auswahl und Integritätsprüfung kontrollieren.",
  busy:"Dateien werden lokal übernommen und eingeordnet …",
  noFiles:"Bitte zuerst Dateien auswählen.",size:"Bitte die Auswahl auf 160 Dateien und insgesamt 150 MB begrenzen.",
  uploading:"Teilpaket {current} von {total} wird übernommen …",
  blockedFolder:"Ordner lassen sich hier nicht direkt ablegen. Bitte einzelne Dateien auswählen.",
  done:"{added} Datei(en) neu eingeordnet. {skipped} bereits vorhandene Datei(en) übersprungen.",
  more:"Weitere {remaining} Datei(en) warten. Noch einmal auf „Inbox-Dateien einordnen“ klicken.",
  noNew:"Keine neuen Dateien. Bereits bekannte Unterlagen wurden nicht doppelt importiert.",
  savedOnly:"Die Dateien liegen sicher im Eingangsordner. Die Einordnung wurde nicht abgeschlossen. Über „Inbox-Dateien einordnen“ erneut starten.",
  failure:"Der Vorgang konnte nicht abgeschlossen werden. Die bisherigen Unterlagen bleiben erhalten.",
  caseFailure:"Der Fall konnte nicht angelegt werden. Bitte den Namen prüfen.",
  fallback:"Standard-Arbeitsbereich",confirm:"Ungespeicherte Änderungen vor dem Fallwechsel sichern. Fortfahren?",
  count:"{count} Dokument(e) im Register",status:"Prüfstatus",imported:"Eingeordnet",unchecked:"Noch nicht geprüft"
 },
 en:{
  headline:"Your case, made simple.",lead:"Choose a case, add documents and work from a clear overview.",
  caseTitle:"1. Choose a case",caseLabel:"Current case",newCase:"Create a new case",
  newLabel:"Name of the new case",create:"Create and open case",
  filesTitle:"2. Add files",drop:"Drop files here or use the selection button.",
  gate:"Dropping or selecting starts local intake and document registration. No AI analysis or external sharing.",
  pick:"Choose files",existing:"Organize files already in the inbox",
  limits:"Large selections are automatically divided into safe batches (up to 160 files / 150 MB). Originals remain unchanged.",
  listTitle:"3. Your documents",empty:"No documents in this case yet.",
  openDocuments:"Edit register",openTimeline:"Edit timeline",openExport:"Prepare handoff",
  advanced:"Advanced view",basic:"Simple view",
  exportHelp:"First mark the documents to include in the handoff in the document register. Export starts only after your confirmation.",
  chooseExport:"Select documents for handoff",exportNow:"Create handoff package",
  exportConfirm:"Create a local handoff package from the selected documents now?",
  exportNothing:"No documents marked for handoff yet. Select documents in the register first.",
  exportDone:"Local handoff package created. Nothing was transmitted.",
  exportFailed:"Could not create the handoff package. Check the selection and integrity review.",
  busy:"Adding and organizing files locally …",
  noFiles:"Choose files first.",size:"Please limit your selection to 160 files and 150 MB total.",
  uploading:"Uploading batch {current} of {total} …",
  blockedFolder:"Folders cannot be dropped here. Please select individual files.",
  done:"{added} new file(s) organized; {skipped} existing file(s) skipped.",
  more:"{remaining} more file(s) are waiting. Select “Organize inbox files” again.",
  noNew:"No new files. Previously registered documents were not imported twice.",
  savedOnly:"Files are safely in the inbox, but registration did not finish. Use “Organize inbox files” to retry.",
  failure:"Could not finish the operation. Existing documents remain untouched.",
  caseFailure:"Could not create the case. Please check the name.",
  fallback:"Default workspace",confirm:"Save unsaved changes before switching cases. Continue?",
  count:"{count} document(s) in the register",status:"Review status",imported:"Registered",unchecked:"Not reviewed"
 }
};
let cachedRows=[],lastNotice=null,exportNotice=null,busy=false,uploading=false;
const lang=()=>String(localStorage.getItem("local_case_organizer_ui_lang")||"de").startsWith("de")?"de":"en";
const t=(key)=>L[lang()][key]||key;
const el=(id)=>document.getElementById(id);
function text(key,replacements){
 let value=t(key);
 for(const [name,content] of Object.entries(replacements||{}))value=value.replace("{"+name+"}",String(content));
 return value;
}
function notice(kind,key,details){
 lastNotice={kind,key,details};
 const node=el("lco-simple-result");
 if(node){node.dataset.kind=kind;node.textContent=text(key,details)}
}
function renderRows(){
 const root=el("lco-simple-list"),heading=el("lco-simple-count");
 if(!root||!heading)return;
 root.replaceChildren();
 heading.textContent=text("count",{count:cachedRows.length});
 if(!cachedRows.length){const li=document.createElement("li");li.textContent=t("empty");root.append(li);return}
 for(const row of cachedRows.slice(0,24)){
   const li=document.createElement("li"),strong=document.createElement("strong"),small=document.createElement("small");
   strong.textContent=String(row.original_name||row.file_id||"-");
   small.textContent=t("status")+": "+(row.review_status==="unreviewed"?t("unchecked"):String(row.review_status||t("imported")));
   li.append(strong,small);root.append(li);
 }
}
function copy(){
 document.querySelectorAll("#lco-easy-home [data-simple-copy],#lco-quick-export [data-simple-copy]").forEach(node=>{node.textContent=t(node.dataset.simpleCopy)});
 const fallback=el("lco-simple-cases")?.querySelector('option[value="legacy-default"]');
 if(fallback)fallback.textContent=t("fallback");
 if(el("lco-simple-return"))el("lco-simple-return").textContent=t("basic");
 if(lastNotice)notice(lastNotice.kind,lastNotice.key,lastNotice.details);
 const exportStatus=el("lco-quick-export-result");
 if(exportStatus&&exportNotice)exportStatus.textContent=t(exportNotice);
 renderRows();
}
function setMode(simple){
 localStorage.setItem(STORAGE_MODE,simple?"simple":"advanced");
 document.body.classList.toggle("lco-simple-mode",simple);
 if(!simple){document.getElementById("lco-workspace-nav")?.scrollIntoView({block:"nearest"});}
}
async function responseJson(response){
 const data=await response.json();
 if(!response.ok)throw new Error(data.error||"HTTP "+response.status);
 return data;
}
async function refreshDocuments(){
 try{
  const data=await responseJson(await fetch("/api/register-data"));
  cachedRows=Array.isArray(data.rows)?data.rows:[];
  renderRows();
 }catch(error){console.warn("Document overview unavailable",error);}
}
async function refreshCases(){
 const data=await responseJson(await fetch("/api/cases"));
 const picker=el("lco-simple-cases");if(!picker)return;
 const selected=sessionStorage.getItem(CASE_KEY)||data.selected_case||"legacy-default";
 picker.replaceChildren();
 const existing=[{case_id:"legacy-default",title:t("fallback")}].concat(data.cases||[]);
 for(const row of existing){
   const option=document.createElement("option");
   option.value=row.case_id;
   option.textContent=row.case_id==="legacy-default"?t("fallback"):String(row.title||row.case_id);
   option.selected=option.value===selected;
   picker.append(option);
 }
}
async function organize(fileNames){
 if(busy)return false;
 busy=true;el("lco-simple-pick").disabled=true;el("lco-simple-inbox").disabled=true;
 notice("working","busy");
 try{
  const result=await responseJson(await fetch("/api/quick-organize",{
    method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({files:Array.isArray(fileNames)?fileNames:null})
  }));
  notice("ok",result.imported_files?"done":"noNew",{added:result.imported_files||0,skipped:result.already_present||0});
  if(result.remaining_files)notice("ok","more",{remaining:result.remaining_files});
  await refreshDocuments();
  if(typeof window.LCORefreshWorkspace==="function")await window.LCORefreshWorkspace();
  // After explicit intake, the bounded local worker prepares searchable
  // derivatives and updates its visible progress panel. No background run on
  // page load, no model call or automatic export.
  if(result.imported_files>0 && window.LCOAutopilot?.runAfterImport){
    await window.LCOAutopilot.runAfterImport();
  }
  if(typeof window.refreshStatus==="function")await window.refreshStatus();
  return true;
 }catch(error){console.warn("Local intake failed",error);notice("error","savedOnly");return false}
 finally{busy=false;el("lco-simple-pick").disabled=uploading;el("lco-simple-inbox").disabled=uploading}
}
async function upload(files){
 if(busy||uploading)return;
 if(!files?.length){notice("error","noFiles");return}
 const selected=Array.from(files);
 if(selected.length>160||selected.reduce((size,file)=>size+file.size,0)>150*1024*1024){
   notice("error","size");return;
 }
 // Split on file count and bytes to stay below the existing 32 MiB
 // HTTP multipart limit, including form boundary overhead.
 const batches=[];let batch=[],bytes=0;
 for(const file of selected){
   if(file.size>26*1024*1024){notice("error","size");return}
   if(batch.length>=20 || (batch.length && bytes+file.size>26*1024*1024)){
      batches.push(batch);batch=[];bytes=0;
   }
   batch.push(file);bytes+=file.size;
 }
 if(batch.length)batches.push(batch);
 busy=true;uploading=true;el("lco-simple-pick").disabled=true;el("lco-simple-inbox").disabled=true;
 try{
   for(let index=0;index<batches.length;index++){
     notice("working","uploading",{current:index+1,total:batches.length});
     const form=new FormData();
     for(const file of batches[index])form.append("files",file,file.name);
     const saved=await responseJson(await fetch("/api/upload",{method:"POST",body:form}));
     // The importer and autopilot both use their existing bounded APIs.
     busy=false;
     const done=await organize(saved.uploaded_files);
     if(!done)throw new Error("A locally saved batch has not been registered");
     busy=true;
   }
 }catch(error){
   console.warn("Upload or case import stopped",error);
   notice("error","failure");
 }finally{
   uploading=false;busy=false;el("lco-simple-pick").disabled=false;el("lco-simple-inbox").disabled=false;
   el("lco-simple-files").value="";
 }
}
function build(){
 const wrap=document.querySelector(".wrap");
 const brand=el("lco-brandbar");
 if(!wrap||!brand||el("lco-easy-home"))return;
 const root=document.createElement("section");root.id="lco-easy-home";
 root.innerHTML=[
 '<header class="lco-easy-intro"><h1 data-simple-copy="headline"></h1><p data-simple-copy="lead"></p></header>',
 '<section class="lco-easy-card"><h2 data-simple-copy="caseTitle"></h2><div class="lco-easy-case">',
 '<div class="lco-easy-field"><label for="lco-simple-cases" data-simple-copy="caseLabel"></label><select id="lco-simple-cases"></select></div>',
 '<button type="button" id="lco-simple-new" class="secondary" data-simple-copy="newCase"></button></div>',
 '<form id="lco-simple-new-form" class="lco-easy-new" hidden><label for="lco-simple-case-name" data-simple-copy="newLabel"></label>',
 '<input id="lco-simple-case-name" type="text" maxlength="110" required>',
 '<button type="submit" data-simple-copy="create"></button></form></section>',
 '<section class="lco-easy-card"><h2 data-simple-copy="filesTitle"></h2>',
 '<div id="lco-simple-drop" class="lco-easy-drop">',
 '<h2 data-simple-copy="drop"></h2><p data-simple-copy="gate"></p>',
 '<button type="button" id="lco-simple-pick" data-simple-copy="pick"></button>',
 '<input id="lco-simple-files" type="file" multiple hidden></div>',
 '<div class="lco-easy-secondary"><button type="button" id="lco-simple-inbox" class="ghost" data-simple-copy="existing"></button>',
 '<span class="lco-easy-help" data-simple-copy="limits"></span></div>',
 '<div id="lco-simple-result" class="lco-easy-result" role="status" aria-live="polite"></div></section>',
 '<section class="lco-easy-card"><h2 data-simple-copy="listTitle"></h2><p id="lco-simple-count"></p>',
 '<ul id="lco-simple-list" class="lco-easy-documents"></ul>',
 '<div class="lco-easy-actions"><button type="button" id="lco-simple-documents" data-simple-copy="openDocuments"></button>',
 '<button type="button" id="lco-simple-timeline" class="secondary" data-simple-copy="openTimeline"></button>',
 '<button type="button" id="lco-simple-export" class="secondary" data-simple-copy="openExport"></button>',
 '<button type="button" id="lco-simple-advanced" class="ghost" data-simple-copy="advanced"></button></div></section>'
 ].join("");
 brand.insertAdjacentElement("afterend",root);
 const nav=el("lco-workspace-nav");
 if(nav&&!el("lco-simple-return")){
   const button=document.createElement("button");button.type="button";button.id="lco-simple-return";button.className="ghost";
   button.addEventListener("click",()=>setMode(true));nav.insertBefore(button,nav.firstChild);
 }
 el("lco-simple-pick").addEventListener("click",()=>el("lco-simple-files").click());
 el("lco-simple-files").addEventListener("change",event=>upload(event.target.files));
 el("lco-simple-inbox").addEventListener("click",()=>organize());
 const zone=el("lco-simple-drop");
 zone.addEventListener("dragover",event=>{event.preventDefault();zone.classList.add("dragging")});
 zone.addEventListener("dragleave",()=>zone.classList.remove("dragging"));
 zone.addEventListener("drop",event=>{
   event.preventDefault();zone.classList.remove("dragging");
   if(Array.from(event.dataTransfer?.items||[]).some(item=>item.webkitGetAsEntry?.()?.isDirectory)){
     notice("error","blockedFolder");return;
   }
   upload(event.dataTransfer?.files);
 });
 el("lco-simple-cases").addEventListener("change",event=>{
   if(!window.confirm(t("confirm"))){refreshCases();return}
   sessionStorage.setItem(CASE_KEY,event.target.value);window.location.reload();
 });
 el("lco-simple-new").addEventListener("click",()=>{
   const form=el("lco-simple-new-form");form.hidden=!form.hidden;
   if(!form.hidden)el("lco-simple-case-name").focus();
 });
 el("lco-simple-new-form").addEventListener("submit",async event=>{
   event.preventDefault();const title=el("lco-simple-case-name").value.trim();if(!title)return;
   let slug=title.normalize("NFKD").replace(/[\u0300-\u036f]/g,"").toLowerCase()
     .replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"").slice(0,30)||"fall";
   slug=slug+"-"+Date.now().toString(36).slice(-6);
   try{
     const caseRecord=await responseJson(await fetch("/api/create-case",{
       method:"POST",headers:{"Content-Type":"application/json"},
       body:JSON.stringify({case_id:slug,title})
     }));
     sessionStorage.setItem(CASE_KEY,caseRecord.case_id);window.location.reload();
   }catch(error){console.warn("Case creation failed",error);notice("error","caseFailure")}
 });
 function openView(id){
   setMode(false);el("lco-tab-"+id)?.click();
 }
 const exportEditor=el("export-history")?.closest(".editor");
 if(exportEditor&&!el("lco-quick-export")){
   const panel=document.createElement("div");
   panel.id="lco-quick-export";
   panel.className="lco-quick-export";
   panel.innerHTML=[
     '<p data-simple-copy="exportHelp"></p><div class="lco-quick-export-actions">',
     '<button type="button" id="lco-quick-export-choose" class="secondary" data-simple-copy="chooseExport"></button>',
     '<button type="button" id="lco-quick-export-now" data-simple-copy="exportNow"></button></div>',
     '<div id="lco-quick-export-result" class="lco-quick-export-result" role="status" aria-live="polite"></div>'
   ].join("");
   exportEditor.insertBefore(panel,exportEditor.firstChild);
   el("lco-quick-export-choose").addEventListener("click",()=>openView("documents"));
   el("lco-quick-export-now").addEventListener("click",async()=>{
     const button=el("lco-quick-export-now");if(button.disabled)return;
     button.disabled=true;
     const output=el("lco-quick-export-result");
     const show=(key,kind)=>{exportNotice=key;output.dataset.kind=kind;output.textContent=t(key)};
     try{
       const status=await responseJson(await fetch("/api/status"));
       if(!(status.summary?.selected_export_count>0)){show("exportNothing","error");return}
       if(!window.confirm(t("exportConfirm")))return;
       await responseJson(await fetch("/api/export-package",{method:"POST"}));
       show("exportDone","ok");
       if(typeof window.loadExportHistory==="function")await window.loadExportHistory();
     }catch(error){console.warn("Local handoff export failed",error);show("exportFailed","error")}
     finally{button.disabled=false}
   });
 }
 el("lco-simple-documents").addEventListener("click",()=>{if(window.LCOOpenSimplePanel)window.LCOOpenSimplePanel("lco-ws-documents");else openView("documents")});
 el("lco-simple-timeline").addEventListener("click",()=>{if(window.LCOOpenSimplePanel)window.LCOOpenSimplePanel("lco-ws-timeline");else openView("timeline")});
 el("lco-simple-export").addEventListener("click",()=>{if(window.LCOOpenSimplePanel)window.LCOOpenSimplePanel("lco-ws-handoff");else openView("export")});
 el("lco-simple-advanced").addEventListener("click",()=>setMode(false));
 const prior=window.LCOApplyExtraCopy;
 window.LCOApplyExtraCopy=function(){
   if(typeof prior==="function")prior();
   copy();
 };
 setMode(localStorage.getItem(STORAGE_MODE)!=="advanced");
 copy();
 refreshCases().catch(error=>{console.warn("Case list unavailable",error);notice("error","failure")});
 refreshDocuments();
}
document.addEventListener("DOMContentLoaded",build);
})();
</script>'''
