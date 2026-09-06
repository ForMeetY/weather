# -*- coding: utf-8 -*-
"""评估A 统一重跑（2022-23 滚动1步，AR3 口径）：
AR(3) / GBDT / 纯气候态 / 去年同日 —— 与多城市脚本同口径(气候态=训练段逐日平均)"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(r"F:\Users\肖炳旭\Desktop\tm\项目相关\weather")
df = pd.read_csv(ROOT / "forecast" / "data" / "weather_data_clean.csv", parse_dates=["record_date"])
tr = df[df["record_date"] < "2022-01-01"]
te = df[df["record_date"] >= "2022-01-01"]
y_tr, y_te = tr["avg_temp"].values, te["avg_temp"].values
tr_md = tr["record_date"].dt.strftime("%m-%d")
clim_tr = pd.Series(y_tr, index=tr_md).groupby(level=0).mean()
te_md = te["record_date"].dt.strftime("%m-%d").values
te_anom = y_te - clim_tr.reindex(te_md).values


def mae(a, b): return float(np.mean(np.abs(a - b)))
def rmse(a, b): return float(np.sqrt(np.mean((a - b) ** 2)))


# --- AR(3) ---
def fit_ar(series, p):
    n = len(series)
    X = np.column_stack([series[p - 1 - i: n - 1 - i] for i in range(p)])
    phi, *_ = np.linalg.lstsq(X, series[p:], rcond=None)
    return phi

anom_tr = y_tr - clim_tr.reindex(tr_md).values
phi = fit_ar(anom_tr, 3)
hist = list(anom_tr)
yh_ar3 = np.zeros(len(te))
for i in range(len(te)):
    w = hist[-3:]
    yh_ar3[i] = clim_tr.reindex([te_md[i]]).values[0] + sum(phi[j] * w[-1 - j] for j in range(3))
    hist.append(te_anom[i])

# --- 纯气候态 ---
yh_clim = clim_tr.reindex(te_md).values

# --- 去年同日 ---
date_to_y = df.set_index("record_date")["avg_temp"]
yh_naive = np.array([date_to_y[d - pd.DateOffset(years=1)] if (d - pd.DateOffset(years=1)) in date_to_y.index else np.nan
                     for d in te["record_date"]])

# --- GBDT ---
from sklearn.ensemble import GradientBoostingRegressor
te_dates = te["record_date"]
all_y = np.concatenate([y_tr, y_te])
all_doy = np.concatenate([tr["record_date"].dt.dayofyear.values, te_dates.dt.dayofyear.values])
all_m = np.concatenate([tr["record_date"].dt.month.values, te_dates.dt.month.values])
tr_idx = np.arange(len(tr))
te_idx = np.arange(len(tr), len(tr) + len(te))


def feats_full(idx):
    out = []
    for i in idx:
        f = [all_m[i], all_doy[i]]
        for k in range(1, 3):
            f += [np.sin(2 * np.pi * k * all_doy[i] / 365.25), np.cos(2 * np.pi * k * all_doy[i] / 365.25)]
        for L in [1, 2, 3, 7, 30, 365]:
            f.append(all_y[i - L] if i >= L else np.nan)
        out.append(f)
    return np.array(out)


Xtr, Xte = feats_full(tr_idx), feats_full(te_idx)
oktr = ~np.isnan(Xtr).any(1)
gb = GradientBoostingRegressor(n_estimators=200, learning_rate=0.07, max_depth=4, subsample=0.9, random_state=42)
gb.fit(Xtr[oktr], y_tr[oktr])
yh_gbdt = gb.predict(Xte)

print(f"{'模型':<14}{'MAE':<10}{'RMSE':<10}")
for name, yh in [("气候态+AR(3)", yh_ar3), ("GBDT", yh_gbdt), ("纯气候态", yh_clim), ("去年同日", yh_naive)]:
    mask = ~np.isnan(yh)
    print(f"{name:<14}{mae(y_te[mask], yh[mask]):<10.3f}{rmse(y_te[mask], yh[mask]):<10.3f}")
print(f"\nAR(3) 较气候态提升: {(1-mae(y_te,yh_ar3)/mae(y_te,yh_clim))*100:.0f}%")
