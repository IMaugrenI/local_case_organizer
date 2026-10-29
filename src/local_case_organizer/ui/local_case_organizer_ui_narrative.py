"""Read-only chronological case work summary on the existing simple page.

Untrusted source text is always rendered with textContent; the panel makes no
automatic claims or changes and loads only when expanded.
"""
NARRATIVE_CSS = r'''<style>
#lco-easy-home #lco-narrative{margin:14px 0 22px;padding:16px 18px;border:1px solid var(--lco-border,#857a70);border-radius:14px;background:var(--lco-panel,#171615)}
#lco-easy-home #lco-narrative>summary{font-size:1.16rem;font-weight:750;cursor:pointer;padding:7px 0}
#lco-easy-home #lco-narrative>p{line-height:1.55;opacity:.86}
#lco-easy-home .lco-narrative-section{border-top:1px solid var(--lco-border,#857a70);padding:14px 0 5px}
#lco-easy-home .lco-narrative-section>h3{font-size:1.05rem;margin:0 0 5px}
#lco-easy-home .lco-narrative-list{list-style:none;margin:7px 0;padding:0}
#lco-easy-home .lco-narrative-list>li{padding:10px 0;border-bottom:1px solid var(--lco-border,#857a70);overflow-wrap:anywhere;line-height:1.5}
#lco-easy-home .lco-narrative-list>li:last-child{border:0}
#lco-easy-home .lco-narrative-list small{display:block;opacity:.78;margin:4px 0}
body.lco-light #lco-easy-home #lco-narrative{background:#fbf8f2}
</style>'''

NARRATIVE_SCRIPT = r'''<script>
(function(){
"use strict";
const I={
 de:{
  heading:"Sachverhalt – automatisch geordneter Arbeitsstand",
  intro:"Quellenbelegte Datumsnennungen, manuelle Einträge, Beteiligte und mögliche Wertabweichungen an einer Stelle. Nichts davon gilt ohne fachliche Prüfung als bewiesen.",
  count:"{n} chronologische Einträge · {p} Beteiligte · {d} mögliche Abweichungen",
  chronology:"Chronologischer Arbeitsstand",people:"Manuell erfasste Beteiligte",
  differences:"Mögliche Wertabweichungen (keine bewiesenen Widersprüche)",
  questions:"Offene Fragen für die Prüfung",
  empty:"Keine quellenbezogenen Einträge vorhanden.",
  recorded:"Manuell erfasst, nicht automatisch verifiziert",
  mentioned:"Datumsnennung aus überprüfter Quelle – kein bestätigtes Ereignis",
  page:"Seite",line:"Zeile",source:"Quelle",
  error:"Die Sachverhaltsübersicht konnte nicht geladen werden. Die Unterlagen bleiben unverändert.",
  loading:"Sachverhaltsübersicht wird zusammengestellt …",
  scope:"Die Übersicht ist begrenzt; fehlende Einträge beweisen keine Vollständigkeit. Im Anwalts-Export erscheinen nur ausdrücklich ausgewählte Originalquellen."
 },
 en:{
  heading:"Case narrative – automatically ordered working draft",
  intro:"Source-linked date mentions, manual entries, participants and potential value differences in one place. None is an established fact without professional review.",
  count:"{n} chronological entries · {p} participants · {d} possible differences",
  chronology:"Chronological working draft",people:"Manually entered participants",
  differences:"Potential differences (not proven contradictions)",
  questions:"Open questions for review",
  empty:"No source-linked entries available.",
  recorded:"Entered manually; not automatically verified",
  mentioned:"Date mention in verified original – not an established event",
  page:"Page",line:"Line",source:"Source",
  error:"The case narrative could not be loaded. Existing documents remain untouched.",
  loading:"Preparing source-grounded overview …",
  scope:"This overview is bounded. Missing entries do not prove completeness. The lawyer handoff only contains explicitly selected originals."
 }
};
const el=id=>document.getElementById(id);
const t=key=>(String(localStorage.getItem("local_case_organizer_ui_lang")||"de").startsWith("de")?I.de:I.en)[key]||key;
const fmt=(name,data)=>Object.entries(data||{}).reduce((s,[k,v])=>s.replace("{"+k+"}",String(v)),t(name));
let cached=null,loading=false,failed=false;
function li(root,title,description){
 const item=document.createElement("li");
 const strong=document.createElement("strong");strong.textContent=String(title||"");
 item.append(strong);
 if(description){const small=document.createElement("small");small.textContent=String(description);item.append(small)}
 root.append(item);
}
function populate(){
 const panel=el("lco-narrative");if(!panel)return;
 panel.querySelectorAll("[data-narr-copy]").forEach(n=>n.textContent=t(n.dataset.narrCopy));
 const status=el("lco-narr-status");
 status.textContent=loading?t("loading"):failed?t("error"):"";
 if(!cached)return;
 const data=cached;
 el("lco-narr-count").textContent=fmt("count",{
  n:data.counts?.chronology_items||0,p:data.counts?.participants||0,
  d:data.counts?.potential_value_differences||0
 });
 const chrono=el("lco-narr-chronology");chrono.replaceChildren();
 for(const event of (data.chronology||[]).slice(0,80)){
  const kind=event.source_kind==="verified_source_date_mention_not_an_event"?t("mentioned"):t("recorded");
  const location=event.page==null?"":", "+t("page")+" "+event.page+", "+t("line")+" "+event.line;
  li(chrono, String(event.date)+" · "+String(event.title),
    kind+" · "+t("source")+": "+(event.file_ids||[]).join(", ")+location+
    (event.excerpt?" · "+event.excerpt:""));
 }
 const people=el("lco-narr-people");people.replaceChildren();
 for(const person of (data.participants||[]).slice(0,60)){
  li(people,person.name||"–",(person.role||"")+" · "+t("source")+": "+
   (person.file_ids||[]).join(", "));
 }
 const diff=el("lco-narr-differences");diff.replaceChildren();
 for(const item of (data.potential_differences||[]).slice(0,20)){
  li(diff,String(item.topic)+" ("+item.kind+")",
    (item.sources||[]).map(x=>x.file_id+" / "+t("page")+" "+x.page+
     " / "+x.value+" / "+x.quote).join(" · "));
 }
 const questions=el("lco-narr-questions");questions.replaceChildren();
 for(const item of (data.open_questions||[]).slice(0,9)){
  li(questions,item.text,item.basis);
 }
 for(const root of [chrono,people,diff,questions]){
  if(!root.children.length)li(root,t("empty"),"");
 }
}
async function refresh(){
 if(loading)return;
 loading=true;failed=false;populate();
 try{
  const response=await fetch("/api/case-narrative");
  const payload=await response.json();
  if(!response.ok)throw Error("HTTP "+response.status);
  cached=payload;failed=false;
 }catch(error){console.warn("Source narrative unavailable",error);failed=true}
 finally{loading=false;populate()}
}
function init(){
 const briefing=el("lco-briefing");if(!briefing||el("lco-narrative"))return;
 const box=document.createElement("details");box.id="lco-narrative";
 box.innerHTML=[
  '<summary data-narr-copy="heading"></summary>',
  '<p data-narr-copy="intro"></p><p id="lco-narr-status" aria-live="polite"></p>',
  '<p id="lco-narr-count"></p>',
  '<section class="lco-narrative-section"><h3 data-narr-copy="chronology"></h3>',
  '<ul class="lco-narrative-list" id="lco-narr-chronology"></ul></section>',
  '<section class="lco-narrative-section"><h3 data-narr-copy="people"></h3>',
  '<ul class="lco-narrative-list" id="lco-narr-people"></ul></section>',
  '<section class="lco-narrative-section"><h3 data-narr-copy="differences"></h3>',
  '<ul class="lco-narrative-list" id="lco-narr-differences"></ul></section>',
  '<section class="lco-narrative-section"><h3 data-narr-copy="questions"></h3>',
  '<ul class="lco-narrative-list" id="lco-narr-questions"></ul></section>',
  '<p data-narr-copy="scope"></p>'
 ].join("");
 briefing.insertAdjacentElement("afterend",box);
 box.addEventListener("toggle",()=>{if(box.open)refresh()});
 const originalCopy=window.LCOApplyExtraCopy;
 window.LCOApplyExtraCopy=function(){
  if(typeof originalCopy==="function")originalCopy();populate();
 };
 const originalRefresh=window.LCORefreshWorkspace;
 window.LCORefreshWorkspace=async function(){
  if(typeof originalRefresh==="function")await originalRefresh();
  if(box.open)await refresh();
 };
 populate();
}
document.addEventListener("DOMContentLoaded",init);
})();
</script>'''
