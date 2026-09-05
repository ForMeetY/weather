# -*- coding: utf-8 -*-
"""
trainer_gbdt.py —— 机器学习基线：梯度提升回归(GBDT) vs 统计方法
================================================================
定位：作为"数据驱动 ML 基线"，与 气候态+异常AR(1) / 谐波回归 形成
      "结构先验 vs 数据驱动" 的方法学对照（CS 方向面试叙事）。

特征工程（只用预测日之前的信息，无泄漏）：
  - 日历特征: month, dayofyear, sin/cos(2π·doy/365.25) ×K
  - 滞后特征: lag1, lag2, lag3, lag7, lag30, lag365  （气温自身的近期记忆）

评估协议（与 trainer_short.py 完全一致，便于对比）：
  - 训练: 2004-2023 全部（滚动回测只允许用起点之前信息 → 用 2004-起点前1天 训练？）
  - 为了公平且可复现，这里统一"训练 2004-2021，预测 2022-2023 留出段(评估A)"
    + "2024 年每7天起点滚动回测未来30天(评估B)"

实现要点：
  - 短期(≤30天)多步用"递归多步预测"：每步用上一步预测值作为新 lag。
  - 只输出评估结果 JSON + 图，供前端/报告使用。
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "model" / "img"
IMG.mkdir(parents=True, exist_ok=True)

# ---------------- 数据 ----------------
df = pd.read_csv(ROOT / "data" / "weather_data_clean.csv", parse_dates=["record_date"])
df = df.sort_values("record_date").reset_index(drop=True)
y = df["avg_temp"].values
dates = df["record_date"]
doy = dates.dt.dayofyear.values.astype(float)
month = dates.dt.month.values.astype(float)
n = len(df)

# 2024 真实值（供滚动回测对比）
from sqlalchemy import create_engine, text
pw = os.environ.get("DB_PASSWORD", "1234")
e = create_engine(f"mysql+pymysql://root:{pw}@localhost:3306/weatherdb")
with e.connect() as c:
    rows = c.execute(text("SELECT date, avg_temp FROM weather_data_2024")).fetchall()
cur = pd.DataFrame(rows, columns=["record_date", "avg_temp"])
cur["record_date"] = pd.to_datetime(cur["record_date"])
cur = cur.sort_values("record_date").reset_index(drop=True)
y24 = cur["avg_temp"].values
dates24 = cur["record_date"]
print(f"历史 {n} 天；2024 真实 {len(cur)} 天")


# ---------------- 特征构建 ----------------
def add_lags(arr, lags):
    """对一维序列 arr 构造滞后列矩阵（NaN 表示不足）"""
    cols = []
    for L in lags:
        v = np.full(len(arr), np.nan)
        v[L:] = arr[:-L]
        cols.append(v)
    return np.column_stack(cols)


def build_features(arr, doy_arr, month_arr, K=2):
    """arr: 目标序列(长度为 L)，doy/month 同长 → 特征矩阵"""
    cols = [month_arr, doy_arr]
    for k in range(1, K + 1):
        cols.append(np.sin(2 * np.pi * k * doy_arr / 365.25))
        cols.append(np.cos(2 * np.pi * k * doy_arr / 365.25))
    cols.append(add_lags(arr, [1, 2, 3, 7, 30, 365]))
    return np.column_stack(cols)


LAGS = [1, 2, 3, 7, 30, 365]

# ---------------- 评估A: 训练2004-2021 → 滚动1步预测2022-2023 ----------------
# 注意 GBDT 没有显式"昨日异常"结构，滚动1步 = 每步真实 lag 已知
tr_end = df[df["record_date"] < "2022-01-01"].index[-1]  # 训练到2021-12-31
te_idx = np.arange(tr_end + 1, n)

X_all = build_features(y, doy, month)
X_tr, X_te = X_all[: tr_end + 1], X_all[te_idx]
mask_tr = ~np.isnan(X_tr).any(axis=1)
mask_te = ~np.isnan(X_te).any(axis=1)

gb = GradientBoostingRegressor(
    n_estimators=300, learning_rate=0.06, max_depth=4,
    subsample=0.9, random_state=42)
gb.fit(X_tr[mask_tr], y[: tr_end + 1][mask_tr])

yhat_te = gb.predict(X_te[mask_te])
y_te = y[te_idx][mask_te]
mae_gbdt_roll1 = float(np.mean(np.abs(y_te - yhat_te)))
rmse_gbdt_roll1 = float(np.sqrt(np.mean((y_te - yhat_te) ** 2)))
print(f"\n[评估A GBDT 滚动1步 2022-2023] MAE={mae_gbdt_roll1:.3f} RMSE={rmse_gbdt_roll1:.3f}  (n={len(y_te)})")
print(f"  对照: 气候态+异常AR1 滚动1步 MAE=2.226")

# 评估B：模型只在 2004-2023 训练一次（2024 全程不参与训练 → 无泄漏），
# 滚动回测时把"起点前已观测的 2024 真实值"作为 lag 输入同一模型。
# （时序回测标准做法：模型参数固定，测试期只更新特征。）
LEAD = 30
# 训练模型（历史全量，含 lag365 需要的前 365 天丢弃）
X_hist = build_features(y, doy, month)
ok_hist = ~np.isnan(X_hist).any(axis=1)
g_model = GradientBoostingRegressor(
    n_estimators=250, learning_rate=0.07, max_depth=4,
    subsample=0.9, random_state=42)
g_model.fit(X_hist[ok_hist], y[ok_hist])
print("[训练] GBDT 历史模型完成 (n=%d)" % ok_hist.sum())


def recursive_forecast_window(s0, days_ahead):
    """从起点 s0 递归预测 days_ahead 天，返回 (dates[], preds[], actuals[])"""
    # 已观测序列 = 2004-2023 全量 + 2024 起点前的真实
    offset = (s0 - pd.Timestamp("2024-01-01")).days
    obs_y = np.concatenate([y, y24[:offset]])
    dates_out, preds, actuals = [], [], []
    hist = list(obs_y)
    for lead in range(1, days_ahead + 1):
        d = s0 + pd.Timedelta(days=lead - 1)
        if d > dates24.max():
            break
        ddoy, dmonth = float(d.dayofyear), float(d.month)
        feats = [dmonth, ddoy]
        for k in range(1, 3):
            feats += [np.sin(2 * np.pi * k * ddoy / 365.25),
                      np.cos(2 * np.pi * k * ddoy / 365.25)]
        cv = np.array(hist)
        feats += [cv[-L] if len(cv) >= L else np.nan for L in LAGS]
        pred = float(g_model.predict(np.array(feats).reshape(1, -1))[0])
        dates_out.append(d)
        preds.append(pred)
        actuals.append(y24[offset + lead - 1])
        hist.append(pred)
    return dates_out, np.array(preds), np.array(actuals)


starts = pd.date_range("2024-01-01", dates24.max() - pd.Timedelta(days=LEAD), freq="7D")
rec_mae_by_lead = {L: [] for L in range(1, LEAD + 1)}
for s0 in starts:
    _, preds, actuals = recursive_forecast_window(s0, LEAD)
    for i, (p, a) in enumerate(zip(preds, actuals), start=1):
        rec_mae_by_lead[i].append(abs(p - a))

# 每月1号窗口 → 前端（同样用已训练模型）
gbdt_windows = []
for m in range(1, 13):
    s0 = pd.Timestamp(f"2024-{m:02d}-01")
    dates_out, preds, actuals = recursive_forecast_window(s0, 30)
    w = [{"date": d.strftime("%Y-%m-%d"), "y": round(float(a), 2), "yhat": round(float(p), 2)}
         for d, p, a in zip(dates_out, preds, actuals)]
    gbdt_windows.append({"start": s0.strftime("%Y-%m-%d"), "label": f"2024-{m:02d}", "window": w})

gbdt_lead_mae = {L: float(np.mean(v)) if v else None for L, v in rec_mae_by_lead.items()}

# 汇总分段 MAE
def seg(lo, hi):
    vals = []
    for L in range(lo, hi + 1):
        if gbdt_lead_mae[L] is not None:
            vals.append(gbdt_lead_mae[L])
    return float(np.mean(vals)) if vals else None

print(f"\n[评估B GBDT 30天递归回测 2024] lead1-7={seg(1,7):.3f}  8-15={seg(8,15):.3f}  16-30={seg(16,30):.3f}")
print("  对照(气候态+AR1): lead1-7=2.816 8-15=3.055 16-30=3.031")

# ---------------- 输出 JSON + 图 ----------------
payload = {
    "model": "GBDT 梯度提升(GradientBoosting)",
    "lead": list(range(1, LEAD + 1)),
    "mae": [round(gbdt_lead_mae[L], 3) if gbdt_lead_mae[L] else None for L in range(1, LEAD + 1)],
    "seg_1_7": round(seg(1, 7), 3), "seg_8_15": round(seg(8, 15), 3), "seg_16_30": round(seg(16, 30), 3),
    "mae_roll1_2022_23": round(mae_gbdt_roll1, 3),
    "windows": gbdt_windows,
}
out = ROOT / "model" / "gbdt_backtest.json"
out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
print("[JSON]", out)

# 图: GBDT lead-MAE vs AR1(读 short_forecast.json)
try:
    ar1 = json.loads((ROOT / "model" / "short_forecast.json").read_text(encoding="utf-8"))
    ar1_mae = ar1["mae"]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(range(1, LEAD + 1), ar1_mae, marker="o", ms=4, color="#2563eb", lw=2, label="气候态+异常AR(1)")
    ax.plot(range(1, LEAD + 1), [gbdt_lead_mae[L] for L in range(1, LEAD + 1)],
            marker="s", ms=4, color="#d85a30", lw=2, label="GBDT(ML基线)")
    ax.set_xlabel("预测天数 lead (天)"); ax.set_ylabel("MAE (℃)")
    ax.set_title("2024 滚动回测: 统计方法 vs 机器学习基线 (MAE vs lead)")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(IMG / "gbdt_vs_ar1_lead_mae.png", dpi=150)
    plt.close(fig)
    print("[图] model/img/gbdt_vs_ar1_lead_mae.png")
except Exception as ex:
    print("绘图对照跳过:", ex)

print("\n[完成]")
