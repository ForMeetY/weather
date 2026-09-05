# -*- coding: utf-8 -*-
"""
统一对比实验【轻量模型部分】：气候态/趋势/谐波/异常AR(1)/去年同日
运行环境：默认 Python（无 statsmodels 依赖）。结果落盘 compare_light.json + compare_light_data.npz
切分：训练 2004-01-01 ~ 2021-12-31，测试 2022-01-01 ~ 2023-12-31（730 天）
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
tr = df[(df["record_date"] >= "2004-01-01") & (df["record_date"] <= "2021-12-31")].reset_index(drop=True)
te = df[(df["record_date"] >= "2022-01-01") & (df["record_date"] <= "2023-12-31")].reset_index(drop=True)
y_tr = tr["avg_temp"].values
y_te = te["avg_temp"].values
md_tr = tr["record_date"].dt.strftime("%m-%d").values
md_te = te["record_date"].dt.strftime("%m-%d").values
te_dates = te["record_date"]

# ---------- 模型 ----------
def make_climatology():
    s = pd.Series(y_tr, index=md_tr)
    return s.groupby(level=0).mean()

clim = make_climatology()

def trend_adjusted_climatology():
    yr_mean = tr.groupby(tr["record_date"].dt.year)["avg_temp"].mean()
    ys = yr_mean.index.values.astype(float)
    k, b = np.polyfit(ys, yr_mean.values, 1)
    ref = ys[-1]
    def predict(md_arr, year_arr):
        base = clim.reindex(md_arr).values
        return base + k * (year_arr - ref)
    return predict

def harmonic_ols(K=3):
    def build_design(dates):
        t = (dates - pd.Timestamp("2004-01-01")).dt.days.values.astype(float)
        doy = dates.dt.dayofyear.values.astype(float)
        cols = [np.ones_like(t), t / 365.25]
        for k in range(1, K + 1):
            cols.append(np.sin(2 * np.pi * k * doy / 365.25))
            cols.append(np.cos(2 * np.pi * k * doy / 365.25))
        return np.column_stack(cols)
    X_tr = build_design(tr["record_date"])
    beta, *_ = np.linalg.lstsq(X_tr, y_tr, rcond=None)
    def predict(dates):
        return build_design(dates) @ beta
    return predict

anom_tr = y_tr - clim.reindex(md_tr).values
phi = np.sum(anom_tr[1:] * anom_tr[:-1]) / np.sum(anom_tr[:-1] ** 2)

def metrics(y, yhat):
    return float(np.mean(np.abs(y - yhat))), float(np.sqrt(np.mean((y - yhat) ** 2)))

def season_bucket(dates, y, yhat):
    months = dates.dt.month.values
    out = {}
    for name, ms in [("春", [3, 4, 5]), ("夏", [6, 7, 8]), ("秋", [9, 10, 11]), ("冬", [12, 1, 2])]:
        m = np.isin(months, ms)
        if m.sum() > 0:
            out[name] = round(float(np.mean(np.abs(y[m] - yhat[m]))), 3)
    return out

# 去年同日 yhat(d)=实测(d-365)
date_to_y = df.set_index("record_date")["avg_temp"]

def seasonal_naive_1day(pred_dates):
    out = np.full(len(pred_dates), np.nan)
    for i, d in enumerate(pred_dates):
        pd_ = d - pd.DateOffset(days=365)
        if pd_ in date_to_y.index:
            out[i] = date_to_y[pd_]
    return out

results = {}
yhat_store = {}

# ===== 评估 A：滚动 1 步 =====
print("== 评估A 滚动1步 ==")
models_A = {
    "A_C1_climatology": lambda: clim.reindex(md_te).values,
    "A_C5_seasonal_naive": lambda: seasonal_naive_1day(te_dates),
    "A_C4_clim_anom_ar1": None,
    "A_C2_trend_clim": None,
}
# C4 循环实现
yhat_c4 = np.zeros(len(te))
for i in range(len(te)):
    a_prev = anom_tr[-1] if i == 0 else (y_te[i - 1] - clim.reindex([md_te[i - 1]]).values[0])
    yhat_c4[i] = clim.reindex([md_te[i]]).values[0] + phi * a_prev
yhat_store["A_C4"] = yhat_c4
mae, rmse = metrics(y_te, yhat_c4)
results["A_C4_clim_anom_ar1"] = {"mae": mae, "rmse": rmse, "season": season_bucket(te_dates, y_te, yhat_c4)}
print(f"A_C4 气候态+异常AR(1) MAE {mae:.3f} RMSE {rmse:.3f}")

for name in ["A_C1_climatology", "A_C5_seasonal_naive"]:
    yh = models_A[name]()
    yhat_store[name.replace("A_", "A_")] = yh
    mae, rmse = metrics(y_te, yh)
    results[name] = {"mae": mae, "rmse": rmse, "season": season_bucket(te_dates, y_te, yh)}
    print(f"{name} MAE {mae:.3f} RMSE {rmse:.3f}")

predC2 = trend_adjusted_climatology()
yh = predC2(md_te, te_dates.dt.year.values.astype(float))
yhat_store["A_C2"] = yh
mae, rmse = metrics(y_te, yh)
results["A_C2_trend_clim"] = {"mae": mae, "rmse": rmse, "season": season_bucket(te_dates, y_te, yh)}
print(f"A_C2 趋势修正气候态 MAE {mae:.3f} RMSE {rmse:.3f}")

for K in [2, 3, 4]:
    p3 = harmonic_ols(K)
    yh = p3(te_dates)
    if K == 3:
        yhat_store["A_C3"] = yh
    mae, rmse = metrics(y_te, yh)
    results[f"A_C3_harmonic_K{K}"] = {"mae": mae, "rmse": rmse, "season": season_bucket(te_dates, y_te, yh)}
    print(f"A_C3 谐波OLS K={K} MAE {mae:.3f} RMSE {rmse:.3f}")

# ===== 评估 B：固定起点 730 天 =====
print("== 评估B 固定起点730天 ==")
yh = clim.reindex(md_te).values
yhat_store["B_C1"] = yh
mae, rmse = metrics(y_te, yh)
results["B_C1_climatology"] = {"mae": mae, "rmse": rmse, "season": season_bucket(te_dates, y_te, yh)}
print(f"B_C1 气候态 MAE {mae:.3f} RMSE {rmse:.3f}")

yh = predC2(md_te, te_dates.dt.year.values.astype(float))
yhat_store["B_C2"] = yh
mae, rmse = metrics(y_te, yh)
results["B_C2_trend_clim"] = {"mae": mae, "rmse": rmse, "season": season_bucket(te_dates, y_te, yh)}
print(f"B_C2 趋势修正气候态 MAE {mae:.3f} RMSE {rmse:.3f}")

p3 = harmonic_ols(3)
yh = p3(te_dates)
yhat_store["B_C3"] = yh
mae, rmse = metrics(y_te, yh)
results["B_C3_harmonic_K3"] = {"mae": mae, "rmse": rmse, "season": season_bucket(te_dates, y_te, yh)}
print(f"B_C3 谐波OLS K=3 MAE {mae:.3f} RMSE {rmse:.3f}")

# B_C4: 固定起点，距平按 phi^k 衰减
a0 = anom_tr[-1]
n_te = len(te)
decay = a0 * (phi ** np.arange(1, n_te + 1))
yh = clim.reindex(md_te).values + decay
yhat_store["B_C4"] = yh
mae, rmse = metrics(y_te, yh)
results["B_C4_clim_anom_ar1"] = {"mae": mae, "rmse": rmse, "season": season_bucket(te_dates, y_te, yh)}
print(f"B_C4 气候态+异常AR(1) MAE {mae:.3f} RMSE {rmse:.3f}")

np.savez_compressed(
    OUT / "compare_light_data.npz",
    te_dates=te_dates.values.astype("datetime64[D]"), y_te=y_te,
    A_c1=yhat_store.get("A_C1_climatology"), A_c5=yhat_store.get("A_C5_seasonal_naive"),
    A_c4=yhat_store.get("A_C4"), A_c2=yhat_store.get("A_C2"), A_c3=yhat_store.get("A_C3"),
    B_c1=yhat_store.get("B_C1"), B_c2=yhat_store.get("B_C2"),
    B_c3=yhat_store.get("B_C3"), B_c4=yhat_store.get("B_C4"),
)
with open(OUT / "compare_light.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\n[完成] compare_light.json + compare_light_data.npz 已保存")
