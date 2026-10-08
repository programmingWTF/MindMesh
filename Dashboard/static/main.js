
var API_BASE=window.MINDMESH_API||"";
var META={
 OpenClaw:{c:"#D9483C",i:"openclaw.png"},
 ClaudeCode:{c:"#D97757",i:"claude.svg"},
 GitHubCopilot:{c:"#A371F7",i:"githubcopilot.svg"},
 Qoder:{c:"#C4C4CC",i:"qoder.png"},
 KimiCode:{c:"#2A7FE0",i:"kimi.png"},
 ZCode:{c:"#D6D3D1",i:"zcode.png"},
 DeepSeekHarness:{c:"#4D6BFE",i:"deepseek.png"},
 WorkBuddy:{c:"#0EC9A3",i:"workbuddy.png"},
 Reasonix:{c:"#0957E7",i:"reasonix.png"},
 Pi:{c:"#4D9ABF",i:"pi.png"},
 OpenCode:{c:"#AEB6BF",i:"opencode.svg"},
 Cursor:{c:"#E5E7EB",i:"cursor.png"},
 Antigravity:{c:"#3E87EA",i:"antigravity.png"},
 Codex:{c:"#10A37F",i:"codex.svg"},
 Gemini:{c:"#7C6FE0",i:"gemini.png"}
};
function hexA(h,a){var r=parseInt(h.slice(1,3),16),g=parseInt(h.slice(3,5),16),b=parseInt(h.slice(5,7),16);return "rgba("+r+","+g+","+b+","+a+")";}
var HUES=[16,205,142,275,32,330,190,55,255,105,20,300,170];
var DATA=null, TMR=null;
var S={q:"",range:"all",agents:{},hideIdle:false,exp:{}};
function hue(n){var h=0;for(var i=0;i<n.length;i++){h=(h*31+n.charCodeAt(i))%100000;}return HUES[h%HUES.length];}
function color(n){var m=META[n];if(m&&m.c)return m.c;return "hsl("+hue(n)+",88%,62%)";}
var ICONV=6;
function iconOf(n){var m=META[n];return (m&&m.i)?("/icons/"+m.i+"?v="+ICONV):null;}
function isSvg(p){return p&&p.indexOf(".svg")>0;}
function initial(n){return (n||"?").charAt(0).toUpperCase();}
/* 2026-10-08: agent 徽章 HTML 统一在这里生成（原本 main.js 和 extra.js 各写一份） */
window.badgeHTML=function(agent,col){
 col=col||color(agent);var ic=iconOf(agent);
 if(ic&&isSvg(ic)){return "<span class=badge style=\"background:"+hexA(col,0.20)+";color:"+col+";border:1px solid "+hexA(col,0.45)+"\"><span class=ic style=\"width:12px;height:12px;display:inline-block;vertical-align:-2px;margin-right:5px;-webkit-mask-image:url("+ic+");mask-image:url("+ic+")\"></span>"+esc(agent)+"</span>";}
 if(ic){return "<span class=badge style=\"background:"+hexA(col,0.20)+";color:"+col+";border:1px solid "+hexA(col,0.45)+"\"><img src=\""+ic+"\" alt=\"\" style=\"width:12px;height:12px;border-radius:3px;vertical-align:-2px;margin-right:5px;object-fit:cover\">"+esc(agent)+"</span>";}
 return "<span class=badge style=\"background:"+col+"\">"+esc(agent)+"</span>";
};
function rel(iso){if(!iso)return "never";var t=new Date(iso).getTime();if(isNaN(t))return "?";
 var s=(Date.now()-t)/1000;
 if(s<60)return Math.floor(s)+"s ago";
 if(s<3600)return Math.floor(s/60)+"m ago";
 if(s<86400)return Math.floor(s/3600)+"h ago";
 return Math.floor(s/86400)+"d ago";}
function esc(s){return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
function daysAgo(n){var d=new Date(Date.now()-n*86400000);return d.toISOString().slice(0,10);}
function selectedList(){return Object.keys(S.agents).filter(function(k){return S.agents[k];});}
function passAgent(name){var L=selectedList();return L.length===0||L.indexOf(name)>=0;}
function filtered(){
 if(!DATA)return [];
 var list=DATA.commits.filter(function(c){return passAgent(c.agent);});
 if(S.range!=="all"){var cut=0;
  if(S.range==="24h")cut=Date.now()-86400000;
  else if(S.range==="7d")cut=Date.now()-7*86400000;
  else if(S.range==="30d")cut=Date.now()-30*86400000;
  list=list.filter(function(c){return new Date(c.date).getTime()>=cut;});}
 if(S.q){var q=S.q.toLowerCase();
  list=list.filter(function(c){
   if((c.subject||"").toLowerCase().indexOf(q)>=0)return true;
   if((c.agent||"").toLowerCase().indexOf(q)>=0)return true;
   if((c.hash||"").toLowerCase().indexOf(q)>=0)return true;
   for(var i=0;i<c.files.length;i++){if(c.files[i].toLowerCase().indexOf(q)>=0)return true;}
   return false;});}
 return list;
}
function spark(arr,col){var w=210,hh=28,mx=Math.max.apply(null,arr.concat([1])),n=arr.length,bw=w/n,bars="";
 for(var i=0;i<n;i++){var v=arr[i],bh=v>0?(3+(v/mx)*(hh-6)):1.2;
  bars+="<rect x="+(i*bw+0.6).toFixed(1)+" y="+(hh-bh).toFixed(1)+" width="+(bw-1.2).toFixed(1)+" height="+bh.toFixed(1)+" rx=1 fill="+col+" opacity="+(v>0?0.92:0.15)+"/>";}
 return "<svg class=spark viewBox=\"0 0 "+w+" "+hh+"\" preserveAspectRatio=none>"+bars+"</svg>";}
function stat(k,v){return "<div class=stat><div class=k>"+k+"</div><div class=\"v mono\">"+v+"</div></div>";}
function pill(cls,txt){return "<div class=pill><span class=\"dot "+cls+"\"></span>"+txt+"</div>";}
function renderHead(){
 var d=DATA,r=d.repo,h=d.health;
 document.getElementById("gen").textContent="· 更新于 "+d.generated;
 document.getElementById("stats").innerHTML=
  stat("Commits",r.commits)+stat("Files",r.tracked_files.toLocaleString())+stat("Repo",r.git_size)+stat("Branch",r.branch);
 var lp=(h.links_ok===h.links_total)?"ok":(h.links_ok>0?"warn":"bad");
 var src=(d.source&&d.source.kind==="bare")?"数据源 Forgejo 裸仓库（零延迟）":"数据源 工作副本";
 document.getElementById("pills").innerHTML=
  pill("ok",src)+
  (h.links_total>0?pill(lp,"记忆文件 "+h.links_ok+"/"+h.links_total):"")+
  pill("ok","最后提交 "+rel(r.last_commit))+
  (h.maintenance?pill("ok","维护报告 "+h.maintenance):"");
}
function renderAgents(){
 var d=DATA,sel=selectedList();
 var list=d.agents.slice();
 list.sort(function(a,b){
   var sa=passAgent(a.name)?0:1, sb=passAgent(b.name)?0:1;
   if(sa!==sb)return sa-sb; return b.commits-a.commits;});
 var html="";
 list.forEach(function(a){
  if(a.commits===0 && S.hideIdle)return;
  var c=color(a.name), isSel=!!S.agents[a.name], dim=(sel.length>0&&!isSel);
  html+="<div class=\"agent"+(isSel?" sel":"")+(dim?" dim":"")+"\" data-agent=\""+esc(a.name)+"\">";
  html+="<div class=glow style=\"background:"+c+"\"></div>";
  var ic=iconOf(a.name);
  html+="<div class=top>";
  if(ic&&isSvg(ic)){html+="<div class=av style=\"background:"+hexA(c,0.16)+";border:1px solid "+hexA(c,0.42)+";color:"+c+"\"><span class=ic style=\"-webkit-mask-image:url("+ic+");mask-image:url("+ic+")\"></span></div>";}
  else if(ic){html+="<div class=av style=\"padding:0;overflow:hidden;background:"+hexA(c,0.12)+";border:1px solid "+hexA(c,0.35)+"\"><img src=\""+ic+"\" alt=\"\" style=\"width:100%;height:100%;object-fit:cover;display:block\"></div>";}
  else{html+="<div class=av style=\"background:"+c+"\">"+initial(a.name)+"</div>";}
  html+="<div><div class=nm>"+esc(a.name)+"</div><div class=meta>"+(a.commits?("活跃 "+rel(a.last)):"待接入")+"</div></div></div>";
  html+="<div class=nums><div class=num><div class=v>"+a.commits+"</div><div class=k>Commits</div></div>";
  html+="<div class=num><div class=v>"+a.unique_files+"</div><div class=k>Files</div></div>";
  html+="<div class=num><div class=v>"+a.files_touched+"</div><div class=k>Touches</div></div></div>";
  if(a.commits>0){html+=spark(a.spark,c);}
  html+="</div>";});
 document.getElementById("agents").innerHTML=html||"<div class=empty>没有匹配的 Agent</div>";
 var nodes=document.querySelectorAll(".agent");
 for(var i=0;i<nodes.length;i++){(function(n){
   var nm=n.getAttribute("data-agent");
   if(nm) n.onclick=function(){S.agents[nm]=!S.agents[nm];if(!S.agents[nm])delete S.agents[nm];sync();render();};})(nodes[i]);}
 var sb=document.getElementById("selbar");
 if(sel.length){sb.innerHTML="<div class=pills style=\"margin:0 0 14px\"><span class=pill style=\"color:#ffb08a;border-color:rgba(255,122,69,.5)\">已选 "+sel.length+" 个 Agent</span>"+
   sel.map(function(x){return "<span class=chip style=\"cursor:pointer\" data-un=\""+esc(x)+"\">"+esc(x)+" ✕</span>";}).join("")+"</div>";
  var us=document.querySelectorAll("[data-un]");
  for(var j=0;j<us.length;j++){(function(n){n.onclick=function(){delete S.agents[n.getAttribute("data-un")];sync();render();};})(us[j]);}}
 else sb.innerHTML="";
}
function renderChart(){
 var d=DATA; if(!d||!d.daily||!d.daily.length) return;
 var rows=d.daily, mode=S.chartMode||"agent", partOf=(S.chartParts||{});
 rows.forEach(function(r){
  var parts=[];
  if(mode==="agent"){ Object.keys(r.by).forEach(function(k){ if(passAgent(k)&&r.by[k]>0) parts.push([k,r.by[k]]); }); }
  else { (d.cats||[]).forEach(function(k){ var v=(r.bycat||{})[k]; if(v>0) parts.push([k,v]); }); }
  parts.sort(function(a,b){ return b[1]-a[1]; });
  var t=0; parts.forEach(function(p){ t+=p[1]; });
  var shown=[];
  if(partOf&&partOf.type===mode&&partOf.key){ parts.forEach(function(p){ if(p[0]===partOf.key) shown.push(p); }); }
  if(!shown.length) shown=parts;
  var st=0; shown.forEach(function(p){ st+=p[1]; });
  r._parts=shown; r._t=(partOf&&partOf.type===mode&&partOf.key)?st:t;
 });
 var max=1,sum=0;
 rows.forEach(function(r){ if(r._t>max)max=r._t; sum+=r._t; });
 document.getElementById("chartTotal").textContent=sum;
 var yh="";
 [max, Math.round(max/2), 0].forEach(function(v){ yh+="<span>"+v+"</span>"; });
 document.getElementById("yax").innerHTML=yh;
 document.getElementById("gridlines").innerHTML="<i></i><i></i><i></i>";
 var ph="";
 rows.forEach(function(r,i){
  ph+="<div class=bcol data-i=\""+i+"\">";
  r._parts.forEach(function(pr){
   var col = mode==="agent" ? color(pr[0]) : catColor(pr[0]);
   var h = max>0 ? (pr[1]/max)*100 : 0;
   ph+="<div class=bseg style=\"height:"+h.toFixed(2)+"%;background:"+col+"\"></div>";
  });
  ph+="</div>";
 });
 var plot=document.getElementById("plot"); plot.innerHTML=ph;
 var xh="", n=rows.length-1;
 [0, Math.round(n/3), Math.round(n*2/3), n].forEach(function(i){
  if(i<0||i>n) return;
  xh+="<span style=\"left:"+((i/Math.max(1,n))*100).toFixed(2)+"%\">"+rows[i].date.slice(5)+"</span>";
 });
 document.getElementById("xax").innerHTML=xh;
 var cols=plot.querySelectorAll(".bcol");
 for(var i=0;i<cols.length;i++){(function(el){
   el.onmouseenter=function(){ chartTip(el, rows[+el.getAttribute("data-i")], mode); };
   el.onmouseleave=function(){ chartTipHide(); };
 })(cols[i]);}
}
function catColor(k){ var m={"记忆":"#FF7A45","技能库":"#A371F7","脚本":"#10B981","文档":"#38BDF8","其他":"#8B93A1"}; return m[k]||"#8B93A1"; }
function chartTip(el,row,mode){
 var wrap=document.getElementById("cwrap"), line=document.getElementById("curline"), tip=document.getElementById("chartTip");
 var er=el.getBoundingClientRect(), wr=wrap.getBoundingClientRect();
 var x=er.left-wr.left+er.width/2;
 line.style.left=x+"px"; line.style.display="block";
 var h="<div class=th><span>"+row.date.slice(5)+"</span><span class=tv>"+row._t+"</span></div>";
 if(!row._parts.length){ h+="<div class=tr><span class=lb>（无活动）</span><span class=vl>0</span></div>"; }
 row._parts.forEach(function(pr){
  var col = mode==="agent" ? color(pr[0]) : catColor(pr[0]);
  h+="<div class=tr><span class=sq style=\"background:"+col+"\"></span><span class=lb>"+esc(pr[0])+"</span><span class=vl>"+pr[1]+"</span></div>";
 });
 tip.innerHTML=h; tip.style.display="block";
 var tw=tip.offsetWidth||200;
 var left=x+14; if(left+tw>wr.width) left=x-14-tw; if(left<0) left=4;
 tip.style.left=left+"px"; tip.style.top="14px";
}
function chartTipHide(){
 document.getElementById("curline").style.display="none";
 document.getElementById("chartTip").style.display="none";
}
function initChart(){
 var seg=document.getElementById("chartSeg"); if(!seg) return;
 var sp=seg.querySelectorAll("span");
 for(var i=0;i<sp.length;i++){(function(el){
  el.onclick=function(){
   S.chartMode=el.getAttribute("data-m");
   for(var j=0;j<sp.length;j++){ sp[j].classList.toggle("on", sp[j]===el); }
   renderChart();
  };})(sp[i]);}
}
function renderList(){
 var list=filtered(),d=DATA;
 document.getElementById("cnt").textContent=list.length+" / "+d.commits.length+" 条提交";
 document.getElementById("cmhint").textContent="（显示 "+Math.min(list.length,200)+" 条）";
 var html="";
 list.slice(0,200).forEach(function(c){
  var col=color(c.agent), open=!!S.exp[c.hash];
  html+="<div class=cmt data-h=\""+c.hash+"\"><div class=row1>"+badgeHTML(c.agent,col);
  html+="<div class=bd><div class=msg>"+esc(c.subject)+"</div>";
  html+="<div class=det><span class=mono>"+c.short+"</span><span>"+rel(c.date)+"</span><span>"+c.nfiles+" 个文件</span></div>";
  if(!open&&c.files.length){var f=c.files.slice(0,4).map(esc).join(" · ");if(c.files.length>4)f+=" · +"+(c.files.length-4);
   html+="<div class=f>"+f+"</div>";}
  html+="</div></div>";
  if(open&&c.files.length){html+="<div class=fil>"+c.files.map(function(x){return "<div>"+esc(x)+"</div>";}).join("")+"</div>";}
  html+="</div>";});
 document.getElementById("commits").innerHTML=html||"<div class=empty>没有匹配的提交</div>";
 var cms=document.querySelectorAll(".cmt");
 for(var i=0;i<cms.length;i++){(function(n){n.onclick=function(){var h=n.getAttribute("data-h");
   S.exp[h]=!S.exp[h];renderList();};})(cms[i]);}
 var fc={};
 list.forEach(function(c){c.files.forEach(function(f){fc[f]=(fc[f]||0)+1;});});
 var hot=Object.keys(fc).map(function(k){return [k,fc[k]];}).sort(function(a,b){return b[1]-a[1];}).slice(0,40);
 var mx=hot.length?hot[0][1]:1,hh="";
 hot.forEach(function(x){hh+="<div class=hm title=\""+esc(x[0])+"\"><div class=bar style=\"width:"+(6+(x[1]/mx)*70)+"px\"></div>"+
  "<div class=\"n f\">"+esc(x[0])+"</div><div class=c>"+x[1]+"x</div></div>";});
 document.getElementById("hot").innerHTML=hh||"<div class=empty>暂无数据</div>";
}
function render(){renderHead();renderAgents();renderChart();renderList();}
function sync(){
 var q=[];if(S.q)q.push("q="+encodeURIComponent(S.q));
 if(S.range!=="all")q.push("range="+S.range);
 var s=selectedList();if(s.length)q.push("a="+encodeURIComponent(s.join(",")));
 if(S.hideIdle)q.push("idle=0");
 var url=location.pathname+(q.length?("?"+q.join("&")):"");
 history.replaceState(null,"",url);}
function loadUrl(){
 var p=new URLSearchParams(location.search);
 if(p.get("q")){S.q=p.get("q");document.getElementById("q").value=S.q;}
 if(p.get("range"))S.range=p.get("range");
 if(p.get("a"))p.get("a").split(",").forEach(function(x){if(x)S.agents[x]=true;});
 if(p.get("idle")==="0")S.hideIdle=true;
}
function load(){
 fetch(API_BASE+"/api/summary",{cache:"no-store",credentials:"include"}).then(function(r){return r.json();}).then(function(d){
  DATA=d;render();}).catch(function(){document.getElementById("gen").textContent="· 数据加载失败";});}
function initUI(){
 var q=document.getElementById("q");
 q.value=S.q;
 q.oninput=function(){S.q=q.value;sync();renderList();};
 var chips=document.querySelectorAll(".chip[data-range]");
 for(var i=0;i<chips.length;i++){(function(el){
  el.onclick=function(){S.range=el.getAttribute("data-range");
   var all=document.querySelectorAll(".chip[data-range]");
   for(var j=0;j<all.length;j++)all[j].classList.remove("on");
   el.classList.add("on");sync();render();};})(chips[i]);}
 var hi=document.getElementById("hideidle"); hi.checked=S.hideIdle;
 hi.onchange=function(){S.hideIdle=hi.checked;sync();renderAgents();};
 document.getElementById("reset").onclick=function(){
  S.q="";S.range="all";S.agents={};S.hideIdle=false;S.exp={};
  q.value="";hi.checked=false;
  var all=document.querySelectorAll(".chip[data-range]");
  for(var j=0;j<all.length;j++){all[j].classList.toggle("on",all[j].getAttribute("data-range")==="all");}
  sync();render();};
 document.addEventListener("keydown",function(e){
  if(e.key==="/"&&document.activeElement!==q){e.preventDefault();q.focus();}
  if(e.key==="Escape"&&document.activeElement===q){q.blur();}});
 var cs=document.querySelectorAll(".chip[data-range]");
 for(var k=0;k<cs.length;k++){cs[k].classList.toggle("on",cs[k].getAttribute("data-range")===S.range);}
}
loadUrl();
load();
initUI();
initChart();
setInterval(function(){ if(!document.hidden) load(); },30000);
document.addEventListener("visibilitychange",function(){ if(!document.hidden) load(); });
