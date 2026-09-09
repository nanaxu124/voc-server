(function(){
  const KEY='voc-dashboard-state-v1';
  const DEFAULT_STATE={
    npi:'FY25 Fall NPI',
    product:'iPhone 17 Series',
    fw:'',
    date_from:'',
    date_to:'',
    npi_sublobs:[],
    n1_sublobs:[]
  };
  const ARRAY_KEYS=new Set(['npi_sublobs','n1_sublobs']);

  function clone(v){return JSON.parse(JSON.stringify(v));}
  function normalize(state){
    const out={...clone(DEFAULT_STATE),...(state||{})};
    for(const key of ARRAY_KEYS){
      const value=out[key];
      out[key]=Array.isArray(value)?value.filter(Boolean):String(value||'').split(',').map(x=>x.trim()).filter(Boolean);
    }
    return out;
  }
  function readStored(){
    try{return normalize(JSON.parse(localStorage.getItem(KEY)||'{}'));}
    catch(_){return clone(DEFAULT_STATE);}
  }
  function read(){
    const state=readStored();
    const params=new URLSearchParams(location.search);
    for(const key of Object.keys(DEFAULT_STATE)){
      if(!params.has(key)) continue;
      state[key]=ARRAY_KEYS.has(key)?params.get(key).split(',').map(x=>x.trim()).filter(Boolean):params.get(key);
    }
    return normalize(state);
  }
  function save(patch){
    const next=normalize({...readStored(),...(patch||{})});
    localStorage.setItem(KEY,JSON.stringify(next));
    return next;
  }
  function toQuery(state, keys){
    const source=normalize(state||readStored());
    const params=new URLSearchParams();
    const use=keys||Object.keys(DEFAULT_STATE);
    for(const key of use){
      const value=source[key];
      if(Array.isArray(value)){if(value.length)params.set(key,value.join(','));}
      else if(value)params.set(key,value);
    }
    return params;
  }
  function notify(patch){
    const next=save(patch);
    if(window.parent!==window){
      window.parent.postMessage({type:'voc-dashboard-state',patch:patch||{},state:next},location.origin);
    }
    return next;
  }
  function notifyMeta(text){
    if(window.parent!==window){
      window.parent.postMessage({type:'voc-dashboard-meta',text:String(text||'')},location.origin);
    }
  }
  function ensureOption(select,value,label){
    if(!select||!value)return;
    if(!Array.from(select.options).some(o=>o.value===value)){
      const option=document.createElement('option');option.value=value;option.textContent=label||value;select.appendChild(option);
    }
    select.value=value;
  }
  function setMulti(select,values){
    if(!select)return;
    const wanted=new Set(values||[]);
    for(const value of wanted)ensureOption(select,value,value);
    Array.from(select.options).forEach(o=>{o.selected=wanted.has(o.value)});
  }
  function selected(select){return select?Array.from(select.selectedOptions).map(o=>o.value).filter(Boolean):[];}

  window.VOCDashboardState={DEFAULT_STATE,read,save,toQuery,notify,notifyMeta,ensureOption,setMulti,selected};
})();
