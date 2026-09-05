# -*- coding: utf-8 -*-
"""对比实验绘图（默认 Python matplotlib）"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd

cjk = None
for cand in ["SimHei", "Microsoft YaHei"]:
    try:
        fp = fm.findfont(fm.FontProperties(family=cand), fallback_to_default=False)
        if "DejaVu" not in fp:
            cjk = cand
            break
    except Exception:
        continue
if cjk:
    plt.rcParams["font.sans-serif"] = [cjk]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "img"
OUT.mkdir(parents=True, exist_ok=True)
with open(ROOT / "experiments" / "compare_light.json", encoding="utf-8") as f:
    R = json.load(f)
d = np.load(ROOT / "experiments" / "compare_light_data.npz", allow_pickle=False)
te_dates = pd.to_datetime(d["te_dates"])
y_te = d["y_te"]

MAE = {k: v["mae"] for k, v in R.items()}

# ---- 图1: 评估A MAE 条形图 ----
names_A = ["A_C4_clim_anom_ar1", "A_C3_harmonic_K4", "A_C3_harmonic_K3", "A_C3_harmonic_K2",
           "A_C2_trend_clim", "A_C1_climatology", "A_C5_seasonal_naive"]
labels_A = ["气候态+异常AR(1)", "谐波回归 K=4", "谐波回归 K=3", "谐波回归 K=2",
            "趋势修正气候态", "气候态基准", "去年同日(naive)"]
fig, ax = plt.subplots(figsize=(10, 4.5))
vals = [MAE[n] for n in names_A]
colors = ["#dc2626" if i == 0 else "#64748b" for i in range(len(vals))]
bars = ax.barh(labels_A, vals, color=colors)
ax.invert_yaxis()
for b, v in zip(bars, vals):
    ax.text(b.get_width() + 0.03, b.get_y() + b.get_height() / 2, f"{v:.2f}", va="center", fontsize=10)
ax.set_xlabel("MAE (℃)"); ax.set_title("评估 A：滚动 1 步预测（2002-2023 测试段）MAE 对比", fontsize=13)
ax.set_xlim(0, 5.0); ax.grid(axis="x", alpha=0.3)
fig.tight_layout(); fig.savefig(OUT / "cmpA_1step_mae.png", dpi=150); plt.close(fig)

# ---- 图2: 评估B MAE 条形图 ----
names_B = ["B_C3_harmonic_K3", "B_C2_trend_clim", "B_C4_clim_anom_ar1", "B_C1_climatology"]
labels_B = ["谐波回归 K=3", "趋势修正气候态", "气候态+异常AR(1)", "气候态基准"]
fig, ax = plt.subplots(figsize=(10, 3.6))
vals = [MAE[n] for n in names_B]
colors = ["#dc2626" if i == 0 else "#64748b" for i in range(len(vals))]
bars = ax.barh(labels_B, vals, color=colors)
ax.invert_yaxis()
for b, v in zip(bars, vals):
    ax.text(b.get_width() + 0.01, b.get_y() + b.get_height() / 2, f"{v:.2f}", va="center", fontsize=10)
ax.set_xlabel("MAE (℃)"); ax.set_title("评估 B：固定起点 730 天长预测 MAE 对比（无近期信息可用）", fontsize=13)
ax.set_xlim(0, 3.6); ax.grid(axis="x", alpha=0.3)
fig.tight_layout(); fig.savefig(OUT / "cmpB_long_mae.png", dpi=150); plt.close(fig)

# ---- 图3: 测试段真实 vs 关键模型（前200天 A）----
fig, ax = plt.subplots(figsize=(15, 5.2))
idx = np.arange(200)
ax.plot(te_dates[idx], y_te[idx], lw=1.2, color="black", label="真实 avg_temp", zorder=5)
ax.plot(te_dates[idx], d["A_c4"][idx], lw=1.0, color="#dc2626", label="气候态+异常AR(1)  MAE 2.23")
ax.plot(te_dates[idx], d["A_c3"][idx], lw=0.9, color="#2563eb", alpha=0.85, label="谐波回归 K=3  MAE 3.17")
ax.plot(te_dates[idx], d["A_c1"][idx], lw=0.9, color="#64748b", ls="--", label="气候态基准  MAE 3.27")
ax.set_title("评估 A 前 200 天：滚动 1 步预测对真实曲线的跟踪", fontsize=13)
ax.legend(loc="upper right"); ax.grid(alpha=0.3); ax.set_ylabel("气温(℃)")
fig.tight_layout(); fig.savefig(OUT / "cmpA_1step_track.png", dpi=150); plt.close(fig)

# ---- 图4: 测试段 B 长期预测 vs 真实（整段）----
fig, ax = plt.subplots(figsize=(15, 5.2))
ax.plot(te_dates, y_te, lw=1.0, color="black", label="真实 avg_temp", zorder=5)
ax.plot(te_dates, d["B_c3"], lw=1.0, color="#2563eb", label="谐波回归 K=3 (730天长预测)  MAE 3.17")
ax.plot(te_dates, d["B_c2"], lw=0.9, color="#f59e0b", ls="--", label="趋势修正气候态  MAE 3.26")
ax.set_title("评估 B：固定起点 730 天长预测（只用训练期信息）——各模型差异很小", fontsize=13)
ax.legend(loc="upper right"); ax.grid(alpha=0.3); ax.set_ylabel("气温(℃)")
fig.tight_layout(); fig.savefig(OUT / "cmpB_long_track.png", dpi=150); plt.close(fig)

# ---- 图5: 分季节 MAE 热对比（A）----
seasons = ["春", "夏", "秋", "冬"]
fig, ax = plt.subplots(figsize=(10, 4.6))
sel = [("A_C4_clim_anom_ar1", "气候态+异常AR(1)"), ("A_C3_harmonic_K3", "谐波回归K3"), ("A_C1_climatology", "气候态")]
x = np.arange(len(seasons)); w = 0.26
for i, (k, lab) in enumerate(sel):
    s = R[k]["season"]
    vals = [s.get(xx, np.nan) for xx in seasons]
    ax.bar(x + (i - 1) * w, vals, w, label=lab)
ax.set_xticks(x); ax.set_xticklabels(seasons)
ax.set_ylabel("MAE (℃)"); ax.set_title("评估 A：分季节 MAE——冬季最难预测")
ax.legend(); ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(OUT / "cmpA_season_mae.png", dpi=150); plt.close(fig)

print("comparison plots saved")
