# -*- coding: utf-8 -*-
"""
AR 定阶最终决策：平台分析 + 阶段B真测试段评估
观点：严格 argmin 在噪声中漂移(3~9)，应取"平台起点"——看 p=1→2→3 的边际改善在哪收敛。
对 AR(1)/AR(2)/AR(3)/AR(4) 在真正测试段(2022-2023)做最终评估（p 选择基于平台逻辑而非 2022-23 调参）。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd
from pathlib import Path

DATA = Path(r"F:\Users\肖炳旭\Desktop\tm\项目相关\weather\forecast\data\multi_city")
CITIES = [("kunming", "昆明"), ("zhengzhou", "郑州"), ("lanzhou", "兰州"), ("beijing", "北京"),
          ("yinchuan", "银川"), ("hohhot", "呼和浩特"), ("changchun", "长春")]
P_TEST = [1, 2, 3, 4]


def fit_ar_ols(series, p):
    n = len(series)
    X = np.column_stack([series[p - 1 - i: n - 1 - i] for i in range(p)])
    phi, *_ = np.linalg.lstsq(X, series[p:], rcond=None)
    return phi


def roll1step(clim_tr, anom_tr, te_df, p, phi):
    te_md = te_df["record_date"].dt.strftime("%m-%d").values
    y_te = te_df["avg_temp"].values
    te_anom = y_te - clim_tr.reindex(te_md).values
    hist = list(anom_tr)
    yhat = np.zeros(len(te_df))
    for i in range(len(te_df)):
        window = hist[-p:]
        pred_anom = sum(phi[j] * window[-1 - j] for j in range(p))
        yhat[i] = clim_tr.reindex([te_md[i]]).values[0] + pred_anom
        hist.append(te_anom[i])
    return y_te, yhat


print("========== 阶段B：真测试段(2022-2023)最终评估 ==========")
print(f"{'城市':<6}" + "".join(f"{'AR('+str(p)+')':>10}" for p in P_TEST))
print("-" * 50)
all_mae = {p: [] for p in P_TEST}
for key, name in CITIES:
    df = pd.read_csv(DATA / f"{key}_2004_2023.csv", parse_dates=["record_date"])
    tr = df[df["record_date"] < "2022-01-01"]
    te = df[df["record_date"] >= "2022-01-01"]
    md_tr = tr["record_date"].dt.strftime("%m-%d")
    clim_tr = pd.Series(tr["avg_temp"].values, index=md_tr).groupby(level=0).mean()
    anom_tr = tr["avg_temp"].values - clim_tr.reindex(md_tr).values
    row = []
    for p in P_TEST:
        phi = fit_ar_ols(anom_tr, p)
        y_true, yhat = roll1step(clim_tr, anom_tr, te, p, phi)
        m = float(np.mean(np.abs(y_true - yhat)))
        all_mae[p].append(m)
        row.append(m)
    print(f"{name:<6}" + "".join(f"{m:>10.3f}" for m in row))

print("\n=== 跨城平均 MAE（7城）===")
for p in P_TEST:
    print(f"AR({p}): {np.mean(all_mae[p]):.4f}  (相对AR1提升 {(1-np.mean(all_mae[1])/np.mean(all_mae[p]))*100:+.2f}%)")
