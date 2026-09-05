# -*- coding: utf-8 -*-
"""
新旧模型在 2024 真实数据上的直接对比
- 旧方案: statsmodels SARIMAX(2,1,3) + Fourier K=3 (全量训练 2004-2023, 预测 2024)
- 新方案: 谐波回归 K=3 (同训练窗口)
- 真实: MySQL weather_data_2024
运行: base Anaconda (有 statsmodels)
"""
import os
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]  # weather/
df = pd.read_csv(ROOT / "forecast" / "data" / "weather_data_clean.csv", parse_dates=["record_date"])
df = df.sort_values("record_date").reset_index(drop=True)

# 真实 2024 从 MySQL 读
from sqlalchemy import create_engine, text
pw = os.environ.get("DB_PASSWORD", "1234")
e = create_engine(f"mysql+pymysql://root:{pw}@localhost:3306/weatherdb")
with e.connect() as c:
    rows = c.execute(text("SELECT date, avg_temp FROM weather_data_2024")).fetchall()
actual = pd.DataFrame(rows, columns=["date", "avg_temp"])
actual["date"] = pd.to_datetime(actual["date"])
actual = actual.sort_values("date").reset_index(drop=True)
print(f"2024 真实数据: {len(actual)} 天  {actual['date'].min().date()} ~ {actual['date'].max().date()}")

dates_2024 = actual["date"]


def fourier_exog(dates, K):
    doy = dates.dt.dayofyear.values.astype(float)
    X = pd.DataFrame({f"sin{k}": np.sin(2 * np.pi * k * doy / 365.25) for k in range(1, K + 1)} |
                     {f"cos{k}": np.cos(2 * np.pi * k * doy / 365.25) for k in range(1, K + 1)}, index=dates)
    return X


# ---------- 旧方案: SARIMAX(2,1,3)+Fourier ----------
from statsmodels.tsa.statespace.sarimax import SARIMAX
y_tr = df["avg_temp"].values
dates_tr = df["record_date"]
exog_tr = fourier_exog(dates_tr, 3)
exog_24 = fourier_exog(dates_2024, 3)
m = SARIMAX(y_tr, exog=exog_tr, order=(2, 1, 3), enforce_stationarity=False, enforce_invertibility=False)
res = m.fit(disp=False, maxiter=300, method="lbfgs")
fc = res.get_forecast(steps=len(dates_2024), exog=exog_24)
old_2024 = fc.predicted_mean.values

# ---------- 新方案: 谐波回归 K=3 ----------
def design(dates, K=3):
    dates = pd.DatetimeIndex(dates)
    t = (dates - pd.Timestamp("2004-01-01")).days.values / 365.25
    doy = dates.dayofyear.values
    cols = [np.ones_like(t), t]
    for k in range(1, K + 1):
        cols.append(np.sin(2 * np.pi * k * doy / 365.25))
        cols.append(np.cos(2 * np.pi * k * doy / 365.25))
    return np.column_stack(cols)

beta, *_ = np.linalg.lstsq(design(dates_tr), y_tr, rcond=None)
new_2024 = design(dates_2024) @ beta

y_24 = actual["avg_temp"].values


def mae(a, b): return float(np.mean(np.abs(a - b)))
def rmse(a, b): return float(np.sqrt(np.mean((a - b) ** 2)))


print("\n================ 2024 全年对比 ================")
print(f"旧方案 ARIMAX+Fourier : MAE {mae(y_24, old_2024):.3f}℃  RMSE {rmse(y_24, old_2024):.3f}℃")
print(f"新方案 谐波回归 K=3   : MAE {mae(y_24, new_2024):.3f}℃  RMSE {rmse(y_24, new_2024):.3f}℃")
print(f"真实 2024 全年均温    : {y_24.mean():.2f}℃")

print("\n================ 逐月 MAE ================")
print(f"{'月份':<8}{'旧ARIMAX':<12}{'新谐波':<12}{'真实均值':<10}")
for mth in range(1, 13):
    m_ = actual["date"].dt.month.values == mth
    if m_.sum() == 0:
        continue
    print(f"{mth}月     {mae(y_24[m_], old_2024[m_]):<10.3f}{mae(y_24[m_], new_2024[m_]):<10.3f}{y_24[m_].mean():<10.2f}")

print("\n================ 逐月真实均值差异(模型系统性偏差诊断) ================")
for mth in range(1, 13):
    m_ = actual["date"].dt.month.values == mth
    if m_.sum() == 0:
        continue
    bias_old = np.mean(old_2024[m_] - y_24[m_])
    bias_new = np.mean(new_2024[m_] - y_24[m_])
    print(f"{mth}月  旧偏差 {bias_old:+.2f}℃  新偏差 {bias_new:+.2f}℃")
