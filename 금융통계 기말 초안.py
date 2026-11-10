from pathlib import Path
import pandas as pd

# 1. 서버 내 원본 데이터 경로 설정 (읽기 전용)
ROOT = Path("/mnt/data/stock")      
CACHE_DIR = Path("parquet")          

def list_files(root: Path = ROOT) -> pd.DataFrame:
    """날짜 폴더와 그 안의 html 파일을 DataFrame으로 반환한다."""
    rows = []
    for day_dir in sorted(root.iterdir()):
        if not day_dir.is_dir():
            continue
        try:
            day = pd.Timestamp(day_dir.name)
        except ValueError:
            continue  
        for f in day_dir.glob("*.html"):
            rows.append({"date": day, "code": f.stem, "path": str(f), "bytes": f.stat().st_size})
    return pd.DataFrame(rows)

def step1():
    files = list_files()
    print(f"파일 수      : {len(files):,}")
    if len(files) > 0:
        print(f"날짜 수      : {files['date'].nunique():,}  ({files['date'].min().date()} ~ {files['date'].max().date()})")
        print(f"종목 수      : {files['code'].nunique():,}")
        per_day = files.groupby("date").size()
        print("\n날짜별 파일 수 요약")
        print(per_day.describe().round(0).to_string())
        
        bdays = pd.bdate_range(files["date"].min(), files["date"].max())
        missing = bdays.difference(per_day.index)
        print(f"\n영업일 중 폴더 없는 날: {len(missing)}일")
        if len(missing):
            print(missing[:10].date, "..." if len(missing) > 10 else "")
            
        small = files[files["bytes"] < 5_000]
        print(f"\n5KB 미만 파일: {len(small):,}개 (다운로드 실패 의심)")
    else:
        print("지정한 경로에서 파일을 찾지 못했습니다. ROOT 경로를 다시 확인해주세요.")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, required=True, choices=[1])
    a = ap.parse_args()
    if a.step == 1:
        step1()