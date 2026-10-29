"""Minimal, persistent progress panel for explicitly triggered local processing.

Loaded only by the existing UI override. Uses its same-origin API adapter.
"""
AUTOPILOT_CSS = r'''<style>
#lco-easy-home .lco-auto-box{margin:15px 0;padding:19px 20px;border:1px solid var(--lco-border,#857a70);border-radius:14px;background:var(--lco-panel,#171615)}
#lco-easy-home .lco-auto-box h2{font-size:1.17rem;margin:0 0 8px}
#lco-easy-home .lco-auto-box p{line-height:1.5;margin:8px 0;overflow-wrap:anywhere}
#lco-easy-home .lco-auto-actions{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:12px}
#lco-easy-home .lco-auto-actions button{padding:9px 12px;font-size:.9rem}
#lco-easy-home .lco-auto-actions label{display:flex;gap:8px;align-items:center}
#lco-easy-home .lco-auto-actions input[type=checkbox]{width:18px;height:18px}
#lco-easy-home .lco-auto-progress{width:100%;height:10px;border-radius:6px;accent-color:#b99454}
#lco-easy-home .lco-auto-warnings{padding-left:20px;margin:8px 0}
#lco-easy-home .lco-auto-warnings li{margin-bottom:6px;overflow-wrap:anywhere}
body.lco-light #lco-easy-home .lco-auto-box{background:#fbf8f2}
</style>'''

AUTOPILOT_SCRIPT = r'''<script>
(function(){
"use strict";
const L={
 de:{
  title:"Automatische Aktenvorbereitung",help:"Nach dem Einfügen werden alle geeigneten Dokumente schrittweise lokal durchsuchbar gemacht. Die Originale bleiben unverändert. Öffne währenddessen keine zweite Verarbeitung.",
  run:"Weiterverarbeiten",retry:"Fehlversuche erneut prüfen",stop:"Nach diesem Schritt stoppen",
  ocr:"Lokale OCR für Scans/Bilder ausdrücklich zulassen",ready:"Bereit. Dateien hinzufügen, um die Verarbeitung zu starten.",
  working:"Verarbeitung läuft. Bitte die Seite geöffnet lassen.",
  complete:"Vorbereitung abgeschlossen. Datumsangaben und weitere Hinweise sind unbestätigte Vorschläge.",
  paused:"Verarbeitung unterbrochen. Über „Weiterverarbeiten“ fortsetzen.",
  error:"Verarbeitung unterbrochen. Dateien bleiben erhalten. Erneut versuchen.",
  stats:"{done} von {total} Quellen vorbereitet oder übersprungen; {pending} stehen noch aus.",
  skip:"{ocr} benötigt möglicherweise OCR; {failed} konnten nicht verarbeitet werden.",
  issues:"Nicht vorbereitete Unterlagen (manuell prüfen)",hint:"Für OCR müssen passende lokale Programme installiert sein; dies ist keine KI- oder Rechtsanalyse.",
  noItems:"Noch keine Unterlagen vorhanden."
 },
 en:{
  title:"Automatic case preparation",help:"After adding files, eligible documents are prepared for local search in bounded steps. Originals are never modified. Avoid running a second import at the same time.",
  run:"Continue processing",retry:"Retry failed items",stop:"Stop after current step",
  ocr:"Explicitly allow local OCR for scans/images",ready:"Ready. Add files to start processing.",
  working:"Processing locally. Keep this browser page open.",
  complete:"Preparation completed. Dates and other hints are unverified suggestions.",
  paused:"Processing paused. Choose Continue processing to resume.",
  error:"Processing interrupted. Files remain safe. Retry.",
  stats:"{done} of {total} sources prepared or skipped; {pending} pending.",
  skip:"{ocr} may need OCR; {failed} could not be processed.",
  issues:"Unprocessed documents (manual review required)",hint:"OCR requires installed local tools; this is not AI or legal analysis.",
  noItems:"No documents available yet."
 }
};
const el=id=>document.getElementById(id);
const t=k=>(String(localStorage.getItem("local_case_organizer_ui_lang")||"de").startsWith("de")?L.de:L.en)[k]||k;
const fmt=(key,args={})=>Object.entries(args).reduce((s,[k,v])=>s.replace("{"+k+"}",String(v)),t(key));
let report=null,running=false,stopRequested=false,phase="ready";
function paint(){
 const n=el("lco-auto-message"),progress=el("lco-auto-progress");
 if(!n||!progress)return;
 document.querySelectorAll("#lco-auto-box [data-auto-copy]").forEach(e=>{e.textContent=t(e.dataset.autoCopy)});
 n.textContent=t(phase);
 const done=Number(report?.completed||0),total=Number(report?.total||0);
 el("lco-auto-stats").textContent=fmt("stats",{
  done,total,pending:Number(report?.pending||0)
 });
 progress.value=total?Math.min(100,Math.round(done*100/total)):0;
 const warning=el("lco-auto-warning");
 warning.textContent=fmt("skip",{
  ocr:Number(report?.needs_ocr||0),failed:Number(report?.failed||0)
 });
 const listing=el("lco-auto-list");
 listing.replaceChildren();
 for(const item of (report?.warnings||[]).slice(0,12)){
  const entry=document.createElement("li");
  entry.textContent=String(item.original_name||item.file_id||"–")+" ("+String(item.reason||"–")+")";
  listing.append(entry);
 }
 el("lco-auto-continue").disabled=running;
 el("lco-auto-retry").disabled=running||!Number(report?.failed||0);
 el("lco-auto-stop").disabled=!running;
}
async function json(response){
 const data=await response.json();
 if(!response.ok)throw new Error(data.error||("HTTP "+response.status));
 return data;
}
async function load(){
 try{report=await json(await fetch("/api/autopilot-status"));paint()}
 catch(error){console.warn("Autopilot status unavailable",error);phase="error";paint()}
}
async function run(retryFailed=false){
 if(running)return;
 running=true;stopRequested=false;phase="working";paint();
 const useOcr=el("lco-auto-ocr").checked;
 try{
  // One action = a bounded sequence of small server-side batches.
  // Pause automatically after 80 requests to avoid infinite requests.
  for(let step=0;step<80;step++){
   report=await json(await fetch("/api/autopilot-process",{
    method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({use_ocr:useOcr,retry_failed:retryFailed && step===0})
   }));
   paint();
   if(stopRequested){phase="paused";break}
   if(!report.remaining){phase="complete";break}
   if(!report.processed_in_batch){phase="paused";break}
   if(step===79){phase="paused"}
  }
  if(typeof window.LCORefreshWorkspace==="function")await window.LCORefreshWorkspace();
 }catch(error){console.warn("Autopilot processing interrupted",error);phase="error"}
 finally{running=false;paint()}
}
function init(){
 const home=el("lco-easy-home");if(!home||el("lco-auto-box"))return;
 const panel=document.createElement("section");panel.id="lco-auto-box";panel.className="lco-auto-box";
 panel.innerHTML=[
 '<h2 data-auto-copy="title"></h2><p data-auto-copy="help"></p>',
 '<p id="lco-auto-message" role="status" aria-live="polite"></p>',
 '<progress id="lco-auto-progress" class="lco-auto-progress" value="0" max="100"></progress>',
 '<p id="lco-auto-stats"></p><p id="lco-auto-warning"></p>',
 '<div class="lco-auto-actions">',
 '<button type="button" id="lco-auto-continue" data-auto-copy="run"></button>',
 '<button type="button" id="lco-auto-retry" class="secondary" data-auto-copy="retry"></button>',
 '<button type="button" id="lco-auto-stop" class="ghost" data-auto-copy="stop"></button>',
 '<label><input type="checkbox" id="lco-auto-ocr"><span data-auto-copy="ocr"></span></label></div>',
 '<details><summary data-auto-copy="issues"></summary><ul class="lco-auto-warnings" id="lco-auto-list"></ul><p data-auto-copy="hint"></p></details>'
 ].join("");
 const files=el("lco-simple-drop")?.closest(".lco-easy-card");
 if(files)files.insertAdjacentElement("afterend",panel);
 else home.append(panel);
 el("lco-auto-continue").addEventListener("click",()=>run(false));
 el("lco-auto-retry").addEventListener("click",()=>run(true));
 el("lco-auto-stop").addEventListener("click",()=>{stopRequested=true});
 window.LCOAutopilot={runAfterImport:()=>run(false),refresh:load};
 const previous=window.LCOApplyExtraCopy;
 window.LCOApplyExtraCopy=function(){if(typeof previous==="function")previous();paint()};
 paint();load();
}
document.addEventListener("DOMContentLoaded",init);
})();
</script>'''
