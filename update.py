import os,subprocess,sys

BASE=os.path.dirname(os.path.abspath(__file__))

def run(file):
    print(f"\n[{file} 실행]")
    r=subprocess.run([sys.executable,os.path.join(BASE,file)])
    if r.returncode:
        print(f"{file} 오류 발생")
        exit(1)

def main():
    print("="*40)
    print("계카이브 전체 업데이트")
    print("="*40)

    run("vod_collector.py")
    run("clip_collector.py")

    print()
    print("전체 업데이트 완료")
    input("엔터를 누르면 종료합니다.")

if __name__=="__main__":
    main()
