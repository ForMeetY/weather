# -*- coding: utf-8 -*-
"""汇总对比：合并轻量 + ARIMAX 结果，画最终综合图 + 生成 markdown 报告"""
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
L = json.load(open(ROOT / "experiments" / "compare_light.json", encoding="utf-8"))
A = json.load(open(ROOT / "experiments" / "compare_arimax.json", encoding="utf-8"))
ALL = {**L, **A}
dL = np.load(ROOT / "experiments" / "compare_light_data.npz", allow_pickle=False)
dA = np.load(ROOT / "experiments" / "compare_arimax_data.npz", allow_pickle=False)
te_dates = pd.to_datetime(dL["te_dates"])
y_te = dL["y_te"]

# ---------- 综合柱状图：评估B（长预测，含ARIMAX） ----------
names_B = ["B_C3_harmonic_K3", "B_C6_arimax_fourier", "B_C2_trend_clim", "B_C4_clim_anom_ar1", "B_C1_climatology"]
labels_B = ["谐波回归 K=3 (提议)", "ARIMAX+Fourier (现有)", "趋势修正气候态", "气候态+异常AR(1)", "气候态基准"]
fig, ax = plt.subplots(figsize=(10.5, 4.2))
vals = [ALL[n]["mae"] for n in names_B]
colors = ["#dc2626" if i == 0 else ("#2563eb" if i == 1 else "#94a3b8") for i in range(len(vals))]
bars = ax.barh(labels_B, vals, color=colors)
ax.invert_yaxis()
for b, v in zip(bars, vals):
    ax.text(b.get_width() + 0.01, b.get_y() + b.get_height() / 2, f"{v:.3f}", va="center", fontsize=10)
ax.set_xlabel("MAE (℃)")
ax.set_title("评估 B：固定起点 730 天长预测 MAE —— 提议的谐波回归最简且最优", fontsize=12.5)
ax.set_xlim(0, 3.6); ax.grid(axis="x", alpha=0.3)
fig.tight_layout(); fig.savefig(OUT / "cmpB_final_mae.png", dpi=150); plt.close(fig)

# ---------- 长预测曲线对比：谐波回归 vs ARIMAX vs 真实 ----------
fig, ax = plt.subplots(figsize=(15, 5.4))
ax.plot(te_dates, y_te, lw=1.1, color="black", label="真实 avg_temp", zorder=5)
ax.plot(te_dates, dL["B_c3"], lw=1.1, color="#dc2626", label="谐波回归 K=3  MAE 3.168 (提议)")
ax.plot(te_dates, dA["yhat"], lw=0.9, color="#2563eb", ls="--", label="ARIMAX+Fourier  MAE 3.182 (现有)")
ax.plot(te_dates, dA["lo"], lw=0.5, color="#2563eb", alpha=0.3)
ax.plot(te_dates, dA["hi"], lw=0.5, color="#2563eb", alpha=0.3)
ax.fill_between(te_dates, dA["lo"], dA["hi"], color="#2563eb", alpha=0.08, label="ARIMAX 95%置信区间")
ax.set_title("评估 B：730 天长预测曲线对比（2022-2023 测试段）", fontsize=13)
ax.legend(loc="upper right", fontsize=10); ax.grid(alpha=0.3); ax.set_ylabel("气温(℃)")
fig.tight_layout(); fig.savefig(OUT / "cmpB_final_track.png", dpi=150); plt.close(fig)

# ---------- 生成 markdown 报告 ----------
def md_table(names, labels):
    rows = ["| 模型 | MAE | RMSE | 覆盖率 |", "|---|---|---|---|"]
    for n, lab in zip(names, labels):
        v = ALL[n]
        cov = f"{v['coverage']:.1%}" if "coverage" in v else "—"
        rows.append(f"| {lab} | {v['mae']:.3f} | {v['rmse']:.3f} | {cov} |")
    return "\n".join(rows)

report = f"""# 气温预测方法对比实验报告（EDA 驱动的方案选型）

> 实验环境：Python；数据：呼和浩特 2004–2023 逐日气温（7305 天，完整无缺失）
> 切分：训练 2004-01-01 ~ 2021-12-31；测试 2022-01-01 ~ 2023-12-31（730 天）
> 说明：所有方法在同一测试集评估；预测目标为日均气温 avg_temp。

## 一、EDA 关键发现（驱动选型的可视化证据）

1. **日-日强持续**：ACF(1)=0.973、ACF(7)=0.910 → 短期预测中"昨日温度"信息量极大，适合对"距平(异常)序列"做自回归。
2. **强年周期**：ACF(365)=0.870、ACF(180)=-0.869 → 年度季节性必须显式建模，且周期稳定（气候态曲线平滑、年际带宽窄）。
3. **年际趋势弱但真实**：年均温 +0.039℃/年(r=0.46)，且主要来自最高温侧(+0.083℃/年)；20 年累计约 +1.7℃（最高温）。
4. **avg_temp 不是 (max+min)/2 的派生值**（r=0.997 但 |差|均值 0.71℃）→ 对 avg_temp 直接建模是独立问题。
5. **日较差稳定**：均值 14.1℃（std 3.0℃），印证"大陆性气候昼夜温差稳定"的物理解释。

## 二、候选方法（均名实相符、可解释）

| 代号 | 方法 | 命名口径 |
|---|---|---|
| C1 | 多年同日平均气候态 | Climatology（气候态基准） |
| C2 | 气候态 + 年际线性漂移 | Trend-adjusted climatology |
| C3 | 傅里叶谐波回归 + 线性年趋势 (OLS, K=3) | **谐波回归 / Harmonic regression** |
| C4 | 气候态 + 距平 AR(1) | 分解式：climatology + anomaly AR(1) |
| C5 | 去年同日 | Seasonal Naive（朴素基线） |
| C6 | statsmodels SARIMAX(2,1,3)+傅里叶外生项 K=3 | ARIMAX + Fourier（**现有方案**，网格搜索 BIC 最优） |

## 三、结果

### 评估 A：滚动 1 步预测（"天气预报"尺度，已知昨日实测）

{md_table(
    ["A_C4_clim_anom_ar1", "A_C3_harmonic_K4", "A_C3_harmonic_K3", "A_C2_trend_clim", "A_C1_climatology", "A_C5_seasonal_naive"],
    ["C4 气候态+异常AR(1) ★", "C3 谐波回归 K=4", "C3 谐波回归 K=3", "C2 趋势修正气候态", "C1 气候态", "C5 去年同日"])}

**解读**：短期预测中，气候态+异常AR(1)（MAE 2.23）比纯气候态(3.27)提升 32% —— 因为日-日持续(ACF1=0.97)意味着"昨日距平"对明日有强预测力。冬季最难预测（各方法 MAE 均更高）。

### 评估 B：固定起点 730 天长期预测（与项目"预测未来两年"用法一致）

{md_table(
    ["B_C3_harmonic_K3", "B_C6_arimax_fourier", "B_C2_trend_clim", "B_C4_clim_anom_ar1", "B_C1_climatology"],
    ["C3 谐波回归 K=3 ★(提议)", "C6 ARIMAX+Fourier (现有)", "C2 趋势修正气候态", "C4 气候态+异常AR(1)", "C1 气候态"])}

**解读**：
- 长预测无法利用近期观测，所有方法收敛到 MAE≈3.2℃（该尺度的信息下界约为气候态的不可约波动）。
- **提议的谐波回归（OLS, K=3）与现有 ARIMAX 精度持平（3.168 vs 3.182），但实现只需最小二乘、无 statsmodels 依赖、参数可直接解释为"季节谐波幅度"**。
- ARIMAX 残差 Ljung-Box p(20)=0.213 > 0.05，残差接近白噪声（模型已捕获线性依赖），但其长预测优势并未转化为更低的 MAE。

## 四、结论与建议（术语口径修正）

1. **修正"SARIMAX"术语**：现有代码未设 seasonal_order，实际是 **ARIMAX + 傅里叶外生项**；若采用本报告的 C3，则模型应准确命名为 **谐波回归（含年趋势的傅里叶回归）**，名实相符、无歧义。
2. **短期预测（≤30 天）**：推荐 **气候态 + 距平 AR(1)/ARIMA**，滚动 MAE 2.23℃，相对气候态提升 32%。
3. **长期预测（≥180 天 / "未来两年"大屏）**：推荐 **谐波回归 K=3**，与 ARIMAX 精度持平且更简单、更可解释；同时应明确"该尺度预测误差下界约 3.2℃"，置信区间比点预测更有意义。
4. 分季节评估建议保留：冬季预测误差最大，是后续用"天气过程/冷空气指数"等外生信息改进的方向。
"""
(ROOT / "experiments" / "对比实验报告.md").write_text(report, encoding="utf-8")
print("final report + figures written")
