# forecast —— 气温时序分析模块

> 本模块按标准时序分析流程（Box-Jenkins）完成日气温的**结构诊断 → 双尺度建模 → 检验 → 预测**，
> 并在多城市复现验证路线可行性（详见 `experiments/` 与《天气分析.md》第四章）。
> 主方案：长期用**谐波回归**（季节显式建模），短期用**气候态 + 异常 AR(3)**（阶数经跨城市定阶实验选定）；
> GBDT 作为数据驱动 ML 对照保留。

## 方案

| 尺度 | 方案 | 依据（EDA） | 测试段指标（2022-2023） |
|---|---|---|---|
| 长期（≥180 天 / "未来两年"） | **谐波回归 K=3**（OLS，季节+趋势） | ACF(365)=0.87 稳定年周期 | MAE **3.168** / RMSE 4.019 |
| 短期（1~30 天） | **气候态 + 异常 AR(3)** | ACF(1)=0.973 日-日强持续；AR 定阶实验（7 城）选 AR(3) | 滚动 1 步 MAE **2.194**（较气候态降 33%） |
| ML 对照 | GBDT（sklearn，数据驱动） | 检验简单结构模型与 ML 的差距 | 滚动 1 步 MAE 2.191（与 AR(3) 差异 <0.01℃） |

> **AR 定阶说明**：异常序列 PACF 一阶主导但高阶仍有小幅信号；跨城市 AR(p)(p=1..10) 定阶实验表明
> AR(1)→AR(2) 为主增益(−2.4%)、AR(3) 后进入平台，严格 argmin 在噪声中漂移 → 统一取 **AR(3)**
> （比 AR(1) 好约 2.5%，参数仅 3 个）。见 `experiments/ar_order_final.py`。

## 目录

```
forecast/
├── data/
│   ├── clean_data.py              # 原始 Excel → 清洗 CSV（按年）
│   ├── get_data.py                # MySQL weather_dwd → weather_data_clean.csv
│   ├── weather_data_clean.csv     # 主数据（呼和浩特 2004-2023）
│   └── multi_city/                # 多城市 ERA5 数据（昆明/郑州/兰州/北京/银川/呼和浩特/长春）
├── model/
│   ├── trainer_harmonic.py        # 长期：谐波回归 K=3，预测未来730天
│   ├── trainer_short.py           # 短期：气候态+异常AR(3)，30天滚动回测
│   ├── trainer_gbdt.py            # ML 对照：GBDT
│   ├── short_forecast.json        # 短期回测结果（前端用）
│   ├── gbdt_backtest.json         # GBDT 回测结果
│   └── img/                       # 评估图
└── experiments/                   # EDA / 诊断 / 定阶 / 多城市复现脚本（按流程组织）
```

## 运行

```bash
# 长期预测（存 CSV/图；设 DB_PASSWORD 后写回 MySQL 供大屏）
set DB_PASSWORD=xxx && python model/trainer_harmonic.py

# 短期回测 + GBDT 对照（需要 MySQL weather_data_2024 作样本外）
set DB_PASSWORD=xxx && python model/trainer_short.py
set DB_PASSWORD=xxx && python model/trainer_gbdt.py
```

## 流程与多城市复现脚本（experiments/）

| 脚本 | 对应流程步骤 |
|---|---|
| `eda_compute.py` / `eda_plot.py` | EDA / 结构诊断（ACF、气候态、趋势） |
| `run_diagnostics.py` | 平稳性(ADF/KPSS)、白噪声(Ljung-Box)、残差诊断 |
| `eval_K_grid.py` | 谐波阶数 K 的网格验证（留出段） |
| `ar_order_final.py` | 短期 AR(p) 定阶实验（7 城，p=1..4 最终评估） |
| `fetch_cities.py` | 拉取多城市 ERA5 日气温（Open-Meteo） |
| `repro_cities_pilot.py` | 多城市复现：同协议诊断+建模+评估 |
| `multicity_plots.py` | 多城市对比图 |
