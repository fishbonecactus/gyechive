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
    r.raise_for_status()
    return r.json()["content"]

def parse(v):
    return {"id":v.get("videoNo"),"title":v.get("videoTitle"),"category":v.get("videoCategoryValue"),"categoryType":v.get("categoryType"),"date":v.get("publishDate"),"duration":v.get("duration"),"views":v.get("readCount"),"thumbnail":v.get("thumbnailImageUrl"),"url":f"https://chzzk.naver.com/video/{v.get('videoId')}"}

def load(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:return json.load(f)
    return []

def state(data):
    if not data:return {}
    return {"lastVodDate":data[0]["date"],"lastVodID":data[0]["id"]}

def save(data):
    os.makedirs(DATA,exist_ok=True)
    with open(OUT,"w",encoding="utf-8") as f:json.dump(data,f,ensure_ascii=False,indent=4)
    with open(STATE,"w",encoding="utf-8") as f:json.dump(state(data),f,ensure_ascii=False,indent=4)

def progress(cur,total):
    p=int(cur/total*100)
    bar="█"*(p//5)+"-"*(20-p//5)
    sys.stdout.write(f"\r[{bar}] {p}%")
    sys.stdout.flush()

def collect():
    old=load(OUT)
    old_state=load(STATE) or state(old)
    first=get(0)
    print(f"총 VOD {first['totalCount']}개 확인")
    new=[]
    for page in range(first["totalPages"]):
        data=first if page==0 else get(page)
        for v in data["data"]:
            if old_state and v["publishDate"]<=old_state["lastVodDate"]:
                return new,old
            new.append(parse(v))
        progress(page+1,first["totalPages"])
        time.sleep(.1)
    print()
    return new,old

def main():
    print("="*40)
    print("계카이브 VOD 업데이트")
    print("="*40)
    new,old=collect()
    merged=new+old
    unique={v["id"]:v for v in merged}
    videos=list(unique.values())
    videos.sort(key=lambda x:x["date"],reverse=True)
    save(videos)
    print(f"신규 VOD {len(new)}개 추가")
    print(f"총 VOD {len(videos)}개 저장")

if __name__=="__main__":
    main()
