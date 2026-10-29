"""Optional expert workflows inside the same local one-page interface.

All operations delegate to the existing backend and remain user-initiated.
The whole specialist section starts collapsed in the simple workspace.
"""
SPECIALIST_CSS = r'''<style>
#lco-easy-home .lco-special-pane{margin:12px 0;border:1px solid var(--lco-border,#7775);border-radius:10px}
#lco-easy-home .lco-special-pane>summary{padding:14px 12px;font-weight:650;cursor:pointer}
#lco-easy-home .lco-special-content{padding:10px 15px 18px}
#lco-easy-home .lco-special-content p{line-height:1.6}
#lco-easy-home .lco-special-content label{display:block;margin:10px 0}
#lco-easy-home .lco-special-content input:not([type=checkbox]),
#lco-easy-home .lco-special-content select,#lco-easy-home .lco-special-content textarea{display:block;margin-top:5px;width:100%;max-width:100%;box-sizing:border-box}
#lco-easy-home .lco-special-content button{font-size:.92rem;padding:10px 13px;margin:5px 8px 5px 0}
#lco-easy-home .lco-special-list{list-style:none;margin:10px 0;padding:0}
#lco-easy-home .lco-special-list li{padding:10px 0;border-bottom:1px solid var(--lco-border,#7775);overflow-wrap:anywhere}
#lco-easy-home .lco-special-list small{display:block;opacity:.75;margin:6px 0}
#lco-easy-home .lco-special-msg{min-height:20px;overflow-wrap:anywhere}
#lco-easy-home .lco-special-msg[data-error=true]{color:#e6a692}
body.lco-light #lco-easy-home .lco-special-msg[data-error=true]{color:#8c3223}
</style>'''
SPECIALIST_SCRIPT = r'''<script>
(function(){
"use strict";
const I={
 de:{
  claims:"Aussagen aus Quellen",claimsHelp:"Aussagen sind menschliche Interpretationen. Ein wörtliches Zitat aus einer lokal indizierten Quelle ist Pflicht.",
  claimSource:"Dokument",page:"Seite",quote:"Wörtliches Quellenzitat",statement:"Eigene Aussage / Interpretation",
  claimAdd:"Aussagenentwurf erfassen",claimReload:"Aussagen anzeigen",claimSaved:"Entwurf gespeichert. Keine Aussage wurde automatisch bestätigt.",
  claimEmpty:"Noch keine Aussagen.",status:"Prüfstatus",draft:"Entwurf",needs_review:"Prüfung nötig",reviewed:"Manuell geprüft",update:"Status aktualisieren",
  compare:"Angaben vergleichen",compareHelp:"Vergleiche sind nur Prüfhinweise, keine automatisch erkannten Wahrheiten.",
  compareClaim:"Aussage",compareTopic:"Gemeinsames Thema (klein geschrieben)",compareType:"Wertart",compareValue:"Wert",
  date:"Datum",amount:"Betrag",text:"Text",compareAdd:"Wert zuordnen",compareReload:"Vergleiche laden",compareEmpty:"Keine möglichen Abweichungen gefunden.",
  ai:"Optionaler KI-Austausch",aiHelp:"Kein eingebautes Modell und kein Versand. Ein Paket mit privaten Textauszügen wird nur nach Zustimmung lokal gespeichert.",
  aiSource:"Indiziertes Dokument",aiMake:"Lokales Paket vorbereiten",aiConfirm:"Die gewählte Quelle kann private Textauszüge enthalten. Lokal ein KI-Übergabepaket erstellen?",
  aiMade:"Lokales Paket gespeichert: ",aiResponse:"Antwort-JSON von einer bewusst gewählten lokalen KI",
  aiImport:"Vorschläge als ungeprüft importieren",aiReload:"Vorschläge prüfen",aiNone:"Keine ungeprüften Vorschläge.",
  aiDraft:"Als Aussagenentwurf übernehmen",aiReject:"Ablehnen",aiWarning:"KI-Vorschläge sind keine verifizierten Fakten. Jede Übernahme ist einzeln zu bestätigen.",
  aiActionConfirm:"Diesen KI-Vorschlag bewusst als ungeprüften Aussagenentwurf übernehmen?",
  audit:"Prüfjournal",auditHelp:"Gespeicherte Änderungs- und Integritätsnachweise, ohne Dokumentinhalte anzuzeigen.",
  auditLoad:"Prüfjournal anzeigen",auditEmpty:"Keine protokollierten Änderungen.",
  ocr:"Optionales Offline-OCR",ocrHelp:"OCR ist niemals automatisch. Es benötigt lokal installierte Werkzeuge und wird nur für das gewählte Dokument ausgelöst.",
  ocrStart:"Ausgewähltes Dokument jetzt lokal mit OCR indizieren",ocrConfirm:"OCR nur lokal für dieses Dokument starten? Ergebnis ist ein Arbeitsindex, Originale bleiben unverändert.",
  done:"Vorgang abgeschlossen.",fail:"Vorgang fehlgeschlagen: ",choose:"Dokument wählen"
 },
 en:{
  claims:"Source-linked claims",claimsHelp:"Claims are human interpretations. An exact quote from an indexed local source is required.",
  claimSource:"Document",page:"Page",quote:"Exact source quote",statement:"Your statement / interpretation",
  claimAdd:"Create draft claim",claimReload:"Show claims",claimSaved:"Draft saved. No claim was automatically confirmed.",
  claimEmpty:"No claims yet.",status:"Review status",draft:"Draft",needs_review:"Needs review",reviewed:"Manually reviewed",update:"Update status",
  compare:"Compare statements",compareHelp:"Comparisons are review hints, not automatically determined truth.",
  compareClaim:"Claim",compareTopic:"Shared topic (lowercase)",compareType:"Value type",compareValue:"Value",
  date:"Date",amount:"Amount",text:"Text",compareAdd:"Assign value",compareReload:"Load comparisons",compareEmpty:"No potential discrepancies found.",
  ai:"Optional AI exchange",aiHelp:"No built-in model or transmission. A packet containing private text excerpts is written locally only after confirmation.",
  aiSource:"Indexed document",aiMake:"Prepare local packet",aiConfirm:"The selected source may include private text excerpts. Create a local AI handoff packet?",
  aiMade:"Local packet saved: ",aiResponse:"Response JSON from an intentionally selected local assistant",
  aiImport:"Import suggestions as unreviewed",aiReload:"Review suggestions",aiNone:"No pending suggestions.",
  aiDraft:"Create draft claim",aiReject:"Reject",aiWarning:"AI suggestions are not verified facts. Each promotion requires an individual decision.",
  aiActionConfirm:"Explicitly promote this AI suggestion to an unreviewed draft claim?",
  audit:"Verification journal",auditHelp:"Saved change and integrity records without exposing document contents.",
  auditLoad:"Show audit history",auditEmpty:"No logged changes.",
  ocr:"Optional offline OCR",ocrHelp:"OCR never starts automatically. It requires installed local tools and only affects the selected document.",
  ocrStart:"Index this document locally using OCR",ocrConfirm:"Start local-only OCR for this document? Only a working index is created; originals remain unchanged.",
  done:"Action completed.",fail:"Action failed: ",choose:"Choose document"
 }
};
const el=id=>document.getElementById(id);
const t=key=>(String(localStorage.getItem("local_case_organizer_ui_lang")||"de").startsWith("de")?I.de:I.en)[key]||key;
const node=(tag,val)=>{const x=document.createElement(tag);if(val!=null)x.textContent=String(val);return x};
async function request(path,payload){
 const options=payload===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)};
 const response=await fetch(path,options);const data=await response.json();
 if(!response.ok)throw new Error(data.error||"HTTP "+response.status);
 return data;
}
function status(id,val,error=false){
 const target=el(id);if(target){target.dataset.error=String(error);target.textContent=val}
}
function localized(){
 document.querySelectorAll("#lco-special-root [data-special-copy]").forEach(n=>n.textContent=t(n.dataset.specialCopy));
}
function selectDoc(id,rows){
 const pick=el(id);if(!pick)return;
 const before=pick.value;pick.replaceChildren();
 const empty=node("option",t("choose"));empty.value="";pick.append(empty);
 rows.forEach(row=>{const option=node("option",row.original_name||row.file_id);option.value=row.file_id;pick.append(option)});
 pick.value=rows.some(r=>r.file_id===before)?before:"";
}
async function docs(){
 const data=await request("/api/register-data");
 const rows=(data.rows||[]).filter(r=>r.file_id);
 selectDoc("lco-special-claim-file",rows);
 selectDoc("lco-special-ai-file",rows);
 selectDoc("lco-special-ocr-file",rows);
}
async function loadClaims(){
 const response=await request("/api/claims");
 const root=el("lco-special-claims");root.replaceChildren();
 const rows=response.claims||[];
 const picker=el("lco-special-compare-claim");picker.replaceChildren();
 const empty=node("option",t("claimEmpty"));empty.value="";picker.append(empty);
 for(const item of rows.slice(-100)){
  const choice=node("option",item.claim_id+" · "+item.file_id);choice.value=item.claim_id;picker.append(choice);
  const li=node("li"),strong=node("strong",item.statement);
  const small=node("small",item.claim_id+" · "+item.file_id+" · "+t("page")+" "+item.source_page+" · "+item.source_quote);
  const label=node("label",t("status")),select=node("select");
  for(const state of ["draft","needs_review","reviewed"]){
   const option=node("option",t(state));option.value=state;option.selected=state===item.review_status;select.append(option);
  }
  const button=node("button",t("update"));button.type="button";
  button.addEventListener("click",async()=>{
   button.disabled=true;
   try{await request("/api/review-claim",{claim_id:item.claim_id,status:select.value});await loadClaims()}
   catch(e){status("lco-special-claim-msg",t("fail")+e.message,true);button.disabled=false}
  });
  label.append(select);li.append(strong,small,label,button);root.append(li);
 }
 if(!rows.length)root.append(node("li",t("claimEmpty")));
}
async function loadComparisons(){
 const report=await request("/api/claim-comparisons");
 const root=el("lco-special-comparisons");root.replaceChildren();
 for(const row of report.review_candidates||[]){
  const li=node("li"),strong=node("strong",row.topic+" · "+row.kind);
  const desc=node("small",(row.sources||[]).map(x=>x.file_id+": "+x.value).join(" | "));
  li.append(strong,desc);root.append(li);
 }
 if(!root.children.length)root.append(node("li",t("compareEmpty")));
}
async function loadSuggestions(){
 const data=await request("/api/ai-suggestions");
 const root=el("lco-special-suggestions");root.replaceChildren();
 for(const suggestion of (data.suggestions||[]).filter(x=>x.status==="pending_review").slice(0,60)){
  const li=node("li"),strong=node("strong",suggestion.statement);
  const small=node("small",suggestion.file_id+" · "+t("page")+" "+suggestion.page+" · "+suggestion.source_quote);
  li.append(strong,small);
  for(const [decision,label] of [["reject","aiReject"],["create_draft_claim","aiDraft"]]){
   const button=node("button",t(label));button.type="button";
   button.addEventListener("click",async()=>{
    if(decision==="create_draft_claim"&&!window.confirm(t("aiActionConfirm")))return;
    button.disabled=true;
    try{await request("/api/review-ai-suggestion",{suggestion_id:suggestion.suggestion_id,decision});
     await loadSuggestions();await loadClaims();
    }catch(e){status("lco-special-ai-msg",t("fail")+e.message,true);button.disabled=false}
   });li.append(button);
  }
  root.append(li);
 }
 if(!root.children.length)root.append(node("li",t("aiNone")));
}
function bind(){
 el("lco-special-claim-form").addEventListener("submit",async event=>{
  event.preventDefault();const button=el("lco-special-claim-add");button.disabled=true;
  try{
   await request("/api/add-claim",{
    file_id:el("lco-special-claim-file").value,page:Number(el("lco-special-claim-page").value),
    quote:el("lco-special-claim-quote").value,statement:el("lco-special-claim-statement").value
   });
   status("lco-special-claim-msg",t("claimSaved"));
   await loadClaims();
  }catch(e){status("lco-special-claim-msg",t("fail")+e.message,true)}
  finally{button.disabled=false}
 });
 el("lco-special-claims-reload").addEventListener("click",()=>loadClaims().catch(console.warn));
 el("lco-special-compare-form").addEventListener("submit",async event=>{
  event.preventDefault();const button=el("lco-special-compare-add");button.disabled=true;
  try{await request("/api/add-comparison",{
   claim_id:el("lco-special-compare-claim").value,
   topic:el("lco-special-compare-topic").value.trim(),
   kind:el("lco-special-compare-kind").value,
   value:el("lco-special-compare-value").value
  });
  status("lco-special-compare-msg",t("done"));await loadComparisons()}
  catch(e){status("lco-special-compare-msg",t("fail")+e.message,true)}
  finally{button.disabled=false}
 });
 el("lco-special-comparisons-reload").addEventListener("click",()=>loadComparisons().catch(console.warn));
 el("lco-special-ai-make").addEventListener("click",async()=>{
  if(!window.confirm(t("aiConfirm")))return;
  const button=el("lco-special-ai-make");button.disabled=true;
  try{const result=await request("/api/prepare-ai-review",{file_ids:[el("lco-special-ai-file").value]});
   status("lco-special-ai-msg",t("aiMade")+result.path)}
  catch(e){status("lco-special-ai-msg",t("fail")+e.message,true)}
  finally{button.disabled=false}
 });
 el("lco-special-ai-import").addEventListener("click",async()=>{
  const button=el("lco-special-ai-import");button.disabled=true;
  try{
   const response=JSON.parse(el("lco-special-ai-json").value);
   await request("/api/import-ai-review",response);
   status("lco-special-ai-msg",t("done"));await loadSuggestions()
  }catch(e){status("lco-special-ai-msg",t("fail")+e.message,true)}
  finally{button.disabled=false}
 });
 el("lco-special-ai-reload").addEventListener("click",()=>loadSuggestions().catch(console.warn));
 el("lco-special-audit-load").addEventListener("click",async()=>{
  const root=el("lco-special-audit-list");root.replaceChildren();
  try{
   const [audits,checks]=await Promise.all([request("/api/audit-history"),request("/api/integrity-history")]);
   for(const row of (audits.changes||[]).slice(0,25)){
    const li=node("li",row.at+" · "+row.area+" · "+row.row_count);root.append(li);
   }
   for(const item of (checks.runs||[]).slice(0,10)){
    root.append(node("li",item.at+" · SHA-256 · "+item.checked));
   }
   if(!root.children.length)root.append(node("li",t("auditEmpty")));
  }catch(e){root.append(node("li",t("fail")+e.message))}
 });
 el("lco-special-ocr-start").addEventListener("click",async()=>{
  if(!window.confirm(t("ocrConfirm")))return;
  const button=el("lco-special-ocr-start");button.disabled=true;
  try{await request("/api/index-document",{file_id:el("lco-special-ocr-file").value,use_ocr:true});
   status("lco-special-ocr-msg",t("done"))}
  catch(e){status("lco-special-ocr-msg",t("fail")+e.message,true)}
  finally{button.disabled=false}
 });
 for(const id of ["lco-special-claims-pane","lco-special-ai-pane","lco-special-ocr-pane"]){
  el(id).addEventListener("toggle",()=>{if(el(id).open)docs().catch(console.warn)});
 }
 el("lco-special-claims-pane").addEventListener("toggle",()=>{if(el("lco-special-claims-pane").open)loadClaims().catch(console.warn)});
 el("lco-special-ai-pane").addEventListener("toggle",()=>{if(el("lco-special-ai-pane").open)loadSuggestions().catch(console.warn)});
 el("lco-special-comparisons-pane").addEventListener("toggle",()=>{if(el("lco-special-comparisons-pane").open)loadComparisons().catch(console.warn)});
}
function init(){
 const root=el("lco-ws-technical")?.querySelector(".lco-ws-body");
 if(!root||el("lco-special-root"))return;
 const pane=document.createElement("div");pane.id="lco-special-root";
 pane.innerHTML=[
 '<details class="lco-special-pane" id="lco-special-claims-pane"><summary data-special-copy="claims"></summary><div class="lco-special-content">',
 '<p data-special-copy="claimsHelp"></p><form id="lco-special-claim-form">',
 '<label><span data-special-copy="claimSource"></span><select id="lco-special-claim-file" required></select></label>',
 '<label><span data-special-copy="page"></span><input type="number" id="lco-special-claim-page" min="1" max="100" value="1" required></label>',
 '<label><span data-special-copy="quote"></span><textarea id="lco-special-claim-quote" minlength="4" maxlength="500" required></textarea></label>',
 '<label><span data-special-copy="statement"></span><textarea id="lco-special-claim-statement" minlength="4" maxlength="800" required></textarea></label>',
 '<button type="submit" id="lco-special-claim-add" data-special-copy="claimAdd"></button>',
 '<button type="button" id="lco-special-claims-reload" data-special-copy="claimReload"></button></form>',
 '<p class="lco-special-msg" id="lco-special-claim-msg" aria-live="polite"></p><ul class="lco-special-list" id="lco-special-claims"></ul>',
 '</div></details>',
 '<details class="lco-special-pane" id="lco-special-comparisons-pane"><summary data-special-copy="compare"></summary><div class="lco-special-content">',
 '<p data-special-copy="compareHelp"></p><form id="lco-special-compare-form">',
 '<label><span data-special-copy="compareClaim"></span><select id="lco-special-compare-claim" required></select></label>',
 '<label><span data-special-copy="compareTopic"></span><input type="text" id="lco-special-compare-topic" pattern="[a-z0-9][a-z0-9_-]*" maxlength="64" required></label>',
 '<label><span data-special-copy="compareType"></span><select id="lco-special-compare-kind">',
 '<option value="text" data-special-copy="text"></option><option value="date" data-special-copy="date"></option><option value="amount" data-special-copy="amount"></option></select></label>',
 '<label><span data-special-copy="compareValue"></span><input id="lco-special-compare-value" type="text" maxlength="120" required></label>',
 '<button type="submit" id="lco-special-compare-add" data-special-copy="compareAdd"></button>',
 '<button type="button" id="lco-special-comparisons-reload" data-special-copy="compareReload"></button></form>',
 '<p class="lco-special-msg" id="lco-special-compare-msg" aria-live="polite"></p>',
 '<ul class="lco-special-list" id="lco-special-comparisons"></ul></div></details>',
 '<details class="lco-special-pane" id="lco-special-ai-pane"><summary data-special-copy="ai"></summary><div class="lco-special-content">',
 '<p data-special-copy="aiHelp"></p><p data-special-copy="aiWarning"></p>',
 '<label><span data-special-copy="aiSource"></span><select id="lco-special-ai-file"></select></label>',
 '<button type="button" id="lco-special-ai-make" data-special-copy="aiMake"></button>',
 '<label><span data-special-copy="aiResponse"></span><textarea id="lco-special-ai-json" maxlength="110000" rows="4"></textarea></label>',
 '<button type="button" id="lco-special-ai-import" data-special-copy="aiImport"></button>',
 '<button type="button" id="lco-special-ai-reload" data-special-copy="aiReload"></button>',
 '<p class="lco-special-msg" id="lco-special-ai-msg" aria-live="polite"></p>',
 '<ul class="lco-special-list" id="lco-special-suggestions"></ul></div></details>',
 '<details class="lco-special-pane" id="lco-special-ocr-pane"><summary data-special-copy="ocr"></summary><div class="lco-special-content">',
 '<p data-special-copy="ocrHelp"></p><label><span data-special-copy="claimSource"></span><select id="lco-special-ocr-file"></select></label>',
 '<button type="button" id="lco-special-ocr-start" data-special-copy="ocrStart"></button>',
 '<p class="lco-special-msg" id="lco-special-ocr-msg" aria-live="polite"></p></div></details>',
 '<details class="lco-special-pane" id="lco-special-audit-pane"><summary data-special-copy="audit"></summary><div class="lco-special-content">',
 '<p data-special-copy="auditHelp"></p><button type="button" id="lco-special-audit-load" data-special-copy="auditLoad"></button>',
 '<ul class="lco-special-list" id="lco-special-audit-list"></ul></div></details>'
 ].join("");
 root.insertBefore(pane,root.lastElementChild);
 localized();bind();
 const prior=window.LCOApplyExtraCopy;
 window.LCOApplyExtraCopy=function(){if(typeof prior==="function")prior();localized()};
}
document.addEventListener("DOMContentLoaded",init);
})();
</script>'''
