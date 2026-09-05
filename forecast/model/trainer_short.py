# -*- coding: utf-8 -*-
"""
trainer_short.py —— 短期预测：气候态 + 异常 AR(1)
=====================================================
依据 EDA：ACF(1)=0.973 → "昨日距平"对次日有强预测力。
模型：y_t = clim(同日气候态) + a_t；a_t = φ·a_{t-1}（异常一阶自回归）

评估：2024 全年滚动回测 —— 每 7 天一个预测起点，从起点前最后一个真实异常出发，
递推预测未来 30 天（lead=1..30），与 weather_data_2024 真实值对比。
只用起点之前的真实数据，无信息泄漏。产出：
  - 图：MAE vs lead(1..30) —— 展示短期优势随预测天数衰减
  - JSON：供前端 forecast 页展示短期回测曲线
"""
import os
import json
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]          # forecast/
IMG = ROOT / "model" / "img"
IMG.mkdir(parents=True, exist_ok=True)

# ---------- 数据：训练 2004-2023（历史），真实 2024 ----------
hist = pd.read_csv(ROOT / "data" / "weather_data_clean.csv", parse_dates=["record_date"])
hist = hist.sort_values("record_date").reset_index(drop=True)

from sqlalchemy import create_engine, text
pw = os.environ.get("DB_PASSWORD", "1234")
e = create_engine(f"mysql+pymysql://root:{pw}@localhost:3306/weatherdb")
with e.connect() as c:
    rows = c.execute(text("SELECT date, avg_temp FROM weather_data_2024")).fetchall()
cur = pd.DataFrame(rows, columns=["record_date", "avg_temp"])
cur["record_date"] = pd.to_datetime(cur["record_date"])
cur = cur.sort_values("record_date").reset_index(drop=True)
print(f"历史 {len(hist)} 天 (2004-2023)  当前/真实 {len(cur)} 天 (2024)")

# ---------- 气候态（按 月-日，历史 20 年同日平均） ----------
def clim_by_md(df_hist):
    md = df_hist["record_date"].dt.strftime("%m-%d")
    return pd.Series(df_hist["avg_temp"].values, index=md).groupby(level=0).mean()

CLIM = clim_by_md(hist)
y_hist = hist["avg_temp"].values
anom_hist = y_hist - CLIM.reindex(hist["record_date"].dt.strftime("%m-%d")).values
phi = np.sum(anom_hist[1:] * anom_hist[:-1]) / np.sum(anom_hist[:-1] ** 2)
print(f"异常AR(1) φ = {phi:.4f}")

# ---------- 2024 滚动回测：起点 2024-01-01 起每 7 天，lead 1..30 ----------
md_cur = cur["record_date"].dt.strftime("%m-%d").values
y_cur = cur["avg_temp"].values
date_to_anom = {}          # 已知真实日期 -> 异常
for i in range(len(cur)):
    date_to_anom[cur["record_date"][i]] = y_cur[i] - CLIM[md_cur[i]]
# 起点前最后一天可能是 2023-12-31（属于历史）也纳入
hist_last = hist.iloc[-1]
date_to_anom[hist_last["record_date"]] = hist_last["avg_temp"] - CLIM[hist_last["record_date"].strftime("%m-%d")]

START = pd.Timestamp("2024-01-01")
LEAD = 30
starts = pd.date_range(START, cur["record_date"].max() - pd.Timedelta(days=LEAD), freq="7D")

# 收集 (lead, abs_err) 对
records = []   # 每个元素: {start_idx, lead, date, y, yhat, err}
for s0 in starts:
    prev_day = s0 - pd.Timedelta(days=1)
    if prev_day not in date_to_anom:
        continue
    a0 = date_to_anom[prev_day]
    for lead in range(1, LEAD + 1):
        d = s0 + pd.Timedelta(days=lead - 1)
        if d not in date_to_anom:   # 超出 2024 无真实
            continue
        clim_v = CLIM[d.strftime("%m-%d")]
        yhat = clim_v + (phi ** lead) * a0
        y_true = date_to_anom[d] + clim_v
        records.append({"start": s0.strftime("%Y-%m-%d"), "lead": lead,
                        "date": d.strftime("%Y-%m-%d"), "y": y_true, "yhat": yhat})

dfr = pd.DataFrame(records)
print(f"回测样本: {len(dfr)} 个 (起点 {dfr['start'].nunique()} 个 × lead)")

# lead-MAE 曲线
lead_mae = dfr.groupby("lead")["err"].mean() if False else \
    dfr.groupby("lead").apply(lambda g: np.mean(np.abs(g["y"] - g["yhat"])), include_groups=False)
lead_mae = lead_mae.reset_index()
lead_mae.columns = ["lead", "mae"]

# 汇总：1-7 / 8-15 / 16-30 天平均 MAE（前端 metric）
def seg_mae(lo, hi):
    s = dfr[(dfr["lead"] >= lo) & (dfr["lead"] <= hi)]
    return float(np.mean(np.abs(s["y"] - s["yhat"]))) if len(s) else None

mae_1_7 = seg_mae(1, 7)
mae_8_15 = seg_mae(8, 15)
mae_16_30 = seg_mae(16, 30)
mae_all = float(np.mean(np.abs(dfr["y"] - dfr["yhat"])))
print(f"MAE lead1-7={mae_1_7:.3f}  8-15={mae_8_15:.3f}  16-30={mae_16_30:.3f}  全体={mae_all:.3f}")

# 每起点误差（画带均值±std 的带状图需要按 lead 的 std）
lead_std = dfr.groupby("lead")["err"].std() if False else \
    dfr.groupby("lead").apply(lambda g: np.std(np.abs(g["y"] - g["yhat"])), include_groups=False)
lead_std = lead_std.reset_index()
lead_std.columns = ["lead", "std"]

# ---------- 图：MAE vs lead ----------
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(lead_mae["lead"], lead_mae["mae"], marker="o", ms=4, color="#dc2626", lw=2, label="短期预测 MAE (气候态+异常AR1)")
ax.fill_between(lead_mae["lead"], lead_mae["mae"] - lead_std["std"] / 2,
                lead_mae["mae"] + lead_std["std"] / 2, color="#dc2626", alpha=0.12, label="±std/2 波动")
# 参考线：长期谐波 MAE、气候态 MAE
ax.axhline(3.168, color="#2563eb", ls="--", lw=1.5, label="长期谐波回归 MAE=3.168")
ax.axhline(3.269, color="#64748b", ls=":", lw=1.5, label="纯气候态 MAE=3.269")
ax.set_xlabel("预测天数 lead (天)")
ax.set_ylabel("MAE (℃)")
ax.set_title("短期预测误差随预测天数增长 (2024年滚动回测, 起点每7天)")
ax.legend(); ax.grid(alpha=0.3)
ax.annotate("昨日记忆期\n(前1-7天最准)", xy=(3, mae_1_7), xytext=(3, mae_1_7 - 1.0),
            arrowprops=dict(arrowstyle="->"), fontsize=10)
fig.tight_layout()
fig.savefig(IMG / "short_lead_mae.png", dpi=150)
plt.close(fig)
print("[图] model/img/short_lead_mae.png")

# ---------- 第二个图：示例窗口（2024-01-01 起 30 天）真实 vs 预测 ----------
ex = dfr[dfr["start"] == START.strftime("%Y-%m-%d")].sort_values("lead")
fig, ax = plt.subplots(figsize=(13, 4.5))
ax.plot(ex["date"], ex["y"], marker="o", ms=3, color="#5470c6", lw=1.5, label="2024 真实")
ax.plot(ex["date"], ex["yhat"], marker="s", ms=3, color="#d85a30", lw=1.5, label="短期预测(气候态+AR1, 起点=2023-12-31)")
ax.set_title("示例窗口：2024-01-01 起 30 天 短期预测 vs 真实（展示前段贴合）")
ax.legend(); ax.grid(alpha=0.3); ax.set_ylabel("气温(℃)")
plt.xticks(rotation=45)
fig.tight_layout(); fig.savefig(IMG / "short_window_example.png", dpi=150)
plt.close(fig)
print("[图] model/img/short_window_example.png")

# ---------- JSON（供前端）：lead-MAE + 多窗口（每月1号起点，lead1..30） ----------
windows = []
for m in range(1, 13):
    s0 = pd.Timestamp(f"2024-{m:02d}-01")
    prev_day = s0 - pd.Timedelta(days=1)
    if prev_day not in date_to_anom:
        continue
    a0 = date_to_anom[prev_day]
    w = []
    for lead in range(1, 31):
        d = s0 + pd.Timedelta(days=lead - 1)
        if d not in date_to_anom:
            break
        clim_v = CLIM[d.strftime("%m-%d")]
        w.append({"date": d.strftime("%Y-%m-%d"),
                  "y": round(date_to_anom[d] + clim_v, 2),
                  "yhat": round(clim_v + (phi ** lead) * a0, 2)})
    windows.append({"start": s0.strftime("%Y-%m-%d"), "label": f"2024-{m:02d}", "window": w})

payload = {
    "model": "气候态 + 异常AR(1)",
    "phi": float(phi),
    "lead": lead_mae["lead"].astype(int).tolist(),
    "mae": [round(v, 3) for v in lead_mae["mae"]],
    "mae_1_7": round(mae_1_7, 3), "mae_8_15": round(mae_8_15, 3),
    "mae_16_30": round(mae_16_30, 3),
    "long_mae_harmonic": 3.168, "clim_mae": 3.269,
    "windows": windows,
}
json_path = ROOT / "model" / "short_forecast.json"
json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
print("[JSON]", json_path)
print("[窗口数]", len(windows))
print("\n[完成] 短期回测产物已生成")
