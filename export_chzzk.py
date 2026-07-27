import os
import json
import time
import re
import requests


# =====================================================
# 기본 설정
# =====================================================

CHANNEL_ID = "a9a343510e132ea3026ff3cf682820b5"

PAGE_SIZE = 30

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "videos.json"
)


API_URL = (
    "https://api.chzzk.naver.com/service/v1/channels/"
    f"{CHANNEL_ID}/videos"
)


HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36",

    "Referer":
        "https://chzzk.naver.com/",

    "Origin":
        "https://chzzk.naver.com"
}


# 상세 썸네일 확인 캐시
thumbnail_cache = {}



# =====================================================
# API 요청
# =====================================================

def get_page(page):

    params = {
        "page": page,
        "size": PAGE_SIZE
    }


    response = requests.get(
        API_URL,
        headers=HEADERS,
        params=params,
        timeout=20
    )


    response.raise_for_status()


    return response.json()



# =====================================================
# 썸네일 처리
# =====================================================

def get_thumbnail(video):

    thumbnail = video.get(
        "thumbnailImageUrl"
    )


    if thumbnail:
        return thumbnail


    data = video.get(
        "thumbnail"
    )


    if isinstance(data, dict):

        return (
            data.get("url")
            or data.get("imageUrl")
        )


    if isinstance(data, str):

        return data


    return None



def get_detail_thumbnail(video_no):

    if not video_no:
        return None


    if video_no in thumbnail_cache:

        return thumbnail_cache[video_no]


    url = (
        f"https://chzzk.naver.com/video/{video_no}"
    )


    thumbnail = None


    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )


        response.raise_for_status()


        match = re.search(
            r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"',
            response.text
        )


        if match:

            thumbnail = match.group(1)


    except Exception:

        pass


    thumbnail_cache[video_no] = thumbnail


    time.sleep(0.2)


    return thumbnail



# =====================================================
# 데이터 변환
# =====================================================

def parse_video(video):

    video_no = video.get(
        "videoNo"
    )


    thumbnail = get_thumbnail(
        video
    )


    # 썸네일 없는 경우만 보충 요청
    if not thumbnail:

        thumbnail = get_detail_thumbnail(
            video_no
        )


    return {

        "id":
            video_no,

        "title":
            video.get("videoTitle"),

        "category":
            video.get("videoCategoryValue"),

        "categoryType":
            video.get("categoryType"),

        "date":
            video.get("publishDate"),

        "duration":
            video.get("duration"),

        "views":
            video.get("readCount"),

        "thumbnail":
            thumbnail,

        "url":
            f"https://chzzk.naver.com/video/{video_no}"

    }



# =====================================================
# 전체 수집
# =====================================================

def collect_all():

    videos = []

    page = 0


    while True:

        print(
            f"{page + 1} 페이지 수집중..."
        )


        data = get_page(
            page
        )


        content = (
            data
            .get("content", {})
            .get("data", [])
        )


        if not content:

            break


        for item in content:

            videos.append(
                parse_video(item)
            )


        if len(content) < PAGE_SIZE:

            break


        page += 1


        time.sleep(0.2)


    return videos



# =====================================================
# JSON 저장
# =====================================================

def save_json(videos):

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            videos,
            f,
            ensure_ascii=False,
            indent=4
        )



# =====================================================
# 실행
# =====================================================

def main():

    print("=" * 50)
    print("치지직 영상 목록 수집기")
    print("=" * 50)


    try:

        videos = collect_all()


        print()

        print(
            f"총 {len(videos)}개 영상 수집 완료"
        )


        print(
            f"썸네일 보충 요청: {len(thumbnail_cache)}개"
        )


        save_json(
            videos
        )


        print()

        print(
            "저장 완료:"
        )

        print(
            OUTPUT_FILE
        )


    except Exception as e:

        print()

        print(
            "오류 발생"
        )

        print(
            type(e).__name__
        )

        print(
            e
        )


    finally:

        print()

        input(
            "완료되었습니다. 엔터를 누르면 종료합니다."
        )



if __name__ == "__main__":

    main()
