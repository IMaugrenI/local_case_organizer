"""Optional local model control nested inside the existing specialist panel."""
MODEL_CSS = r'''<style>
#lco-easy-home .lco-model-box{padding:14px 16px;margin:12px 0 20px;border:1px solid var(--lco-border,#857a70);border-radius:12px}
#lco-easy-home .lco-model-box label{display:block;margin:12px 0;line-height:1.5}
#lco-easy-home .lco-model-box select{width:100%;padding:10px;border-radius:7px;max-width:450px}
#lco-easy-home .lco-model-box button{padding:9px 12px;margin-right:9px}
#lco-easy-home .lco-model-box p{line-height:1.6}
#lco-easy-home .lco-model-status{min-height:24px;overflow-wrap:anywhere}
</style>'''

MODEL_SCRIPT = r'''<script>
(function(){
"use strict";
const M={
 de:{
  heading:"Lokale KI – Vorschläge automatisch vorbereiten",
  intro:"Optional: Ollama auf diesem Computer kann kurze Quellenstellen analysieren. Der Zugriff erfolgt ausschließlich auf 127.0.0.1. Keine Cloud- oder automatische Freigabe.",
  choose:"Lokal installiertes Modell",find:"Lokale Modelle erkennen",
  action:"Ausgewähltes Dokument lokal analysieren",
  wholeCase:"Alle vorbereiteten Dokumente lokal prüfen",
  retryCase:"Fehlgeschlagene Durchläufe wiederholen",
  stopCase:"Nach aktuellem Dokument stoppen",
  caseConfirm:"Die lokal indizierten Dokumente dieser Akte werden nacheinander an dein bewusst gewähltes Ollama-Modell auf 127.0.0.1 übergeben. Jedes Dokument wird überprüft und nur seine gekürzten Textauszüge werden genutzt. Es erfolgt keine automatische Bestätigung. Vollständige Akte jetzt analysieren?",
  caseWorking:"{done} von {total} Dokumenten durchgesehen. {remaining} stehen noch aus.",
  caseDone:"Lokale Aktenanalyse beendet: {done} verarbeitet, {failed} nicht verarbeitet, {total} vorbereitete Dokumente insgesamt. Alle Vorschläge bleiben ungeprüft.",
  casePaused:"Aktenanalyse angehalten. Der Stand bleibt gespeichert; derselbe Knopf setzt ihn fort.",
  confirm:"Für die ausgewählte Akte werden bis zu zwei überprüfte Textstellen an die lokale Ollama-Instanz auf diesem Computer übergeben. Keine externe Übertragung ist vorgesehen. Jetzt ausführen?",
  empty:"Keine Modelle gefunden. Ollama und ein lokal installiertes Modell werden benötigt.",
  ready:"Lokales Modell auswählen und die Analyse ausdrücklich starten.",
  working:"Lokale KI erstellt Vorschläge. Dies kann etwas dauern.",
  done:"{added} ungeprüfte Vorschläge gespeichert, {bad} nicht belegbare verworfen, {old} bereits bekannte übersprungen. Bitte jeden Vorschlag separat prüfen.",
  error:"Lokale KI nicht verfügbar oder Analyse fehlgeschlagen. Vorhandene Unterlagen sind unverändert.",
  manual:"Ohne Ollama kannst du den bisherigen manuellen KI-Austausch weiterhin nutzen."
 },
 en:{
  heading:"Local AI – prepare review suggestions",
  intro:"Optional: Ollama on this computer can examine short source excerpts. The endpoint is fixed to 127.0.0.1; no cloud or automatic approval.",
  choose:"Installed local model",find:"Find local models",
  action:"Analyze selected document locally",
  wholeCase:"Review all prepared documents locally",
  retryCase:"Retry failed documents",
  stopCase:"Stop after current document",
  caseConfirm:"Locally indexed case documents will be reviewed one by one by the Ollama model you selected at 127.0.0.1. Only shortened, verified source excerpts are submitted. No findings are automatically approved. Start the full local review?",
  caseWorking:"{done} of {total} documents reviewed. {remaining} remain.",
  caseDone:"Local review finished: {done} processed, {failed} not processed, {total} indexed documents. All model hints remain unreviewed.",
  casePaused:"Case review paused. Progress is saved; the same button resumes.",
  confirm:"Up to two hash-verified text excerpts from this document will be passed to the local Ollama service on this computer. No external transmission is intended. Continue?",
  empty:"No models found. You need Ollama and an installed local model.",
  ready:"Choose a local model and explicitly start analysis.",
  working:"Local AI is preparing suggestions; this can take some time.",
  done:"{added} unreviewed suggestions saved; {bad} unverifiable rejected; {old} known duplicates skipped. Review each suggestion individually.",
  error:"Local AI unavailable or analysis failed. Existing documents were not changed.",
  manual:"You can still use the previous manual AI exchange without Ollama."
 }
};
const el=id=>document.getElementById(id);
const t=key=>(String(localStorage.getItem("local_case_organizer_ui_lang")||"de").startsWith("de")?M.de:M.en)[key]||key;
const fmt=(key,values={})=>Object.entries(values).reduce((msg,[k,v])=>msg.replace("{"+k+"}",String(v)),t(key));
let stateKey="ready",stateVars={},busy=false,stopRequested=false;
function updateCopy(){
 document.querySelectorAll("#lco-model-box [data-model-copy]").forEach(n=>{n.textContent=t(n.dataset.modelCopy)});
 const msg=el("lco-model-result");if(msg)msg.textContent=fmt(stateKey,stateVars);
}
function status(key,vars={}){stateKey=key;stateVars=vars;updateCopy()}
async function api(path,data){
 const options=data===undefined?{}:{
  method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)
 };
 const result=await fetch(path,options);
 let body={};try{body=await result.json()}catch{}
 if(!result.ok)throw new Error(body.error||("HTTP "+result.status));
 return body;
}
async function models(){
 const select=el("lco-model-selected");if(!select||busy)return;
 busy=true;el("lco-model-find").disabled=true;
 try{
  const found=await api("/api/local-models");
  const old=select.value;select.replaceChildren();
  for(const model of (found.models||[])){
   const option=document.createElement("option");option.textContent=String(model);
   option.value=String(model);select.append(option);
  }
  if((found.models||[]).includes(old))select.value=old;
  status(select.options.length?"ready":"empty");
 }catch(error){console.warn("Local Ollama unavailable",error);status("error")}
 finally{busy=false;el("lco-model-find").disabled=false}
}
async function analyze(){
 if(busy)return;
 const fileId=el("lco-special-ai-file")?.value;
 const model=el("lco-model-selected")?.value;
 if(!fileId||!model){status("empty");return}
 if(!window.confirm(t("confirm")))return;
 busy=true;el("lco-model-run").disabled=true;status("working");
 try{
  const result=await api("/api/local-model-review",{model,file_ids:[fileId]});
  status("done",{
   added:result.accepted_as_pending||0,
   bad:result.rejected_unverifiable||0,
   old:result.skipped_duplicates||0
  });
  // Existing view keeps every model suggestion as untrusted pending review.
  el("lco-special-ai-reload")?.click();
 }catch(error){console.warn("Local model analysis failed",error);status("error")}
 finally{busy=false;el("lco-model-run").disabled=false}
}
async function reviewCase(retryFailed=false){
 if(busy)return;
 const model=el("lco-model-selected")?.value;
 if(!model){status("empty");return}
 if(!window.confirm(t("caseConfirm")))return;
 busy=true;stopRequested=false;
 for(const id of ["lco-model-run","lco-model-case","lco-model-retry","lco-model-find"]){
   el(id).disabled=true;
 }
 el("lco-model-stop").disabled=false;
 let last={};
 try{
  // Browser-driven bounded batches: progress is private on disk after each
  // source. Stop is checked between requests, never while a source is written.
  for(let i=0;i<300;i++){
    last=await api("/api/local-model-batch",{
      model,retry_failed:retryFailed && i===0
    });
    status("caseWorking",{
      done:last.done||0,total:last.total||0,remaining:last.remaining||0
    });
    if(stopRequested){status("casePaused");break}
    if(!last.remaining||!last.processed_in_step){
      status("caseDone",{
        done:last.done||0,failed:last.failed||0,total:last.total||0
      });
      break;
    }
    if(i===299)status("casePaused");
  }
  el("lco-special-ai-reload")?.click();
  if(typeof window.LCORefreshWorkspace==="function")await window.LCORefreshWorkspace();
 }catch(error){console.warn("Local case review interrupted",error);status("error")}
 finally{
  busy=false;
  for(const id of ["lco-model-run","lco-model-case","lco-model-retry","lco-model-find"]){
    el(id).disabled=false;
  }
  el("lco-model-stop").disabled=true;
 }
}
function init(){
 const form=el("lco-special-ai-pane")?.querySelector(".lco-special-content");
 if(!form||el("lco-model-box"))return;
 const area=document.createElement("section");area.id="lco-model-box";area.className="lco-model-box";
 area.innerHTML=[
  '<h3 data-model-copy="heading"></h3>',
  '<p data-model-copy="intro"></p>',
  '<label><span data-model-copy="choose"></span><select id="lco-model-selected"></select></label>',
  '<div><button type="button" id="lco-model-find" data-model-copy="find" class="secondary"></button>',
  '<button type="button" id="lco-model-run" data-model-copy="action"></button></div>',
  '<div><button type="button" id="lco-model-case" data-model-copy="wholeCase"></button>',
  '<button type="button" id="lco-model-retry" class="secondary" data-model-copy="retryCase"></button>',
  '<button type="button" id="lco-model-stop" class="ghost" data-model-copy="stopCase" disabled></button></div>',
  '<p class="lco-model-status" id="lco-model-result" role="status" aria-live="polite"></p>',
  '<p data-model-copy="manual"></p>'
 ].join("");
 form.insertBefore(area,form.firstElementChild);
 el("lco-model-find").addEventListener("click",models);
 el("lco-model-run").addEventListener("click",analyze);
 el("lco-model-case").addEventListener("click",()=>reviewCase(false));
 el("lco-model-retry").addEventListener("click",()=>reviewCase(true));
 el("lco-model-stop").addEventListener("click",()=>{stopRequested=true});
 el("lco-special-ai-pane").addEventListener("toggle",()=>{
  if(el("lco-special-ai-pane").open&&!el("lco-model-selected").options.length)models();
 });
 const previous=window.LCOApplyExtraCopy;
 window.LCOApplyExtraCopy=function(){if(typeof previous==="function")previous();updateCopy()};
 updateCopy();
}
document.addEventListener("DOMContentLoaded",init);
})();
</script>'''
