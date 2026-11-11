/* Mind Mapper app. Loaded by index.html, which holds only the seed block. */
document.getElementById('seed').insertAdjacentHTML('beforebegin',String.raw`<div id="stage"><div id="world"><svg id="edges"></svg><div id="nodes"></div><button id="ex" title="Unlink (Delete)"></button></div></div>
<div id="marq"></div>

<div id="top">
  <button class="mark" id="home" title="Edit question and seeds"><svg viewBox="0 0 30 22" width="30" height="22" aria-hidden="true"><circle cx="5" cy="16" r="4" fill="#1B1A18"/><circle cx="15" cy="6" r="4" fill="#E5493A"/><circle cx="25" cy="16" r="4" fill="#1B1A18"/><path d="M5 16 15 6 25 16" stroke="#1B1A18" stroke-width="1.6" fill="none"/></svg>Mind mapper</button>
  <div class="crumb"><span class="sep">|</span><span class="q" id="crumbq"></span><span class="dot"></span></div>
  <div id="meta"></div>
</div>

<div id="ctx"></div>

<div id="dock">
  <button class="db icon" id="undo" title="Undo (Ctrl+Z)"></button>
  <button class="db icon" id="redo" title="Redo (Ctrl+Shift+Z)"></button>
  <span class="vr"></span>
  <button class="grow" id="grow" title="Keep growing (auto-expand leaves)"><span class="bub"></span><span id="growl">Keep growing</span></button>
  <span class="vr"></span>
  <button class="db" id="add" title="Add idea"></button>
  <button class="db" id="tidy" title="Tidy layout"></button>
  <span class="vr z"></span>
  <button class="db icon" id="zout" title="Zoom out"></button>
  <span id="zoomv">100%</span>
  <button class="db icon" id="zin" title="Zoom in"></button>
  <button class="db icon" id="fit" title="Fit to screen"></button>
  <span class="vr"></span>
  <button class="db" id="export" title="Export / import"></button>
</div>

<div id="help"><kbd>Tab</kbd> new branch · <kbd>Enter</kbd> sibling · <kbd>G</kbd> grow · <kbd>L</kbd> or the link button, then click an idea to link/unlink · drag the corner link handle onto an idea · <kbd>⇧</kbd>+drag to select many · double-click canvas to add</div>
<div id="lbanner" role="status"><span>Click another idea to link it. Esc to cancel</span><button id="lcancel" title="Cancel linking (Esc)" aria-label="Cancel linking"></button></div>
<div id="toast"></div>
<div class="grain"></div>

<!-- setup -->
<div id="setup" hidden>
  <section class="hero">
    <div class="mast"><span class="mark"><svg viewBox="0 0 30 22" width="30" height="22" aria-hidden="true"><circle cx="5" cy="16" r="4" fill="#1B1A18"/><circle cx="15" cy="6" r="4" fill="#E5493A"/><circle cx="25" cy="16" r="4" fill="#1B1A18"/><path d="M5 16 15 6 25 16" stroke="#1B1A18" stroke-width="1.6" fill="none"/></svg>Mind mapper</span></div>
    <div class="wrap">
      <h1>Mind mapper • <span>Start with a question, plant a few seed ideas, and let them branch into something you didn't expect.</span></h1>
      <div class="aside"><svg viewBox="0 0 34 26"><path d="M3 2c0 9 4 15 13 17 4 1 9 0 13-1" stroke="#1B1A18" stroke-width="1.6" fill="none" stroke-linecap="round"/><path d="M24 13l6 5-7 3" stroke="#1B1A18" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Every new idea builds on the one it grows from. No judging until you're done generating.</span></div>
      <label class="fl" for="q">Your question</label>
      <textarea id="q" rows="1" placeholder="How might we…"></textarea>
      <div class="seeds" id="chips"><input id="seedin" placeholder="Type a seed idea, press Enter"></div>
      <div class="hint">Five or six seeds works well. Paste a list to add several at once.</div>
      <button id="ctxtog">Add context (optional)</button>
      <textarea id="sctx" placeholder="Who is this for? Constraints, inspiration, things to avoid…"></textarea>
      <button class="go" id="goBtn"><span class="bub"><svg class="i" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>Map it</button>
      <div class="err" id="serr"></div>
    </div>
    <svg class="tear" viewBox="0 0 1200 46" preserveAspectRatio="none" aria-hidden="true"><path fill="#F7F4EC" d="M0 30 L40 26 L85 33 L130 24 L180 29 L210 21 L260 28 L320 23 L360 31 L420 25 L470 30 L520 19 L575 27 L630 24 L680 32 L730 22 L790 28 L840 25 L890 33 L950 23 L1000 29 L1050 20 L1100 27 L1150 24 L1200 30 L1200 46 L0 46Z"/></svg>
  </section>
  <div class="below" id="below"></div>
</div>

<div id="exp" hidden>
  <div class="card">
    <h2>Take it with you</h2>
    <p>Copy the outline into a doc, or copy the map file to keep a backup. To bring a map back in, paste its file below and choose Import.</p>
    <div class="row" style="margin:0 0 10px"><button class="pill on" id="tOut">Outline</button><button class="pill" id="tJson">Map file</button></div>
    <textarea id="extext" spellcheck="false"></textarea>
    <div class="row"><button class="pill red" id="exCopy">Copy</button><button class="pill" id="exImp">Import</button><span style="flex:1"></span><button class="pill" id="exClose">Close</button></div>
  </div>
</div>`);

/* ---------- icons ---------- */
const IC={
 undo:'<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
 redo:'<path d="m15 14 5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13"/>',
 play:'<path d="M8 5v14l11-7z"/>', stop:'<rect x="6" y="6" width="12" height="12" rx="1.5"/>',
 plus:'<path d="M12 5v14M5 12h14"/>', minus:'<path d="M5 12h14"/>',
 tidy:'<circle cx="12" cy="12" r="2.5"/><circle cx="4.5" cy="6" r="2"/><circle cx="19.5" cy="6" r="2"/><circle cx="12" cy="20.5" r="2"/><path d="M6.3 7.2 10 10.6M17.7 7.2 14 10.6M12 14.5v4"/>',
 fit:'<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
 out:'<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5M5 20h14"/>',
 edit:'<path d="M4 20h4L19 9l-4-4L4 16z"/>',
 star:'<path d="m12 3.5 2.6 5.4 5.9.8-4.3 4.1 1 5.9L12 16.9l-5.2 2.8 1-5.9L3.5 9.7l5.9-.8z"/>',
 trash:'<path d="M4 7h16M9.5 7V4.5h5V7M6.5 7l1 13h9l1-13"/>',
 link:'<path d="M10 14a4 4 0 0 0 5.6 0l3.2-3.2a4 4 0 0 0-5.6-5.6l-1 1"/><path d="M14 10a4 4 0 0 0-5.6 0l-3.2 3.2a4 4 0 0 0 5.6 5.6l1-1"/>',
 unlink:'<path d="M10 14a4 4 0 0 0 5.6 0l3.2-3.2a4 4 0 0 0-5.6-5.6l-1 1"/><path d="M14 10a4 4 0 0 0-5.6 0l-3.2 3.2a4 4 0 0 0 5.6 5.6l1-1"/><path d="M3 3l18 18"/>',
 merge:'<path d="M6 3v5a6 6 0 0 0 6 6 6 6 0 0 1 6 6v1M18 3v5a6 6 0 0 1-6 6"/>',
 x:'<path d="M6 6l12 12M18 6 6 18"/>', branch:'<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.5 6H12a4 4 0 0 1 4 4v5.5"/>'
};
const ic=(n,c='i')=>`<svg class="${c}" viewBox="0 0 24 24">${IC[n]}</svg>`;

/* ---------- constants & state ---------- */
const COLORS=['#FF7AB6','#FFD43B','#58C98F','#6FA2F5','#FF9150','#A88BF5','#3FCBD0','#F7A1A1'];
let SEED=null;try{const t=document.getElementById('seed').textContent.trim();if(t)SEED=JSON.parse(t);if(!SEED||typeof SEED!=='object'||Array.isArray(SEED))SEED=null}catch(e){SEED=null}
const KEY='mindmapper-v2'+(SEED&&SEED.id?':'+SEED.id:'');
const MODES={
  yes:{label:'Yes, and',ins:'Build on this idea ("Yes, and…"): extend it, specialise it, or take it one step further.'},
  wild:{label:'Wilder',ins:'Push it wild: bold, unexpected, even slightly absurd twists that could spark something new.'},
  real:{label:'Concrete',ins:'Make it concrete: specific versions, first experiments, or real-world shapes this could take next week.'},
  flip:{label:'Flip it',ins:'Flip it: invert an assumption, change who/where/when/how, or come at it from the opposite angle.'}
};
let S=null, sel=new Set(), selEdge=null, undoS=[], redoS=[], V={x:0,y:0,k:1}, sample=null, growing=false, busy=new Set(), editing=null;
let linkFrom=null;          // source node while in click-to-link mode
const dragSet=new Set();    // nodes currently being dragged (survive re-renders)
const AP={};                // display-only positions while a node animates in
let epoch=0, loopId=0, loopP=null;      // epoch bumps when the whole map is replaced (new map / import)
const CAP=220;
const $=id=>document.getElementById(id), els={};
const N=id=>S.nodes[id];
const ek=(a,b)=>a<b?a+'|'+b:b+'|'+a;
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- persistence & history ---------- */
function save(){try{localStorage.setItem(KEY,JSON.stringify({S,V}))}catch(e){}}
const clip=t=>String(t==null?'':t).replace(/\s+/g,' ').trim();
const num=(v,d=0)=>typeof v==='number'&&isFinite(v)?v:d;
const IDRE=/^[A-Za-z0-9_-]{1,40}$/;
// Validate and normalise a map (from localStorage or an imported file) so bad data can't
// produce NaN positions, colliding ids (missing/low seq) or markup injection via ids.
function clean(v){
  if(!v||typeof v!=='object'||!v.nodes||typeof v.nodes!=='object'||Array.isArray(v.nodes)||!Array.isArray(v.edges))return null;
  const nodes={};let seq=Math.max(0,Math.floor(num(v.seq)));
  for(const [k,n] of Object.entries(v.nodes)){
    if(!IDRE.test(k)||!n||typeof n!=='object')continue;
    const m=/^n(\d+)$/.exec(k);if(m)seq=Math.max(seq,+m[1]);
    nodes[k]={id:k,text:clip(n.text)||(k==='root'?'Untitled question':'Untitled idea'),x:num(n.x),y:num(n.y),
      c:Number.isInteger(n.c)&&n.c>=0?n.c:null,ai:!!n.ai,seed:!!n.seed,star:k!=='root'&&!!n.star,r:Math.max(-3,Math.min(3,num(n.r)))};
  }
  if(!nodes.root)return null;
  Object.assign(nodes.root,{c:null,ai:false,seed:false,r:0});
  const seen=new Set();
  v.edges.forEach(e=>{if(typeof e!=='string')return;const p=e.split('|');if(p.length===2&&p[0]!==p[1]&&nodes[p[0]]&&nodes[p[1]])seen.add(ek(p[0],p[1]))});
  return {q:nodes.root.text,ctx:typeof v.ctx==='string'?v.ctx:'',seq,nodes,edges:[...seen]};
}
function load(){try{const r=JSON.parse(localStorage.getItem(KEY)||'null'),c=r&&clean(r.S);
  if(c){S=c;const v=r.V;if(v&&[v.x,v.y,v.k].every(Number.isFinite)&&v.k>0)V={x:v.x,y:v.y,k:Math.min(2.5,Math.max(.15,v.k))}}}catch(e){}}
const snap=()=>JSON.stringify(S);
function commit(pre){undoS.push(pre||snap());if(undoS.length>120)undoS.shift();redoS=[]}
function restore(str){S=JSON.parse(str);[...sel].forEach(i=>{if(!S.nodes[i])sel.delete(i)});if(selEdge&&!S.edges.includes(selEdge))selEdge=null;if(linkFrom&&!S.nodes[linkFrom])endLink();save();render()}
function undo(){if(!undoS.length)return;redoS.push(snap());restore(undoS.pop())}
function redo(){if(!redoS.length)return;undoS.push(snap());restore(redoS.pop())}

/* ---------- graph helpers ---------- */
function nbrs(id){const o=[];S.edges.forEach(k=>{const[a,b]=k.split('|');if(a===id)o.push(b);else if(b===id)o.push(a)});return o}
function hasEdge(a,b){return S.edges.includes(ek(a,b))}
function link(a,b){if(a!==b&&!hasEdge(a,b))S.edges.push(ek(a,b))}
function unlink(a,b){S.edges=S.edges.filter(k=>k!==ek(a,b))}
function bfs(){
  const dist={root:0},prev={},q=['root'],adj={};
  Object.keys(S.nodes).forEach(i=>adj[i]=[]);
  S.edges.forEach(k=>{const[a,b]=k.split('|');if(adj[a]&&adj[b]){adj[a].push(b);adj[b].push(a)}});
  while(q.length){const c=q.shift();adj[c].forEach(n=>{if(dist[n]==null){dist[n]=dist[c]+1;prev[n]=c;q.push(n)}})}
  return {dist,prev,adj};
}
function pathTo(id,prev){const p=[];let c=id,g=0;while(c&&g++<50){p.unshift(N(c).text);c=prev[c]}return p}
function mkNode(text,x,y,o={}){
  const id='n'+(++S.seq);
  S.nodes[id]={id,text,x,y,c:o.c==null?null:o.c,ai:!!o.ai,seed:!!o.seed,star:false,r:+(Math.random()*3-1.5).toFixed(2)};
  return id;
}
const colorOf=n=>n.c==null?'#1B1A18':COLORS[n.c%COLORS.length];
const count=()=>Object.keys(S.nodes).length;

/* ---------- view ---------- */
function applyV(){$('world').style.transform=`translate(${V.x}px,${V.y}px) scale(${V.k})`;
  const st=$('stage');st.style.backgroundSize=`${28*V.k}px ${28*V.k}px`;st.style.backgroundPosition=`${V.x}px ${V.y}px`;
  $('zoomv').textContent=Math.round(V.k*100)+'%';placeCtx()}
const toWorld=(cx,cy)=>({x:(cx-V.x)/V.k,y:(cy-V.y)/V.k});
const P=id=>AP[id]||N(id); // where a node is drawn (differs from the model only while animating in)
function zoomAt(k,cx,cy){k=Math.min(2.5,Math.max(.15,k));V.x=cx-(cx-V.x)*(k/V.k);V.y=cy-(cy-V.y)*(k/V.k);V.k=k;applyV();save()}
function fit(animate=true){
  const ns=Object.values(S.nodes);if(!ns.length)return;
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  ns.forEach(n=>{const w=(n._w||180)/2,h=(n._h||60)/2;x0=Math.min(x0,n.x-w);x1=Math.max(x1,n.x+w);y0=Math.min(y0,n.y-h);y1=Math.max(y1,n.y+h)});
  const top=70,bot=90,aw=innerWidth-80,ah=innerHeight-top-bot;
  const k=Math.max(.15,Math.min(1.15,aw/(x1-x0||1),ah/(y1-y0||1)));
  const T={k,x:40+(aw-(x1-x0)*k)/2-x0*k,y:top+(ah-(y1-y0)*k)/2-y0*k};
  if(!animate||reduce){Object.assign(V,T);applyV();save();return}
  const F={...V},t0=performance.now();
  (function st(t){const p=Math.min(1,(t-t0)/380),e=1-Math.pow(1-p,3);V.k=F.k+(T.k-F.k)*e;V.x=F.x+(T.x-F.x)*e;V.y=F.y+(T.y-F.y)*e;applyV();if(p<1)requestAnimationFrame(st);else save()})(t0);
}

/* ---------- render ---------- */
let dirty=false;
function updateSel(){Object.entries(els).forEach(([i,el])=>el.classList.toggle('sel',sel.has(i)));drawEdges();ui();placeCtx()}
function render(){
  if(editing){dirty=true;return}   // rebuilt when the edit finishes (see startEdit)
  dirty=false;
  if(linkFrom&&!S.nodes[linkFrom])endLink();
  const layer=$('nodes');layer.innerHTML='';for(const k in els)delete els[k];
  Object.values(S.nodes).forEach(n=>{
    const el=document.createElement('div');el.dataset.id=n.id;
    el.className='node'+(n.id==='root'?' root':'')+(n.seed?' seed':'')+(n.ai?' ai':'')+(n.c==null&&n.id!=='root'?' free':'')+(sel.has(n.id)?' sel':'')+(busy.has(n.id)?' busy':'')+(dragSet.has(n.id)?' dragging':'')+(linkFrom===n.id?' linksrc':'');
    el.style.setProperty('--c',colorOf(n));el.style.setProperty('--r',(n.id==='root'?0:n.r)+'deg');
    const p=P(n.id);el.style.left=p.x+'px';el.style.top=p.y+'px';
    const tx=document.createElement('div');tx.className='tx';tx.textContent=n.text;el.appendChild(tx);
    if(n.star)el.insertAdjacentHTML('beforeend',`<span class="stk">${ic('star')}</span>`);
    const hd=document.createElement('span');hd.className='hd';hd.title='Drag onto another idea to link — drop on empty space to add a connected idea';hd.innerHTML=ic('link');el.appendChild(hd);
    el.addEventListener('pointerdown',e=>nodeDown(e,n.id));
    el.addEventListener('dblclick',e=>{e.stopPropagation();startEdit(n.id)});
    layer.appendChild(el);els[n.id]=el;
  });
  Object.values(S.nodes).forEach(n=>{const el=els[n.id];n._w=el.offsetWidth;n._h=el.offsetHeight});
  drawEdges();ui();placeCtx();
}
function setPos(id){const el=els[id];if(el&&S.nodes[id]){const n=P(id);el.style.left=n.x+'px';el.style.top=n.y+'px'}}
function hash(s){let h=0;for(const c of s)h=(h*31+c.charCodeAt(0))|0;return h}
function edgeGeom(k){const[a,b]=k.split('|');if(!S.nodes[a]||!S.nodes[b])return null;const A=P(a),B=P(b);
  const dx=B.x-A.x,dy=B.y-A.y,L=Math.hypot(dx,dy)||1,s=(hash(k)&1?1:-1)*Math.min(40,L*.12);
  const cx=(A.x+B.x)/2-dy/L*s,cy=(A.y+B.y)/2+dx/L*s;
  return {d:`M${A.x},${A.y} Q${cx},${cy} ${B.x},${B.y}`,mx:.25*A.x+.5*cx+.25*B.x,my:.25*A.y+.5*cy+.25*B.y,a,b}}
let tmpPath='';
function drawEdges(){
  let h='';S.edges.forEach(k=>{const g=edgeGeom(k);if(!g)return;const hot=sel.has(g.a)||sel.has(g.b);
    h+=`<path class="e${hot?' hot':''}${selEdge===k?' picked':''}" d="${g.d}"/><path class="hit" data-k="${k}" d="${g.d}"/>`});
  $('edges').innerHTML=h+tmpPath;
  const ex=$('ex');
  if(selEdge&&S.edges.includes(selEdge)){const g=edgeGeom(selEdge);ex.style.display='grid';ex.style.left=g.mx+'px';ex.style.top=g.my+'px'}else ex.style.display='none';
}
$('ex').innerHTML=ic('x');
$('ex').onclick=e=>{e.stopPropagation();delEdge()};
function delEdge(){if(!selEdge||!S.edges.includes(selEdge)){selEdge=null;return}commit();S.edges=S.edges.filter(k=>k!==selEdge);selEdge=null;save();render();toast('Unlinked')}
$('edges').addEventListener('pointerdown',e=>{const k=e.target.dataset&&e.target.dataset.k;if(!k||editing)return;e.stopPropagation();if(linkFrom)endLink();selEdge=k;sel.clear();render()});

/* ---------- interactions ---------- */
function nodeDown(e,id){
  if(editing||e.button!==0)return;
  e.stopPropagation();
  if(e.target.closest('.hd')&&!linkFrom)return startLink(e,id);
  const el=els[id];try{el.setPointerCapture(e.pointerId)}catch(_){}
  const movers=(sel.has(id)?[...sel]:[id]).filter(i=>S.nodes[i]);
  const start=movers.map(i=>({i,x:N(i).x,y:N(i).y}));const sx=e.clientX,sy=e.clientY,pre=snap(),S0=S,pid=e.pointerId;let moved=false;
  // Listen on window, not the node: a re-render (e.g. Keep growing) replaces the element mid-drag.
  const mv=ev=>{if(ev.pointerId!==pid||S!==S0)return;const dx=(ev.clientX-sx)/V.k,dy=(ev.clientY-sy)/V.k;
    if(!moved&&Math.hypot(dx,dy)*V.k<4)return;
    if(!moved){moved=true;movers.forEach(i=>{dragSet.add(i);delete AP[i];els[i]&&els[i].classList.add('dragging')});$('ctx').style.display='none'}
    start.forEach(s=>{if(!S.nodes[s.i])return;N(s.i).x=s.x+dx;N(s.i).y=s.y+dy;setPos(s.i)});drawEdges()};
  const up=ev=>{if(ev.pointerId!==pid)return;removeEventListener('pointermove',mv);removeEventListener('pointerup',up);removeEventListener('pointercancel',up);
    movers.forEach(i=>{dragSet.delete(i);els[i]&&els[i].classList.remove('dragging')});
    if(moved){if(S===S0){commit(pre);save()}placeCtx();ui()}
    else if(ev.type==='pointercancel'){}
    else if(linkFrom){finishLink(id)}
    else{selEdge=null;if(ev.shiftKey||ev.metaKey||ev.ctrlKey){sel.has(id)?sel.delete(id):sel.add(id)}else{sel.clear();sel.add(id)}updateSel()}};
  addEventListener('pointermove',mv);addEventListener('pointerup',up);addEventListener('pointercancel',up);
}
/* click-to-link mode: Link button / L key, then click another idea */
function beginLink(id){if(!S.nodes[id])return;if(linkFrom===id)return endLink();linkFrom=id;selEdge=null;sel.clear();sel.add(id);
  $('stage').classList.add('linking');$('lbanner').classList.add('on');render()}
function endLink(){if(!linkFrom&&!$('lbanner').classList.contains('on'))return;const was=linkFrom;linkFrom=null;$('stage').classList.remove('linking');$('lbanner').classList.remove('on');
  const el=was&&els[was];if(el)el.classList.remove('linksrc');placeCtx()}
function finishLink(tid){
  const src=linkFrom;endLink();if(!src||!S.nodes[src]||!S.nodes[tid])return;
  if(tid===src){updateSel();return}
  commit();if(hasEdge(src,tid)){unlink(src,tid);toast('Unlinked')}else{link(src,tid);toast('Linked')}
  sel.clear();sel.add(src);save();render();
}
function linkToEmpty(src,p){commit();const nid=mkNode('New idea',p.x,p.y,{c:N(src).c});link(src,nid);sel.clear();sel.add(nid);save();render();startEdit(nid)}
function startLink(e,id){
  e.preventDefault();const A=N(id);if(linkFrom)endLink();
  const mv=ev=>{const p=toWorld(ev.clientX,ev.clientY);tmpPath=`<path class="tmp" d="M${A.x},${A.y} L${p.x},${p.y}"/>`;drawEdges()};
  const pid=e.pointerId,S0=S;
  const up=ev=>{if(ev.pointerId!==pid)return;removeEventListener('pointermove',mv);removeEventListener('pointerup',up);removeEventListener('pointercancel',up);tmpPath='';
    if(ev.type==='pointercancel'||S!==S0||!S.nodes[id]){drawEdges();return}
    const t=document.elementFromPoint(ev.clientX,ev.clientY),tn=t&&t.closest&&t.closest('.node'),tid=tn&&tn.dataset.id;
    if(tid&&tid!==id){if(hasEdge(id,tid)){toast('Already linked');drawEdges();return}commit();link(id,tid);save();render();toast('Linked')}
    else if(!tid&&t&&t.closest&&t.closest('#stage')){const p=toWorld(ev.clientX,ev.clientY);if(Math.hypot(p.x-A.x,p.y-A.y)<40){drawEdges();return}
      linkToEmpty(id,p)}
    else drawEdges()};
  addEventListener('pointermove',mv);addEventListener('pointerup',up);addEventListener('pointercancel',up);
}
const stage=$('stage');
// Two-finger pinch on touch screens: zoom around the midpoint. While pinching, single-pointer
// pan/marquee gestures are suspended so the two fingers don't fight each other.
const touches=new Map();let pinch=null;
function pinchState(){const [a,b]=[...touches.values()];return {d:Math.hypot(a.x-b.x,a.y-b.y)||1,x:(a.x+b.x)/2,y:(a.y+b.y)/2}}
addEventListener('pointermove',e=>{if(!touches.has(e.pointerId))return;touches.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(pinch&&touches.size===2){const c=pinchState();V.x+=c.x-pinch.x;V.y+=c.y-pinch.y;pinch.x=c.x;pinch.y=c.y;zoomAt(pinch.k*c.d/pinch.d,c.x,c.y)}});
const touchEnd=e=>{touches.delete(e.pointerId);if(touches.size<2&&pinch){pinch=null;save()}};
addEventListener('pointerup',touchEnd);addEventListener('pointercancel',touchEnd);
stage.addEventListener('pointerdown',e=>{
  if(e.pointerType==='touch'&&!e.target.closest('.node')){touches.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(touches.size===2){const c=pinchState();pinch={...c,k:V.k};$('marq').style.display='none';return}}
  if(pinch||e.target.closest('.node')||e.target.closest('#ex')||e.button!==0)return;
  if(editing)return;
  const sx=e.clientX,sy=e.clientY,vx=V.x,vy=V.y,pid=e.pointerId;let moved=false,pinched=false;
  const marq=e.shiftKey,mq=$('marq');
  try{stage.setPointerCapture(pid)}catch(_){}
  const mv=ev=>{if(ev.pointerId!==pid)return;if(pinch){pinched=true;return}const dx=ev.clientX-sx,dy=ev.clientY-sy;if(Math.abs(dx)+Math.abs(dy)>3)moved=true;
    if(marq){Object.assign(mq.style,{display:'block',left:Math.min(sx,ev.clientX)+'px',top:Math.min(sy,ev.clientY)+'px',width:Math.abs(dx)+'px',height:Math.abs(dy)+'px'})}
    else if(!pinched){stage.classList.add('panning');V.x=vx+dx;V.y=vy+dy;applyV()}};
  const up=ev=>{if(ev.pointerId!==pid)return;stage.removeEventListener('pointermove',mv);stage.removeEventListener('pointerup',up);stage.removeEventListener('pointercancel',up);stage.classList.remove('panning');mq.style.display='none';
    if(ev.type==='pointercancel'||pinched||pinch){save();return}
    if(marq&&moved){const a=toWorld(Math.min(sx,ev.clientX),Math.min(sy,ev.clientY)),b=toWorld(Math.max(sx,ev.clientX),Math.max(sy,ev.clientY));
      Object.values(S.nodes).forEach(n=>{if(n.x>a.x&&n.x<b.x&&n.y>a.y&&n.y<b.y)sel.add(n.id)});selEdge=null;updateSel()}
    else if(!moved&&linkFrom){const src=linkFrom;endLink();if(S.nodes[src])linkToEmpty(src,toWorld(ev.clientX,ev.clientY))}
    else if(!moved){sel.clear();selEdge=null;updateSel()} else save()};
  stage.addEventListener('pointermove',mv);stage.addEventListener('pointerup',up);stage.addEventListener('pointercancel',up);
});
stage.addEventListener('dblclick',e=>{if(e.target.closest('.node')||editing||linkFrom)return;const p=toWorld(e.clientX,e.clientY);commit();const id=mkNode('New idea',p.x,p.y);sel.clear();sel.add(id);save();render();startEdit(id)});
stage.addEventListener('wheel',e=>{e.preventDefault();if(e.ctrlKey||e.metaKey)zoomAt(V.k*Math.exp(-Math.max(-40,Math.min(40,e.deltaY))*.006),e.clientX,e.clientY);else{V.x-=e.deltaX;V.y-=e.deltaY;applyV();clearTimeout(stage._s);stage._s=setTimeout(save,300)}},{passive:false});

/* ---------- editing ---------- */
let editFin=null;
function startEdit(id){
  if(editing===id)return;
  if(editing&&editFin)editFin(true);   // finish the current edit first (it re-renders)
  if(dirty)render();
  if(linkFrom)endLink();
  const el=els[id];if(!el||!S.nodes[id])return;const tx=el.querySelector('.tx'),old=N(id).text,S0=S;editing=id;$('ctx').style.display='none';
  tx.contentEditable='true';tx.focus();const r=document.createRange();r.selectNodeContents(tx);const s=getSelection();s.removeAllRanges();s.addRange(r);
  let done=false;const fin=keep=>{if(done)return;done=true;editing=null;editFin=null;tx.contentEditable='false';tx.onblur=tx.onkeydown=tx.onpaste=null;const v=clip(tx.textContent);
    if(keep&&v&&v!==old&&S===S0&&S.nodes[id]){N(id).text=old;commit();N(id).text=v;if(id==='root')S.q=v;save()}
    render()};   // always re-render: this also flushes any render deferred while editing
  editFin=fin;
  tx.onkeydown=e=>{e.stopPropagation();if(e.isComposing)return;
    if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();fin(true)}
    else if(e.key==='Escape'){e.preventDefault();fin(false)}
    else if(e.key==='Tab'){e.preventDefault();fin(true);if(S.nodes[id])addChild(id)}};
  tx.onpaste=e=>{e.preventDefault();const t=clip((e.clipboardData||window.clipboardData).getData('text'));document.execCommand('insertText',false,t)};
  tx.onblur=()=>fin(true);
}
function addConnected(pid){
  const id=mkNode('New idea',0,0,{c:pid==='root'?nextColor():N(pid).c,seed:pid==='root'});
  link(pid,id);placeAround(pid,[id]);return id;
}
function nextColor(){const used=Object.values(S.nodes).filter(n=>n.seed).length;return used}
function addChild(pid){commit();const id=addConnected(pid);sel.clear();sel.add(id);save();render();relax([id]);render();startEdit(id)}
function addSibling(id){if(id==='root')return addChild('root');const {prev}=bfs();addChild(prev[id]||id)}
function delSel(){const ids=[...sel].filter(i=>i!=='root'&&S.nodes[i]);if(!ids.length){if(selEdge)delEdge();else if(sel.has('root'))toast('The question stays. Edit it instead.');return}
  commit();ids.forEach(i=>{delete S.nodes[i];S.edges=S.edges.filter(k=>!k.split('|').includes(i))});sel.clear();save();render();toast(ids.length>1?`Deleted ${ids.length} ideas`:'Deleted')}

/* ---------- layout ---------- */
function placeAround(pid,ids){
  const P=N(pid),{prev}=bfs();let base;
  if(pid==='root'){const ang=nbrs('root').filter(i=>!ids.includes(i)).map(i=>Math.atan2(N(i).y-P.y,N(i).x-P.x)).sort((a,b)=>a-b);
    if(!ang.length)base=-Math.PI/2;else{let best=0,bg=-1;for(let i=0;i<ang.length;i++){const a=ang[i],b=i+1<ang.length?ang[i+1]:ang[0]+2*Math.PI;if(b-a>bg){bg=b-a;best=a+(b-a)/2}}base=best}}
  else{const q=prev[pid]?N(prev[pid]):null;base=q?Math.atan2(P.y-q.y,P.x-q.x):Math.random()*6.28}
  const n=ids.length,spread=n>1?Math.min(Math.PI*.95,.5*(n-1)):0;
  ids.forEach((id,i)=>{const a=base-spread/2+(n>1?spread*i/(n-1):0),r=250+(i%2)*55;N(id).x=P.x+Math.cos(a)*r;N(id).y=P.y+Math.sin(a)*r});
}
function overlap(a,b,pad=22){const dx=b.x-a.x,dy=b.y-a.y,ox=((a._w||190)+(b._w||190))/2+pad-Math.abs(dx),oy=((a._h||56)+(b._h||56))/2+pad-Math.abs(dy);return ox>0&&oy>0?{dx,dy,ox,oy}:null}
function relax(ids,it=90){
  const all=Object.values(S.nodes),mov=new Set(ids);
  for(let t=0;t<it;t++){let any=false;
    ids.forEach(id=>{const a=N(id);if(!a)return;all.forEach(b=>{if(b===a)return;const o=overlap(a,b);if(!o)return;any=true;
      const both=mov.has(b.id)&&b.id!=='root',f=both?.5:1;
      if(o.ox<o.oy){const s=(o.dx>0?-1:1)*o.ox*f;a.x+=s;if(both)b.x-=s}else{const s=(o.dy>0?-1:1)*o.oy*f;a.y+=s;if(both)b.y-=s}})});
    if(!any)break}
}
// Animates only the drawn position (AP); the model keeps its final coordinates throughout, so
// saves, snapshots, relax() and the next grow never see half-way positions.
function animateFrom(ids,from){
  if(reduce){ids.forEach(setPos);drawEdges();return}
  const t0=performance.now();ids.forEach(i=>AP[i]={x:from.x,y:from.y});ids.forEach(setPos);
  (function st(t){const p=Math.min(1,(t-t0)/460),e=1-Math.pow(1-p,3);
    ids.forEach(i=>{const n=S.nodes[i];if(!n||!AP[i]){delete AP[i];return}if(p<1)AP[i]={x:from.x+(n.x-from.x)*e,y:from.y+(n.y-from.y)*e};else delete AP[i];setPos(i)});
    drawEdges();if(p<1)requestAnimationFrame(st);else placeCtx()})(t0);
}
let tidying=false;
function tidy(){
  if(tidying)return;tidying=true;commit();
  const S0=S,ns=Object.values(S.nodes);let f=0;Object.keys(AP).forEach(k=>delete AP[k]);
  (function step(){
    if(S!==S0){tidying=false;return}   // map was replaced (undo/import/new map) mid-animation
    for(let it=0;it<(reduce?70:1);it++){   // reduced motion: run the whole simulation in one go
    for(let s=0;s<3;s++){
      const F={};ns.forEach(n=>F[n.id]={x:0,y:0});
      for(let i=0;i<ns.length;i++)for(let j=i+1;j<ns.length;j++){const a=ns[i],b=ns[j];let dx=b.x-a.x,dy=b.y-a.y,d2=dx*dx+dy*dy+.01;if(d2>700*700)continue;const d=Math.sqrt(d2),rep=42000/d2;dx/=d;dy/=d;F[a.id].x-=dx*rep;F[a.id].y-=dy*rep;F[b.id].x+=dx*rep;F[b.id].y+=dy*rep}
      S.edges.forEach(k=>{const[a,b]=k.split('|'),A=N(a),B=N(b);if(!A||!B||!F[a]||!F[b])return;let dx=B.x-A.x,dy=B.y-A.y,d=Math.hypot(dx,dy)||1,str=(d-(a==='root'||b==='root'?300:230))*.045;dx/=d;dy/=d;F[a].x+=dx*str;F[a].y+=dy*str;F[b].x-=dx*str;F[b].y-=dy*str});
      const R=N('root');ns.forEach(n=>{if(n.id==='root'||!S.nodes[n.id])return;const c=Math.min(12,Math.max(-12,F[n.id].x+(R.x-n.x)*.002)),d=Math.min(12,Math.max(-12,F[n.id].y+(R.y-n.y)*.002));n.x+=c;n.y+=d});
    }
    relax(ns.filter(n=>n.id!=='root').map(n=>n.id),2);
    }
    ns.forEach(n=>setPos(n.id));drawEdges();
    if(!reduce&&++f<70)requestAnimationFrame(step);else{relax(ns.filter(n=>n.id!=='root').map(n=>n.id),60);ns.forEach(n=>setPos(n.id));drawEdges();tidying=false;save();fit()}
  })();
}

/* ---------- AI ---------- */
// Strip list markers ("- ", "* ", "1. ", "2) ") but keep real leading digits ("3D-printed", "24-hour").
const unlist=t=>clip(t).replace(/^(?:[-*•–]\s*|\d{1,2}[.)]\s+)/,'').replace(/^["“'](.*)["”']$/,'$1').trim();
async function ask(prompt){
  const s=sample;if(!s)throw{code:'none'};
  let v;
  try{if(typeof s.json!=='function')throw new TypeError('no json');v=await s.json(prompt)}
  catch(e){if(e&&e.code)throw e;const r=await s(prompt);const txt=typeof r==='string'?r:(r&&r.text)||'';const m=txt.match(/\[[\s\S]*\]/);
    try{v=m?JSON.parse(m[0]):[]}catch(_){v=[]}}
  if(!Array.isArray(v))v=(v&&typeof v==='object'&&(Array.isArray(v.ideas)?v.ideas:Object.values(v).find(Array.isArray)))||[];
  const seen=new Set();
  return v.map(x=>x&&typeof x==='object'?(x.idea||x.text||x.title||x.name||''):(typeof x==='string'||typeof x==='number'?x:''))
    .map(unlist).filter(t=>{const k=t.toLowerCase();if(!t||seen.has(k))return false;seen.add(k);return true});
}
function aiError(e,what){
  if(e&&e.code==='not_granted'){sample=null;growing=false;ui();toast('Idea generation was not allowed. You can still add ideas by hand.')}
  else if(e&&e.code==='rate_limited')toast('Generating too fast. Wait a moment, then try again.');
  else if(e&&e.code==='none')toast('Idea generation is off in this view. You can still add ideas by hand.');
  else if(e&&e.code==='stale'){}
  else toast(what+': '+(e&&e.message||'unknown error'));
}
const head=()=>`You are a brainstorming partner in the GENERATION stage of design thinking. Rules: defer judgment (no feasibility talk, no criticism), go for quantity, welcome wild ideas, build on others' ideas ("Yes, and…").
Question at the centre of the map: ${S.q}
${S.ctx?'Context: '+S.ctx+'\n':''}`;
async function grow(id,mode='yes',n=4,limit=Infinity){
  if(!sample){toast('Idea generation is off in this view. You can still add ideas by hand.');throw{code:'none'}}
  if(!S.nodes[id]||busy.has(id))return;
  const node=N(id),{prev}=bfs(),ep=epoch;
  const near=nbrs(id).map(i=>N(i).text);
  const prompt=head()+`Path from the question to this idea: ${pathTo(id,prev).join(' → ')}
Idea to grow from: "${node.text}"
Already connected to it (don't repeat): ${near.join(' | ')||'nothing yet'}
Task: ${id==='root'?'Generate fresh, distinct directions that answer the question.':MODES[mode].ins}
Generate ${n} new ideas. Each one a vivid, specific phrase of 14 words or fewer. No numbering, no explanations.
Return only a JSON array of strings.`;
  busy.add(id);render();
  try{
    let ideas=await ask(prompt);
    if(ep!==epoch)throw{code:'stale'};            // a new map was started / imported meanwhile
    const cur=S.nodes[id];if(!cur)return;         // deleted (or undone away) while generating
    const have=new Set(nbrs(id).map(i=>N(i).text.toLowerCase()));
    ideas=ideas.filter(t=>!have.has(t.toLowerCase())).slice(0,Math.max(0,Math.min(n+1,limit)));
    if(!ideas.length){cur._dry=(cur._dry||0)+1;toast('Nothing came back for that idea. Try another mode.');return}
    commit();
    const ids=ideas.map(t=>{const nid=mkNode(t,0,0,{ai:true,c:id==='root'?nextColor():cur.c});if(id==='root')N(nid).seed=true;link(id,nid);return nid});
    placeAround(id,ids);busy.delete(id);render();relax(ids);render();animateFrom(ids,{x:cur.x,y:cur.y});save();
  }catch(e){aiError(e,'Could not generate ideas');throw e}
  finally{if(busy.delete(id))render()}
}
async function combine(){
  const ids=[...sel].filter(i=>S.nodes[i]);if(ids.length<2)return;
  if(!sample)return toast('Idea generation is off in this view.');const ep=epoch;
  const cx=ids.reduce((a,i)=>a+N(i).x,0)/ids.length,cy=ids.reduce((a,i)=>a+N(i).y,0)/ids.length;
  commit();const hub=mkNode(ids.map(i=>N(i).text.split(/\s+/).slice(0,3).join(' ')).join(' + '),cx,cy+40,{c:N(ids[0]).c});
  ids.forEach(i=>link(i,hub));sel.clear();sel.add(hub);render();relax([hub]);render();save();
  const prompt=head()+`Combine these ideas into hybrids, merging the most interesting part of each:
${ids.map(i=>'- '+N(i).text).join('\n')}
Generate 4 hybrid ideas, each a vivid, specific phrase of 16 words or fewer.
Return only a JSON array of strings.`;
  busy.add(hub);render();
  try{const ideas=(await ask(prompt)).slice(0,5);
    if(ep!==epoch||!S.nodes[hub])return;          // hub deleted / undone, or map replaced
    if(!ideas.length){toast('Nothing came back. Try combining different ideas.');return}
    commit();                                      // hybrids are their own undo step
    const H=N(hub),nids=ideas.map(t=>{const n=mkNode(t,0,0,{ai:true,c:H.c});link(hub,n);return n});
    placeAround(hub,nids);busy.delete(hub);render();relax(nids);render();animateFrom(nids,{x:H.x,y:H.y});save()}
  catch(e){aiError(e,'Could not combine')}finally{if(busy.delete(hub))render()}
}
function pickTarget(){
  const {dist,prev,adj}=bfs(),ids=Object.keys(S.nodes);
  const kids={};ids.forEach(i=>{if(prev[i])(kids[prev[i]]=kids[prev[i]]||[]).push(i)});
  const starred=ids.filter(i=>N(i).star);
  const scope=new Set(sel.size?[...sel]:starred.length?starred:[]);
  const inScope=i=>{if(!scope.size)return true;let c=i,g=0;while(c&&g++<60){if(scope.has(c))return true;c=prev[c]}return false};
  let pool=ids.filter(i=>inScope(i)&&(N(i)._dry||0)<2&&!busy.has(i)&&(i==='root'?adj.root.length===0:!(kids[i]&&kids[i].length)));
  if(!pool.length)return null;
  const d=i=>dist[i]==null?99:dist[i];const m=Math.min(...pool.map(d));pool=pool.filter(i=>d(i)===m);
  return pool[Math.floor(Math.random()*pool.length)];
}
const MODEKEYS=['yes','yes','wild','real','flip'];
async function growLoop(){
  const me=++loopId;let modeIx=0;   // only the newest loop may run: stop+start must not leave two going
  const live=()=>growing&&me===loopId;
  if(loopP)await loopP.catch(()=>{}); // let a request from a just-stopped loop land first (no overlapping calls)
  while(live()){
    if(count()>=CAP){toast(`Your map has ${CAP} ideas, so growing paused. Tidy or prune it, then keep going.`);break}
    const t=pickTarget();if(!t){toast('Every branch in focus has grown. Select or star a node to focus.');break}
    try{await (loopP=grow(t,MODEKEYS[modeIx++%MODEKEYS.length],3,CAP-count()))}catch(e){break}finally{loopP=null}
    await new Promise(r=>setTimeout(r,250));
  }
  if(me===loopId){growing=false;ui()}
}
function stopGrowing(){growing=false;loopId++;if(S)ui()}

/* ---------- chrome ---------- */
function toast(m){const t=$('toast');t.textContent=m;t.classList.add('on');clearTimeout(t._t);t._t=setTimeout(()=>t.classList.remove('on'),2600)}
function ui(){
  $('undo').disabled=!undoS.length;$('redo').disabled=!redoS.length;
  const g=$('grow');g.classList.toggle('on',growing);g.querySelector('.bub').innerHTML=ic(growing?'stop':'play','i');
  g.disabled=!sample;$('growl').textContent=growing?'Stop growing':(sel.size?'Grow selected':(Object.values(S.nodes).some(n=>n.star)?'Grow starred':'Keep growing'));
  $('add').innerHTML=ic('plus')+'<span class="lbl">Add idea</span>';
  const all=Object.values(S.nodes),ai=all.filter(n=>n.ai).length;
  $('crumbq').textContent=S.q;
  $('meta').innerHTML=`<b>${all.length-1}</b> ideas<span class="gx"> · ${ai} generated${sample?'':' · generation off'}</span>`;
}
function placeCtx(){
  const c=$('ctx');if(!S||editing||dragSet.size||(!sel.size&&!selEdge)){c.style.display='none';return}
  const ids=[...sel].filter(i=>els[i]&&S.nodes[i]);
  if(!ids.length){c.style.display='none';return}
  let html='';
  if(ids.length===1){const id=ids[0],n=N(id);
    html=Object.entries(MODES).map(([k,m])=>`<button class="gen" data-g="${k}" ${!sample||busy.has(id)?'disabled':''}>${k==='yes'?ic('branch'):''}${m.label}</button>`).join('')+
      `<span class="vr"></span><button data-a="child" title="Add your own (Tab)">${ic('plus')}</button><button data-a="linkmode" class="${linkFrom===id?'on':''}" title="Link to another idea (L)">${ic('link')}${linkFrom===id?'Cancel':'Link'}</button><button data-a="edit" title="Edit (F2)">${ic('edit')}</button>`+
      (id!=='root'?`<button data-a="star" title="Star — growing focuses here (S)">${ic('star')}${n.star?'Unstar':''}</button><button data-a="del" title="Delete">${ic('trash')}</button>`:'');
  }else{
    const pair=ids.length===2,linked=pair&&hasEdge(ids[0],ids[1]);
    html=`<button class="gen" data-a="combine" ${sample?'':'disabled'}>${ic('merge')}Combine ${ids.length}</button><span class="vr"></span>`+
      (pair?(linked?`<button data-a="unlink">${ic('unlink')}Unlink these</button>`:`<button data-a="link">${ic('link')}Link these</button>`)
           :`<button data-a="link" title="Link them in a chain">${ic('link')}Link</button><button data-a="unlink" title="Remove links between them">${ic('unlink')}Unlink</button>`)+
      `<button data-a="del" title="Delete">${ic('trash')}</button>`;
  }
  // Only touch the DOM when the toolbar changes, so a click isn't lost to a mid-click rebuild.
  if(c._h!==html){c.innerHTML=html;c._h=html}c.style.display='flex';
  let x0=1e9,y0=1e9,x1=-1e9;ids.forEach(i=>{const r=els[i].getBoundingClientRect();x0=Math.min(x0,r.left);x1=Math.max(x1,r.right);y0=Math.min(y0,r.top)});
  const w=c.offsetWidth;let top=y0-c.offsetHeight-16;if(top<64){let yb=-1e9;ids.forEach(i=>yb=Math.max(yb,els[i].getBoundingClientRect().bottom));top=yb+16}
  top=Math.max(8,Math.min(innerHeight-c.offsetHeight-8,top));
  c.style.left=Math.max(w/2+8,Math.min(innerWidth-w/2-8,(x0+x1)/2))+'px';c.style.top=top+'px';
}
// The toolbar appears on pointerup; on touch screens the follow-up compatibility click lands
// on whatever is now under the finger. Only accept clicks that began on the toolbar
// (or keyboard activation, detail===0).
let ctxDown=false;
$('ctx').addEventListener('pointerdown',e=>{e.stopPropagation();ctxDown=true});
$('ctx').addEventListener('click',e=>{
  const ok=ctxDown||e.detail===0;ctxDown=false;if(!ok)return;
  const b=e.target.closest('button');if(!b||b.disabled)return;const ids=[...sel].filter(i=>S.nodes[i]),id=ids[0];if(!id)return;
  if(b.dataset.g)return grow(id,b.dataset.g,4).catch(()=>{});
  const a=b.dataset.a;
  if(a==='child')addChild(id);
  else if(a==='edit')startEdit(id);
  else if(a==='linkmode')beginLink(id);
  else if(a==='star'){commit();N(id).star=!N(id).star;save();render()}
  else if(a==='del')delSel();
  else if(a==='combine')combine();
  else if(a==='link'){const before=S.edges.length,pre=snap();for(let i=1;i<ids.length;i++)link(ids[i-1],ids[i]);
    if(S.edges.length===before){toast('Already linked');return}commit(pre);save();render();toast(ids.length>2?'Linked in a chain':'Linked')}
  else if(a==='unlink'){const before=S.edges.length,pre=snap();S.edges=S.edges.filter(k=>{const[x,y]=k.split('|');return!(sel.has(x)&&sel.has(y))});
    if(S.edges.length===before){toast('No links between these');return}commit(pre);save();render();toast('Unlinked')}
});

$('undo').innerHTML=ic('undo');$('redo').innerHTML=ic('redo');$('zin').innerHTML=ic('plus');$('zout').innerHTML=ic('minus');$('fit').innerHTML=ic('fit');
$('tidy').innerHTML=ic('tidy')+'<span class="lbl">Tidy</span>';$('export').innerHTML=ic('out')+'<span class="lbl">Export</span>';$('lcancel').innerHTML=ic('x');
$('lcancel').onclick=()=>endLink();
$('undo').onclick=undo;$('redo').onclick=redo;
$('zin').onclick=()=>zoomAt(V.k*1.2,innerWidth/2,innerHeight/2);$('zout').onclick=()=>zoomAt(V.k/1.2,innerWidth/2,innerHeight/2);
$('fit').onclick=()=>fit();$('tidy').onclick=tidy;
$('add').onclick=()=>{const o=sel.size===1?[...sel][0]:null;if(o)return addChild(o);const p=toWorld(innerWidth/2,innerHeight/2);commit();const id=mkNode('New idea',p.x+(Math.random()*80-40),p.y+(Math.random()*80-40));sel.clear();sel.add(id);save();render();relax([id]);render();startEdit(id)};
$('grow').onclick=()=>{if(growing)return stopGrowing();if(!sample)return;growing=true;ui();growLoop()};

/* export */
let exMode='out';
function outline(){const {prev,dist}=bfs(),kids={};Object.keys(S.nodes).forEach(i=>{if(prev[i])(kids[prev[i]]=kids[prev[i]]||[]).push(i)});
  let o='';(function w(id,d){o+=(d?'  '.repeat(d-1)+'- ':'# ')+N(id).text+(N(id).star?' ★':'')+'\n';(kids[id]||[]).forEach(c=>w(c,d+1))})('root',0);
  const loose=Object.keys(S.nodes).filter(i=>dist[i]==null);if(loose.length){o+='\nUnlinked ideas\n';loose.forEach(i=>o+='- '+N(i).text+'\n')}return o}
function showEx(){$('extext').value=exMode==='out'?outline():JSON.stringify({q:S.q,ctx:S.ctx,seq:S.seq,edges:S.edges,nodes:Object.fromEntries(Object.entries(S.nodes).map(([k,n])=>[k,{id:n.id,text:n.text,x:Math.round(n.x),y:Math.round(n.y),c:n.c,ai:n.ai,seed:n.seed,star:n.star,r:n.r}]))});
  $('tOut').classList.toggle('on',exMode==='out');$('tJson').classList.toggle('on',exMode==='json')}
$('export').onclick=()=>{exMode='out';showEx();$('exp').hidden=false};
$('tOut').onclick=()=>{exMode='out';showEx()};$('tJson').onclick=()=>{exMode='json';showEx()};
$('exClose').onclick=()=>$('exp').hidden=true;
$('exCopy').onclick=async()=>{try{await navigator.clipboard.writeText($('extext').value);toast('Copied')}catch(e){$('extext').select();toast('Copying was blocked. The text is selected, so press Ctrl+C.')}};
$('exImp').onclick=()=>{let v=null;try{v=clean(JSON.parse($('extext').value))}catch(e){}
  if(!v)return toast('That isn\'t a map file. Paste one exported from here, then choose Import.');
  stopGrowing();epoch++;busy.clear();endLink();commit();S=v;sel.clear();selEdge=null;save();render();fit();$('exp').hidden=true;toast('Imported')};

/* keyboard */
document.addEventListener('keydown',e=>{
  if(!$('exp').hidden&&e.key==='Escape'){$('exp').hidden=true;return}
  if(!S||!$('setup').hidden||!$('exp').hidden||editing)return;
  if(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||e.target.isContentEditable)return;
  const mod=e.ctrlKey||e.metaKey,k=e.key,lk=k.length===1?k.toLowerCase():k,o=sel.size===1&&S.nodes[[...sel][0]]?[...sel][0]:null;
  if(k==='Escape'&&linkFrom){endLink();return}
  if(mod&&k.toLowerCase()==='z'){e.preventDefault();e.shiftKey?redo():undo();return}
  if(mod&&k.toLowerCase()==='y'){e.preventDefault();redo();return}
  if(mod&&k.toLowerCase()==='a'){e.preventDefault();Object.keys(S.nodes).forEach(i=>sel.add(i));render();return}
  if(k==='Escape'){sel.clear();selEdge=null;updateSel();return}
  if(k==='Delete'||k==='Backspace'){e.preventDefault();delSel();return}
  if(!o||mod||e.altKey)return;
  if(k==='Tab'){e.preventDefault();addChild(o)}
  else if(k==='Enter'){e.preventDefault();addSibling(o)}
  else if(k==='F2'||lk==='e'){e.preventDefault();startEdit(o)}
  else if(lk==='g'){grow(o,'yes',4).catch(()=>{})}
  else if(lk==='l'){e.preventDefault();beginLink(o)}
  else if(lk==='s'&&o!=='root'){commit();N(o).star=!N(o).star;save();render()}
});
addEventListener('resize',()=>placeCtx());

/* ---------- setup ---------- */
let seeds=[];
function drawChips(){
  const box=$('chips');box.querySelectorAll('.chip').forEach(c=>c.remove());
  seeds.forEach((s,i)=>{const c=document.createElement('span');c.className='chip';c.style.setProperty('--c',COLORS[i%COLORS.length]);c.style.setProperty('--r',((i*37%5)-2)*.6+'deg');
    c.innerHTML=`<span></span><button title="Remove" aria-label="Remove">${ic('x')}</button>`;c.firstChild.textContent=s;
    c.querySelector('button').onclick=()=>{seeds.splice(i,1);drawChips()};box.insertBefore(c,$('seedin'))});
}
function addSeeds(txt){txt.split(/\n|;/).map(unlist).filter(Boolean).forEach(s=>seeds.push(s));drawChips()}
$('seedin').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();if(e.target.value.trim()){addSeeds(e.target.value);e.target.value=''}}else if(e.key==='Backspace'&&!e.target.value&&seeds.length){seeds.pop();drawChips()}});
$('seedin').addEventListener('paste',e=>{const t=(e.clipboardData||window.clipboardData).getData('text');if(/\n/.test(t)){e.preventDefault();addSeeds(e.target.value+'\n'+t);e.target.value=''}});
const growQ=()=>{const q=$('q');q.style.height='auto';q.style.height=q.scrollHeight+'px'};
$('q').addEventListener('input',growQ);$('q').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.isComposing){e.preventDefault();$('seedin').focus()}});
$('ctxtog').onclick=()=>{const t=$('sctx');t.style.display=t.style.display==='block'?'none':'block';if(t.style.display==='block')t.focus()};
function seedList(){return SEED&&Array.isArray(SEED.seeds)?SEED.seeds.filter(x=>typeof x==='string'||typeof x==='number').map(unlist).filter(Boolean):[]}
function openSetup(){
  endLink();
  // With no map yet, prefill from a seed block that couldn't boot (e.g. a question but no seeds).
  const pre=S||(SEED&&typeof SEED==='object'?{q:clip(SEED.q),ctx:clip(SEED.ctx)}:null);
  $('q').value=pre?pre.q||'':'';$('sctx').value=pre?pre.ctx||'':'';$('sctx').style.display=pre&&pre.ctx?'block':'none';
  seeds=S?[]:seedList();drawChips();$('serr').textContent='';
  $('below').innerHTML=S?`<button id="backBtn">Back to your map</button><span class="hint">Mapping again starts a fresh map. Use Undo on the map to get the old one back.</span>`:'';
  if(S)$('backBtn').onclick=()=>{$('setup').hidden=true};
  $('setup').hidden=false;requestAnimationFrame(()=>{growQ();if(!$('setup').contains(document.activeElement))$('q').focus()});
}
$('home').onclick=openSetup;
$('goBtn').onclick=()=>{
  const pending=$('seedin').value.trim();if(pending){addSeeds(pending);$('seedin').value=''}
  const q=$('q').value.trim();
  if(!q){$('serr').textContent='Write the question you want to explore.';$('q').focus();return}
  if(!seeds.length){$('serr').textContent='Add at least one seed idea to start a branch.';$('seedin').focus();return}
  buildMap(q,$('sctx').value.trim(),seeds);
};
function buildMap(q,ctx,seeds){
  const pre=S?snap():null;
  stopGrowing();epoch++;busy.clear();endLink();Object.keys(AP).forEach(k=>delete AP[k]);
  S={q,ctx,seq:0,nodes:{},edges:[]};
  S.nodes.root={id:'root',text:q,x:0,y:0,c:null,ai:false,seed:false,star:false,r:0};
  const ids=seeds.map((s,i)=>{const id=mkNode(s,0,0,{c:i,seed:true});link('root',id);return id});
  const tall=innerHeight>innerWidth*1.2,rx=tall?190:300,ry=tall?340:230;   // portrait phones: lay seeds out tall, not wide
  ids.forEach((id,i)=>{const a=-Math.PI/2+i*2*Math.PI/ids.length;N(id).x=Math.cos(a)*rx;N(id).y=Math.sin(a)*ry});
  if(pre)commit(pre);sel.clear();selEdge=null;
  $('setup').hidden=true;render();relax(ids);render();V={x:innerWidth/2,y:innerHeight/2,k:1};applyV();fit(false);animateFrom(ids,{x:0,y:0});save();
}

/* ---------- boot ---------- */
load();
const seedSeeds=seedList();
if(S){applyV();render()}else if(SEED&&clip(SEED.q)&&seedSeeds.length){buildMap(clip(SEED.q),clip(SEED.ctx),seedSeeds)}else openSetup();
(async()=>{try{sample=window.claude&&typeof window.claude.use==='function'?await window.claude.use('sample'):null}catch(e){sample=null}if(S){ui();placeCtx()}})();
