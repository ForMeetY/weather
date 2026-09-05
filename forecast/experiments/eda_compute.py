# -*- coding: utf-8 -*-
"""
EDA 计算阶段（不画图，只算数值并落盘），运行环境：系统默认 Python。
结论打印到日志，供"选预测方案"决策使用。
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "weather_data_clean.csv"
OUT = ROOT / "experiments"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["record_date"])
df = df.sort_values("record_date").reset_index(drop=True)
n = len(df)
print(f"[数据] {n} 行, {df['record_date'].min().date()} ~ {df['record_date'].max().date()}")

# ---------- Q1 连续性 ----------
full = pd.date_range(df["record_date"].min(), df["record_date"].max(), freq="D")
missing = full.difference(pd.DatetimeIndex(df["record_date"]))
print(f"[连续性] 应有 {len(full)} 天, 缺失 {len(missing)} 天")
for c in ["avg_temp", "min_temp", "max_temp"]:
    print(f"  {c}: NaN {df[c].isna().sum()}")

# ---------- 基础统计 ----------
desc = df[["avg_temp", "min_temp", "max_temp", "daily_range"]].describe().round(3)
print("\n[描述统计]\n", desc.to_string())

# ---------- Q2 年际趋势 ----------
df["year"] = df["record_date"].dt.year
yearly = df.groupby("year").agg(
    yavg=("avg_temp", "mean"), ymax=("max_temp", "mean"), ymin=("min_temp", "mean"),
    yavgmax=("avg_temp", "max"), yavgmin=("avg_temp", "min"),
    range_mean=("daily_range", "mean"),
).reset_index()
print("\n[年际线性斜率 ℃/年]")
for col in ["yavg", "ymax", "ymin", "yavgmax", "yavgmin"]:
    k, b = np.polyfit(yearly["year"].values, yearly[col].values, 1)
    r = np.corrcoef(yearly["year"].values, yearly[col].values)[0, 1]
    print(f"  {col}: {k:+.4f}  (r={r:+.3f})")

# ---------- Q3 季节性：气候态 ----------
doy = df["record_date"].dt.dayofyear.values
clim = df.groupby(doy)["avg_temp"].agg(["mean", "std"])
clim.columns = ["mean", "std"]
print(f"\n[气候态] 年内峰(约第{clim['mean'].idxmax()}天 {clim['mean'].max():.2f}℃) "
      f"谷(第{clim['mean'].idxmin()}天 {clim['mean'].min():.2f}℃) "
      f"振幅 {(clim['mean'].max()-clim['mean'].min())/2:.2f}℃")

# 逐月统计
df["month"] = df["record_date"].dt.month
monthly = df.groupby("month")["avg_temp"].agg(["mean", "std"])
print("\n[逐月 avg_temp]\n", monthly.round(2).to_string())

# ---------- Q4 自相关 ----------
def acf_manual(y, maxlag):
    y = y - y.mean()
    v = np.dot(y, y)
    out = np.ones(maxlag + 1)
    for L in range(1, maxlag + 1):
        out[L] = np.dot(y[L:], y[:-L]) / v
    return out


def pacf_levinson(y, maxlag):
    """Levinson-Durbin 递推求偏自相关"""
    acv = np.correlate(y - y.mean(), y - y.mean(), mode="full")[len(y) - 1:] / len(y)
    pacf = np.zeros(maxlag + 1)
    pacf[0] = 1.0
    ar_coef = np.array([])
    for k in range(1, maxlag + 1):
        if k == 1:
            phi = acv[1] / acv[0]
            ar_coef = np.array([phi])
        else:
            num = acv[k] - np.dot(ar_coef, acv[k - 1:0:-1])
            den = acv[0] - np.dot(ar_coef, acv[1:k])
            phi = num / den
            ar_coef = np.concatenate([ar_coef - phi * ar_coef[::-1], [phi]])
        pacf[k] = phi
    return pacf


y = df["avg_temp"].values
acf = acf_manual(y, 800)
pacf = pacf_levinson(y, 60)
for lag in [1, 2, 7, 30, 90, 180, 364, 365, 366, 700, 730]:
    print(f"  ACF lag={lag:3d}: {acf[lag]:+.3f}")
print("  PACF lag1~5:", np.round(pacf[1:6], 3))

# ---------- Q5 avg vs (max+min)/2 ----------
mid = (df["max_temp"] + df["min_temp"]) / 2.0
diff = (df["avg_temp"] - mid).values
corr = np.corrcoef(df["avg_temp"], mid)[0, 1]
print(f"\n[avg vs (max+min)/2] r={corr:.4f}, mean差={diff.mean():+.4f}℃, |差|均值={np.abs(diff).mean():.4f}℃")

# 年度内标准差：判断用一年前同日做预测(seasonal naive)是否合理 => 残差波动
print(f"\n[日较差] 全年均值 {df['daily_range'].mean():.2f}℃, 全序列 std {df['daily_range'].std():.2f}℃")

# ---------- 存档绘图所需数据 ----------
np.savez_compressed(
    OUT / "eda_data.npz",
    dates=df["record_date"].values.astype("datetime64[D]"),
    avg_temp=df["avg_temp"].values,
    daily_range=df["daily_range"].values,
    year=yearly["year"].values, yavg=yearly["yavg"].values,
    ymax=yearly["ymax"].values, ymin=yearly["ymin"].values,
    clim_doy=clim.index.values, clim_mean=clim["mean"].values, clim_std=clim["std"].values,
    monthly_mean=monthly["mean"].values, monthly_std=monthly["std"].values,
    acf=acf, pacf=pacf, avg_mid_diff=diff, mid=mid.values,
    pivot=df.pivot_table(index="year", columns="month", values="avg_temp", aggfunc="mean").values,
    pivot_years=df.pivot_table(index="year", columns="month", values="avg_temp", aggfunc="mean").index.values,
)
print("\n[完成] 数值已打印，绘图数据存至 eda_data.npz")
