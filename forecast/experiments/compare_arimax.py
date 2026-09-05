# -*- coding: utf-8 -*-
"""
C6 复现：现有方案 ARIMAX+Fourier（statsmodels SARIMAX(2,1,3), K=3, 原网格BIC最优）
运行环境：base Anaconda（numpy 1.26 + statsmodels 0.14.2，原生库正常）
评估 B：固定起点 730 天长期预测（与项目实际用法一致）
输出：compare_arimax.json + npz
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from statsmodels.tsa.statespace.sarimax import SARIMAX

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "weather_data_clean.csv"
OUT = ROOT / "experiments"

df = pd.read_csv(DATA, parse_dates=["record_date"])
df = df.sort_values("record_date").reset_index(drop=True)
tr = df[(df["record_date"] >= "2004-01-01") & (df["record_date"] <= "2021-12-31")].reset_index(drop=True)
te = df[(df["record_date"] >= "2022-01-01") & (df["record_date"] <= "2023-12-31")].reset_index(drop=True)
y_tr = tr["avg_temp"].values
y_te = te["avg_temp"].values
print(f"train n={len(tr)} test n={len(te)}")

def build_fourier(dates, K):
    doy = dates.dt.dayofyear.values.astype(float)
    X = {}
    for k in range(1, K + 1):
        X[f"sin{k}"] = np.sin(2 * np.pi * k * doy / 365.25)
        X[f"cos{k}"] = np.cos(2 * np.pi * k * doy / 365.25)
    return pd.DataFrame(X, index=dates)

K = 3
exog_tr = build_fourier(tr["record_date"], K)
exog_te = build_fourier(te["record_date"], K)

print("fitting SARIMAX(2,1,3) exog K=3 ...")
m = SARIMAX(y_tr, exog=exog_tr, order=(2, 1, 3),
            enforce_stationarity=False, enforce_invertibility=False)
res = m.fit(disp=False, maxiter=300, method="lbfgs")
print("fit done aic=%.1f bic=%.1f" % (res.aic, res.bic))

fc = res.get_forecast(steps=len(te), exog=exog_te)
yhat = fc.predicted_mean.values
ci = fc.conf_int(alpha=0.05)
lo, hi = ci.iloc[:, 0].values, ci.iloc[:, 1].values

mae = float(np.mean(np.abs(y_te - yhat)))
rmse = float(np.sqrt(np.mean((y_te - yhat) ** 2)))
cov = float(np.mean((y_te >= lo) & (y_te <= hi)))
print(f"B_C6 MAE {mae:.3f} RMSE {rmse:.3f} coverage {cov:.2%}")

# 按季节分桶 MAE
months = te["record_date"].dt.month.values
season = {}
for name, ms in [("春", [3, 4, 5]), ("夏", [6, 7, 8]), ("秋", [9, 10, 11]), ("冬", [12, 1, 2])]:
    m_ = np.isin(months, ms)
    if m_.sum() > 0:
        season[name] = round(float(np.mean(np.abs(y_te[m_] - yhat[m_]))), 3)

# 残差检验：Ljung-Box（白噪声检验，评估模型是否捕获了自相关）
from statsmodels.stats.diagnostic import acorr_ljungbox
resid = y_tr - res.fittedvalues
lb = acorr_ljungbox(resid, lags=[20], return_df=True)
lb_p = float(lb["lb_pvalue"].iloc[0])
print(f"残差 Ljung-Box p(20)={lb_p:.4f} (越小越说明残差仍有自相关)")

json.dump(
    {"B_C6_arimax_fourier": {"mae": mae, "rmse": rmse, "coverage": cov,
                              "season": season, "aic": float(res.aic), "bic": float(res.bic),
                              "ljungbox_p20": lb_p}},
    open(OUT / "compare_arimax.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2,
)
np.savez_compressed(OUT / "compare_arimax_data.npz",
                    te_dates=te["record_date"].values.astype("datetime64[D]"),
                    y_te=y_te, yhat=yhat, lo=lo, hi=hi)
print("[完成] compare_arimax.json saved")
