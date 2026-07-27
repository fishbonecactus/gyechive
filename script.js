const VIDEO_PER_PAGE=16;
let videos=[];
let filteredVideos=[];
let currentPage=1;

async function loadVideos(){
    try{
        const response=await fetch("./data/videos.json");
        videos=await response.json();
        filteredVideos=[...videos];
        renderVideos();
        renderPagination();
    }catch(e){
        console.error("데이터 로드 실패",e);
    }
}

function formatDate(date){
    if(!date)return "";
    const d=date.split(" ")[0].split("-");
    return d.length===3?`${d[0]}.${d[1]}.${d[2]}`:date;
}

function formatDuration(seconds){
    if(!seconds)return "";
    seconds=Number(seconds);
    const h=Math.floor(seconds/3600);
    const m=Math.floor((seconds%3600)/60);
    const s=seconds%60;
    const result=[];
    if(h>0)result.push(`${h}시간`);
    if(m>0)result.push(`${m}분`);
    if(s>0||result.length===0)result.push(`${s}초`);
    return result.join(" ");
}

function missingThumbnail(){
    return `
    <div class="thumbnail-placeholder">
        <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="38"></circle>
            <text x="50" y="58" text-anchor="middle">19</text>
            <line x1="22" y1="22" x2="78" y2="78"></line>
        </svg>
    </div>`;
}

function renderThumbnail(video){
    if(!video.thumbnail)return missingThumbnail();
    return `<img class="thumbnail" src="${video.thumbnail}" loading="lazy" onerror="this.parentElement.innerHTML=missingThumbnail()">`;
}

function renderVideos(){
    const list=document.querySelector("#video-list");
    list.innerHTML="";

    const start=(currentPage-1)*VIDEO_PER_PAGE;
    const pageVideos=filteredVideos.slice(start,start+VIDEO_PER_PAGE);

    pageVideos.forEach(video=>{
        const card=document.createElement("article");
        card.className="video-card";

        card.innerHTML=`
        <a href="${video.url}" target="_blank">
            <div class="thumbnail-box">
                ${renderThumbnail(video)}
            </div>
            <div class="video-info">
                <h3>${video.title}</h3>
                <div class="meta">
                    <span>${formatDate(video.date)} · ${formatDuration(video.duration)}</span>
                    <span>조회 ${Number(video.views||0).toLocaleString()}</span>
                </div>
            </div>
        </a>`;

        list.appendChild(card);
    });
}

function movePage(page){
    currentPage=page;
    renderVideos();
    renderPagination();

    window.scrollTo({
        top:0,
        behavior:"smooth"
    });
}

function renderPagination(){
    const pagination=document.querySelector("#pagination");
    pagination.innerHTML="";

    const total=Math.ceil(filteredVideos.length/VIDEO_PER_PAGE);

    const addButton=(text,page)=>{
        const button=document.createElement("button");
        button.textContent=text;

        if(page===currentPage){
            button.classList.add("active");
        }

        button.onclick=()=>{
            movePage(page);
        };

        pagination.appendChild(button);
    };

    if(currentPage>1){
        addButton("<<",1);
        addButton("<",currentPage-1);
    }

    let start=Math.max(1,currentPage-2);
    let end=Math.min(total,start+4);

    if(end-start<4){
        start=Math.max(1,end-4);
    }

    for(let i=start;i<=end;i++){
        addButton(i,i);
    }

    if(currentPage<total){
        addButton(">",currentPage+1);
        addButton(">>",total);
    }
}

const search=document.querySelector("#search");

if(search){
    search.addEventListener("input",e=>{
        const keyword=e.target.value.trim().toLowerCase();

        filteredVideos=videos.filter(video=>
            video.title.toLowerCase().includes(keyword)
        );

        currentPage=1;
        renderVideos();
        renderPagination();
    });
}

document.addEventListener("keydown",e=>{
    const total=Math.ceil(filteredVideos.length/VIDEO_PER_PAGE);

    if(e.key==="ArrowLeft"&&currentPage>1){
        movePage(currentPage-1);
    }

    if(e.key==="ArrowRight"&&currentPage<total){
        movePage(currentPage+1);
    }
});

const themeButton=document.querySelector("#theme-toggle");

function setTheme(theme){
    if(theme==="light"){
        document.body.classList.add("light-mode");
    }else{
        document.body.classList.remove("light-mode");
    }

    localStorage.setItem("theme",theme);
}

if(themeButton){
    themeButton.onclick=()=>{
        const isLight=document.body.classList.contains("light-mode");
        setTheme(isLight?"dark":"light");
    };
}

const savedTheme=localStorage.getItem("theme");

if(savedTheme){
    setTheme(savedTheme);
}else{
    setTheme("dark");
}

loadVideos();