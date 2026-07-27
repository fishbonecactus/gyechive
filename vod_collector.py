import os,json,time,requests,sys

CHANNEL_ID="a9a343510e132ea3026ff3cf682820b5"
PAGE_SIZE=30
BASE=os.path.dirname(os.path.abspath(__file__))
DATA=os.path.join(BASE,"data")
OUT=os.path.join(DATA,"vod.json")
STATE=os.path.join(DATA,"vod_state.json")
API=f"https://api.chzzk.naver.com/service/v1/channels/{CHANNEL_ID}/videos"
HEAD={"User-Agent":"Mozilla/5.0","Referer":"https://chzzk.naver.com/","Origin":"https://chzzk.naver.com"}

def get(page=0):
    r=requests.get(API,headers=HEAD,params={"page":page,"size":PAGE_SIZE},timeout=20)
    if r.status_code!=200:
        print(r.text);sys.exit(1)
    return r.json()["content"]

def parse(v):
    no=v.get("videoNo")
    if not no:return None
    return {
        "id":str(no),
        "title":v.get("videoTitle"),
        "category":v.get("videoCategoryValue"),
        "categoryType":v.get("categoryType"),
        "date":v.get("publishDate"),
        "duration":v.get("duration"),
        "views":v.get("readCount"),
        "thumbnail":v.get("thumbnailImageUrl"),
        "url":f"https://chzzk.naver.com/video/{no}"
    }

def load(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:return json.load(f)
    return []

def save(path,data):
    os.makedirs(DATA,exist_ok=True)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

def update():
    old=load(OUT)
    state=load(STATE)
    first=get(0)
    new=[]

    for page in range(first["totalPages"]):
        data=first if page==0 else get(page)

        for v in data["data"]:
            if state and v["publishDate"]<=state["lastVodDate"]:
                page=999
                break

            item=parse(v)
            if item:new.append(item)

        time.sleep(.1)

    videos={v["id"]:v for v in new+old}
    videos=list(videos.values())
    videos.sort(key=lambda x:x["date"],reverse=True)

    save(OUT,videos)

    if videos:
        save(STATE,{
            "lastVodDate":videos[0]["date"],
            "lastVodID":videos[0]["id"]
        })

    print(f"신규 {len(new)}개 / 총 {len(videos)}개")

if __name__=="__main__":
    update()