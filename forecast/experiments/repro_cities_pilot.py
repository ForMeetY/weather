# -*- coding: utf-8 -*-
"""
跨城市复现可行性验证：乌鲁木齐(强季节) vs 昆明(弱季节)
========================================================
与呼和浩特研究完全同协议：
  训练 2004-01-01 ~ 2021-12-31；测试 2022-01-01 ~ 2023-12-31（730 天）
对每城输出：
  1) 结构诊断：ACF(1)、ACF(365)、季节振幅(气候态 7月-1月)、年均温趋势斜率
  2) 长期：谐波回归 K=3 vs 纯气候态 vs 趋势修正气候态（730 天 MAE/RMSE）
  3) 短期：气候态+异常AR(1) 滚动1步 vs 纯气候态（MAE/RMSE）
目的：验证"ACF诊断→双尺度建模"思路在不同季节强度城市都可迁移。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd
from pathlib import Path

DATA = Path(r"F:\Users\肖炳旭\Desktop\tm\项目相关\weather\forecast\data\multi_city")


def load(city_key):
    f = DATA / f"{city_key}_2004_2023.csv"
    df = pd.read_csv(f, parse_dates=["record_date"])
    return df.sort_values("record_date").reset_index(drop=True)


def design(dates, K=3):
    d = pd.DatetimeIndex(dates)
    t = (d - pd.Timestamp("2004-01-01")).days.values / 365.25
    doy = d.dayofyear.values
    cols = [np.ones_like(t), t]
    for k in range(1, K + 1):
        cols += [np.sin(2 * np.pi * k * doy / 365.25), np.cos(2 * np.pi * k * doy / 365.25)]
    return np.column_stack(cols)


def analyze(city_key, city_name):
    df = load(city_key)
    y = df["avg_temp"].values
    dates = df["record_date"]
    tr = df[df["record_date"] < "2022-01-01"]
    te = df[df["record_date"] >= "2022-01-01"]
    y_tr, y_te = tr["avg_temp"].values, te["avg_temp"].values

    # ---- 结构诊断 ----
    def acf(s, lag):
        s = s - s.mean()
        return float(np.dot(s[lag:], s[:-lag]) / np.dot(s, s))

    doy = dates.dt.dayofyear.values
    md = dates.dt.strftime("%m-%d")
    clim = pd.Series(y, index=md).groupby(level=0).mean()
    monthly = pd.Series(y, index=dates.dt.month).groupby(level=0).mean()
    amp = monthly[7] - monthly[1]
    yearly = df.groupby(dates.dt.year)["avg_temp"].mean()
    trend = float(np.polyfit(yearly.index.values, yearly.values, 1)[0])
    a1 = acf(y, 1)
    a365 = acf(y, 365)
    print(f"\n===== {city_name} =====")
    print(f"[结构] 年均温={y.mean():.2f}℃ | 季节振幅(7-1月)={amp:.1f}℃ | "
          f"ACF(1)={a1:.3f} | ACF(365)={a365:.3f} | 年趋势={trend:+.4f}℃/yr")

    # ---- 长期：谐波 K=3 vs 气候态 vs 趋势气候态 ----
    X = design(tr["record_date"])
    beta, *_ = np.linalg.lstsq(X, y_tr, rcond=None)
    yh_harm = design(te["record_date"]) @ beta
    # 气候态（用训练段月-日平均）
    tr_md = tr["record_date"].dt.strftime("%m-%d")
    clim_tr = pd.Series(y_tr, index=tr_md).groupby(level=0).mean()
    yh_clim = clim_tr.reindex(te["record_date"].dt.strftime("%m-%d")).values
    # 趋势修正气候态
    yr_tr = tr.groupby(tr["record_date"].dt.year)["avg_temp"].mean()
    k, b = np.polyfit(yr_tr.index.values, yr_tr.values, 1)
    yh_trendclim = yh_clim + k * (te["record_date"].dt.year.values - yr_tr.index.values[-1])

    def mae(a, bb): return float(np.mean(np.abs(a - bb)))
    def rmse(a, bb): return float(np.sqrt(np.mean((a - bb) ** 2)))
    print("[长期730天 2022-23] 谐波K3: MAE=%.3f RMSE=%.3f | 气候态: MAE=%.3f | 趋势气候态: MAE=%.3f"
          % (mae(y_te, yh_harm), rmse(y_te, yh_harm), mae(y_te, yh_clim), mae(y_te, yh_trendclim)))

    # ---- 短期：滚动1步 AR(3) vs 气候态 ----
    anom_tr = y_tr - clim_tr.reindex(tr_md).values


    def fit_ar_ols(series, p):
        n = len(series)
        X = np.column_stack([series[p - 1 - i: n - 1 - i] for i in range(p)])
        phi, *_ = np.linalg.lstsq(X, series[p:], rcond=None)
        return phi


    P = 3
    phi = fit_ar_ols(anom_tr, P)
    te_md = te["record_date"].dt.strftime("%m-%d").values
    hist_anom = list(anom_tr)          # 真实异常历史（滚动中追加）
    yh_ar = np.zeros(len(te))
    for i in range(len(te)):
        window = hist_anom[-P:]
        pred_anom = sum(phi[j] * window[-1 - j] for j in range(P))
        yh_ar[i] = clim_tr.reindex([te_md[i]]).values[0] + pred_anom
        # 滚动1步：加入 te[i] 真实异常供下一步使用
        hist_anom.append(y_te[i] - clim_tr.reindex([te_md[i]]).values[0])
    yh_clim_1step = clim_tr.reindex(te_md).values
    print("[短期滚动1步] AR(%d)(φ=%s): MAE=%.3f | 气候态: MAE=%.3f | 提升 %.0f%%"
          % (P, ",".join(f"{v:.3f}" for v in phi), mae(y_te, yh_ar), mae(y_te, yh_clim_1step),
             (1 - mae(y_te, yh_ar) / mae(y_te, yh_clim_1step)) * 100))
    return {"city": city_name, "amp": amp, "acf1": a1, "acf365": a365, "trend": trend,
            "harm_mae": mae(y_te, yh_harm), "clim_mae": mae(y_te, yh_clim),
            "ar1_mae": mae(y_te, yh_ar), "phi": float(phi[0])}


if __name__ == "__main__":
    rows = []
    for key, name in [("kunming", "昆明"), ("zhengzhou", "郑州"), ("beijing", "北京"),
                      ("yinchuan", "银川"), ("lanzhou", "兰州"), ("hohhot", "呼和浩特"),
                      ("changchun", "长春")]:
        rows.append(analyze(key, name))
    print("\n===== 汇总 =====")
    import json
    df_out = pd.DataFrame(rows).round(3)
    print(df_out.to_string(index=False))
    # 存结果供文档/画图用
    (Path(__file__).resolve().parents[2] / "forecast" / "experiments" / "multicity_results.json").write_text(
        df_out.to_json(orient="records", force_ascii=False), encoding="utf-8")

