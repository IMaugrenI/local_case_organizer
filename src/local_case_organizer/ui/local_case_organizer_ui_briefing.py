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
#lco-easy-home .lco-review-list{list-style:none;padding:0;max-height:370px;overflow:auto}
#lco-easy-home .lco-review-list>li{border-bottom:1px solid var(--lco-border,#7775);padding:10px 0;overflow-wrap:anywhere}
#lco-easy-home .lco-review-list small{display:block;opacity:.85;margin:4px 0}
#lco-easy-home .lco-review-list button{margin:6px 8px 0 0;font-size:.87rem}
#lco-easy-home #lco-brief-review>p{line-height:1.55;opacity:.87}
body.lco-light #lco-easy-home .lco-review-list{color:#262626}
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
 ai:"Ungeprüfte KI-Hinweise",noAi:"Keine nachweisbar quellengebundenen KI-Vorschläge vorhanden.",
 aiReview:"KI-Hinweise prüfen",aiLimit:"Diese Texte sind ungeprüfte KI-Vorschläge, keine bestätigten Tatsachen oder rechtlichen Bewertungen.",
 reviewHeading:"Prüf-Cockpit – offene Quellennachweise und Entscheidungen",
 reviewLead:"Nur organisatorische Prüfschritte. Ein menschlicher Prüfstatus bestätigt weder die Richtigkeit eines Dokuments noch einen rechtlichen Sachverhalt.",
 reviewDocs:"Unterlagen mit offenem Prüfstatus",reviewClaims:"Aussagen mit Quellenstellen",reviewConnections:"Mögliche Dokumentverbindungen",
 reviewCount:"Offen: {d} Unterlagen · {c} Aussagen · {s} erneut zu prüfen · {l} Verbindungen",
 reviewGotoDocs:"Im Dokumentregister öffnen",reviewGotoClaims:"Aussagenprüfung öffnen",reviewGotoLinks:"Verbindungen prüfen",
 reviewSource:"Originalquelle",reviewPage:"Seite",reviewConfirmClaim:"Diese ausdrücklich zitierte Aussage als manuell geprüft markieren? Das bestätigt nicht ihre Richtigkeit.",
 reviewClaimButton:"Als manuell geprüft kennzeichnen",reviewClaimStatus:"Quellennachweis ungültig oder nicht verfügbar – bitte Original und Index überprüfen",
 reviewLinkPending:"Verbindung noch ungeprüft",reviewLinkStale:"Verknüpfung erneut prüfen",
 reviewActionError:"Prüfaktion fehlgeschlagen: ",reviewNoEntries:"Derzeit keine offenen Einträge aus den verfügbaren Quellen.",
 reviewIncomplete:"Die Dokumentverknüpfungsprüfung ist unvollständig. Es können weitere unbekannte Einträge bestehen.",
 review_claims:"Aussagen mit offener Quellenprüfung: ",review_connections:"Mögliche Dokumentverbindungen zur Prüfung: ",
 review_documents:"Unterlagen ohne abgeschlossenen Prüfstatus: ",
 review_dates:"Datumsangaben in überprüften Textquellen: ",
 review_ai:"Ungeprüfte lokale KI-Vorschläge: ",
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
 ai:"Unreviewed AI hints",noAi:"No verifiable source-linked AI suggestions currently available.",
 aiReview:"Review AI hints",aiLimit:"These are unreviewed model suggestions, not established facts or legal conclusions.",
 reviewHeading:"Review cockpit – source citations and manual decisions",
 reviewLead:"Organizational review only. A human review status does not establish document truth or any legal fact.",
 reviewDocs:"Documents awaiting manual review",reviewClaims:"Statements and source quotations",reviewConnections:"Possible document relationships",
 reviewCount:"Open: {d} documents · {c} statements · {s} need recheck · {l} links",
 reviewGotoDocs:"Open document register",reviewGotoClaims:"Open statement review",reviewGotoLinks:"Review relationships",
 reviewSource:"Original source",reviewPage:"Page",reviewConfirmClaim:"Mark this sourced statement as manually reviewed? This does not confirm its truth.",
 reviewClaimButton:"Mark manually reviewed",reviewClaimStatus:"Source evidence no longer verifiable – check original and index",
 reviewLinkPending:"Link not reviewed",reviewLinkStale:"Relationship needs another review",
 reviewActionError:"Review action failed: ",reviewNoEntries:"No open entries found in available sources.",
 reviewIncomplete:"Connection scan is incomplete. Additional entries may be unknown.",
 review_claims:"Statements awaiting source review: ",review_connections:"Possible document links awaiting review: ",
 review_documents:"Documents awaiting manual review: ",
 review_dates:"Date mentions in verified text originals: ",
 review_ai:"Unreviewed local AI suggestions: ",
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
 const ai=el("lco-brief-ai-list");ai.replaceChildren();
 for(const item of (cached.ai_review_samples||[]).slice(0,6)){
  const li=document.createElement("li");li.className="lco-brief-date";
  li.textContent=String(item.file_id)+" · P"+String(item.page)+" · "+
   String(item.statement)+" — Quelle: "+String(item.source_quote);
  ai.append(li);
 }
 if(!ai.children.length){const li=document.createElement("li");li.textContent=t("noAi");ai.append(li)}

 const queue=cached.review_queue||{};
 const qCounts={
  d:totals.review_pending||0,c:totals.claim_review_pending||0,
  s:totals.claim_recheck_required||0,l:totals.connection_review_pending||0
 };
 el("lco-review-count").textContent=Object.entries(qCounts).reduce(
  (acc,[k,v])=>acc.replace("{"+k+"}",String(v)),t("reviewCount"));
 const documents=el("lco-review-docs");documents.replaceChildren();
 for(const item of (queue.document_samples||[]).slice(0,20)){
  const li=document.createElement("li");li.textContent=String(item.original_name||item.file_id)+" · "+String(item.file_id)+" · "+String(item.review_status);
  const btn=document.createElement("button");btn.type="button";btn.textContent=t("reviewGotoDocs");
  btn.addEventListener("click",()=>openPanel("lco-ws-documents"));li.append(btn);documents.append(li);
 }
 const claims=el("lco-review-claims");claims.replaceChildren();
 for(const item of (queue.claim_samples||[]).slice(0,20)){
  const li=document.createElement("li");
  li.textContent=String(item.claim_id)+" · "+t("reviewSource")+": "+String(item.file_id);
  const info=document.createElement("small");
  info.textContent=item.status==="recheck_required"?t("reviewClaimStatus"):
    t("reviewPage")+" "+String(item.source_page)+" · "+String(item.source_quote)+" · "+String(item.statement);
  li.append(info);
  const btn=document.createElement("button");btn.type="button";
  if(item.status==="pending_review"){
   btn.textContent=t("reviewClaimButton");
   btn.addEventListener("click",()=>reviewClaim(String(item.claim_id)));
  }else{
   btn.textContent=t("reviewGotoClaims");
   btn.addEventListener("click",()=>{openPanel("lco-ws-technical");openPanel("lco-special-claims-pane")});
  }
  li.append(btn);claims.append(li);
 }
 const links=el("lco-review-links");links.replaceChildren();
 for(const item of (queue.connection_samples||[]).slice(0,20)){
  const li=document.createElement("li");
  li.textContent=String(item.reference_label)+": "+String(item.reference)+
   " · "+String(item.document_count)+" · "+
   t(item.status==="recheck_required"?"reviewLinkStale":"reviewLinkPending");
  const btn=document.createElement("button");btn.type="button";btn.textContent=t("reviewGotoLinks");
  btn.addEventListener("click",()=>openPanel("lco-narrative"));li.append(btn);links.append(li);
 }
 for(const root of [documents,claims,links]){
  if(!root.children.length){const li=document.createElement("li");li.textContent=t("reviewNoEntries");root.append(li)}
 }
 el("lco-review-incomplete").textContent=queue.connection_scan_incomplete?t("reviewIncomplete"):"";

}
let reviewingClaim=false;
async function reviewClaim(claimId){
 if(reviewingClaim||!window.confirm(t("reviewConfirmClaim")))return;
 reviewingClaim=true;
 try{
  const response=await fetch("/api/review-claim",{
   method:"POST",headers:{"Content-Type":"application/json"},
   body:JSON.stringify({claim_id:claimId,status:"reviewed"})
  });
  const result=await response.json();
  if(!response.ok)throw Error(result.error||"HTTP "+response.status);
  el("lco-brief-message").textContent="";
  await refresh();
 }catch(error){el("lco-brief-message").textContent=t("reviewActionError")+String(error.message||error)}
 finally{reviewingClaim=false}
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
 '<details id="lco-brief-review"><summary data-brief-copy="reviewHeading"></summary>',
 '<p data-brief-copy="reviewLead"></p><p id="lco-review-count"></p>',
 '<h3 data-brief-copy="reviewDocs"></h3><ul class="lco-review-list" id="lco-review-docs"></ul>',
 '<h3 data-brief-copy="reviewClaims"></h3><ul class="lco-review-list" id="lco-review-claims"></ul>',
 '<h3 data-brief-copy="reviewConnections"></h3><ul class="lco-review-list" id="lco-review-links"></ul>',
 '<p id="lco-review-incomplete"></p></details>',
 '<details><summary data-brief-copy="waiting"></summary><ul id="lco-brief-steps"></ul></details>',
 '<details><summary data-brief-copy="dates"></summary><ul id="lco-brief-date-list"></ul>',
 '<p data-brief-copy="limit"></p></details>',
 '<details><summary data-brief-copy="types"></summary><ul id="lco-brief-type-list"></ul>',
 '<p data-brief-copy="typeLimit"></p></details>',
 '<details><summary data-brief-copy="ai"></summary><ul id="lco-brief-ai-list"></ul>',
 '<p data-brief-copy="aiLimit"></p><button type="button" id="lco-brief-ai-review" data-brief-copy="aiReview"></button></details>',
 '<p id="lco-brief-message" role="status" aria-live="polite"></p>'
 ].join("");
 home.querySelector(".lco-easy-intro")?.insertAdjacentElement("afterend",root);
 el("lco-brief-docs").addEventListener("click",()=>openPanel("lco-ws-documents"));
 el("lco-brief-timeline").addEventListener("click",()=>openPanel("lco-ws-timeline"));
 el("lco-brief-handoff").addEventListener("click",()=>openPanel("lco-ws-handoff"));
 el("lco-brief-ai-review").addEventListener("click",()=>{
  openPanel("lco-ws-technical");openPanel("lco-special-ai-pane");
 });
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
