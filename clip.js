const VIDEO_PER_PAGE=16;
let clips=[],filteredClips=[],currentPage=1,sort="latest";

async function loadClips(){
try{
clips=await(await fetch("./data/clip.json")).json();
filteredClips=[...clips];
applySort();
renderClips();
renderPagination();
}catch(e){console.error("클립 데이터 로드 실패",e);}
}

function formatDate(date){
if(!date)return "";
const d=date.split(" ")[0].split("-");
return d.length===3?`${d[0]}.${d[1]}.${d[2]}`:date;
}

function missingThumbnail(){
return `<div class="thumbnail-placeholder"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="38"></circle><text x="50" y="58" text-anchor="middle">19</text><line x1="22" y1="22" x2="78" y2="78"></line></svg></div>`;
}

function renderThumbnail(clip){
return clip.thumbnail?`<img class="thumbnail" src="${clip.thumbnail}" loading="lazy" onerror="this.parentElement.innerHTML=missingThumbnail()">`:missingThumbnail();
}

function renderClips(){
const list=document.querySelector("#video-list");
list.innerHTML="";

if(filteredClips.length===0){
list.innerHTML=`<article class="video-card no-result">검색 결과가 없습니다.</article>`;
return;
}

const start=(currentPage-1)*VIDEO_PER_PAGE;

filteredClips.slice(start,start+VIDEO_PER_PAGE).forEach(clip=>{
const card=document.createElement("article");
card.className="video-card";

card.innerHTML=`
<a href="${clip.url||"#"}" target="_blank">
<div class="thumbnail-box">${renderThumbnail(clip)}</div>
<div class="video-info">
<h3>${clip.title||"제목 없음"}</h3>
<div class="meta">
<span>${formatDate(clip.date)}</span>
<span>조회 ${Number(clip.views||0).toLocaleString()}</span>
</div>
</div>
</a>`;

list.appendChild(card);
});
}

function scrollToCards(){
const list=document.querySelector("#video-list");
if(list)window.scrollTo({top:list.getBoundingClientRect().top+window.scrollY-90,behavior:"smooth"});
}

function movePage(page){
currentPage=page;
renderClips();
renderPagination();
setTimeout(scrollToCards,50);
}

function renderPagination(){
const pagination=document.querySelector("#pagination");
pagination.innerHTML="";

const total=Math.ceil(filteredClips.length/VIDEO_PER_PAGE);
if(total<=1)return;

const addButton=(text,page)=>{
const button=document.createElement("button");
button.textContent=text;
if(page===currentPage)button.classList.add("active");
button.onclick=()=>movePage(page);
pagination.appendChild(button);
};

const group=Math.floor((currentPage-1)/10);
const start=group*10+1;
const end=Math.min(total,start+9);

if(start>1){
addButton("<<",1);
addButton("<",start-1);
}

for(let i=start;i<=end;i++)addButton(i,i);

if(end<total){
addButton(">",end+1);
addButton(">>",total);
}
}

function updateClearButton(){
const clear=document.querySelector("#clear-search");
const search=document.querySelector("#search");
if(!clear||!search)return;
clear.style.display=search.value?"block":"none";
}

const search=document.querySelector("#search");

if(search){
search.oninput=e=>{
const keyword=e.target.value.trim().toLowerCase();

filteredClips=clips.filter(v=>{
const title=(v.title||"").toLowerCase();

let date="";
if(v.date){
const d=v.date.split(" ")[0].split("-");
if(d.length===3)date=`${d[0]}.${d[1]}.${d[2]}`;
}

return title.includes(keyword)||date.includes(keyword);
});

currentPage=1;
applySort();
renderClips();
renderPagination();
updateClearButton();
};
}

const clearSearch=document.querySelector("#clear-search");

if(clearSearch){
clearSearch.onclick=()=>{
search.value="";
filteredClips=[...clips];
currentPage=1;
applySort();
renderClips();
renderPagination();
updateClearButton();
};
}

function applySort(){
if(sort==="views")
filteredClips.sort((a,b)=>(b.views||0)-(a.views||0));
else
filteredClips.sort((a,b)=>new Date(b.date)-new Date(a.date));
}

document.querySelectorAll(".sort-button").forEach(btn=>{
btn.onclick=()=>{
document.querySelectorAll(".sort-button").forEach(b=>b.classList.remove("active"));
btn.classList.add("active");
sort=btn.dataset.sort;
currentPage=1;
applySort();
renderClips();
renderPagination();
};
});

const themeButton=document.querySelector("#theme-toggle");

function setTheme(theme){
document.body.classList.toggle("light-mode",theme==="light");
localStorage.setItem("theme",theme);
}

if(themeButton)
themeButton.onclick=()=>setTheme(document.body.classList.contains("light-mode")?"dark":"light");

setTheme(localStorage.getItem("theme")||"dark");
loadClips();