import os,json,time,requests,sys

CHANNEL_ID="a9a343510e132ea3026ff3cf682820b5"
PAGE_SIZE=50
BASE=os.path.dirname(os.path.abspath(__file__))
DATA=os.path.join(BASE,"data")
OUT=os.path.join(DATA,"clip.json")
STATE=os.path.join(DATA,"clip_state.json")
API=f"https://api.chzzk.naver.com/service/v1/channels/{CHANNEL_ID}/clips"
HEAD={"User-Agent":"Mozilla/5.0","Referer":"https://chzzk.naver.com/","Origin":"https://chzzk.naver.com"}

def get(uid=None,count=None):
    p={"filterType":"ALL","orderType":"RECENT","page":0,"size":PAGE_SIZE}

    if uid:
        p["clipUID"]=uid

    if count:
        p["readCount"]=count

    r=requests.get(API,headers=HEAD,params=p,timeout=20)

    if r.status_code!=200:
        print("\n클립 API 오류")
        print(r.url)
        print(r.text)
        exit(1)

    return r.json()["content"]

def parse(v):
    cid=v.get("clipUID")
    vid=v.get("videoId")

    return {
        "id":cid,
        "title":v.get("clipTitle"),
        "category":v.get("clipCategory"),
        "categoryType":v.get("categoryType"),
        "date":v.get("createdDate"),
        "duration":v.get("duration"),
        "views":v.get("readCount"),
        "thumbnail":v.get("thumbnailImageUrl"),
        "url":f"https://chzzk.naver.com/clips/{cid}",
        "vodUrl":f"https://chzzk.naver.com/video/{vid}" if vid else None
    }

def load(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)

    return []

def make_state(data):
    if not data:
        return {}

    return {
        "lastClipDate":data[0]["date"],
        "lastClipUID":data[0]["id"]
    }

def save(data):
    os.makedirs(DATA,exist_ok=True)

    with open(OUT,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

    with open(STATE,"w",encoding="utf-8") as f:
        json.dump(make_state(data),f,ensure_ascii=False,indent=4)

def spin(i):
    s="|/-\\"
    sys.stdout.write(f"\r클립 수집 중 {s[i%4]}")
    sys.stdout.flush()

def collect():
    old=load(OUT)
    state=load(STATE)

    if not state and old:
        state=make_state(old)

    new=[]
    cursor=None
    i=0

    while True:
        if cursor:
            data=get(cursor.get("clipUID"),cursor.get("readCount"))
        else:
            data=get()

        for v in data["data"]:
            if state and v["createdDate"]<=state["lastClipDate"]:
                return new,old

            new.append(parse(v))

        spin(i)
        i+=1

        cursor=data["page"].get("next")

        if not cursor:
            break

        time.sleep(.2)

    print()
    return new,old

def main():
    print("="*40)
    print("계카이브 클립 업데이트")
    print("="*40)

    new,old=collect()

    merged=new+old
    unique={c["id"]:c for c in merged}

    clips=list(unique.values())
    clips.sort(key=lambda x:x["date"],reverse=True)

    save(clips)

    print(f"\n신규 클립 {len(new)}개 추가")
    print(f"총 클립 {len(clips)}개 저장")

if __name__=="__main__":
    main()