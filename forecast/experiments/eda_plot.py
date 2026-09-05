# -*- coding: utf-8 -*-
"""EDA 绘图（默认 Python matplotlib 3.10.0 可用）"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd

plt.rcParams["axes.unicode_minus"] = False

# 中文字体探测
cjk = None
for cand in ["SimHei", "Microsoft YaHei", "KaiTi", "SimSun"]:
    try:
        fp = fm.findfont(fm.FontProperties(family=cand), fallback_to_default=False)
        if "DejaVu" not in fp:
            cjk = cand
            break
    except Exception:
        continue
print("CJK font:", cjk)
if cjk:
    plt.rcParams["font.sans-serif"] = [cjk]

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "img"
OUT.mkdir(parents=True, exist_ok=True)
d = np.load(ROOT / "experiments" / "eda_data.npz", allow_pickle=False)
dates = pd.to_datetime(d["dates"])
avg = d["avg_temp"]
rng = d["daily_range"]
yr = d["year"]; yavg = d["yavg"]; ymax = d["ymax"]; ymin = d["ymin"]
cdoy = d["clim_doy"]; cmean = d["clim_mean"]
mmean = d["monthly_mean"]

# 图1 全序列 + 年平均
fig, axes = plt.subplots(2, 1, figsize=(15, 8))
axes[0].plot(dates, avg, lw=0.4, color="#2563eb", alpha=0.8)
axes[0].plot(pd.to_datetime(yr.astype(str) + "-07-01"), yavg, lw=2, color="#dc2626", label="年均温")
axes[0].set_title("呼和浩特日均气温全序列 (2004-2023)", fontsize=14)
axes[0].set_ylabel("气温(℃)"); axes[0].legend(); axes[0].grid(alpha=0.3)
axes[1].plot(yr, yavg, marker="o", color="#dc2626", label="年平均")
axes[1].plot(yr, ymax, marker="^", ls="--", color="#f59e0b", label="平均最高温")
axes[1].plot(yr, ymin, marker="v", ls="--", color="#3b82f6", label="平均最低温")
k1, _ = np.polyfit(yr, yavg, 1); k2, _ = np.polyfit(yr, ymax, 1); k3, _ = np.polyfit(yr, ymin, 1)
axes[1].set_title(f"年际趋势: 年均 {k1:+.3f}℃/yr | 平均最高 {k2:+.3f} | 平均最低 {k3:+.3f}", fontsize=13)
axes[1].set_xlabel("年份"); axes[1].set_ylabel("气温(℃)"); axes[1].legend(); axes[1].grid(alpha=0.3)
fig.tight_layout(); fig.savefig(OUT / "eda1_timeseries_trend.png", dpi=150); plt.close(fig)

# 图2 气候态
fig, ax = plt.subplots(figsize=(14, 4.5))
ax.plot(cdoy, cmean, color="#2563eb", lw=2, label="气候态均值(多年同日平均)")
ax.fill_between(cdoy, cmean - 1.5 * d["clim_std"], cmean + 1.5 * d["clim_std"],
                color="#2563eb", alpha=0.15, label="±1.5σ 年际带宽")
ax.set_title("气候态曲线: 一年内的平均气温与年际波动", fontsize=13)
ax.set_xlabel("年内第几天"); ax.set_ylabel("气温(℃)"); ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(OUT / "eda2_climatology.png", dpi=150); plt.close(fig)

# 图3 逐月箱线
tmp = pd.DataFrame({"month": pd.to_datetime(dates).month, "avg_temp": avg})
fig, ax = plt.subplots(figsize=(11, 4.5))
tmp.boxplot(column="avg_temp", by="month", ax=ax, grid=False, showfliers=False)
ax.set_title("逐月日均气温分布"); ax.set_xlabel("月份"); ax.set_ylabel("气温(℃)")
fig.suptitle(""); fig.tight_layout(); fig.savefig(OUT / "eda3_monthly_box.png", dpi=150); plt.close(fig)

# 图4 ACF/PACF
lags = np.arange(len(d["acf"]))
fig, axes = plt.subplots(2, 1, figsize=(14, 7))
axes[0].vlines(lags, 0, d["acf"], color="#2563eb"); axes[0].axhline(0)
axes[0].axvline(365, color="red", ls="--", lw=1, label="365天")
axes[0].plot(lags, 1.96 / np.sqrt(len(avg)) * np.ones_like(lags), "k--", lw=0.7)
axes[0].plot(lags, -1.96 / np.sqrt(len(avg)) * np.ones_like(lags), "k--", lw=0.7)
axes[0].set_title("日频 ACF (前800阶) — 1阶0.97、365阶0.87 显示强持续+年周期"); axes[0].legend()
axes[0].set_xlim(0, 800)
pl = np.arange(len(d["pacf"]))
axes[1].vlines(pl, 0, d["pacf"], color="#059669"); axes[1].axhline(0)
axes[1].set_title("PACF (前60阶) — 1阶后快速衰减"); axes[1].set_xlim(0, 60)
fig.tight_layout(); fig.savefig(OUT / "eda4_acf_pacf.png", dpi=150); plt.close(fig)

# 图5 avg 与 (max+min)/2
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].scatter(d["mid"], avg, s=2, alpha=0.3, color="#2563eb")
lim = [avg.min(), avg.max()]
axes[0].plot(lim, lim, ls="--", color="gray")
axes[0].set_xlabel("(max+min)/2 (℃)"); axes[0].set_ylabel("avg_temp (℃)")
axes[0].set_title("avg 与 (max+min)/2 高度相关但非恒等")
axes[1].hist(d["avg_mid_diff"], bins=100, color="#2563eb", alpha=0.8)
axes[1].axvline(0, color="gray", ls="--")
axes[1].set_xlabel("avg − (max+min)/2 (℃)"); axes[1].set_ylabel("天数")
axes[1].set_title("差值分布 (|差|均值 %.2f℃)" % np.abs(d["avg_mid_diff"]).mean())
fig.tight_layout(); fig.savefig(OUT / "eda5_avg_vs_midrange.png", dpi=150); plt.close(fig)

# 图6 daily_range
fig, axes = plt.subplots(2, 1, figsize=(15, 7))
axes[0].plot(dates, rng, lw=0.3, color="#059669", alpha=0.6)
axes[0].axhline(rng.mean(), color="#dc2626", lw=1.5, label=f"均值 {rng.mean():.2f}℃")
axes[0].set_title("气温日较差全序列"); axes[0].legend(); axes[0].grid(alpha=0.3)
tmp2 = pd.DataFrame({"month": pd.to_datetime(dates).month, "daily_range": rng})
tmp2.boxplot(column="daily_range", by="month", ax=axes[1], grid=False, showfliers=False)
axes[1].set_title("逐月日较差分布"); axes[1].set_xlabel("月份"); axes[1].set_ylabel("日较差(℃)")
fig.suptitle(""); fig.tight_layout(); fig.savefig(OUT / "eda6_daily_range.png", dpi=150); plt.close(fig)

# 图7 年×月热力
piv = d["pivot"]; pyrs = d["pivot_years"]
fig, ax = plt.subplots(figsize=(11, 4.8))
im = ax.imshow(piv, aspect="auto", cmap="RdBu_r", vmin=-22, vmax=30)
ax.set_yticks(range(len(pyrs))); ax.set_yticklabels(pyrs.astype(int))
ax.set_xticks(range(12)); ax.set_xticklabels([f"{m}月" for m in range(1, 13)])
ax.set_title("年 × 月 平均气温热力图")
fig.colorbar(im, ax=ax, label="℃")
fig.tight_layout(); fig.savefig(OUT / "eda7_year_month_heatmap.png", dpi=150); plt.close(fig)

print("plots saved to", OUT)
