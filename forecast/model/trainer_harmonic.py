# -*- coding: utf-8 -*-
"""
trainer_harmonic.py —— 呼和浩特日均气温预测（名实相符的新方案）
====================================================================
由 EDA 驱动的建模结论（见 experiments/对比实验报告.md）：
  1) 长期预测(≥180天，大屏"未来两年")：**谐波回归 Harmonic Regression**
     模型：avg_temp = a + b·(t/365.25) + Σ_k [α_k·sin(2πk·doy/365.25) + β_k·cos(2πk·doy/365.25)] + ε
     即"线性年趋势 + K 阶傅里叶季节谐波"的最小二乘回归。
     评估(2022-2023 测试段)：MAE 3.168℃ / RMSE 4.019℃，优于原 ARIMAX+Fourier(3.182)。
  2) 短期预测(1~30天)：**气候态 + 异常AR(3)**（climatology + anomaly AR(3)）
     依据：ACF(1)=0.973 → "昨日距平"对明日有强预测力；滚动 1 步 MAE 2.194℃。

术语口径：本脚本不再使用 "SARIMAX" 名称 —— 原代码未设置季节差分(seasonal_order)，
实际为 ARIMAX+傅里叶外生项；此处长期方案改为纯谐波回归(OLS)，短期方案为气候态+AR(3)。

用法：
    python trainer_harmonic.py            # 只训练+评估+画图+存CSV
    set DB_PASSWORD=xxx && python trainer_harmonic.py   # 额外把长期预测写回 MySQL(ads_weather_forecast)
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]          # forecast/
DATA = ROOT / "data" / "weather_data_clean.csv"
IMG = ROOT / "model" / "img"
OUT = ROOT / "model"
IMG.mkdir(parents=True, exist_ok=True)

# 允许无显示器环境
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

RNG = np.random.default_rng(0)

# ================= 1. 读数据 =================
df = pd.read_csv(DATA, parse_dates=["record_date"]).sort_values("record_date").reset_index(drop=True)
df = df.asfreq("D") if False else df  # 数据本身连续
print(f"[数据] {len(df)} 行 {df['record_date'].min().date()} ~ {df['record_date'].max().date()}")

# ================= 2. 谐波回归 =================
def design_matrix(dates, K):
    """设计矩阵：截距 + 线性年趋势(以年为单位) + K 阶傅里叶季节谐波"""
    dates = pd.DatetimeIndex(dates)
    t = (dates - pd.Timestamp("2004-01-01")).days.values / 365.25
    doy = dates.dayofyear.values
    cols = [np.ones_like(t), t]
    names = ["const", "trend"]
    for k in range(1, K + 1):
        cols.append(np.sin(2 * np.pi * k * doy / 365.25))
        cols.append(np.cos(2 * np.pi * k * doy / 365.25))
        names += [f"sin{k}", f"cos{k}"]
    return np.column_stack(cols), names


def fit_harmonic(y, dates, K):
    X, names = design_matrix(dates, K)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    return beta, names, resid


def predict_harmonic(beta, dates, K):
    X, _ = design_matrix(dates, K)
    return X @ beta

# ================= 3. 长期方案评估（2022-2023 留出测试段） =================
split_date = pd.Timestamp("2022-01-01")
tr = df[df["record_date"] < split_date]
te = df[df["record_date"] >= split_date]
print(f"[切分] 训练 {tr['record_date'].min().date()}~{tr['record_date'].max().date()} "
      f"({len(tr)} 天)  测试 {len(te)} 天")

K = 3  # 实验报告选定
beta, names, resid_tr = fit_harmonic(tr["avg_temp"].values, tr["record_date"], K)
yhat_te = predict_harmonic(beta, te["record_date"], K)
y_te = te["avg_temp"].values
mae = np.mean(np.abs(y_te - yhat_te))
rmse = np.sqrt(np.mean((y_te - yhat_te) ** 2))
sigma = resid_tr.std(ddof=len(beta))
print(f"[谐波回归 K={K}] 测试段 MAE {mae:.3f}℃  RMSE {rmse:.3f}℃  残差σ {sigma:.3f}℃")
print(f"  回归系数: " + ", ".join(f"{n}={b:.3f}" for n, b in zip(names, beta)))

# 画：测试段拟合对比
fig, ax = plt.subplots(figsize=(15, 5))
ax.plot(te["record_date"], y_te, lw=1.1, color="black", label="真实")
ax.plot(te["record_date"], yhat_te, lw=1.1, color="#dc2626", label=f"谐波回归 K={K} (MAE {mae:.2f})")
ax.set_title("谐波回归长期预测 vs 真实 (2022-2023 留出测试段)")
ax.legend(); ax.grid(alpha=0.3); ax.set_ylabel("气温(℃)")
fig.tight_layout(); fig.savefig(IMG / "harmonic_eval_2022_2023.png", dpi=150); plt.close(fig)

# ================= 4. 短期方案：气候态 + 异常 AR(3) =================
clim = tr.groupby(tr["record_date"].dt.strftime("%m-%d"))["avg_temp"].mean()
anom_tr = tr["avg_temp"].values - clim.reindex(tr["record_date"].dt.strftime("%m-%d")).values


def fit_ar_ols(series, p):
    """对平稳异常序列做 AR(p) 最小二乘拟合，返回 φ 系数"""
    n = len(series)
    X = np.column_stack([series[p - 1 - i: n - 1 - i] for i in range(p)])
    phi, *_ = np.linalg.lstsq(X, series[p:], rcond=None)
    return phi


P = 3  # AR 阶数（跨城市定阶实验选定，见 experiments/ar_order_final.py）
phi = fit_ar_ols(anom_tr, P)
print(f"[异常AR({P})] " + ", ".join(f"φ{i+1}={v:.3f}" for i, v in enumerate(phi))
      + "  (滚动1步测试 MAE 2.194℃ 见实验报告)")

# ================= 5. 全量训练并预测未来 730 天（写 MySQL 与 CSV） =================
print("\n[全量训练 2004-2023 → 预测未来 730 天]")
betaF, namesF, residF = fit_harmonic(df["avg_temp"].values, df["record_date"], K)
sigmaF = residF.std(ddof=len(betaF))
future = pd.date_range(df["record_date"].max() + pd.Timedelta(days=1), periods=730)
yhatF = predict_harmonic(betaF, future, K)

# 残差按月份分桶估计 σ（季节异方差：冬季残差大）
tr_pred = predict_harmonic(betaF, df["record_date"], K)
resid_month = pd.DataFrame({
    "month": df["record_date"].dt.month.values,
    "r": (df["avg_temp"].values - tr_pred) ** 2,
}).groupby("month")["r"].mean().apply(np.sqrt)

z = 1.96
future_month = future.month
sigma_m = resid_month.reindex(future_month).values
yhat_lo = yhatF - z * sigma_m
yhat_hi = yhatF + z * sigma_m

forecast_df = pd.DataFrame({
    "ds": future.strftime("%Y-%m-%d"),
    "yhat": np.round(yhatF, 3),
    "yhat_lower": np.round(yhat_lo, 3),
    "yhat_upper": np.round(yhat_hi, 3),
})
forecast_df.to_csv(OUT / "forecast_future_730d.csv", index=False, encoding="utf-8-sig")
print(f"[CSV] 预测已存 model/forecast_future_730d.csv ({len(forecast_df)} 行)")

# 画：未来两年预测 + 置信带
fig, ax = plt.subplots(figsize=(15, 5.5))
ax.plot(df["record_date"], df["avg_temp"], lw=0.3, color="#94a3b8", alpha=0.7, label="历史 (2004-2023)")
ax.plot(future, yhatF, lw=1.6, color="#dc2626", label="谐波回归预测 (未来730天)")
ax.fill_between(future, yhat_lo, yhat_hi, color="#dc2626", alpha=0.15, label="95% 预测区间(按月残差σ)")
ax.set_title("呼和浩特日均气温：谐波回归未来两年预测")
ax.legend(); ax.grid(alpha=0.3); ax.set_ylabel("气温(℃)")
fig.tight_layout(); fig.savefig(IMG / "harmonic_forecast_730d.png", dpi=150); plt.close(fig)
print(f"[图] model/img/harmonic_forecast_730d.png")

# 写 MySQL（可选：与 show 模块 ads_weather_forecast 表兼容）
pw = os.environ.get("DB_PASSWORD")
if pw:
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(f"mysql+pymysql://root:{pw}@localhost:3306/weatherdb")
        forecast_df.to_sql("ads_weather_forecast_temp", con=engine, if_exists="replace", index=False)
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS ads_weather_forecast;"))
            conn.execute(text("RENAME TABLE ads_weather_forecast_temp TO ads_weather_forecast;"))
        print("[MySQL] 已写入 ads_weather_forecast")
    except Exception as e:
        print(f"[MySQL] 写入失败(跳过): {type(e).__name__}: {e}")
else:
    print("[MySQL] 未设置 DB_PASSWORD，跳过写库（仅存 CSV）")

print("\n[完成] 长期=谐波回归 K=3 | 短期=气候态+异常AR(3) —— 术语口径已与实验报告一致")
