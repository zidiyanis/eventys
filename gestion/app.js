/* Eventys Gestion — app privée de Yanis.
   Les données vivent dans Supabase : seul le compte propriétaire peut les lire
   (règles RLS côté base). La clé ci-dessous est la clé publique, faite pour
   être visible. Prix et stocks : /gestion/catalogue.js. */
(function(){
'use strict';
const SB_URL='https://qtktxkolgxytroblylae.supabase.co',SB_KEY='sb_publishable_Wf4Qc4XkVxI9-5fnFoRoVg_1Yir0Jlt';
/* Mode essai, uniquement sur l'ordinateur de développement : données fictives en mémoire. */
const MOCK=/^(localhost|127\.0\.0\.1)$/.test(location.hostname)&&/[?&]mock=1/.test(location.search);
const CAT=window.EV_CAT,ITEMS=CAT.items;
const stOf=r=>(r.statut==='devis'||r.statut==='demande')&&r.devisAccepte?['Devis accepté','good']:STAT[r.statut];
const STAT={demande:['À traiter','warn'],devis:['Devis envoyé','acc'],confirmee:['Confirmée','good'],livree:['Livrée','acc'],terminee:['Terminée','mut'],annulee:['Annulée','bad']};
const pad=n=>String(n).padStart(2,'0');
const localIso=d=>d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate());
let TODAY=localIso(new Date()),NOW='00:00';
function tick(){const d=new Date();TODAY=localIso(d);NOW=pad(d.getHours())+':'+pad(d.getMinutes())}
tick();
const addDays=(iso,n)=>{const d=new Date(iso+'T12:00:00');d.setDate(d.getDate()+n);return localIso(d)};
const nextSat=()=>{const d=new Date(TODAY+'T12:00:00');return addDays(TODAY,((6-d.getDay())+7)%7||7)};
const DEFSET={acompte:30,hiver:false,min:100,livMin:60,livPub:false,charge:30,marge:10,livDef:80,camDef:75,paiement:'',msgs:{},cn:{}};
const lsGet=(k,d)=>{try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}};
const lsSet=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}};
const S={
 ready:false,user:null,err:'',busy:false,login:{email:''},
 tab:'agenda',sel:TODAY,month:false,mo:{y:+TODAY.slice(0,4),m:+TODAY.slice(5,7)-1},filter:'tout',
 sheet:null,sub:null,edit:false,disc:false,arm:false,arm2:false,anim:false,msgType:'devis',waEdit:null,chk:lsGet('ev_chk',{}),
 set:JSON.parse(JSON.stringify(DEFSET)),ics:'',
 nf:null,pin:{a:'',m:'Espèces'},res:[],stab:'chiffres',cex:null,tpl:'devis'
};
const newNf=()=>{const d=nextSat();return {client:'',tel:'',canal:'WhatsApp',date:d,heure:'14:00',retour:addDays(d,1),mode:'livraison',ville:'',adr:'',trajet:20,items:{},liv:S.set.livDef,camion:S.set.camDef}};

const $=s=>document.querySelector(s);
const eur=n=>Math.round(n).toLocaleString('fr-FR')+' €';
const D=iso=>new Date(iso+'T12:00:00');
const isoOf=localIso;
const fd=(iso,o)=>D(iso).toLocaleDateString('fr-FR',o||{weekday:'long',day:'numeric',month:'long'});
const cap=s=>s.charAt(0).toUpperCase()+s.slice(1);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const tm=h=>{const p=h.split(':');return +p[0]*60+ +p[1]};
const hm=m=>{m=((m%1440)+1440)%1440;return pad(Math.floor(m/60))+':'+pad(m%60)};
const dur=m=>m>=60?Math.floor(m/60)+' h '+pad(m%60):m+' min';
const price=k=>k==='chaise'&&S.set.hiver?CAT.hiverChaise:itemOf(k).p;
const itemOf=k=>ITEMS.find(i=>i.k===k)||{k:k,n:k,c:k,cp:k,s:'',p:0,stock:null,img:''};
const loc=it=>Object.keys(it).reduce((t,k)=>t+it[k]*price(k),0);
const isL=r=>r.mode==='livraison';
const total=r=>Math.max(0,loc(r.items)+(isL(r)?r.liv:0)+(+r.decoPrix||0)-(r.remise||0));
const DECO=CAT.deco||[],decoN=k=>{const d=DECO.find(x=>x.k===k);return d?d.n:k};
const hasArt=r=>Object.keys(r.items).some(k=>r.items[k]>0)||(r.deco||[]).length>0;
const net=r=>total(r)-(isL(r)?r.camion:0);
const sigOf=r=>{const t=total(r),p=t?net(r)/t:0;return p>=.6?['good','Rentable']:p>=.4?['warn','Juste']:['bad','À revoir']};
const acompte=r=>Math.round(total(r)*S.set.acompte/100);
const paid=r=>(r.pay||[]).reduce((s,p)=>s+p.a,0);
const due=r=>total(r)-paid(r);
const firm=r=>['confirmee','livree','terminee'].includes(r.statut);
const live=r=>r.statut!=='annulee';
const byId=id=>S.res.find(r=>r.id===id);
const trip=r=>isL(r)?(r.trajet||0):0;
const departOf=(r,h)=>tm(h)-trip(r)-S.set.marge;
const addrOf=r=>r.adr||r.ville;
const telClean=t=>t.replace(/\s/g,'');
const waNum=t=>{let d=t.replace(/\D/g,'');if(d[0]==='0')d='33'+d.slice(1);return d};
const qtyText=it=>Object.keys(it).filter(k=>it[k]>0).map(k=>it[k]+' '+(it[k]>1?itemOf(k).cp:itemOf(k).c)).join(', ');

const IC={
 cal:'<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/>',
 list:'<path d="M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01"/>',
 gear:'<circle cx="12" cy="12" r="3"/><path d="M19.400 15a1.700 1.700 0 0 0 .3 1.800l.1.100a2 2 0 1 1-2.800 2.800l-.1-.1a1.700 1.700 0 0 0-1.800-.3 1.700 1.700 0 0 0-1 1.500V21a2 2 0 1 1-4 0v-.1a1.700 1.700 0 0 0-1.100-1.500 1.700 1.700 0 0 0-1.800.3l-.1.100a2 2 0 1 1-2.800-2.800l.1-.1a1.700 1.700 0 0 0 .3-1.800 1.700 1.700 0 0 0-1.500-1H3a2 2 0 1 1 0-4h.1a1.700 1.700 0 0 0 1.500-1.100 1.700 1.700 0 0 0-.3-1.800l-.1-.1a2 2 0 1 1 2.800-2.800l.1.100a1.700 1.700 0 0 0 1.800.3H9a1.700 1.700 0 0 0 1-1.500V3a2 2 0 1 1 4 0v.1a1.700 1.700 0 0 0 1 1.500 1.700 1.700 0 0 0 1.800-.3l.1-.1a2 2 0 1 1 2.800 2.800l-.1.100a1.700 1.700 0 0 0-.3 1.800V9a1.700 1.700 0 0 0 1.500 1H21a2 2 0 1 1 0 4h-.1a1.700 1.700 0 0 0-1.500 1z"/>',
 chart:'<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
 plus:'<path d="M12 5v14M5 12h14"/>',x:'<path d="M6 6l12 12M18 6L6 18"/>',
 left:'<path d="M15 5l-7 7 7 7"/>',right:'<path d="M9 5l7 7-7 7"/>',
 truck:'<path d="M2 7h11v9H2zM13 10h4l4 3v3h-8z"/><circle cx="6.500" cy="17.500" r="1.700"/><circle cx="17" cy="17.500" r="1.700"/>',
 nav:'<path d="M3 11l18-8-8 18-2-8z"/>',
 phone:'<path d="M5 4h4l2 5-2.500 1.500a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
 msg:'<path d="M4 5h16v11H9l-5 4z"/>',
 check:'<path d="M5 12l5 5 9-10"/>',copy:'<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
 pin:'<path d="M12 21s7-6 7-11a7 7 0 0 0-14 0c0 5 7 11 7 11z"/><circle cx="12" cy="10" r="2.500"/>',
 link:'<path d="M10 14a4 4 0 0 0 5.700 0l3-3a4 4 0 0 0-5.700-5.700l-1 1M14 10a4 4 0 0 0-5.700 0l-3 3a4 4 0 0 0 5.700 5.700l1-1"/>'
};
const ic=(n,s=22)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${IC[n]}</svg>`;
function brand(k,s){
  const g={
   waze:'<rect width="48" height="48" rx="11" fill="#33CCFF"/><path fill="#fff" d="M24 10c-8 0-14 5.600-14 12.600 0 2.800 1 5.300 2.700 7.400-.4 1.500-1.200 3-2.400 4 2.300.2 4.400-.5 6.200-1.800 2.200.9 4.600 1.400 7.200 1.400h.3c8 0 14-5.700 14-12.700S32 10 24 10z"/><circle cx="19.500" cy="21" r="1.900" fill="#0B2A3C"/><circle cx="28.500" cy="21" r="1.900" fill="#0B2A3C"/><path d="M19 26c2.500 2.600 7.500 2.600 10 0" fill="none" stroke="#0B2A3C" stroke-width="2" stroke-linecap="round"/><circle cx="18" cy="35" r="2.600" fill="#0B2A3C"/><circle cx="31" cy="35" r="2.600" fill="#0B2A3C"/>',
   gmaps:'<rect width="48" height="48" rx="11" fill="#fff" stroke="#DADCE0" stroke-width="2"/><path fill="#EA4335" d="M24 8c-5.500 0-10 4.300-10 9.800 0 7.200 10 20.200 10 20.200s10-13 10-20.200C34 12.300 29.500 8 24 8z"/><circle cx="24" cy="17.800" r="4" fill="#fff"/><path d="M24 38l6-8" stroke="#FBBC04" stroke-width="3" stroke-linecap="round"/><path d="M14 36l6-4" stroke="#34A853" stroke-width="3" stroke-linecap="round"/>',
   plans:'<rect width="48" height="48" rx="11" fill="#EFEBE2"/><path d="M0 14L22 0h8L0 22z" fill="#A9D1F2"/><path d="M48 30L30 48h18z" fill="#A8DC9B"/><path d="M6 44L44 6" stroke="#F4C35A" stroke-width="3"/><circle cx="24" cy="24" r="9" fill="#2F7DF6"/><path fill="#fff" d="M24 17l5 11-5-2.500L19 28z"/>'
  };
  return `<svg width="${s}" height="${s}" viewBox="0 0 48 48" aria-hidden="true">${g[k]}</svg>`;
}
Object.assign(IC,{
 out:'<path d="M15 4h4a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-4M10 16l4-4-4-4M14 12H4"/>',
 dl:'<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>',
 sync:'<path d="M20 11a8 8 0 0 0-14.500-4.500L4 8M4 4v4h4M4 13a8 8 0 0 0 14.500 4.500L20 16M20 20v-4h-4"/>',
 euro:'<path d="M18 7a6.500 6.500 0 1 0 0 10M5 10h9M5 14h8"/>',
 trash:'<path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-12M9 7V4h6v3"/>'
});

/* ---------- données dérivées ---------- */
function events(iso){
  const out=[];
  S.res.filter(live).forEach(r=>{
    if(r.date===iso)out.push({r,t:isL(r)?'Livraison':'Retrait',h:r.heure});
    if(r.retour===iso)out.push({r,t:isL(r)?'Récupération':'Retour',h:r.heureRetour});
  });
  return out.sort((a,b)=>a.h<b.h?-1:1);
}
const depLine=(r,h)=>isL(r)&&!['terminee','annulee'].includes(r.statut)?`<div class="dep">${ic('truck',14)}Départ ${hm(departOf(r,h))} · ${r.trajet} min</div>`:'';
function evCard(e){
  const r=e.r,[sl,sc]=stOf(r),d=due(r),showRest=firm(r)&&d>0&&r.statut!=='terminee';
  return `<button class="ev" data-act="open" data-id="${r.id}"><div class="tm">${e.h}<small>${e.t}</small></div>
   <div class="mn"><div class="nm">${esc(r.client)}</div><div class="sm mut">${r.ville?esc(r.ville)+' · ':''}${qtyText(r.items)}</div>${depLine(r,e.h)}</div>
   <div class="rt"><span class="st c-${sc}">${sl}</span><b>${eur(total(r))}</b>${showRest?`<span class="sm c-warn">Reste ${eur(d)}</span>`:''}</div></button>`;
}

/* ---------- à faire aujourd'hui ---------- */
function todos(){
  const out=[],tom=addDays(TODAY,1),wk=addDays(TODAY,-7);
  S.res.forEach(r=>{const sv=r.suivi||{};
    if(r.statut==='demande')out.push({r,i:'msg',t:`Répondre à ${r.client}`,s:isL(r)&&r.liv===0?'Demande reçue · fixe le prix de livraison':(r.deco||[]).length&&!r.decoPrix?'Demande reçue · fixe le prix de la déco':'Demande reçue · envoie le devis',m:'devis'});
    else if(r.statut==='devis'&&paid(r)===0&&r.devisAccepte)out.push({r,i:'euro',t:`${r.client} a accepté le devis`,s:`Attends l’acompte de ${eur(acompte(r))}, puis confirme`});
    else if(r.statut==='devis'&&paid(r)===0){const j=sv.devis?Math.round((D(TODAY)-D(sv.devis))/864e5):null;
      if(j===null||j>=2)out.push({r,i:'msg',t:`Relancer ${r.client}`,s:`Devis ${j===null?'envoyé':'envoyé il y a '+j+' j'} · acompte de ${eur(acompte(r))} pas reçu`,m:'relance'})}
    if(r.statut==='confirmee'&&r.date===tom&&!sv.rappel)out.push({r,i:'msg',t:`Rappel de la veille à ${r.client}`,s:`${isL(r)?'Livraison':'Retrait'} demain à ${r.heure}`,m:'rappel'});
    if(firm(r)&&r.statut!=='terminee'&&due(r)>0&&(r.date===TODAY||r.retour===TODAY))out.push({r,i:'euro',t:`Encaisser ${eur(due(r))}`,s:`${r.client} · aujourd’hui`});
    if((r.statut==='confirmee'||r.statut==='livree')&&r.retour<TODAY)out.push({r,i:'check',t:`Clore ${r.client}`,s:'Le retour est passé : marque « Terminé »'});
    if(r.statut==='terminee'&&!sv.merci&&r.retour<=TODAY&&r.retour>=wk)out.push({r,i:'msg',t:`Dire merci à ${r.client}`,s:'Location terminée',m:'merci'});
  });
  return out;
}
function todoBlock(){
  const t=todos();if(!t.length)return '';
  return `<div class="sec"><h2>À faire · ${t.length}</h2></div>${t.map(x=>`<button class="todo" data-act="todo" data-id="${x.r.id}" data-m="${x.m||''}"><span class="ico">${ic(x.i,16)}</span><span class="grow"><span class="b" style="display:block">${esc(x.t)}</span><span class="sm mut">${esc(x.s)}</span></span>${ic('right',16)}</button>`).join('')}`;
}

/* ---------- agenda ---------- */
function vAgenda(){
  const sel=S.sel,f=S.res.filter(firm);
  let reste=0;f.forEach(r=>reste+=Math.max(0,due(r)));
  const toDo=S.res.filter(r=>r.statut==='demande'||r.statut==='devis').length;
  const mon=(()=>{const d=D(sel),k=(d.getDay()+6)%7;d.setDate(d.getDate()-k);return d})();
  let strip='';
  if(!S.month){
    strip='<div class="wk"><button class="ar" data-act="wk" data-d="-7" aria-label="Semaine précédente">'+ic('left',18)+'</button>';
    for(let i=0;i<7;i++){const d=new Date(mon);d.setDate(d.getDate()+i);const iso=isoOf(d),n=Math.min(3,events(iso).length);
      strip+=`<button class="dy${iso===TODAY?' today':''}" aria-pressed="${iso===sel}" data-act="day" data-iso="${iso}" aria-label="${fd(iso)}"><small>${'LMMJVSD'[i]}</small><span class="n">${d.getDate()}</span><span class="dots">${'<i></i>'.repeat(n)}</span></button>`}
    strip+='<button class="ar" data-act="wk" data-d="7" aria-label="Semaine suivante">'+ic('right',18)+'</button></div>';
  }else{
    const c=S.mo,first=new Date(c.y,c.m,1),padn=(first.getDay()+6)%7,days=new Date(c.y,c.m+1,0).getDate();
    let cells='';for(let i=0;i<padn;i++)cells+='<div></div>';
    for(let d=1;d<=days;d++){const iso=`${c.y}-${pad(c.m+1)}-${pad(d)}`,n=Math.min(3,events(iso).length);
      cells+=`<button class="dy${iso===TODAY?' today':''}" aria-pressed="${iso===sel}" data-act="day" data-iso="${iso}"><span class="n">${d}</span><span class="dots">${'<i></i>'.repeat(n)}</span></button>`}
    strip=`<div class="mhd"><button class="rb" data-act="mo" data-d="-1" aria-label="Mois précédent">${ic('left',18)}</button><b>${cap(first.toLocaleDateString('fr-FR',{month:'long',year:'numeric'}))}</b><button class="rb" data-act="mo" data-d="1" aria-label="Mois suivant">${ic('right',18)}</button></div><div class="cal">${['L','M','M','J','V','S','D'].map(h=>`<div class="h">${h}</div>`).join('')}${cells}</div>`;
  }
  const runs=events(TODAY).filter(e=>isL(e.r)&&!['terminee','annulee'].includes(e.r.statut)).map(e=>({e,dep:departOf(e.r,e.h)})).sort((a,b)=>a.dep-b.dep);
  const nx=runs.find(x=>x.dep>=tm(NOW));
  const next=nx?`<button class="next" data-act="open" data-id="${nx.e.r.id}"><div><div class="l">Prochain départ</div><div class="t">${hm(nx.dep)}</div></div><div class="grow"><div class="b">${esc(nx.e.r.client)} · ${nx.e.t.toLowerCase()} ${nx.e.h}</div><div class="sm" style="opacity:.8">Dans ${dur(nx.dep-tm(NOW))}${nx.e.r.ville?' · '+esc(nx.e.r.ville):''}</div></div>${ic('right',18)}</button>`:'';
  const ev=events(sel);
  const dl=cap(fd(sel,{weekday:'long',day:'numeric'}))+(sel===TODAY?' · Aujourd’hui':'');
  return `<div class="hd"><div class="grow"><h1>${cap(D(sel).toLocaleDateString('fr-FR',{month:'long'}))}</h1><div class="mut">${dl}</div></div>
   <button class="rb" aria-pressed="${S.month}" data-act="monthtoggle" aria-label="Vue mois">${ic('cal',20)}</button><button class="rb pri" data-act="new" aria-label="Nouvelle demande">${ic('plus',24)}</button></div>
   ${strip}
   <div class="chips"><button class="fchip" data-act="gofilter" data-f="encaisser"><b>${eur(reste)}</b> à encaisser</button><button class="fchip" data-act="gofilter" data-f="traiter"><b>${toDo}</b> à traiter</button></div>
   ${next}
   ${todoBlock()}
   <div class="sec"><h2>${ev.length} passage${ev.length>1?'s':''}</h2></div>
   ${ev.length?ev.map(evCard).join(''):`<div class="empty">Rien de prévu ce jour-là.<br><button class="lnk" data-act="new" style="margin-top:8px">Nouvelle demande</button></div>`}`;
}

/* ---------- liste ---------- */
function vListe(){
  const F=[['tout','Tout'],['traiter','À traiter'],['venir','À venir'],['encaisser','À encaisser'],['finies','Terminées']];
  const list=S.res.filter(r=>S.filter==='tout'?true:S.filter==='traiter'?(r.statut==='demande'||r.statut==='devis'):S.filter==='venir'?(r.statut==='confirmee'||r.statut==='livree'):S.filter==='encaisser'?(firm(r)&&due(r)>0&&r.statut!=='terminee'||firm(r)&&due(r)>0):r.statut==='terminee'||r.statut==='annulee').sort((a,b)=>a.date<b.date?-1:1);
  const card=r=>{const [sl,sc]=stOf(r),d=due(r),s=sigOf(r);
   return `<button class="ev" style="grid-template-columns:1fr auto" data-act="open" data-id="${r.id}"><div><div class="nm">${esc(r.client)}</div><div class="sm mut">${cap(fd(r.date,{weekday:'short',day:'numeric',month:'short'}))} · ${r.heure} · ${isL(r)?esc(r.ville):'Retrait au box'}</div>${isL(r)&&r.liv===0&&r.statut==='demande'?'<div class="st c-bad" style="margin-top:6px">Prix de livraison à fixer</div>':depLine(r,r.heure)}</div>
   <div class="rt"><span class="st c-${sc}">${sl}</span><b>${eur(total(r))}</b>${firm(r)?(d>0?`<span class="sm c-warn">Reste ${eur(d)}</span>`:d<0?`<span class="sm c-warn">Trop-perçu ${eur(-d)}</span>`:'<span class="sm c-good">Soldée</span>'):`<span class="sm c-${s[0]}">Marge ${eur(net(r))}</span>`}</div></button>`};
  return `<div class="hd"><div class="grow"><h1>Réservations</h1></div><button class="rb pri" data-act="new" aria-label="Nouvelle demande">${ic('plus',24)}</button></div>
   <div class="chips" role="group" aria-label="Filtres">${F.map(f=>`<button class="fchip" aria-pressed="${S.filter===f[0]}" data-act="filter" data-f="${f[0]}">${f[1]}</button>`).join('')}</div>
   <div style="margin-top:12px">${list.length?list.map(card).join(''):'<div class="empty">Aucune réservation dans cette liste.</div>'}</div>`;
}

const stp=(minus,plus,label,w=62)=>`<div class="step"><button ${minus} aria-label="Moins">−</button><b style="min-width:${w}px">${label}</b><button ${plus} aria-label="Plus">+</button></div>`;
const sw=(on,act,attrs='')=>`<button class="rw" role="switch" aria-checked="${on}" data-act="${act}" ${attrs}>`;

/* ---------- stats & clients ---------- */
const MN=['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];
const ALL=()=>S.res;
const pct=(a,b)=>b?Math.round(a/b*100):0;
function monthsBack(n){const out=[];let y=+TODAY.slice(0,4),m=+TODAY.slice(5,7);for(let i=0;i<n;i++){out.unshift(y+'-'+pad(m));m--;if(m<1){m=12;y--}}return out}
function bars(rows){const mx=Math.max(1,...rows.map(r=>r[1]));return rows.map(r=>`<div style="margin:10px 0"><div class="pr" style="padding:0 0 4px"><span>${r[0]}</span><b>${r[2]}</b></div><div class="bar acc"><i style="width:${Math.max(3,Math.round(r[1]/mx*100))}%"></i></div></div>`).join('')}
function vStats(){
  const st=S.stab||'chiffres';
  const head=`<div class="hd"><div class="grow"><h1>Stats</h1></div></div>`;
  const seg=`<div class="seg" style="margin:4px 0 14px"><button data-act="stab" data-v="chiffres" aria-pressed="${st==='chiffres'}">Chiffres</button><button data-act="stab" data-v="clients" aria-pressed="${st==='clients'}">Clients</button></div>`;
  if(st==='clients')return head+seg+vClients();
  if(!ALL().length)return head+seg+'<div class="empty">Pas encore de réservation. Tes chiffres apparaîtront ici dès la première.</div>';
  const A=ALL(),F=A.filter(firm),cur=TODAY.slice(0,7),ms=monthsBack(12),M={};
  ms.forEach(m=>M[m]={ca:0,net:0,n:0});
  F.forEach(r=>{const m=r.date.slice(0,7);if(M[m]){M[m].ca+=total(r);M[m].net+=net(r);M[m].n++}});
  const c=M[cur],p=M[ms[10]],dl=c.ca-p.ca,mx=Math.max(1,...ms.map(m=>M[m].ca));
  const T12=ms.reduce((s,m)=>s+M[m].ca,0),N12=ms.reduce((s,m)=>s+M[m].net,0),R12=ms.reduce((s,m)=>s+M[m].n,0);
  const chart=`<div class="mchart">${ms.map(m=>`<div class="mc${m===cur?' cur':''}"><i style="height:${Math.max(M[m].ca?4:1,Math.round(M[m].ca/mx*100))}%"></i><span>${MN[+m.slice(5,7)-1].charAt(0).toUpperCase()}</span></div>`).join('')}</div>`;
  const enc=A.reduce((s,r)=>s+(r.pay||[]).filter(x=>x.d.slice(0,7)===cur).reduce((t,x)=>t+x.a,0),0);
  const att=F.filter(r=>due(r)>0).reduce((s,r)=>s+due(r),0);
  const conf=F.length,ann=A.filter(r=>r.statut==='annulee').length,att2=A.filter(r=>r.statut==='demande'||r.statut==='devis').length;
  const can={};F.forEach(r=>{const k=r.canal;(can[k]=can[k]||{n:0,ca:0});can[k].n++;can[k].ca+=total(r)});
  const canR=Object.keys(can).sort((a,b)=>can[b].ca-can[a].ca);
  const art=ITEMS.map(i=>[i.n,F.reduce((s,r)=>s+(r.items[i.k]||0)*price(i.k),0)]).concat([['Décoration',F.reduce((s,r)=>s+(+r.decoPrix||0),0)]]).filter(x=>x[1]>0).sort((a,b)=>b[1]-a[1]);
  const D2=F.filter(isL),aLiv=D2.length?D2.reduce((s,r)=>s+r.liv,0)/D2.length:0,aCam=D2.length?D2.reduce((s,r)=>s+r.camion,0)/D2.length:0,loss=D2.filter(r=>r.liv<r.camion);
  const fid=clientsAgg().filter(x=>x.n>=2).length;
  const tips=[];
  if(loss.length)tips.push(`<b>${loss.length} livraison${loss.length>1?'s':''} facturée${loss.length>1?'s':''} moins que le camion</b> (${loss.slice(0,3).map(r=>esc(r.client)).join(', ')}). Fixe la livraison au-dessus du coût du camion, ou impose un minimum de ${eur(S.set.min)}.`);
  if(T12&&N12/T12<.6)tips.push(`<b>Ta marge est de ${pct(N12,T12)} %</b> sur 12 mois : en dessous de 60 %, c’est surtout le camion qui la mange. Groupe les livraisons le même jour quand c’est possible.`);
  if(canR.length)tips.push(`<b>${esc(canR[0])} est ton meilleur canal</b> (${eur(can[canR[0]].ca)}, ${can[canR[0]].n} réservations). Publie-y plus souvent.`);
  if(fid)tips.push(`<b>${fid} client${fid>1?'s ont':' a'} déjà loué plusieurs fois.</b> Un message de relance avant leur prochain événement coûte 0 € : onglet Clients.`);
  if(att>0)tips.push(`<b>${eur(att)} restent à encaisser</b> sur des réservations confirmées.`);
  return head+seg+`
  <div class="kpis"><div class="kpi big"><div class="lab">${cap(fd(cur+'-15',{month:'long',year:'numeric'}))} · confirmé</div><b>${eur(c.ca)}</b><div class="sm" style="opacity:.85">${dl>=0?'+':'−'}${eur(Math.abs(dl))} vs ${MN[+ms[10].slice(5,7)-1]} (${eur(p.ca)})</div></div>
   <div class="kpi"><div class="lab">Net après camion</div><b>${eur(c.net)}</b><div class="sm c-${c.ca&&c.net/c.ca>=.6?'good':c.ca&&c.net/c.ca>=.4?'warn':'bad'}">Marge ${pct(c.net,c.ca)} %</div></div>
   <div class="kpi"><div class="lab">Réservations</div><b>${c.n}</b><div class="sm mut">Panier ${eur(c.n?c.ca/c.n:0)}</div></div></div>
  <div class="sec"><h2>12 derniers mois</h2><span class="sm mut">${eur(T12)}</span></div>
  <div class="box">${chart}<div class="sm mut" style="margin-top:10px">${R12} réservations · net ${eur(N12)} (${pct(N12,T12)} %).</div></div>
  <div class="sec"><h2>Argent</h2></div>
  <div class="kpis"><div class="kpi"><div class="lab">Encaissé ce mois</div><b>${eur(enc)}</b></div><div class="kpi"><div class="lab">À encaisser</div><b class="c-warn">${eur(att)}</b></div></div>
  <div class="sec"><h2>Demandes</h2></div>
  <div class="box"><div class="pr"><span>Devenues des réservations</span><b>${conf}</b></div><div class="pr"><span>Annulées</span><b>${ann}</b></div><div class="pr"><span>En attente de réponse</span><b>${att2}</b></div><div class="pr tot"><span>Taux de confirmation</span><span>${pct(conf,conf+ann)} %</span></div></div>
  <div class="sec"><h2>D’où viennent les clients</h2></div>
  <div class="box">${bars(canR.map(k=>[k,can[k].ca,eur(can[k].ca)+' · '+can[k].n]))}</div>
  <div class="sec"><h2>Ce qui rapporte</h2></div>
  <div class="box">${bars(art.map(a=>[a[0],a[1],eur(a[1])]))}</div>
  <div class="sec"><h2>Livraisons</h2></div>
  <div class="box"><div class="pr"><span>Livraison facturée en moyenne</span><b>${eur(aLiv)}</b></div><div class="pr"><span>Camion en moyenne</span><b>${eur(aCam)}</b></div><div class="pr tot"><span>Livraison moins camion</span><span class="c-${aLiv-aCam>=40?'good':aLiv-aCam>=15?'warn':'bad'}">${eur(aLiv-aCam)}</span></div></div>
  <div class="sec"><h2>Conseils</h2></div>
  <div class="stack">${tips.map(t=>`<div class="box sm">${t}</div>`).join('')||'<div class="empty">Rien à signaler.</div>'}</div>
  <div style="height:16px"></div>`;
}
const ckey=r=>{const d=waNum(r.tel||'');return d.length>=9?'t'+d:'n'+r.client.trim().toLowerCase()};
function clientsAgg(){
  const g={};
  ALL().forEach(r=>{if(r.statut==='annulee')return;const k=ckey(r),x=g[k]=g[k]||{key:k,name:r.client,tel:r.tel,canal:r.canal,n:0,ca:0,last:'',any:'',rs:[]};
   x.rs.push(r);if(r.date>=x.any){x.any=r.date;x.name=r.client;if(r.tel)x.tel=r.tel}
   if(firm(r)){x.n++;x.ca+=total(r);if(r.date>x.last)x.last=r.date}});
  return Object.keys(g).map(k=>g[k]).sort((a,b)=>b.ca-a.ca||(a.name<b.name?-1:1));
}
function vClients(){
  const L=clientsAgg(),days=d=>Math.round((D(TODAY)-D(d))/864e5),fid=L.filter(x=>x.n>=2).length,cl=L.filter(x=>x.n>0);
  if(!L.length)return '<div class="empty">Pas encore de client. Ils apparaîtront ici dès la première réservation.</div>';
  const tag=x=>x.n===0?['En cours','acc']:days(x.last)>60?['À relancer','warn']:x.n>=2?['Fidèle','good']:['Nouveau','mut'];
  const row=x=>{const t=tag(x),open=S.cex===x.key,rs=x.rs.slice().sort((a,b)=>a.date<b.date?1:-1),msg=msgText(rs[0],'client');
   return `<div class="cli"><button data-act="cex" data-c="${esc(x.key)}" style="width:100%;text-align:left;display:flex;justify-content:space-between;gap:10px;align-items:center"><div><div class="nm">${esc(x.name)}</div><div class="sm mut">${x.n?x.n+' réservation'+(x.n>1?'s':'')+' · dernière '+fd(x.last,{day:'numeric',month:'short'}):'Pas encore de réservation'} · ${esc(x.canal)}</div></div><div style="text-align:right"><b>${eur(x.ca)}</b><div class="st c-${t[1]}" style="justify-content:flex-end">${t[0]}</div></div></button>
   ${open?`<div style="margin-top:10px;border-top:1px solid var(--line);padding-top:8px">${rs.map(r=>`<button class="pr sm" style="width:100%" data-act="open" data-id="${r.id}"><span>${fd(r.date,{day:'numeric',month:'short',year:'2-digit'})} · ${qtyText(r.items)||'—'}</span><b>${eur(total(r))}</b></button>`).join('')}
    <div class="field" style="margin:8px 0"><label for="cn-${esc(x.key)}">Note sur ce client</label><textarea class="inp" id="cn-${esc(x.key)}" data-cn="${esc(x.key)}" placeholder="Préférences, détails à retenir…">${esc(S.set.cn[x.key]||'')}</textarea></div>
    ${x.tel?`<div class="sm mut" style="margin:6px 0">${esc(x.tel)}</div><a class="btn" style="min-height:46px" target="_blank" rel="noopener" href="https://wa.me/${waNum(x.tel)}?text=${encodeURIComponent(msg)}">Relancer sur WhatsApp</a>`:'<div class="sm mut">Pas de numéro enregistré.</div>'}</div>`:''}</div>`};
  return `<div class="kpis"><div class="kpi"><div class="lab">Clients</div><b>${L.length}</b></div><div class="kpi"><div class="lab">Fidèles (2 fois et +)</div><b>${fid}</b><div class="sm mut">${pct(fid,cl.length)} % des clients</div></div><div class="kpi" style="grid-column:1/-1"><div class="lab">Dépense moyenne par client</div><b>${eur(cl.length?cl.reduce((s,x)=>s+x.ca,0)/cl.length:0)}</b></div></div>
  <div class="sec"><h2>Tous les clients</h2><span class="sm mut">par chiffre d’affaires</span></div>${L.map(row).join('')}<div style="height:16px"></div>`;
}

/* ---------- messages WhatsApp ---------- */
const TPL={
 devis:['Devis',"Bonjour {prenom}, voici ton devis Eventys pour le {date} :\n{lien}\n\nTotal : {total}. Pour bloquer la date, acompte de {pct} % : {acompte}.\nTu peux l'accepter directement sur la page. À très vite !"],
 relance:['Relance',"Bonjour {prenom}, je reviens vers toi pour ton devis du {date} ({total}). Je te garde le matériel dès que tu me confirmes avec l'acompte de {acompte}.{paiement}"],
 confirm:['Acompte reçu',"Merci {prenom}, j'ai bien reçu ton acompte. Ta réservation est confirmée pour le {date} à {heure}. Il restera {reste} à régler le jour J."],
 rappel:['Rappel J-1',"Bonjour {prenom}, petit rappel : {rdv} demain, {date}, à {heure}. Peux-tu me confirmer l'adresse et un contact sur place ?"],
 merci:['Merci',"Merci {prenom} pour ta confiance ! J'espère que ton événement s'est bien passé. N'hésite pas à m'envoyer une photo ou à me recommander à tes proches."],
 client:['Ancien client',"Bonjour {prenom}, c'est Yanis d'Eventys. Tu as un événement de prévu prochainement ? Je peux te refaire un devis rapidement."]
};
const tplOf=t=>(S.set.msgs&&S.set.msgs[t])||TPL[t][1];
/* ---------- devis en ligne ---------- */
const newTok=()=>{const a=new Uint8Array(24);crypto.getRandomValues(a);return Array.from(a,b=>b.toString(16).padStart(2,'0')).join('')};
const tokOf=r=>r.devisToken||(r._tok=r._tok||newTok());
const devisUrl=r=>location.origin+'/devis?d='+tokOf(r);
function nextNum(){const y=TODAY.slice(0,4);let m=0;S.res.forEach(r=>{const n=r.devis&&r.devis.num||'';const k=n.match(/^DEV-(\d{4})-(\d+)$/);if(k&&k[1]===y)m=Math.max(m,+k[2])});return 'DEV-'+y+'-'+String(m+1).padStart(3,'0')}
function snapshot(r){
  const L=isL(r),keys=Object.keys(r.items).filter(k=>r.items[k]>0);
  return {num:r.devis&&r.devis.num||nextNum(),emis:TODAY,valide:addDays(TODAY,7),client:r.client.trim(),
   date:r.date,heure:r.heure,retour:r.retour,heureRetour:r.heureRetour,mode:r.mode,ville:L?r.ville:'',
   lignes:keys.map(k=>({n:itemOf(k).n,q:r.items[k],pu:price(k),m:r.items[k]*price(k)})),
   deco:(r.deco||[]).map(decoN),decoPrix:+r.decoPrix||0,
   location:loc(r.items),livraison:L?r.liv:0,remise:r.remise||0,total:total(r),pct:S.set.acompte,acompte:acompte(r),
   paye:paid(r),paiement:(S.set.paiement||'').trim()};
}
function sendDevis(r){
  const d=snapshot(r);r.devis=d;r.devisToken=tokOf(r);
  const patch={devis:d,devisToken:r.devisToken};
  if(r.statut==='demande'){r.statut='devis';patch.statut='devis'}
  r.suivi=Object.assign({},r.suivi,{devis:TODAY});patch.suivi=r.suivi;
  saveRes(r,patch,true);toast('Devis '+d.num+' envoyé');setTimeout(render,80);
}
function msgText(r,type){
  const L=isL(r),v={prenom:r.client.trim().split(' ')[0],date:fd(r.date),heure:r.heure,ville:r.ville||'',
   articles:Object.keys(r.items).filter(k=>r.items[k]>0).map(k=>`• ${r.items[k]} × ${itemOf(k).n} (${eur(price(k))})`).concat((r.deco||[]).length?[`• Décoration (${(r.deco||[]).map(decoN).join(', ')}) : ${r.decoPrix?eur(r.decoPrix):'sur devis'}`]:[]).join('\n'),
   livraison:L?(r.liv>0?`• Livraison${r.ville?' '+r.ville:''} : ${eur(r.liv)}`:'• Livraison : prix à confirmer'):'• Retrait au box à Soisy-sous-Montmorency',
   remise:r.remise?`\n• Remise : −${eur(r.remise)}`:'',total:eur(total(r)),pct:S.set.acompte,acompte:eur(acompte(r)),
   reste:eur(Math.max(0,due(r))),paye:eur(paid(r)),lien:devisUrl(r),paiement:S.set.paiement&&S.set.paiement.trim()?'\n'+S.set.paiement.trim():'',rdv:L?'je te livre':'tu passes au box'};
  let t=tplOf(type).replace(/\{(\w+)\}/g,(m,k)=>k in v?v[k]:m);
  if(type==='devis'&&t.indexOf(v.lien)<0)t+='\n'+v.lien;
  return t;
}

/* ---------- réglages ---------- */
function vReglages(){
  const s=S.set,host=location.host,ics=S.ics?`https://${host}/api/calendrier?t=${S.ics}`:'',lien=`https://${host}/reserver`;
  const tp=S.tpl,custom=!!(s.msgs&&s.msgs[tp]);
  return `<div class="hd"><div class="grow"><h1>Réglages</h1></div><button class="rb" data-act="refresh" aria-label="Actualiser">${ic('sync',20)}</button></div>
  <div class="gt" style="margin-top:4px">Calendrier Apple</div>
  <div class="box">${ics?`<div class="b">Abonnement au calendrier</div>
   <div class="sm mut" style="margin:6px 0 12px">Tes réservations confirmées apparaissent dans l’app Calendrier, avec une alerte à l’heure du chargement.</div>
   <a class="btn" href="webcal://${host}/api/calendrier?t=${S.ics}">${ic('cal',18)}S’abonner sur cet appareil</a>
   <button class="btn ghost s" style="width:100%;margin-top:8px" data-act="copy" data-t="${esc(ics)}">${ic('copy',18)}Copier le lien</button>
   <ol class="sm mut" style="padding-left:18px;margin:12px 0 0"><li>Sur l’iPhone, touche « S’abonner » et valide.</li><li>Si rien ne s’ouvre : Réglages, Calendrier, Comptes, Ajouter un compte, Autre, « Ajouter un calendrier avec abonnement », puis colle le lien.</li><li>Dans les réglages de ce calendrier, désactive « Supprimer les alarmes » pour garder les alertes.</li></ol>
   <div class="sm mut" style="margin-top:10px">Sens unique : l’app envoie vers Apple. Apple met à jour de lui-même, de temps en temps. Ne partage pas ce lien : il montre tes réservations.</div>`:'<div class="sm mut">Lien du calendrier indisponible. Actualise.</div>'}</div>
  <div class="gt">Tarifs et règles</div>
  <div class="box" style="padding-block:4px">
   <div class="rw"><span class="b">Acompte</span>${stp('data-act="set" data-f="acompte" data-d="-5"','data-act="set" data-f="acompte" data-d="5"',s.acompte+' %',52)}</div>
   <div class="rw"><div class="grow"><div class="b">Livraison par défaut</div><div class="sm mut">Proposée dans une nouvelle demande</div></div>${stp('data-act="set" data-f="livDef" data-d="-5"','data-act="set" data-f="livDef" data-d="5"',eur(s.livDef))}</div>
   <div class="rw"><div class="grow"><div class="b">Camion par défaut</div><div class="sm mut">Ton coût aller-retour habituel</div></div>${stp('data-act="set" data-f="camDef" data-d="-5"','data-act="set" data-f="camDef" data-d="5"',eur(s.camDef))}</div>
   <div class="rw"><div class="grow"><div class="b">Minimum pour livrer</div><div class="sm mut">Dessous, propose le retrait</div></div>${stp('data-act="set" data-f="min" data-d="-10"','data-act="set" data-f="min" data-d="10"',eur(s.min))}</div>
   <div class="rw"><div class="grow"><div class="b">Livraison à partir de</div><div class="sm mut">Montré au client si le prix est visible</div></div>${stp('data-act="set" data-f="livMin" data-d="-5"','data-act="set" data-f="livMin" data-d="5"',eur(s.livMin))}</div>
   <div class="rw"><div class="grow"><div class="b">Temps de chargement</div><div class="sm mut">Au box, avant de partir</div></div>${stp('data-act="set" data-f="charge" data-d="-5"','data-act="set" data-f="charge" data-d="5"',s.charge+' min')}</div>
   <div class="rw"><div class="grow"><div class="b">Marge de sécurité</div><div class="sm mut">Ajoutée au trajet</div></div>${stp('data-act="set" data-f="marge" data-d="-5"','data-act="set" data-f="marge" data-d="5"',s.marge+' min')}</div>
   ${sw(s.livPub,'livpub')}<div class="grow"><div class="b">Prix de livraison sur le lien client</div><div class="sm mut">${s.livPub?'Visible : « à partir de '+eur(s.livMin)+' »':'Caché : tu fixes la livraison sur WhatsApp'}</div></div><span class="sw"></span></button>
   ${sw(s.hiver,'hiver')}<div class="grow"><div class="b">Tarif hiver</div><div class="sm mut">Chaise à ${eur(CAT.hiverChaise)} au lieu de ${eur(itemOf('chaise').p)}</div></div><span class="sw"></span></button></div>
  <div class="gt">Lien client</div>
  <div class="box"><div class="b">Page de demande</div><div class="msg mono" style="margin:8px 0 10px">${esc(lien)}</div>
   <div class="row"><button class="btn s grow" data-act="copy" data-t="${esc(lien)}">${ic('copy',18)}Copier le lien</button><a class="btn ghost s grow" target="_blank" rel="noopener" href="/reserver">Voir la page</a></div>
   <div class="sm mut" style="margin-top:10px">Envoie ce lien au client : il choisit sa date et son matériel. Sa demande arrive dans « À traiter ». ${s.livPub?'':'Il ne voit pas le prix de la livraison.'}</div></div>
  <div class="gt">Infos de paiement</div>
  <div class="field"><label for="set-pay">Ajoutées à la fin du devis (RIB, Lydia, PayPal…)</label><textarea class="inp" id="set-pay" data-set="paiement" placeholder="Ex. Acompte par virement : IBAN FR76…">${esc(s.paiement||'')}</textarea></div>
  <div class="gt">Messages WhatsApp</div>
  <div class="chips">${Object.keys(TPL).map(k=>`<button class="fchip" aria-pressed="${tp===k}" data-act="tpl" data-v="${k}">${TPL[k][0]}</button>`).join('')}</div>
  <div class="field" style="margin-top:10px"><label for="set-msg">Texte du message « ${TPL[tp][0]} »</label><textarea class="inp tall" id="set-msg" data-msg="${tp}">${esc(tplOf(tp))}</textarea></div>
  <div class="row sp" style="margin-top:6px"><span class="sm mut">${custom?'Texte modifié par toi':'Texte d’origine'}</span>${custom?'<button class="lnk" data-act="tplreset">Remettre l’origine</button>':''}</div>
  <div class="sm mut" style="margin-top:8px">Mots remplacés tout seuls : {prenom} {date} {heure} {lien} {articles} {livraison} {remise} {total} {acompte} {pct} {reste} {paye} {paiement} {rdv} {ville}</div>
  <div class="gt">Catalogue</div>
  <div class="box">${ITEMS.map(i=>`<div class="pr"><span>${i.n}${i.stock?` <span class="sm mut">· ${i.stock} en stock</span>`:''}</span><b>${eur(price(i.k))}</b></div>`).join('')}</div>
  <div class="gt">Mes données</div>
  <div class="box stack"><button class="btn ghost s" style="width:100%" data-act="csv">${ic('dl',18)}Exporter les réservations (CSV)</button><button class="btn ghost s" style="width:100%" data-act="backup">${ic('dl',18)}Sauvegarde complète (JSON)</button><div class="sm mut">${S.res.length} réservation${S.res.length>1?'s':''} enregistrée${S.res.length>1?'s':''}.</div></div>
  <div class="gt">Compte</div>
  <div class="box row sp"><div class="grow" style="min-width:0"><div class="lab">Connecté</div><div class="b" style="overflow:hidden;text-overflow:ellipsis">${esc(S.user&&S.user.email||'')}</div></div><button class="btn ghost s" data-act="logout">${ic('out',18)}Quitter</button></div>
  <div style="height:16px"></div>`;
}

/* ---------- feuilles ---------- */
const closeBtn=`<button class="x" data-act="close" aria-label="Fermer">${ic('x',20)}</button>`;
function used(date){const u={};S.res.forEach(r=>{if(!firm(r))return;if(r.date<=date&&r.retour>=date)for(const k in r.items)u[k]=(u[k]||0)+r.items[k]});return u}
function stockWarn(date,items){const u=used(date),w=[];ITEMS.forEach(it=>{if(it.stock&&items[it.k]&&(u[it.k]||0)+items[it.k]>it.stock)w.push(`${it.n} : ${Math.max(0,it.stock-(u[it.k]||0))} dispo ce jour-là`)});return w}
const thumb=k=>{const it=itemOf(k);return it.img?`<img class="thumb" src="/assets/img/${it.img}" alt="" loading="lazy" width="46" height="46">`:`<div class="thumb">${esc(it.n.charAt(0))}</div>`};
function stepRow(scope,k,q){const it=itemOf(k);return `<div class="irow">${thumb(k)}<div class="grow"><div class="b" style="font-size:14px">${it.n}</div><div class="sm mut">${eur(price(k))}${it.s?' · '+it.s:''}</div></div><div class="step"><button data-act="step" data-scope="${scope}" data-k="${k}" data-d="-1" ${q?'':'disabled'} aria-label="Retirer">−</button><b>${q}</b><button data-act="step" data-scope="${scope}" data-k="${k}" data-d="1" aria-label="Ajouter">+</button></div></div>`}
const qchips=(act,cur)=>`<div><div class="lab" style="margin-bottom:6px">Chaises, en un tap</div><div class="qchips">${[20,30,40,50,60,80,100].map(n=>`<button data-act="${act}" data-n="${n}" aria-pressed="${cur===n}">${n}</button>`).join('')}</div></div>`;
function timeline(r){
  const st=(t,l,s,k)=>`<div class="stp ${k||''}"><b>${t}</b><div class="sm">${l}</div>${s?`<div class="sm mut">${s}</div>`:''}</div>`;
  if(isL(r)){const d1=departOf(r,r.heure),d2=departOf(r,r.heureRetour);
    return st(hm(d1-S.set.charge),'Chargement au box',S.set.charge+' min')+st(hm(d1),'Départ',`Trajet ${r.trajet} min + ${S.set.marge} min de marge`,'go')+st(r.heure,'Livraison',cap(fd(r.date)),'end')
     +st(hm(d2),'Départ pour la récupération','','go')+st(r.heureRetour,'Récupération',cap(fd(r.retour)),'end')}
  return st(r.heure,'Retrait au box',cap(fd(r.date)),'end')+st(r.heureRetour,'Retour au box',cap(fd(r.retour)),'end');
}
function payBlock(r){
  const T=total(r),P=paid(r),d=due(r),a=acompte(r),pc=T?Math.min(100,Math.round(P/T*100)):0;
  const head=d>0?`<div class="lab">Reste à payer</div><div class="big">${eur(d)}</div>`:d===0?`<div class="lab">Paiement</div><div class="big" style="color:var(--good)">Soldé</div>`:`<div class="lab">Trop-perçu</div><div class="big" style="color:var(--warn)">${eur(-d)}</div>`;
  let quick='';
  if(d>0){if(P<a)quick+=`<button class="btn ghost s grow" data-act="payq" data-a="${a-P}">Acompte ${eur(a-P)}</button>`;quick+=`<button class="btn ghost s grow" data-act="payq" data-a="${d}">Tout le reste ${eur(d)}</button>`}
  const list=(r.pay||[]).map((p,i)=>`<div class="row sp" style="padding:8px 0;border-top:1px solid var(--line)"><div><div class="b">${eur(p.a)}</div><div class="sm mut">${cap(fd(p.d,{day:'numeric',month:'short'}))} · ${p.m}</div></div><button class="lnk c-bad" data-act="paydel" data-i="${i}">Retirer</button></div>`).join('');
  return `<div class="box stack"><div class="row sp" style="align-items:flex-end"><div>${head}</div><div class="sm mut" style="text-align:right">Payé ${eur(P)}<br>sur ${eur(T)}</div></div><div class="bar" role="img" aria-label="${pc} % payé"><i style="width:${pc}%"></i></div>
   ${d<0?`<div class="tip">Il a payé ${eur(-d)} de plus que le total. Rends-le ou garde-le, le montant reste noté.</div>`:''}
   ${quick?`<div class="row">${quick}</div>`:''}
   <div class="field"><label for="pay-a">Autre montant reçu</label><div class="row"><input class="inp grow" id="pay-a" type="number" inputmode="decimal" min="0" step="1" placeholder="Ex. 100" value="${esc(S.pin.a)}"><button class="btn s" data-act="payadd">Ajouter</button></div></div>
   <div class="seg">${['Espèces','Virement','Autre'].map(m=>`<button data-act="paym" data-v="${m}" aria-pressed="${S.pin.m===m}">${m}</button>`).join('')}</div>
   ${list?`<div>${list}</div>`:'<div class="sm mut">Aucun paiement noté.</div>'}</div>`;
}
function devisBlock(r){
  if(r.statut==='annulee')return '';
  const d=r.devis,L=isL(r),open=['demande','devis'].includes(r.statut),num=waNum(r.tel||'');
  const changed=d&&(d.total!==total(r)||d.livraison!==(L?r.liv:0)||(d.decoPrix||0)!==(+r.decoPrix||0)||d.location!==loc(r.items));
  const st=d?`<div class="row sp"><div><div class="b">Devis ${esc(d.num)}</div><div class="sm mut">${r.devisAccepte?'Accepté le '+fd(localIso(new Date(r.devisAccepte)),{day:'numeric',month:'long'}):'Envoyé le '+fd(d.emis,{day:'numeric',month:'long'})+' · pas encore accepté'}</div></div><a class="lnk" target="_blank" rel="noopener" href="${devisUrl(r)}">Voir</a></div>`:'';
  if(!open)return d?`<div class="box">${st}</div>`:'';
  const warn=L&&r.liv===0?'<div class="tip bad">Fixe d’abord le prix de la livraison ci-dessous.</div>':!hasArt(r)?'<div class="tip bad">Ajoute les articles avec « Modifier ».</div>':(r.deco||[]).length&&!r.decoPrix?'<div class="tip bad">Fixe d’abord le prix de la déco ci-dessous.</div>':'';
  const lbl=!d?'Envoyer le devis':changed?'Renvoyer le devis mis à jour':'Renvoyer le devis';
  return `<div class="box stack">${st}${changed?'<div class="tip">Le prix a changé depuis l’envoi : renvoie le devis.</div>':''}${warn}
   <a class="btn${d&&!changed?' ghost':''}" target="_blank" rel="noopener" data-act="sendevis" href="https://wa.me/${num}?text=${encodeURIComponent(msgText(r,'devis'))}">${ic('msg',18)}${lbl} · ${eur(total(r))}</a>
   <div class="sm mut">Crée une page de devis à ton nom (n°, détail, acompte, bouton « J’accepte ») et ouvre WhatsApp avec le lien, prêt à envoyer.</div></div>`;
}
function sheetDetail(r){
  const [sl,sc]=stOf(r),L=isL(r),go=L&&!['terminee','annulee'].includes(r.statut),s=sigOf(r),lo=loc(r.items);
  const keys=Object.keys(r.items).filter(k=>r.items[k]>0);
  const items=keys.map(k=>`<div class="pr"><span>${r.items[k]} × ${itemOf(k).n}</span><b>${eur(r.items[k]*price(k))}</b></div>`).join('');
  const ck=S.chk[r.id]||{};
  const chk=[...(L?['Camion loué et récupéré']:[]),...keys.map(k=>`${r.items[k]} × ${itemOf(k).n}`),...(L?['Sangles et diable','Photos du montage']:[])];
  const w=firm(r)?[]:stockWarn(r.date,r.items);
  const ed=S.edit?`<div class="box stack">
    <div class="field"><label for="e-cl">Client</label><input class="inp" id="e-cl" data-e="client" value="${esc(r.client)}" autocomplete="off"></div>
    <div class="field"><label for="e-tel">Téléphone</label><input class="inp" type="tel" id="e-tel" data-e="tel" value="${esc(r.tel)}" placeholder="06 00 00 00 00"></div>
    <div class="seg"><button data-act="eset" data-f="mode" data-v="livraison" aria-pressed="${L}">Livraison</button><button data-act="eset" data-f="mode" data-v="retrait" aria-pressed="${!L}">Retrait au box</button></div>
    <div class="row"><div class="field grow"><label for="e-date">Date</label><input class="inp" type="date" id="e-date" data-e="date" value="${r.date}"></div><div class="field" style="width:118px"><label for="e-h">Heure</label><input class="inp" type="time" id="e-h" data-e="heure" value="${r.heure}"></div></div>
    <div class="row"><div class="field grow"><label for="e-ret">Retour</label><input class="inp" type="date" id="e-ret" data-e="retour" value="${r.retour}"></div><div class="field" style="width:118px"><label for="e-hr">Heure</label><input class="inp" type="time" id="e-hr" data-e="heureRetour" value="${r.heureRetour}"></div></div>
    ${L?`<div class="field"><label for="e-adr">Adresse</label><input class="inp" id="e-adr" data-e="adr" value="${esc(r.adr)}" placeholder="Numéro, rue, code postal, ville"></div><div class="field"><label for="e-v">Ville</label><input class="inp" id="e-v" data-e="ville" value="${esc(r.ville)}"></div><div class="row sp"><div><div class="b">Trajet</div><div class="sm mut">Aller simple depuis le box</div></div>${stp('data-act="adj" data-f="trajet" data-d="-5"','data-act="adj" data-f="trajet" data-d="5"',r.trajet+' min')}</div>`:''}
    ${qchips('edq',r.items.chaise||0)}
    <div>${ITEMS.map(i=>stepRow('ed',i.k,r.items[i.k]||0)).join('')}</div>
    <div><div class="lab" style="margin-bottom:6px">Décoration (sur devis)</div><div class="qchips">${DECO.map(d=>`<button data-act="edeco" data-k="${d.k}" aria-pressed="${(r.deco||[]).indexOf(d.k)>=0}">${esc(d.n)}</button>`).join('')}</div></div>
    <button class="btn s" data-act="edit">Terminé</button></div>`:'';
  return `<div class="grab"></div><div class="sh-hd"><span class="st c-${sc}" style="margin-top:8px">${sl}</span>${closeBtn}</div>
  <div class="name-l">${esc(r.client)}</div>
  <div class="row sp" style="margin-bottom:14px"><div class="mut">${cap(fd(r.date,{weekday:'long',day:'numeric',month:'long'}))} · ${r.heure}<br><span class="sm">Venu par ${esc(r.canal)}</span></div><button class="lnk" data-act="edit">${S.edit?'Fermer':'Modifier'}</button></div>
  <div class="stack">
  ${ed}
  ${go?`<div class="dtl"><div><div class="lab">Départ</div><div class="t">${hm(departOf(r,r.heure))}</div></div><div class="grow sm mut">${r.trajet} min de route + ${S.set.marge} min de marge<br>Arrivée ${r.heure}</div>${ic('truck',26)}</div>`:''}
  ${L&&r.liv===0&&['demande','devis'].includes(r.statut)?'<div class="tip bad">Prix de livraison à fixer : le client n’en a vu aucun. Règle la livraison et le camion plus bas, puis envoie le devis.</div>':''}
  ${w.map(x=>`<div class="tip bad">Stock insuffisant ce jour-là : ${x}</div>`).join('')}
  ${!r.tel?'<div class="tip">Pas de numéro : ajoute-le avec « Modifier » pour ouvrir WhatsApp sur ce client.</div>':''}
  <div class="box">${items||(r.deco||[]).length?items:'<div class="sm mut">Aucun article. Ajoute-les avec « Modifier ».</div>'}${(r.deco||[]).length?`<div class="${items?'irow':''}" style="${items?'':'padding:0'}"><div class="grow"><div class="lab">Décoration demandée</div><div class="b">${(r.deco||[]).map(k=>esc(decoN(k))).join(' · ')}</div></div></div>`:''}</div>
  ${(r.deco||[]).length||r.decoPrix?`<div class="box row sp"><div><div class="b">Prix de la décoration</div><div class="sm mut">Sur devis : le client ne l’a pas vu</div></div>${stp('data-act="adj" data-f="decoPrix" data-d="-10"','data-act="adj" data-f="decoPrix" data-d="10"',eur(r.decoPrix||0))}</div>`:''}
  <div><div class="lab" style="margin:0 2px 6px">Détail du prix</div>
   <div class="pr"><span>Location</span><b>${eur(lo)}</b></div>
   ${L?`<div class="pr"><span>Livraison</span><b>+${eur(r.liv)}</b></div>`:''}
   ${r.decoPrix?`<div class="pr"><span>Décoration</span><b>+${eur(r.decoPrix)}</b></div>`:''}
   ${r.remise?`<div class="pr"><span>Remise</span><b>−${eur(r.remise)}</b></div>`:''}
   <div class="pr tot"><span>Total</span><span>${eur(total(r))}</span></div>
   <button class="lnk" data-act="disc" style="margin-top:6px">Faire une remise</button>
   ${S.disc?`<div class="row sp" style="margin-top:8px"><span class="sm mut">Remise</span>${stp('data-act="rem" data-d="-5"','data-act="rem" data-d="5"',eur(r.remise||0))}</div>`:''}
  </div>
  ${L?`<div class="box stack"><div class="row sp"><div><div class="b">Livraison facturée</div></div>${stp('data-act="adj" data-f="liv" data-d="-5"','data-act="adj" data-f="liv" data-d="5"',eur(r.liv))}</div><div class="row sp"><div><div class="b">Coût du camion</div><div class="sm mut">Aller-retour, pour toi</div></div>${stp('data-act="adj" data-f="camion" data-d="-5"','data-act="adj" data-f="camion" data-d="5"',eur(r.camion))}</div></div>`:''}
  ${devisBlock(r)}
  <div class="mg ${s[0]}"><div class="v">${eur(net(r))}</div><div><div class="b">Ta marge · ${s[1]}</div><div class="sm">${total(r)?Math.round(net(r)/total(r)*100):0} % du total${L?' · camion '+eur(r.camion):''}</div></div></div>
  ${L&&r.liv<r.camion&&r.liv>0?`<div class="tip bad">Livraison sous le coût du camion : tu perds ${eur(r.camion-r.liv)} sur le trajet.</div>`:''}
  ${L&&lo>0&&lo<S.set.min?`<div class="tip">Location de ${eur(lo)} : sous ton minimum de livraison (${eur(S.set.min)}). Propose le retrait au box.</div>`:''}
  ${L?(addrOf(r)?`<div><div class="row" style="align-items:flex-start;margin:0 2px 10px">${ic('pin',18)}<div class="grow b">${esc(addrOf(r))}</div><button class="lnk" data-act="copy" data-t="${esc(addrOf(r))}">Copier</button></div><button class="btn" data-act="sub" data-v="nav">${ic('nav',20)}Itinéraire</button></div>`:`<div class="box row">${ic('pin',18)}<div class="grow sm mut">Adresse à ajouter avec « Modifier ».</div></div>`):`<div class="box row">${ic('pin',18)}<div class="grow">Retrait au box · Soisy-sous-Montmorency</div></div>`}
  ${payBlock(r)}
  ${paid(r)>0&&['demande','devis'].includes(r.statut)?'<div class="tip">Un paiement est noté : pense à passer la réservation en « Confirmer ».</div>':''}
  <div class="field"><label for="notes">Notes internes</label><textarea class="inp" id="notes" data-e="notes" placeholder="Code portail, instructions particulières…">${esc(r.notes)}</textarea></div>
  <div class="box"><div class="lab" style="margin-bottom:6px">Le jour J</div><div class="tl">${timeline(r)}</div></div>
  <div class="box"><div class="lab" style="margin-bottom:4px">Check-list de chargement · ${chk.filter((c,i)=>ck[i]).length}/${chk.length}</div>${chk.map((c,i)=>`<button class="chk" role="checkbox" aria-checked="${!!ck[i]}" data-act="chk" data-i="${i}"><span class="bx">${ck[i]?ic('check',14):''}</span><span class="t">${esc(c)}</span></button>`).join('')}</div>
  <div class="trio"><button class="ob good" aria-pressed="${r.statut==='confirmee'}" data-act="setst" data-v="confirmee"><span>Confirmer</span></button>
   <button class="ob acc" aria-pressed="${r.statut==='livree'||r.statut==='terminee'}" data-act="setst" data-v="${r.statut==='confirmee'?'livree':'terminee'}"><span>${r.statut==='confirmee'?'Livré':'Terminé'}</span></button>
   <button class="ob bad" aria-pressed="${r.statut==='annulee'}" data-act="cancel"><span>${S.arm?'Sûr ?':'Annuler'}</span></button></div>
  ${r.statut==='annulee'?`<button class="btn ghost s" style="width:100%;color:var(--bad)" data-act="del">${ic('trash',18)}${S.arm2?'Sûr ? Supprimer pour de bon':'Supprimer définitivement'}</button>`:''}
  ${r.tel?`<div class="box row"><div class="grow"><div class="lab">Téléphone</div><div class="b">${esc(r.tel)}</div></div><button class="lnk" data-act="copy" data-t="${esc(r.tel)}">Copier</button></div>
  <div class="ct"><a href="tel:${telClean(r.tel)}">${ic('phone',18)}Appeler</a><a href="sms:${telClean(r.tel)}">${ic('msg',18)}Message</a><button data-act="sub" data-v="wa">WhatsApp</button></div>`:`<button class="btn ghost" data-act="sub" data-v="wa">Préparer un message WhatsApp</button>`}
  </div>`;
}
function sheetNav(r){
  const q=encodeURIComponent(addrOf(r));
  const row=(k,l,h)=>`<a class="nav-row" target="_blank" rel="noopener" href="${h}">${brand(k,44)}<span class="grow b" style="font-size:18px">${l}</span>${ic('right',18)}</a>`;
  return `<div class="grab"></div><div class="sh-hd"><div><div class="name-l" style="font-size:26px;margin-top:4px">Ouvrir avec</div></div><button class="x" data-act="closesub" aria-label="Fermer">${ic('x',20)}</button></div>
   <div class="mut" style="margin:2px 0 14px">${esc(addrOf(r))}</div>
   <div class="box" style="padding:0;overflow:hidden">${row('plans','Plans','https://maps.apple.com/?daddr='+q+'&dirflg=d')}${row('waze','Waze','https://waze.com/ul?q='+q+'&navigate=yes')}${row('gmaps','Google Maps','https://www.google.com/maps/dir/?api=1&destination='+q)}</div>`;
}
function sheetWa(r){
  const M=['devis','relance','confirm','rappel','merci'],txt=S.waEdit!==null?S.waEdit:msgText(r,S.msgType),num=waNum(r.tel||'');
  return `<div class="grab"></div><div class="sh-hd"><div class="name-l" style="font-size:26px;margin-top:4px">WhatsApp</div><button class="x" data-act="closesub" aria-label="Fermer">${ic('x',20)}</button></div>
   <div class="mut" style="margin-bottom:12px">Pour ${esc(r.client)}${r.tel?' · '+esc(r.tel):''}</div>
   <div class="stack"><div class="chips">${M.map(m=>`<button class="fchip" aria-pressed="${S.msgType===m}" data-act="msgtype" data-v="${m}">${TPL[m][0]}</button>`).join('')}</div>
   <textarea class="inp tall" id="wa-txt" data-wa="1" aria-label="Message">${esc(txt)}</textarea>
   <a class="btn" id="wa-go" target="_blank" rel="noopener" data-act="wasend" href="https://wa.me/${num}?text=${encodeURIComponent(txt)}">Ouvrir WhatsApp</a>
   <button class="btn ghost" data-act="copywa">${ic('copy',18)}Copier le message</button>
   <div class="sm mut">${num?'WhatsApp s’ouvre sur ce client avec le message déjà écrit : tu n’as plus qu’à appuyer sur Envoyer.':'Pas de numéro : WhatsApp te demandera à qui l’envoyer.'} Tu peux corriger le texte ici avant d’envoyer.</div></div>`;
}
function sheetNew(){
  const n=S.nf,r={items:n.items,mode:n.mode,liv:n.liv,camion:n.camion,remise:0},s=sigOf(r),L=loc(n.items),w=stockWarn(n.date,n.items);let tips='';
  if(n.mode==='livraison'&&L>0&&L<S.set.min)tips+=`<div class="tip">Location de ${eur(L)} : sous ton minimum de livraison (${eur(S.set.min)}). Propose le retrait au box.</div>`;
  if(n.mode==='livraison'&&n.liv<n.camion)tips+=`<div class="tip bad">Livraison facturée ${eur(n.liv)} pour un camion à ${eur(n.camion)} : tu perds ${eur(n.camion-n.liv)}.</div>`;
  w.forEach(x=>tips+=`<div class="tip bad">Stock insuffisant : ${x}</div>`);
  return `<div class="grab"></div><div class="sh-hd"><div class="name-l" style="font-size:28px;margin-top:4px">Nouvelle demande</div>${closeBtn}</div><div class="stack" style="margin-top:10px">
  <div class="field"><label for="nf-client">Client</label><input class="inp" id="nf-client" data-n="client" value="${esc(n.client)}" placeholder="Prénom et initiale" autocomplete="off"></div>
  <div class="field"><label for="nf-tel">Téléphone</label><input class="inp" type="tel" id="nf-tel" data-n="tel" value="${esc(n.tel)}" placeholder="06 00 00 00 00" autocomplete="off"></div>
  <div class="field"><span class="lab">Il t’a écrit sur</span><div class="seg">${['WhatsApp','Instagram','TikTok','Autre'].map(c=>`<button data-act="nfset" data-f="canal" data-v="${c}" aria-pressed="${n.canal===c}">${c}</button>`).join('')}</div></div>
  <div class="field"><span class="lab">Récupération du matériel</span><div class="seg"><button data-act="nfset" data-f="mode" data-v="livraison" aria-pressed="${n.mode==='livraison'}">Livraison</button><button data-act="nfset" data-f="mode" data-v="retrait" aria-pressed="${n.mode==='retrait'}">Retrait au box</button></div></div>
  <div class="row"><div class="field grow"><label for="nf-date">Date</label><input class="inp" type="date" id="nf-date" data-nr="date" value="${n.date}"></div><div class="field" style="width:118px"><label for="nf-h">Heure</label><input class="inp" type="time" id="nf-h" data-nr="heure" value="${n.heure}"></div></div>
  <div class="field"><label for="nf-ret">Retour du matériel</label><input class="inp" type="date" id="nf-ret" data-nr="retour" value="${n.retour}"></div>
  ${n.mode==='livraison'?`<div class="field"><label for="nf-adr">Adresse de l’événement</label><input class="inp" id="nf-adr" data-n="adr" value="${esc(n.adr)}" placeholder="Numéro, rue, code postal, ville" autocomplete="off"></div><div class="field"><label for="nf-ville">Ville</label><input class="inp" id="nf-ville" data-n="ville" value="${esc(n.ville)}" placeholder="Ex. Sarcelles" autocomplete="off"></div><div class="box row sp"><div><div class="b">Temps de trajet</div><div class="sm mut">Aller simple depuis le box</div></div>${stp('data-act="nfnum" data-f="trajet" data-d="-5"','data-act="nfnum" data-f="trajet" data-d="5"',n.trajet+' min')}</div>`:''}
  ${qchips('nfq',n.items.chaise||0)}
  <div class="box">${ITEMS.map(i=>stepRow('nf',i.k,n.items[i.k]||0)).join('')}</div>
  ${n.mode==='livraison'?`<div class="box stack"><div class="row sp"><div><div class="b">Livraison facturée</div><div class="sm mut">À partir de ${eur(S.set.livMin)}</div></div>${stp('data-act="nfnum" data-f="liv" data-d="-5"','data-act="nfnum" data-f="liv" data-d="5"',eur(n.liv))}</div><div class="row sp"><div><div class="b">Coût du camion</div><div class="sm mut">Aller-retour, pour toi</div></div>${stp('data-act="nfnum" data-f="camion" data-d="-5"','data-act="nfnum" data-f="camion" data-d="5"',eur(n.camion))}</div></div>`:''}
  ${tips}
  <div class="box"><div class="pr"><span>Location</span><b>${eur(L)}</b></div>${n.mode==='livraison'?`<div class="pr"><span>Livraison</span><b>${eur(n.liv)}</b></div>`:''}<div class="pr tot"><span>Total client</span><span>${eur(total(r))}</span></div><div class="pr"><span class="mut">Acompte ${S.set.acompte} %</span><b>${eur(acompte(r))}</b></div></div>
  <div class="mg ${s[0]}"><div class="v">${eur(net(r))}</div><div><div class="b">Marge nette · ${s[1]}</div><div class="sm">${total(r)?Math.round(net(r)/total(r)*100):0} % du total</div></div></div>
  <button class="btn" data-act="nfsave" ${S.busy?'disabled':''}>${S.busy?'Enregistrement…':'Créer la demande'}</button></div>`;
}

/* ---------- données (Supabase) ---------- */
let sb=null;
const KEYMAP={heureRetour:'heure_retour',decoPrix:'deco_prix',devisToken:'devis_token',devisAccepte:'devis_accepte'};
const toDb=p=>{const o={};for(const k in p)o[KEYMAP[k]||k]=p[k];return o};
const hhmm=(v,d)=>/^\d\d:\d\d/.test(v||'')?v.slice(0,5):d;
const fromDb=x=>({id:x.id,created:x.created_at||'',client:x.client||'',tel:x.tel||'',canal:x.canal||'Autre',mode:x.mode==='retrait'?'retrait':'livraison',date:x.date,heure:hhmm(x.heure,'14:00'),retour:x.retour||addDays(x.date,1),heureRetour:hhmm(x.heure_retour,'11:00'),ville:x.ville||'',adr:x.adr||'',trajet:+x.trajet||0,items:x.items&&typeof x.items==='object'?x.items:{},liv:+x.liv||0,camion:+x.camion||0,remise:+x.remise||0,statut:STAT[x.statut]?x.statut:'demande',notes:x.notes||'',suivi:x.suivi&&typeof x.suivi==='object'?x.suivi:{},deco:Array.isArray(x.deco)?x.deco:[],decoPrix:+x.deco_prix||0,devis:x.devis||null,devisToken:x.devis_token||'',devisAccepte:x.devis_accepte||'',pay:[]});
const ok=x=>{if(x.error)throw x.error;return x.data};
const REAL={
  async session(){const {data}=await sb.auth.getSession();return data.session?data.session.user:null},
  async login(email,pw){return ok(await sb.auth.signInWithPassword({email,password:pw})).user},
  async logout(){await sb.auth.signOut()},
  async load(){const [a,b,c,d]=await Promise.all([sb.from('reservations').select('*'),sb.from('paiements').select('*').order('date'),sb.from('reglages').select('donnees').eq('id',1).maybeSingle(),sb.from('secrets').select('ics_token').eq('id',1).maybeSingle()]);
    const s=ok(c),t=ok(d);return {res:ok(a),pay:ok(b),set:s?s.donnees:{},ics:t?t.ics_token:''}},
  async insRes(o){return ok(await sb.from('reservations').insert(o).select().single())},
  async updRes(id,p){ok(await sb.from('reservations').update(p).eq('id',id).select('id').single())},
  async delRes(id){ok(await sb.from('reservations').delete().eq('id',id))},
  async insPay(o){return ok(await sb.from('paiements').insert(o).select().single())},
  async delPay(id){ok(await sb.from('paiements').delete().eq('id',id))},
  async saveSet(d){ok(await sb.from('reglages').update({donnees:d}).eq('id',1).select('id').single())}
};
function mockDb(){
  let n=1;const id=()=>'m'+(n++),d=k=>addDays(TODAY,k),cp=v=>v===undefined?v:JSON.parse(JSON.stringify(v));
  const COLS=['client','tel','canal','mode','date','heure','retour','heure_retour','ville','adr','trajet','items','liv','camion','remise','statut','notes','suivi','devis','devis_token','devis_accepte','deco','deco_prix'];
  const chk=o=>{for(const k in o)if(COLS.indexOf(k)<0)throw new Error('colonne inconnue : '+k)};
  const R=[
   {client:'Thomas P.',tel:'06 00 00 00 01',canal:'WhatsApp',mode:'livraison',date:d(0),heure:'23:30',retour:d(1),heure_retour:'11:00',ville:'Franconville',adr:'12 rue des Lilas, 95130 Franconville',trajet:15,items:{chaise:30,rect:3},liv:70,camion:65,statut:'confirmee'},
   {client:'Sarah M.',tel:'06 00 00 00 03',canal:'Instagram',mode:'livraison',date:d(1),heure:'14:00',retour:d(2),heure_retour:'11:00',ville:'Sarcelles',adr:'25 rue Victor Hugo, 95200 Sarcelles',trajet:25,items:{chaise:40,ronde:2,rect:2},liv:80,camion:75,statut:'confirmee'},
   {client:'Karim B.',tel:'06 00 00 00 04',canal:'TikTok',mode:'retrait',date:d(5),heure:'10:00',retour:d(6),heure_retour:'18:00',ville:'',adr:'',trajet:0,items:{chaise:20,rect:2,mange:1},liv:0,camion:0,statut:'devis',suivi:{devis:d(-3)}},
   {client:'Inès L.',tel:'06 00 00 00 08',canal:'Lien client',mode:'livraison',date:d(12),heure:'14:00',retour:null,heure_retour:'11:00',ville:'Sarcelles',adr:'',trajet:0,items:{chaise:30,rect:3},liv:0,camion:0,statut:'demande',notes:'Message du client : 2e étage sans ascenseur'},
   {client:'Julie D.',tel:'06 00 00 00 07',canal:'WhatsApp',mode:'livraison',date:d(-9),heure:'14:00',retour:d(-8),heure_retour:'10:00',ville:'Soisy-sous-Montmorency',adr:'5 rue du Moulin, 95230 Soisy-sous-Montmorency',trajet:5,items:{chaise:50,rect:5},liv:80,camion:70,statut:'confirmee'},
   {client:'Julie D.',tel:'06 00 00 00 07',canal:'WhatsApp',mode:'livraison',date:d(-70),heure:'14:00',retour:d(-69),heure_retour:'10:00',ville:'Soisy-sous-Montmorency',adr:'5 rue du Moulin',trajet:5,items:{chaise:40,rect:4},liv:60,camion:70,statut:'terminee'},
   {client:'Nadia R.',tel:'',canal:'Instagram',mode:'livraison',date:d(-3),heure:'15:00',retour:d(-2),heure_retour:'18:30',ville:'Eaubonne',adr:'2 avenue de Paris, 95600 Eaubonne',trajet:10,items:{chaise:50,rect:4,vaisselle:30},liv:80,camion:70,statut:'terminee'}
  ].map(x=>Object.assign({id:id(),created_at:TODAY,remise:0,notes:'',suivi:{}},x));
  const P=[{id:id(),reservation_id:R[0].id,montant:48,date:d(-3),moyen:'Virement'},{id:id(),reservation_id:R[5].id,montant:220,date:d(-70),moyen:'Espèces'},{id:id(),reservation_id:R[6].id,montant:330,date:d(-3),moyen:'Espèces'}];
  let set={};
  const wait=v=>new Promise(r=>setTimeout(()=>r(cp(v)),120));
  return {session:async()=>null,login:async e=>({email:e}),logout:async()=>{},
   load:()=>wait({res:R,pay:P,set:set,ics:'0123456789abcdef0123456789abcdef'}),
   insRes:async o=>{chk(o);const x=Object.assign({id:id(),created_at:TODAY,remise:0,notes:'',suivi:{},heure_retour:'11:00'},cp(o));R.push(x);return wait(x)},
   updRes:async(i,p)=>{chk(p);const x=R.find(r=>r.id===i);if(!x)throw new Error('introuvable');Object.assign(x,cp(p));return wait()},
   delRes:async i=>{const k=R.findIndex(r=>r.id===i);if(k>=0)R.splice(k,1);return wait()},
   insPay:async o=>{const x=Object.assign({id:id()},o);P.push(x);return wait(x)},
   delPay:async i=>{const k=P.findIndex(p=>p.id===i);if(k>=0)P.splice(k,1);return wait()},
   saveSet:async v=>{set=cp(v);return wait()}};
}
const DB=MOCK?mockDb():REAL;

function apply(d){
  const by={};S.res=(d.res||[]).map(fromDb);S.res.forEach(r=>by[r.id]=r);
  (d.pay||[]).forEach(p=>{const r=by[p.reservation_id];if(r)r.pay.push({id:p.id,a:+p.montant,d:p.date,m:p.moyen})});
  S.set=Object.assign(JSON.parse(JSON.stringify(DEFSET)),d.set||{});if(!S.set.msgs||typeof S.set.msgs!=='object')S.set.msgs={};if(!S.set.cn||typeof S.set.cn!=='object')S.set.cn={};
  S.ics=d.ics||'';
  if(S.sheet&&S.sheet!=='new'&&!byId(S.sheet)){S.sheet=null;S.sub=null}
}
let busyN=0;const pend={},timers={};let setTimer=null,setDirty=false;
const dirty=()=>busyN>0||setDirty||Object.keys(pend).length>0;
function fail(e){console.error(e);toast('Non enregistré. Vérifie ta connexion.');setTimeout(()=>{if(!dirty())refresh()},1500)}
function track(p){busyN++;return p.then(v=>{busyN--;return v},e=>{busyN--;fail(e)})}
function flushRes(id){clearTimeout(timers[id]);const p=pend[id];delete pend[id];if(p)track(DB.updRes(id,p))}
function saveRes(r,patch,now){Object.assign(pend[r.id]=pend[r.id]||{},toDb(patch));clearTimeout(timers[r.id]);if(now)flushRes(r.id);else timers[r.id]=setTimeout(()=>flushRes(r.id),700)}
function flushSet(){clearTimeout(setTimer);if(!setDirty)return;setDirty=false;track(DB.saveSet(S.set))}
function saveSet(now){setDirty=true;clearTimeout(setTimer);if(now)flushSet();else setTimer=setTimeout(flushSet,700)}
function flushAll(){Object.keys(pend).forEach(flushRes);flushSet()}
let lastLoad=0;
async function refresh(first){
  try{apply(await DB.load());lastLoad=Date.now();S.err='';if(!first)render()}
  catch(e){console.error(e);if(first)S.err='Impossible de charger les données. Vérifie ta connexion, puis recharge la page.';else toast('Connexion impossible')}
}
function download(name,text,mime){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:mime}));a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},1000)}
function exportCsv(){
  const q=v=>'"'+String(v==null?'':v).replace(/"/g,'""')+'"',n=v=>String(Math.round(v*100)/100).replace('.',',');
  const H=['Date','Heure','Client','Téléphone','Canal','Mode','Ville','Adresse','Articles','Location','Livraison','Remise','Total','Camion','Marge','Payé','Reste','Statut'];
  const rows=S.res.slice().sort((a,b)=>a.date<b.date?-1:1).map(r=>[r.date,r.heure,r.client,r.tel,r.canal,r.mode,r.ville,r.adr,qtyText(r.items),n(loc(r.items)),n(isL(r)?r.liv:0),n(r.remise||0),n(total(r)),n(isL(r)?r.camion:0),n(net(r)),n(paid(r)),n(due(r)),STAT[r.statut][0]].map(q).join(';'));
  download('eventys-reservations-'+TODAY+'.csv','\ufeff'+H.map(q).join(';')+'\r\n'+rows.join('\r\n'),'text/csv;charset=utf-8');
}

/* ---------- connexion ---------- */
function vLogin(){
  return `<form class="login" id="login" autocomplete="on" novalidate>
   <img src="/gestion/icone-192.png" alt="" width="88" height="88" style="border-radius:22px">
   <div style="text-align:center"><h1>Eventys</h1><div class="mut">Gestion · accès privé</div></div>
   <div class="field"><label for="l-email">E-mail</label><input class="inp" id="l-email" name="email" type="email" inputmode="email" autocomplete="username" autocapitalize="none" value="${esc(S.login.email)}"></div>
   <div class="field"><label for="l-pw">Mot de passe</label><input class="inp" id="l-pw" name="password" type="password" autocomplete="current-password"></div>
   ${S.err?`<div class="tip bad" role="alert">${esc(S.err)}</div>`:''}
   <button class="btn" type="submit" ${S.busy?'disabled':''}>${S.busy?'Connexion…':'Se connecter'}</button>
   ${MOCK?'<div class="sm mut" style="text-align:center">Mode essai : données fictives, n’importe quel identifiant.</div>':''}
  </form>`;
}

/* ---------- rendu ---------- */
function render(){
  tick();
  const app=$('#app'),tabs=$('#tabs');
  if(!S.ready){app.innerHTML='<div class="load">Chargement…</div>';tabs.style.display='none';$('#layer').innerHTML='';return}
  if(!S.user){app.innerHTML=vLogin();tabs.style.display='none';$('#layer').innerHTML='';document.body.style.overflow='';return}
  if(S.err){app.innerHTML=`<div class="load"><div style="text-align:center"><div class="tip bad" style="margin-bottom:12px">${esc(S.err)}</div><button class="btn s" data-act="refresh">Réessayer</button></div></div>`;tabs.style.display='none';$('#layer').innerHTML='';return}
  tabs.style.display='';
  app.innerHTML=S.tab==='agenda'?vAgenda():S.tab==='liste'?vListe():S.tab==='stats'?vStats():vReglages();
  const T=[['agenda','cal','Agenda'],['liste','list','Réservations'],['stats','chart','Stats'],['reglages','gear','Réglages']];
  tabs.innerHTML=T.map(t=>`<button class="tab" data-act="tab" data-t="${t[0]}" ${S.tab===t[0]?'aria-current="page"':''}>${ic(t[1])}<span>${t[2]}</span></button>`).join('');
  const old=document.querySelector('.sheet.main'),top=old?old.scrollTop:0;
  let h='';
  const r=S.sheet&&S.sheet!=='new'?byId(S.sheet)||null:null;
  if(S.sheet==='new'||r){
    const body=S.sheet==='new'?sheetNew():sheetDetail(r);
    h+=`<div class="scrim" data-act="close"></div><div class="sheet main${S.anim&&!old?' in':''}" role="dialog" aria-modal="true">${body}</div>`;
    if(S.sub&&r)h+=`<div class="scrim sub" data-act="closesub"></div><div class="sheet sub in" role="dialog" aria-modal="true">${S.sub==='nav'?sheetNav(r):sheetWa(r)}</div>`;
  }
  $('#layer').innerHTML=h;document.body.style.overflow=h?'hidden':'';
  const nw=document.querySelector('.sheet.main');if(nw&&old)nw.scrollTop=top;
}
const toast=m=>{const t=$('#toast');t.textContent=m;t.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(()=>t.classList.remove('on'),2200)};
const openS=(s)=>{S.sheet=s;S.sub=null;S.edit=false;S.disc=false;S.arm=false;S.arm2=false;S.waEdit=null;S.anim=true;render();S.anim=false};
const cleanItems=it=>{const o={};for(const k in it)if(it[k]>0)o[k]=it[k];return o};

document.addEventListener('click',e=>{
  const b=e.target.closest('[data-act]');if(!b)return;
  const a=b.dataset.act,g=b.dataset,r=S.sheet&&S.sheet!=='new'?byId(S.sheet)||null:null;
  if(a==='tab'){S.tab=g.t;S.sheet=null;S.sub=null;render();window.scrollTo(0,0)}
  else if(a==='open'){S.msgType='devis';openS(g.id)}
  else if(a==='todo'){openS(g.id);if(g.m){S.msgType=g.m;S.sub='wa';render()}}
  else if(a==='new'){if(!S.nf)S.nf=newNf();openS('new')}
  else if(a==='refresh'){flushAll();toast('Actualisation…');setTimeout(()=>refresh(),dirty()?900:0)}
  else if(a==='logout'){flushAll();setTimeout(()=>DB.logout().finally(()=>{S.user=null;S.res=[];S.sheet=null;S.err='';render()}),dirty()?900:0)}
  else if(a==='csv'){exportCsv();toast('Fichier CSV prêt')}
  else if(a==='backup'){download('eventys-sauvegarde-'+TODAY+'.json',JSON.stringify({date:TODAY,reglages:S.set,reservations:S.res},null,1),'application/json');toast('Sauvegarde prête')}
  else if(a==='stab'){S.stab=g.v;render()}
  else if(a==='cex'){S.cex=S.cex===g.c?null:g.c;render()}
  else if(a==='tpl'){S.tpl=g.v;render()}
  else if(a==='tplreset'){delete S.set.msgs[S.tpl];saveSet(true);render();toast('Texte d’origine remis')}
  else if(a==='close'){if(S.sub){S.sub=null;S.waEdit=null}else{S.sheet=null}S.arm=false;S.arm2=false;render()}
  else if(a==='closesub'){S.sub=null;S.waEdit=null;render()}
  else if(a==='day'){S.sel=g.iso;render()}
  else if(a==='wk'){S.sel=addDays(S.sel,+g.d);render()}
  else if(a==='monthtoggle'){S.month=!S.month;const d=D(S.sel);S.mo={y:d.getFullYear(),m:d.getMonth()};render()}
  else if(a==='mo'){let m=S.mo.m+(+g.d),y=S.mo.y;if(m<0){m=11;y--}if(m>11){m=0;y++}S.mo={y,m};render()}
  else if(a==='gofilter'){S.filter=g.f;S.tab='liste';render();window.scrollTo(0,0)}
  else if(a==='filter'){S.filter=g.f;render()}
  else if(a==='copy'){copy(g.t)}
  else if(a==='set'){const v=(+S.set[g.f]||0)+(+g.d);S.set[g.f]=Math.max(0,g.f==='acompte'?Math.min(100,v):v);saveSet();render()}
  else if(a==='hiver'){S.set.hiver=!S.set.hiver;saveSet(true);render()}
  else if(a==='livpub'){S.set.livPub=!S.set.livPub;saveSet(true);render()}
  else if(a==='step'){
    if(g.scope==='nf'){const it=S.nf.items;it[g.k]=Math.max(0,(it[g.k]||0)+(+g.d));render()}
    else if(r){r.items[g.k]=Math.max(0,(r.items[g.k]||0)+(+g.d));r.items=cleanItems(r.items);saveRes(r,{items:r.items});render()}}
  else if(a==='nfq'){S.nf.items.chaise=+g.n;render()}
  else if(a==='nfset'){S.nf[g.f]=g.v;render()}
  else if(a==='nfnum'){S.nf[g.f]=Math.max(0,S.nf[g.f]+(+g.d));render()}
  else if(a==='nfsave'){const n=S.nf;if(S.busy)return;if(!n.client.trim()){toast('Ajoute le nom du client');return}
    const L=n.mode==='livraison',o={client:n.client.trim().slice(0,80),tel:n.tel.trim().slice(0,30),canal:n.canal,mode:n.mode,date:n.date,heure:n.heure,retour:n.retour<n.date?addDays(n.date,1):n.retour,heure_retour:'11:00',ville:L?n.ville.trim():'',adr:L?n.adr.trim():'',trajet:L?n.trajet:0,items:cleanItems(n.items),liv:L?n.liv:0,camion:L?n.camion:0,statut:'demande'};
    S.busy=true;render();
    DB.insRes(o).then(x=>{S.busy=false;const nr=fromDb(x);S.res.push(nr);S.nf=null;S.sel=nr.date;S.msgType='devis';openS(nr.id);toast('Demande créée')},err=>{S.busy=false;render();fail(err)})}
  else if(!r){return}
  else if(a==='sub'){S.sub=g.v;S.waEdit=null;render()}
  else if(a==='edit'){S.edit=!S.edit;render()}
  else if(a==='disc'){S.disc=!S.disc;render()}
  else if(a==='eset'){r[g.f]=g.v;saveRes(r,{[g.f]:g.v},true);render()}
  else if(a==='edeco'){const k=g.k,cur=r.deco||[];r.deco=cur.indexOf(k)>=0?cur.filter(x=>x!==k):cur.concat([k]);saveRes(r,{deco:r.deco});render()}
  else if(a==='edq'){r.items.chaise=+g.n;saveRes(r,{items:r.items});render()}
  else if(a==='rem'){r.remise=Math.max(0,(r.remise||0)+(+g.d));saveRes(r,{remise:r.remise});render()}
  else if(a==='adj'){r[g.f]=Math.max(0,r[g.f]+(+g.d));saveRes(r,{[g.f]:r[g.f]});render()}
  else if(a==='setst'){r.statut=g.v;S.arm=false;S.arm2=false;saveRes(r,{statut:g.v},true);render();toast(STAT[g.v][0])}
  else if(a==='cancel'){if(r.statut==='annulee')return;if(S.arm){r.statut='annulee';S.arm=false;saveRes(r,{statut:'annulee'},true);render();toast('Réservation annulée')}else{S.arm=true;render()}}
  else if(a==='del'){if(!S.arm2){S.arm2=true;render();return}
    const id=r.id;clearTimeout(timers[id]);delete pend[id];S.res=S.res.filter(x=>x.id!==id);S.sheet=null;S.arm2=false;render();toast('Réservation supprimée');track(DB.delRes(id))}
  else if(a==='chk'){const ck=S.chk[r.id]=S.chk[r.id]||{};ck[g.i]=!ck[g.i];lsSet('ev_chk',S.chk);render()}
  else if(a==='payq'||a==='payadd'){const amt=a==='payq'?+g.a:parseFloat(String(S.pin.a).replace(',','.'));
    if(!(amt>0)){toast('Entre un montant');return}
    const p={a:Math.round(amt*100)/100,d:TODAY,m:S.pin.m};r.pay.push(p);S.pin.a='';render();toast(eur(amt)+' noté');
    track(DB.insPay({reservation_id:r.id,montant:p.a,date:p.d,moyen:p.m})).then(x=>{if(x)p.id=x.id})}
  else if(a==='paydel'){const p=r.pay[+g.i];if(!p)return;if(!p.id){toast('Encore en cours d’enregistrement, réessaie');return}
    r.pay.splice(+g.i,1);render();toast('Paiement retiré');track(DB.delPay(p.id))}
  else if(a==='paym'){S.pin.m=g.v;render()}
  else if(a==='msgtype'){S.msgType=g.v;S.waEdit=null;render()}
  else if(a==='sendevis'){const L=isL(r);const nd=(r.deco||[]).length&&!r.decoPrix;if((L&&r.liv===0)||!hasArt(r)||nd){e.preventDefault();toast(L&&r.liv===0?'Fixe d’abord la livraison':nd?'Fixe d’abord le prix de la déco':'Ajoute des articles');return}sendDevis(r)}
  else if(a==='wasend'&&S.msgType==='devis'){sendDevis(r)}
  else if(a==='wasend'){const t=S.msgType;r.suivi=Object.assign({},r.suivi,{[t]:TODAY});const patch={suivi:r.suivi};
    if(t==='devis'&&r.statut==='demande'){r.statut='devis';patch.statut='devis';toast('Marqué « Devis envoyé »')}
    saveRes(r,patch,true);setTimeout(render,80)}
  else if(a==='copywa'){copy(S.waEdit!==null?S.waEdit:msgText(r,S.msgType))}
});
function copy(t){try{navigator.clipboard.writeText(t).then(()=>toast('Copié'),()=>toast('Copie impossible : sélectionne le texte'))}catch(x){toast('Copie impossible : sélectionne le texte')}}
const isDT=el=>el.type==='date'||el.type==='time';
document.addEventListener('input',e=>{
  const el=e.target,d=el.dataset,r=S.sheet&&S.sheet!=='new'?byId(S.sheet)||null:null;
  if(el.id==='pay-a')S.pin.a=el.value;
  else if(el.id==='l-email')S.login.email=el.value;
  else if(d.n&&S.nf)S.nf[d.n]=el.value;
  else if(d.nr&&S.nf){if(!el.value)return;S.nf[d.nr]=el.value;if(d.nr==='date'&&S.nf.retour<=el.value)S.nf.retour=addDays(el.value,1)}
  else if(d.e&&r){const k=d.e,v=el.value;
    if(isDT(el)&&!v)return;
    if(k==='client'&&!v.trim())return;
    r[k]=v;const patch={[k]:k==='client'?v.trim().slice(0,80):k==='tel'?v.slice(0,30):v};
    if(k==='date'&&r.retour<v){r.retour=addDays(v,1);patch.retour=r.retour}
    saveRes(r,patch)}
  else if(d.set){S.set[d.set]=el.value;saveSet()}
  else if(d.msg){if(el.value.trim()&&el.value!==TPL[d.msg][1])S.set.msgs[d.msg]=el.value;else delete S.set.msgs[d.msg];saveSet()}
  else if(d.cn){if(el.value.trim())S.set.cn[d.cn]=el.value;else delete S.set.cn[d.cn];saveSet()}
  else if(d.wa&&r){S.waEdit=el.value;const go=$('#wa-go');if(go)go.href='https://wa.me/'+waNum(r.tel||'')+'?text='+encodeURIComponent(el.value)}
});
/* Dates et heures : on redessine quand le sélecteur se ferme, pas pendant qu'il tourne. */
document.addEventListener('focusout',e=>{const el=e.target;if(el&&el.dataset&&isDT(el)&&(el.dataset.e||el.dataset.nr))setTimeout(render,0)});
document.addEventListener('submit',e=>{
  if(e.target.id!=='login')return;e.preventDefault();if(S.busy)return;
  const f=e.target,email=f.email.value.trim(),pw=f.password.value;S.login.email=email;
  if(!email||!pw){S.err='Entre ton e-mail et ton mot de passe.';render();return}
  S.busy=true;S.err='';render();
  DB.login(email,pw).then(async u=>{S.user=u;await refresh(true);S.busy=false;render()},err=>{S.busy=false;S.err=/invalid/i.test(err&&err.message||'')?'E-mail ou mot de passe incorrect.':'Connexion impossible. Vérifie ta connexion internet.';render()});
});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&S.sheet){if(S.sub)S.sub=null;else S.sheet=null;render()}});
/* Mise à jour : au retour sur l'app et toutes les 2 minutes, si rien n'est en cours de saisie. */
const idle=()=>S.user&&!S.sheet&&!dirty()&&!(document.activeElement&&/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName));
document.addEventListener('visibilitychange',()=>{if(document.hidden)flushAll();else if(idle()&&Date.now()-lastLoad>20000)refresh();else if(S.user)render()});
window.addEventListener('pagehide',flushAll);
setInterval(()=>{if(!document.hidden&&idle()&&Date.now()-lastLoad>110000)refresh()},30000);

(async function boot(){
  render();
  if(!MOCK){
    if(!window.supabase){S.ready=true;S.user=null;S.err='L’app n’a pas pu se charger en entier. Recharge la page.';render();return}
    sb=window.supabase.createClient(SB_URL,SB_KEY);
  }
  try{S.user=await DB.session()}catch(e){console.error(e)}
  if(S.user)await refresh(true);
  S.ready=true;render();
})();
})();
