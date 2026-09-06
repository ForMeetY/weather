# -*- coding: utf-8 -*-
"""
标准时序流程补齐检验（供《天气分析.md》重构引用）
覆盖：
  1) 平稳性检验：ADF + KPSS（原始日气温序列 / 去趋势季节后的异常序列）
  2) 白噪声检验：Ljung-Box（原始 / 异常序列）
  3) 模型检验：谐波回归残差 与 AR(1) 残差的 Ljung-Box / 残差描述
  4) 参数显著性：谐波回归系数表（t 值粗略，OLS 标准差）
输出：文本结果 + img/diag_*（平稳性/残差图）
"""
import numpy as np
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX  # noqa (保持依赖提示)

ROOT = Path(__file__).resolve().parents[1]  # forecast/
OUT = ROOT / "model" / "img"
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(ROOT / "data" / "weather_data_clean.csv", parse_dates=["record_date"])
df = df.sort_values("record_date").reset_index(drop=True)
y = df["avg_temp"].values
dates = df["record_date"]

# ---------- 辅助 ----------
def md_key(d):
    return d.strftime("%m-%d")

# 气候态（月-日平均）
clim = pd.Series(y, index=df["record_date"].dt.strftime("%m-%d")).groupby(level=0).mean()
anom = y - clim.reindex(df["record_date"].dt.strftime("%m-%d")).values

print("=" * 70)
print("【1】平稳性检验  ADF(H0:非平稳) 与 KPSS(H0:平稳)")
print("=" * 70)
for name, s in [("原始日气温 avg_temp", y), ("气候态分解后的异常序列 anomaly", anom)]:
    # ADF
    adf = adfuller(s, autolag="AIC")
    # KPSS (需去掉常数项趋势噪声，回归"ct"? 用默认"c")
    try:
        kp = kpss(s, regression="c", nlags="auto")
    except Exception as ex:
        kp = (np.nan, np.nan, None, None)
    print(f"\n序列: {name}  (n={len(s)})")
    print(f"  ADF  统计量={adf[0]:.4f}  p值={adf[1]:.2e}  结论={'平稳(拒绝H0)' if adf[1]<0.05 else '非平稳'}")
    print(f"  KPSS 统计量={kp[0]:.4f}  p值={kp[1]:.2e}  结论={'非平稳(拒绝H0)' if kp[1]<0.05 else '平稳'}")

print("\n" + "=" * 70)
print("【2】白噪声检验 Ljung-Box (m=20)")
print("=" * 70)
for name, s in [("原始日气温", y), ("异常序列(去气候态)", anom)]:
    lb = acorr_ljungbox(s, lags=[20], return_df=True)
    p = float(lb["lb_pvalue"].iloc[0])
    q = float(lb["lb_stat"].iloc[0])
    print(f"{name}: Q(20)={q:.1f}  p={p:.2e}  → {'显著非白噪声(可建模)' if p<0.05 else '接近白噪声'}")

print("\n" + "=" * 70)
print("【3】谐波回归(K=3)残差检验：训练 2004-2021，测试 2022-23")
print("=" * 70)
tr = df[df["record_date"] < "2022-01-01"]
te = df[df["record_date"] >= "2022-01-01"]


def design(dts, K):
    d = pd.DatetimeIndex(dts)
    t = (d - pd.Timestamp("2004-01-01")).days.values / 365.25
    doy = d.dayofyear.values
    c = [np.ones_like(t), t]
    for k in range(1, K + 1):
        c += [np.sin(2 * np.pi * k * doy / 365.25), np.cos(2 * np.pi * k * doy / 365.25)]
    return np.column_stack(c)


K = 3
X = design(tr["record_date"], K)
beta, *_ = np.linalg.lstsq(X, tr["avg_temp"].values, rcond=None)
fit_tr = X @ beta
resid_tr = tr["avg_temp"].values - fit_tr
# OLS 系数标准差（粗略 t 值）
n, pcol = X.shape
sigma2 = resid_tr @ resid_tr / (n - pcol)
covb = sigma2 * np.linalg.inv(X.T @ X)
se = np.sqrt(np.diag(covb))
tvals = beta / se
names = ["const", "trend"] + [f"{s}{k}" for k in range(1, K + 1) for s in ("sin", "cos")]
print("谐波回归系数(训练段 2004-2021):")
print(f"{'参数':<8}{'估计':>10}{'t值':>8}")
for nm, b, t_ in zip(names, beta, tvals):
    print(f"{nm:<8}{b:>10.4f}{t_:>8.2f}")

# 残差白噪声
lb_r = acorr_ljungbox(resid_tr, lags=[10, 20, 40], return_df=True)
print("\n谐波回归训练残差 Ljung-Box:")
for lag in [10, 20, 40]:
    print(f"  m={lag}: p={float(lb_r.loc[lag, 'lb_pvalue']):.4f}")

# 测试残差
Xte = design(te["record_date"], K)
resid_te = te["avg_temp"].values - Xte @ beta
print(f"测试段(2022-23) 残差 MAE={np.mean(np.abs(resid_te)):.3f}  std={resid_te.std():.3f}")

# 异常序列 AR(1) 残差
phi = np.sum(anom[1:] * anom[:-1]) / np.sum(anom[:-1] ** 2)
ar1_resid = anom[1:] - phi * anom[:-1]
lb_ar1 = acorr_ljungbox(ar1_resid, lags=[10, 20], return_df=True)
print(f"\nAR(1) 残差 (φ={phi:.4f}) Ljung-Box:")
for lag in [10, 20]:
    print(f"  m={lag}: p={float(lb_ar1.loc[lag, 'lb_pvalue']):.4f}")

# ---------- 图 ----------
fig, axes = plt.subplots(2, 2, figsize=(14, 8))
# 残差时序
axes[0, 0].plot(tr["record_date"], resid_tr, lw=0.4, color="#2563eb")
axes[0, 0].axhline(0, color="gray", lw=0.8)
axes[0, 0].set_title("谐波回归(K=3)训练残差时序(2004-2021)")
# 残差 ACF
from statsmodels.graphics.tsaplots import plot_acf
plot_acf(resid_tr, lags=60, ax=axes[0, 1], title="谐波回归训练残差 ACF(应落入白噪声带)")
# 原始 vs 异常 ACF 对比用异常ACF
plot_acf(anom, lags=60, ax=axes[1, 0], title="异常序列 ACF (PACF 1阶截尾→AR1)")
# 残差直方
axes[1, 1].hist(resid_tr, bins=80, color="#2563eb", alpha=0.7, density=True)
axes[1, 1].set_title("谐波回归训练残差分布(近似正态?)")
fig.tight_layout()
fig.savefig(OUT / "diag_model_checks.png", dpi=150)
plt.close(fig)
print("\n[图] model/img/diag_model_checks.png")

# 汇总保存
summary = {
    "adf_kpss": {
        "raw_adf_p": float(adfuller(y, autolag="AIC")[1]),
        "raw_kpss_p": float(kpss(y, regression="c", nlags="auto")[1]),
        "anom_adf_p": float(adfuller(anom, autolag="AIC")[1]),
        "anom_kpss_p": float(kpss(anom, regression="c", nlags="auto")[1]),
    },
    "ljungbox": {
        "raw_p20": float(acorr_ljungbox(y, lags=[20], return_df=True)["lb_pvalue"].iloc[0]),
        "anom_p20": float(acorr_ljungbox(anom, lags=[20], return_df=True)["lb_pvalue"].iloc[0]),
        "harm_resid_p20": float(lb_r.loc[20, "lb_pvalue"]),
        "ar1_resid_p20": float(lb_ar1.loc[20, "lb_pvalue"]),
    },
    "harmonic_coefs": dict(zip(names, [round(float(b), 4) for b in beta])),
    "ar1_phi": float(phi),
}
import json
(ROOT / "experiments" / "diagnostics.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("[JSON] experiments/diagnostics.json")
