"""A14 human-confirmed review-to-task workflow on the current one-page UI."""
WORKFLOW_CSS = r'''<style>
#lco-easy-home #lco-review-workflow{margin:14px 0 22px;padding:16px 18px;border:1px solid var(--lco-border,#857a70);border-radius:14px;background:var(--lco-panel,#171615)}
#lco-easy-home #lco-review-workflow>summary{font-size:1.1rem;font-weight:750;cursor:pointer;padding:7px 0}
#lco-easy-home #lco-review-workflow p{line-height:1.55}
#lco-easy-home .lco-flow-list{list-style:none;margin:8px 0;padding:0;max-height:390px;overflow:auto}
#lco-easy-home .lco-flow-list li{padding:9px 0;border-bottom:1px solid var(--lco-border,#7775);overflow-wrap:anywhere}
#lco-easy-home .lco-flow-list small{display:block;margin:4px 0;opacity:.83}
#lco-easy-home .lco-flow-list button{margin-top:6px}
body.lco-light #lco-easy-home #lco-review-workflow{background:#fbf8f2}
</style>'''

WORKFLOW_SCRIPT = r'''<script>
(function(){
"use strict";
const words={
 de:{
  heading:"Prüfaufgaben mit Aktenbezug",
  introduction:"Für bereits erkannte offene Prüfpunkte kannst du bewusst eine Aufgabe anlegen. Eine erledigte Aufgabe bestätigt weder eine Quelle noch einen rechtlichen Sachverhalt.",
  candidates:"Offene Prüfpunkte",
  existing:"Verknüpfte Aufgaben im Fall",
  create:"Aufgabe anlegen",
  openTasks:"Aufgaben öffnen",
  confirm:"Eine neue organisatorische Prüfaufgabe für diesen Eintrag erstellen? Es erfolgt keine automatische Freigabe oder Fristberechnung.",
  created:"Prüfaufgabe angelegt.",already:"Für diesen Prüfpunkt besteht bereits eine offene Aufgabe.",
  loading:"Prüfaufgaben werden aus vorhandenen Einträgen zusammengestellt …",
  error:"Prüfaufgaben konnten nicht geladen oder angelegt werden: ",
  empty:"Keine Einträge in diesem begrenzten Ausschnitt.",
  status_pending_review:"Noch ungeprüft",
  status_recheck_required:"Quellen erneut prüfen",
  status_open_question:"Offene Frage",
  source_review_context_current:"Quellenkontext unverändert",
  source_review_context_changed:"Quellenkontext geändert: Aufgabe erneut bewerten",
  source_review_item_not_in_current_queue:"Prüfpunkt derzeit nicht im begrenzten Ausschnitt – nicht automatisch erledigt",
  task_open:"Offen",task_in_progress:"In Bearbeitung",task_done:"Erledigt",task_cancelled:"Abgebrochen",
  kind_document:"Dokument",kind_claim:"Quellenaussage",kind_connection:"Dokumentbezug",kind_question:"Offene Frage",
  limit:"Die Übersicht ist begrenzt. Aufgaben werden ausschließlich nach Bestätigung erstellt. Eine Aufgabenerledigung ändert keine Review-Entscheidung."
 },
 en:{
  heading:"Source-linked review tasks",
  introduction:"Create a task deliberately for an existing review item. Completing a task never verifies a source or confirms any legal fact.",
  candidates:"Outstanding review items",existing:"Linked case tasks",
  create:"Create task",openTasks:"Open tasks",
  confirm:"Create one organizational review task for this item? No source approval or legal deadline is generated.",
  created:"Review task created.",already:"An open task already exists for this review item.",
  loading:"Preparing review work items from existing case records …",
  error:"Unable to load or create review tasks: ",empty:"No entries in this bounded view.",
  status_pending_review:"Pending review",status_recheck_required:"Source needs recheck",status_open_question:"Open question",
  source_review_context_current:"Source context unchanged",
  source_review_context_changed:"Source context changed: review this task again",
  source_review_item_not_in_current_queue:"Item not in bounded current queue – not automatically resolved",
  task_open:"Open",task_in_progress:"In progress",task_done:"Done",task_cancelled:"Cancelled",
  kind_document:"Document",kind_claim:"Sourced claim",kind_connection:"Document link",kind_question:"Open question",
  limit:"The view is bounded. Tasks require explicit confirmation. Completing a task does not change a review decision."
 }
};
const el=id=>document.getElementById(id);
const t=key=>(String(localStorage.getItem("local_case_organizer_ui_lang")||"de").startsWith("de")?words.de:words.en)[key]||key;
let snapshot=null,loading=false,creating=false;
function listItem(list,title,description){
 const li=document.createElement("li");
 li.textContent=String(title);
 const small=document.createElement("small");small.textContent=String(description);
 li.append(small);list.append(li);return li;
}
function draw(){
 const box=el("lco-review-workflow");if(!box)return;
 box.querySelectorAll("[data-flow-copy]").forEach(node=>node.textContent=t(node.dataset.flowCopy));
 if(!snapshot)return;
 const pending=el("lco-flow-pending");pending.replaceChildren();
 for(const item of (snapshot.candidates||[]).slice(0,80)){
  const row=listItem(pending,t("kind_"+item.kind)+": "+item.title,
    t("status_"+item.status)+" · "+item.ref);
  const button=document.createElement("button");
  button.type="button";button.textContent=t("create");
  button.disabled=creating;button.addEventListener("click",()=>createTask(item));
  row.append(button);
 }
 const active=el("lco-flow-active");active.replaceChildren();
 for(const item of (snapshot.review_tasks||[]).slice(0,60)){
  const row=listItem(active,item.title,
   t("kind_"+item.kind)+" · "+t("task_"+item.task_status)+" · "+
   t("source_"+item.source_status)+" · "+item.linked_file_ids);
  const button=document.createElement("button");
  button.type="button";button.textContent=t("openTasks");
  button.addEventListener("click",()=>openTasks());
  row.append(button);
 }
 for(const list of [pending,active]){
  if(!list.children.length)listItem(list,t("empty"),"");
 }
}
async function refresh(){
 if(loading)return;
 loading=true;el("lco-flow-status").textContent=t("loading");
 try{
  const response=await fetch("/api/review-workflow");
  const data=await response.json();
  if(!response.ok)throw Error(data.error||"HTTP "+response.status);
  snapshot=data;el("lco-flow-status").textContent="";draw();
 }catch(error){el("lco-flow-status").textContent=t("error")+String(error.message||error)}
 finally{loading=false}
}
function openTasks(){
 const panel=el("lco-ws-tasks");
 if(panel){panel.open=true;panel.scrollIntoView({block:"start",behavior:"smooth"})}
}
async function createTask(item){
 if(creating||loading||!window.confirm(t("confirm")))return;
 creating=true;
 try{
  const response=await fetch("/api/create-review-task",{
   method:"POST",headers:{"Content-Type":"application/json"},
   body:JSON.stringify({kind:item.kind,ref:item.ref,token:item.token})
  });
  const result=await response.json();
  if(!response.ok)throw Error(result.error||"HTTP "+response.status);
  el("lco-flow-status").textContent=t(result.created?"created":"already");
  await refresh();
  if(typeof window.LCORefreshWorkspace==="function")await window.LCORefreshWorkspace();
 }catch(error){el("lco-flow-status").textContent=t("error")+String(error.message||error)}
 finally{creating=false;draw()}
}
function init(){
 const briefing=el("lco-briefing");
 if(!briefing||el("lco-review-workflow"))return;
 const box=document.createElement("details");box.id="lco-review-workflow";
 box.innerHTML=[
  '<summary data-flow-copy="heading"></summary>',
  '<p data-flow-copy="introduction"></p><p id="lco-flow-status" aria-live="polite"></p>',
  '<h3 data-flow-copy="candidates"></h3><ul class="lco-flow-list" id="lco-flow-pending"></ul>',
  '<h3 data-flow-copy="existing"></h3><ul class="lco-flow-list" id="lco-flow-active"></ul>',
  '<p data-flow-copy="limit"></p>'
 ].join("");
 briefing.insertAdjacentElement("afterend",box);
 box.addEventListener("toggle",()=>{if(box.open)refresh()});
 const previousCopy=window.LCOApplyExtraCopy;
 window.LCOApplyExtraCopy=function(){
  if(typeof previousCopy==="function")previousCopy();
  draw();
 };
 const previousRefresh=window.LCORefreshWorkspace;
 window.LCORefreshWorkspace=async function(){
  if(typeof previousRefresh==="function")await previousRefresh();
  if(box.open)await refresh();
 };
 draw();
}
document.addEventListener("DOMContentLoaded",init);
})();
</script>'''