"""A13 bounded source-coverage view on the existing case page.

UI only renders read-only case-local data after deliberate expansion. All
untrusted filenames and IDs use textContent, not HTML insertion.
"""
COVERAGE_CSS = r'''<style>
#lco-easy-home #lco-coverage{margin:14px 0 22px;padding:16px 18px;border:1px solid var(--lco-border,#857a70);border-radius:14px;background:var(--lco-panel,#171615)}
#lco-easy-home #lco-coverage>summary{font-size:1.1rem;font-weight:750;cursor:pointer;padding:7px 0}
#lco-easy-home #lco-coverage p{line-height:1.5}
#lco-easy-home #lco-coverage .lco-cov-list{list-style:none;padding:0;max-height:430px;overflow:auto}
#lco-easy-home #lco-coverage .lco-cov-list li{padding:9px 0;border-bottom:1px solid var(--lco-border,#7775);overflow-wrap:anywhere}
#lco-easy-home #lco-coverage .lco-cov-list small{display:block;opacity:.8;margin-top:3px}
#lco-easy-home #lco-coverage .lco-cov-links{display:flex;gap:9px;flex-wrap:wrap}
body.lco-light #lco-easy-home #lco-coverage{background:#fbf8f2}
</style>'''

COVERAGE_SCRIPT = r'''<script>
(function(){
"use strict";
const copy={
 de:{
 heading:"Quellenabdeckung – bekannte Akte prüfen",
 intro:"Diese Übersicht prüft nur bereits registrierte lokale Unterlagen. Sie kann nicht erkennen, welche Dokumente außerhalb dieser Akte fehlen.",
 count:"{n} registriert · {s} geprüft · {u} noch nicht gescannt · {t} mit überprüfbarem Text",
 warning:"Eine fehlende Textsuche ist nicht gleichbedeutend mit einer fehlenden Originaldatei. Auch vollständige lokale Nachweise beweisen nicht die Vollständigkeit des Falls.",
 statusHeading:"Original- und Textstatus",
 linksHeading:"Manuelle Verknüpfungen",
 unlinked:"ohne Dokumentbezug",unknown:"mit unbekannter Dokument-ID",
 noItems:"Keine registrierten Quellen in dieser Anzeige.",
 truncated:"Die Liste zeigt nur Beispiele; andere Quellen können unberücksichtigt bleiben.",
 openDocs:"Dokumentregister öffnen",openSearch:"Lokale Suche / Indizierung",openIntegrity:"Integrität ansehen",
 pending:"Bericht wird lokal zusammengestellt …",error:"Quellenbericht nicht verfügbar; es wurden keine Akten verändert.",
 label_timeline:"Chronologie",label_entities:"Beteiligte",label_tasks:"Aufgaben",label_claims:"Aussagen",
 state_source_text_available:"Original und Textindex geprüft – keine Tatsachenbestätigung",
 state_index_needed:"Original geprüft – kein gültiger lokaler Textindex",
 state_index_has_no_text:"Original geprüft – Textindex ohne durchsuchbaren Text",
 state_original_changed:"Original weicht vom gespeicherten Hash ab",
 state_original_missing:"Originaldatei nicht vorhanden",
 state_original_unavailable:"Originalpfad nicht prüfbar",
 state_provenance_unavailable:"Quellennachweis fehlt oder stimmt nicht überein",
 state_invalid_register_id:"Ungültige Dokument-ID im Register",
 state_verification_size_limit:"Datei überschreitet die Prüfgrenze – ungeprüft",
 state_extraction_size_limit:"Original geprüft – zu groß für lokale Textextraktion",
 state_unsupported_text_format:"Original geprüft – Textformat nicht unterstützt",
 unknownIds:"Manuelle Verweise auf unbekannte IDs (keine Feststellung fehlender Belege): ",
 more:"Es bestehen Anzeige- oder Prüfgrenzen; der Status bleibt unvollständig."
 },
 en:{
 heading:"Source coverage – inspect registered case materials",
 intro:"Only registered local sources are checked. This report cannot identify documents that were never supplied.",
 count:"{n} registered · {s} checked · {u} not scanned · {t} with verifiable searchable text",
 warning:"A missing text index does not mean the original is missing. Fully checked local sources do not prove the case file is complete.",
 statusHeading:"Original and text status",linksHeading:"Manual source links",
 unlinked:"without document link",unknown:"with unknown document ID",
 noItems:"No registered source appears in this view.",
 truncated:"This list shows samples only; additional sources may not be displayed.",
 openDocs:"Open document register",openSearch:"Local search / indexing",openIntegrity:"Inspect integrity",
 pending:"Preparing local coverage report …",error:"Coverage report unavailable; case records were not changed.",
 label_timeline:"Timeline",label_entities:"Participants",label_tasks:"Tasks",label_claims:"Claims",
 state_source_text_available:"Verified original and text index – not a factual finding",
 state_index_needed:"Verified original – no valid local text index",
 state_index_has_no_text:"Verified original – index contains no searchable text",
 state_original_changed:"Original does not match stored SHA-256",
 state_original_missing:"Original is missing",
 state_original_unavailable:"Original path cannot be inspected",
 state_provenance_unavailable:"Source provenance missing or inconsistent",
 state_invalid_register_id:"Invalid register document ID",
 state_verification_size_limit:"File exceeds verification size limit – unchecked",
 state_extraction_size_limit:"Verified original – too large for local extraction",
 state_unsupported_text_format:"Verified original – unsupported text format",
 unknownIds:"Manual references to unknown IDs (not proof of missing evidence): ",
 more:"Display or scanning limits apply; coverage remains incomplete."
 }
};
const el=id=>document.getElementById(id);
const t=key=>(String(localStorage.getItem("local_case_organizer_ui_lang")||"de").startsWith("de")?copy.de:copy.en)[key]||key;
let data=null,loading=false,failed=false;
function render(){
 const panel=el("lco-coverage");if(!panel)return;
 panel.querySelectorAll("[data-cov-copy]").forEach(node=>node.textContent=t(node.dataset.covCopy));
 const status=el("lco-cov-status");
 status.textContent=loading?t("pending"):failed?t("error"):"";
 if(!data)return;
 const counts=data.counts||{};
 el("lco-cov-count").textContent=Object.entries({
  n:data.total_registered||0,s:data.scanned||0,u:data.not_scanned||0,
  t:counts.source_text_available||0
 }).reduce((s,[key,value])=>s.replace("{"+key+"}",String(value)),t("count"));
 const list=el("lco-cov-sources");list.replaceChildren();
 for(const item of (data.source_samples||[])){
  const li=document.createElement("li");
  li.textContent=String(item.original_name||item.file_id)+" ("+String(item.file_id)+")";
  const small=document.createElement("small");
  small.textContent=t("state_"+String(item.status));
  li.append(small);list.append(li);
 }
 if(!list.children.length){
  const li=document.createElement("li");li.textContent=t("noItems");list.append(li);
 }
 const links=el("lco-cov-links");links.replaceChildren();
 for(const [name,row] of Object.entries(data.manual_links?.areas||{})){
  const li=document.createElement("li");
  li.textContent=t("label_"+name)+": "+String(row.without_document_link||0)+
   " "+t("unlinked")+" · "+String(row.with_unknown_document_link||0)+
   " "+t("unknown");
  links.append(li);
 }
 if(!links.children.length){
  const li=document.createElement("li");li.textContent=t("noItems");links.append(li);
 }
 const unknown=data.manual_links?.unknown_document_ids||[];
 el("lco-cov-unknown").textContent=unknown.length?t("unknownIds")+unknown.join(", "):"";
 el("lco-cov-limit").textContent=(data.not_scanned||data.sample_truncated||
  data.manual_links?.unknown_ids_truncated)?t("more"):"";
}
async function refresh(){
 if(loading)return;
 loading=true;failed=false;render();
 try{
  const response=await fetch("/api/case-coverage");
  const result=await response.json();
  if(!response.ok)throw Error("HTTP "+response.status);
  data=result;
 }catch(error){console.warn("Local coverage unavailable",error);failed=true;data=null}
 finally{loading=false;render()}
}
function openExisting(id){
 const node=el(id);
 if(node){node.open=true;node.scrollIntoView({block:"start",behavior:"smooth"})}
}
function init(){
 const briefing=el("lco-briefing");
 if(!briefing||el("lco-coverage"))return;
 const box=document.createElement("details");box.id="lco-coverage";
 box.innerHTML=[
 '<summary data-cov-copy="heading"></summary>',
 '<p data-cov-copy="intro"></p><p id="lco-cov-status" aria-live="polite"></p>',
 '<p id="lco-cov-count"></p>',
 '<div class="lco-cov-links">',
 '<button type="button" id="lco-cov-docs" data-cov-copy="openDocs"></button>',
 '<button type="button" id="lco-cov-search" data-cov-copy="openSearch"></button>',
 '<button type="button" id="lco-cov-integrity" data-cov-copy="openIntegrity"></button></div>',
 '<h3 data-cov-copy="statusHeading"></h3><ul class="lco-cov-list" id="lco-cov-sources"></ul>',
 '<h3 data-cov-copy="linksHeading"></h3><ul class="lco-cov-list" id="lco-cov-links"></ul>',
 '<p id="lco-cov-unknown"></p><p id="lco-cov-limit"></p>',
 '<p data-cov-copy="warning"></p>'
 ].join("");
 briefing.insertAdjacentElement("afterend",box);
 el("lco-cov-docs").addEventListener("click",()=>openExisting("lco-ws-documents"));
 el("lco-cov-search").addEventListener("click",()=>openExisting("lco-ws-search"));
 el("lco-cov-integrity").addEventListener("click",()=>openExisting("lco-ws-integrity"));
 box.addEventListener("toggle",()=>{if(box.open)refresh()});
 const oldCopy=window.LCOApplyExtraCopy;
 window.LCOApplyExtraCopy=function(){if(typeof oldCopy==="function")oldCopy();render()};
 const oldRefresh=window.LCORefreshWorkspace;
 window.LCORefreshWorkspace=async function(){
  if(typeof oldRefresh==="function")await oldRefresh();
  if(box.open)await refresh();
 };
 render();
}
document.addEventListener("DOMContentLoaded",init);
})();
</script>'''
