const $=id=>document.getElementById(id);
function params(extra={}){const q=new URLSearchParams();for(const id of ['date_from','date_to','fw']){const el=$(id);if(el&&el.value.trim())q.set(id,el.value.trim())}Object.entries(extra).forEach(([k,v])=>{if(v)q.set(k,v)});return q.toString()}
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function setState(text,error=false){const el=$('state');if(!el)return;el.className=error?'error':'loading';el.textContent=text}
function fmt(v){if(v===undefined||v===null||v==='')return '--';const n=Number(String(v).replace(/[,%]/g,''));return Number.isFinite(n)&&!String(v).includes('%')?n.toLocaleString():String(v)}
function table(rows,limit=100){if(!rows||!rows.length)return '<div class="empty">没有可展示的结构化行；可查看原始 MCP 响应。</div>';const cols=[...new Set(rows.slice(0,20).flatMap(Object.keys))].slice(0,12);return `<div class="table-wrap"><table><thead><tr>${cols.map(c=>`<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${rows.slice(0,limit).map(r=>`<tr>${cols.map(c=>`<td>${esc(r[c])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`}
function raw(text){return `<pre class="raw">${esc(text||'')}</pre>`}
async function getJSON(url){const r=await fetch(url);const j=await r.json().catch(()=>({}));if(!r.ok||j.success===false)throw new Error(j.error||`HTTP ${r.status}`);return j}
function bindReload(fn){$('reload').onclick=fn;['date_from','date_to','fw'].forEach(id=>{const el=$(id);if(el)el.addEventListener('change',fn)})}
