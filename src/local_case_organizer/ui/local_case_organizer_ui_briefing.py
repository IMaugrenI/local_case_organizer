"""Compact case briefing inside the existing simple workspace.

This renders the read-only /api/case-briefing response; it does not infer facts,
perform legal assessment, write to stores, or upload private material.
"""
BRIEFING_CSS = r'''<style>
#lco-easy-home .lco-briefing{margin:4px 0 22px;padding:18px 20px;border:1px solid var(--lco-border,#7775);border-radius:15px;background:var(--lco-panel,#171615)}
#lco-easy-home .lco-briefing h2{font-size:1.3rem;margin:0 0 6px}
#lco-easy-home .lco-briefing>p{margin:7px 0 15px;max-width:740px;line-height:1.55;opacity:.82}
#lco-easy-home .lco-brief-numbers{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
#lco-easy-home .lco-brief-number{padding:12px 8px;text-align:center;border:1px solid var(--lco-border,#7775);border-radius:10px}
#lco-easy-home .lco-brief-number strong{font-size:1.5rem;display:block}
#lco-easy-home .lco-brief-number span{display:block;font-size:.81rem;line-height:1.3;opacity:.85}
#lco-easy-home .lco-briefing details{margin-top:12px}
#lco-easy-home .lco-briefing summary{cursor:pointer;padding:8px 0;font-weight:650}
#lco-easy-home .lco-briefing ul{padding-left:20px;line-height:1.6}
#lco-easy-home .lco-briefing li{margin-bottom:8px}
#lco-easy-home .lco-brief-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
#lco-easy-home .lco-brief-actions button{padding:9px 12px;font-size:.9rem}
#lco-easy-home .lco-brief-date{font-size:.89rem;overflow-wrap:anywhere}
body.lco-light #lco-easy-home .lco-briefing{background:#fbf8f2}
@media(max-width:580px){#lco-easy-home .lco-brief-numbers{gap:6px}#lco-easy-home .lco-brief-number strong{font-size:1.2rem}#lco-easy-home .lco-briefing{padding:14px}}
</style>'''

BRIEFING_SCRIPT = r'''<script>
(function(){
"use strict";
const translations={
 de:{
 heading:"Dein Fall auf einen Blick",lead:"Aus den vorhandenen Akten zusammengestellt. Vorschläge sind keine bewiesenen Tatsachen.",
 documents:"Unterlagen",pending:"Noch zu prüfen",hints:"Datums-Hinweise",
 waiting:"Offene Arbeitsschritte",none:"Keine dringenden Hinweise aus den vorhandenen Daten. Dies beweist keine Vollständigkeit.",
 dates:"Mögliche Datumsangaben mit Quellen",noDates:"Derzeit keine überprüfbaren Datumsvorschläge.",
 types:"Mögliche Dokumentarten (unbestätigt)",noTypes:"Noch keine Hinweise auf Dokumentarten gefunden.",
 typeLimit:"Nur Suchhilfen aus Dateinamen oder lokal überprüften Textstellen; nicht als Dokumentart bestätigt.",
 openDocs:"Dokumente prüfen",openTimeline:"Zeitangaben ansehen",openHandoff:"Übergabe für Anwalt",
 review_documents:"Unterlagen ohne abgeschlossenen Prüfstatus: ",
 review_dates:"Datumsangaben in überprüften Textquellen: ",
 review_comparisons:"Manuell verbundene Werte zur Prüfung: ",
 manual_date:"Vom Betreiber eingetragene Termine heute/fällig: ",
 organize_sources:"Dokumente noch ohne manuelle Verknüpfung: ",
 error:"Die Fallübersicht konnte nicht geladen werden. Deine Dokumente bleiben unverändert.",
 loading:"Fallübersicht wird geladen …",
 limit:"Geeignete, unveränderte Textdateien und bereits lokal indizierte PDFs werden nach Datumshinweisen durchsucht. Keine automatische rechtliche Fristberechnung."
 },
 en:{
 heading:"Your case at a glance",lead:"Assembled from existing case records. Hints are not proven facts.",
 documents:"Documents",pending:"To review",hints:"Date hints",
 waiting:"Suggested next steps",none:"No urgent hints found in existing data. This does not prove completeness.",
 dates:"Possible date mentions with sources",noDates:"No eligible date suggestions currently found.",
 types:"Possible document types (unverified)",noTypes:"No document type hints found yet.",
 typeLimit:"Search aids from filenames or verified local text only; not confirmed document classifications.",
 openDocs:"Review documents",openTimeline:"Review dates",openHandoff:"Prepare lawyer handoff",
 review_documents:"Documents awaiting manual review: ",
 review_dates:"Date mentions in verified text originals: ",
 review_comparisons:"Manually linked value differences: ",
 manual_date:"Operator-entered overdue/today tasks: ",
 organize_sources:"Documents without a manually entered link: ",
 error:"Case overview unavailable. Your documents remain unchanged.",
 loading:"Loading case overview …",
 limit:"Eligible verified text files and locally indexed PDFs are checked for date mentions. No automatic legal deadline calculation."
 }
};
const el=id=>document.getElementById(id);
const t=key=>(String(localStorage.getItem("local_case_organizer_ui_lang")||"de").startsWith("de")?translations.de:translations.en)[key]||key;
let cached=null;
function populate(){
 if(!el("lco-briefing"))return;
 document.querySelectorAll("#lco-briefing [data-brief-copy]").forEach(node=>node.textContent=t(node.dataset.briefCopy));
 if(!cached)return;
 const totals=cached.totals||{};
 for(const [id,key] of [["lco-brief-total","documents"],["lco-brief-pending","review_pending"],["lco-brief-hints","date_suggestions"]]){
  el(id).textContent=String(totals[key]||0);
 }
 const steps=el("lco-brief-steps");steps.replaceChildren();
 for(const item of (cached.next_actions||[]).slice(0,5)){
  const label=document.createElement("li");
  label.textContent=t(item.kind)+String(item.count);
  steps.append(label);
 }
 if(!steps.children.length){const li=document.createElement("li");li.textContent=t("none");steps.append(li)}
 const dates=el("lco-brief-date-list");dates.replaceChildren();
 for(const item of (cached.date_samples||[]).slice(0,6)){
  const li=document.createElement("li");li.className="lco-brief-date";
  li.textContent=String(item.date)+" · "+String(item.original_name)+" ("+String(item.file_id)+", P"+String(item.page||1)+":"+String(item.line)+")";
  dates.append(li);
 }
 if(!dates.children.length){const li=document.createElement("li");li.textContent=t("noDates");dates.append(li)}
 const types=el("lco-brief-type-list");types.replaceChildren();
 for(const item of (cached.document_type_hints||[]).slice(0,15)){
  const li=document.createElement("li");
  const name=String(item.original_name||item.file_id);
  const label=(String(localStorage.getItem("local_case_organizer_ui_lang")||"de").startsWith("de")?item.label_de:item.label_en);
  li.textContent=name+" · "+label+" ("+String(item.file_id)+")";
  types.append(li);
 }
 if(!types.children.length){const li=document.createElement("li");li.textContent=t("noTypes");types.append(li)}
}
async function refresh(){
 try{
  const response=await fetch("/api/case-briefing");
  const data=await response.json();
  if(!response.ok)throw new Error(data.error||"HTTP "+response.status);
  cached=data;populate();
 }catch(error){console.warn("Case briefing unavailable",error);el("lco-brief-message").textContent=t("error")}
}
function openPanel(id){
 const section=el(id);
 if(section){section.open=true;section.scrollIntoView({block:"start",behavior:"smooth"})}
}
function init(){
 const home=el("lco-easy-home");
 if(!home||el("lco-briefing"))return;
 const root=document.createElement("section");root.id="lco-briefing";root.className="lco-briefing";
 root.innerHTML=[
 '<h2 data-brief-copy="heading"></h2><p data-brief-copy="lead"></p>',
 '<div class="lco-brief-numbers">',
 '<div class="lco-brief-number"><strong id="lco-brief-total">–</strong><span data-brief-copy="documents"></span></div>',
 '<div class="lco-brief-number"><strong id="lco-brief-pending">–</strong><span data-brief-copy="pending"></span></div>',
 '<div class="lco-brief-number"><strong id="lco-brief-hints">–</strong><span data-brief-copy="hints"></span></div></div>',
 '<div class="lco-brief-actions"><button type="button" id="lco-brief-docs" class="secondary" data-brief-copy="openDocs"></button>',
 '<button type="button" id="lco-brief-timeline" class="secondary" data-brief-copy="openTimeline"></button>',
 '<button type="button" id="lco-brief-handoff" data-brief-copy="openHandoff"></button></div>',
 '<details><summary data-brief-copy="waiting"></summary><ul id="lco-brief-steps"></ul></details>',
 '<details><summary data-brief-copy="dates"></summary><ul id="lco-brief-date-list"></ul>',
 '<p data-brief-copy="limit"></p></details>',
 '<details><summary data-brief-copy="types"></summary><ul id="lco-brief-type-list"></ul>',
 '<p data-brief-copy="typeLimit"></p></details>',
 '<p id="lco-brief-message" role="status" aria-live="polite"></p>'
 ].join("");
 home.querySelector(".lco-easy-intro")?.insertAdjacentElement("afterend",root);
 el("lco-brief-docs").addEventListener("click",()=>openPanel("lco-ws-documents"));
 el("lco-brief-timeline").addEventListener("click",()=>openPanel("lco-ws-timeline"));
 el("lco-brief-handoff").addEventListener("click",()=>openPanel("lco-ws-handoff"));
 const priorCopy=window.LCOApplyExtraCopy;
 window.LCOApplyExtraCopy=function(){if(typeof priorCopy==="function")priorCopy();populate()};
 const previousRefresh=window.LCORefreshWorkspace;
 window.LCORefreshWorkspace=async function(){
  if(typeof previousRefresh==="function")await previousRefresh();
  await refresh();
 };
 populate();refresh();
}
document.addEventListener("DOMContentLoaded",init);
})();
</script>'''
