# -*- coding: utf-8 -*-
"""
拉取多城市 2004-2023 逐日气温（Open-Meteo 历史再分析，免费无key）
城市：北京 / 郑州 / 乌鲁木齐 / 昆明（+ 可选呼和浩特，与原研究对齐）
输出：forecast/data/multi_city/<city>_2004_2023.csv (record_date, avg_temp, min_temp, max_temp)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import time
import json
from pathlib import Path
from urllib.request import urlopen
import pandas as pd

CITIES = {
    "beijing":   {"name": "北京",     "lat": 39.90, "lon": 116.40},
    "zhengzhou": {"name": "郑州",     "lat": 34.75, "lon": 113.62},
    "wulumuqi":  {"name": "乌鲁木齐", "lat": 43.83, "lon": 87.62},
    "kunming":   {"name": "昆明",     "lat": 25.04, "lon": 102.71},
    # 呼和浩特（可选，与原研究同城对照）
    "hohhot":    {"name": "呼和浩特", "lat": 40.84, "lon": 111.75},
}

OUT = Path(r"F:\Users\肖炳旭\Desktop\tm\项目相关\weather\forecast\data\multi_city")
OUT.mkdir(parents=True, exist_ok=True)

START, END = "2004-01-01", "2023-12-31"


def fetch_chunk(city, y0, y1):
    url = ("https://archive-api.open-meteo.com/v1/archive"
           f"?latitude={city['lat']}&longitude={city['lon']}"
           f"&start_date={y0}-01-01&end_date={y1}-12-31"
           "&daily=temperature_2m_mean,temperature_2m_max,temperature_2m_min"
           "&timezone=Asia%2FShanghai")
    for attempt in range(4):
        try:
            with urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as ex:
            print(f"  重试 {attempt+1}: {type(ex).__name__}")
            time.sleep(3 * (attempt + 1))
    return None


for key, city in CITIES.items():
    out_p = OUT / f"{key}_2004_2023.csv"
    if out_p.exists():
        print(f"跳过(已存在) {key}")
        continue
    print(f"=== {city['name']} ({city['lat']},{city['lon']}) ===")
    frames = []
    # 每 5 年一块，避免单请求过大
    for y0 in range(2004, 2024, 5):
        y1 = min(y0 + 4, 2023)
        data = fetch_chunk(city, y0, y1)
        if not data or "daily" not in data:
            print(f"  {y0}-{y1} 失败")
            continue
        d = data["daily"]
        df = pd.DataFrame({
            "record_date": d["time"],
            "avg_temp": d["temperature_2m_mean"],
            "min_temp": d["temperature_2m_min"],
            "max_temp": d["temperature_2m_max"],
        })
        df["city"] = city["name"]
        frames.append(df)
        print(f"  {y0}-{y1}: {len(df)} 天")
        time.sleep(1.2)  # 礼貌限速
    if frames:
        all_df = pd.concat(frames, ignore_index=True)
        all_df["record_date"] = pd.to_datetime(all_df["record_date"])
        all_df = all_df.sort_values("record_date").drop_duplicates("record_date").reset_index(drop=True)
        path = OUT / f"{key}_2004_2023.csv"
        all_df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"  保存 {path}: {len(all_df)} 天 "
              f"({all_df['record_date'].min().date()}~{all_df['record_date'].max().date()})")
    print()
print("[完成]")



