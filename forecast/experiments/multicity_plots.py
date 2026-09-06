# -*- coding: utf-8 -*-
"""多城市复现 6 城：生成对比图 + 季节强度-误差散点图"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# 数据由 repro_cities_pilot.py 汇总结果构造（短期为 AR(3)，按季节振幅排序）
DATA = pd.DataFrame([
    {"city": "昆明", "amp": 10.7, "harm": 1.830, "clim": 1.846, "ar1": 1.025, "gain": 44},
    {"city": "郑州", "amp": 26.6, "harm": 2.725, "clim": 2.812, "ar1": 1.670, "gain": 41},
    {"city": "兰州", "amp": 27.6, "harm": 2.489, "clim": 2.509, "ar1": 1.431, "gain": 43},
    {"city": "北京", "amp": 30.5, "harm": 2.313, "clim": 2.384, "ar1": 1.462, "gain": 39},
    {"city": "银川", "amp": 30.7, "harm": 2.618, "clim": 2.733, "ar1": 1.589, "gain": 42},
    {"city": "呼和浩特", "amp": 33.6, "harm": 2.757, "clim": 2.941, "ar1": 1.745, "gain": 41},
    {"city": "长春", "amp": 37.9, "harm": 2.896, "clim": 3.011, "ar1": 2.054, "gain": 32},
])
DATA = DATA.sort_values("amp").reset_index(drop=True)

DOC = pathlib.Path(r"F:\Users\肖炳旭\Desktop\天气数据分析\img")
LOCAL = pathlib.Path(r"F:\Users\肖炳旭\Desktop\tm\项目相关\weather\forecast\model\img")
DOC.mkdir(parents=True, exist_ok=True); LOCAL.mkdir(parents=True, exist_ok=True)

# 图1：分组柱状（长期谐波/短期AR1 vs 气候态基线）
fig, ax = plt.subplots(figsize=(11, 5))
x = np.arange(len(DATA))
w = 0.21
ax.bar(x - 1.5*w, DATA["clim"], w, label="气候态(基线)", color="#94a3b8")
ax.bar(x - 0.5*w, DATA["harm"], w, label="谐波回归(长期)", color="#2563eb")
ax.bar(x + 0.5*w, DATA["clim"], w, color="#94a3b8", alpha=0.45)
ax.bar(x + 1.5*w, DATA["ar1"], w, label="气候态+AR(3)(短期)", color="#dc2626")
ax.set_xticks(x); ax.set_xticklabels(DATA["city"])
ax.set_ylabel("MAE (℃)")
ax.set_title("跨城市复现(7城)：长期(谐波)与短期(AR1) vs 气候态基线 (2022-23 留出段)")
ax.legend(ncol=2, fontsize=9); ax.grid(axis="y", alpha=0.3)
for i, g in enumerate(DATA["gain"]):
    ax.text(i + 1.5*w, DATA["ar1"][i] + 0.06, f"+{g}%", ha="center", fontsize=8, color="#dc2626")
fig.tight_layout()
fig.savefig(DOC / "multicity_mae.png", dpi=150); fig.savefig(LOCAL / "multicity_mae.png", dpi=150)
plt.close(fig)

# 图2：季节振幅 → 预测 MAE 散点
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(DATA["amp"], DATA["harm"], s=100, color="#2563eb", label="谐波回归(长期)", zorder=3)
ax.scatter(DATA["amp"], DATA["ar1"], s=100, marker="s", color="#dc2626", label="AR(3)(短期)", zorder=3)
for _, r in DATA.iterrows():
    ax.annotate(r["city"], (r["amp"], r["harm"]), textcoords="offset points", xytext=(7, 6), fontsize=9, color="#2563eb")
    ax.annotate(r["city"], (r["amp"], r["ar1"]), textcoords="offset points", xytext=(7, -13), fontsize=9, color="#dc2626")
zh = np.polyfit(DATA["amp"], DATA["harm"], 1)
za = np.polyfit(DATA["amp"], DATA["ar1"], 1)
xs = np.linspace(8, 40, 60)
ax.plot(xs, np.polyval(zh, xs), ls="--", color="#2563eb", alpha=0.5)
ax.plot(xs, np.polyval(za, xs), ls="--", color="#dc2626", alpha=0.5)
ax.set_xlabel("季节振幅 (7月−1月气候态差, ℃)")
ax.set_ylabel("预测 MAE (℃)")
ax.set_title("预测难度随季节强度上升（跨7城规律）")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(DOC / "multicity_amp_vs_mae.png", dpi=150); fig.savefig(LOCAL / "multicity_amp_vs_mae.png", dpi=150)
plt.close(fig)
print("[图] multicity_mae.png, multicity_amp_vs_mae.png")


