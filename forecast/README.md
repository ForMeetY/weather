# forecast —— 气温时序预测模块

> 术语口径 v2：本模块主方案为**谐波回归（Harmonic Regression）**与**气候态 + 异常 AR(1)**，
> 早期基于 statsmodels `SARIMAX` 类的实现（实为 ARIMAX + 傅里叶外生项）保留在 `trainer.py` 仅供复现对比。

## 方案总览

| 尺度 | 方案 | 依据（EDA） | 测试段指标（2022-2023） |
|---|---|---|---|
| 长期（≥180 天 / "未来两年"大屏） | **谐波回归 K=3**：`avg = a + b·(t/365.25) + Σ_k(α_k sin + β_k cos)(2πk·doy/365.25)` | ACF(365)=0.87 强年周期且形状稳定 | MAE **3.168** / RMSE 4.019 |
| 短期（1~30 天） | **气候态 + 异常 AR(1)** | ACF(1)=0.973 日-日强持续 | 滚动 1 步 MAE **2.23**（提升 32%） |
| （对照）早期方案 | ARIMAX(2,1,3)+傅里叶（statsmodels） | 原网格搜索 BIC 最优 | MAE 3.182 / 覆盖率 92.6% |

## 目录

```
forecast/
├── data/
│   ├── clean_data.py        # 原始 Excel → 清洗 CSV（按年）
│   ├── get_data.py          # MySQL weather_dwd → weather_data_clean.csv
│   └── weather_data_clean.csv  # 建模用主数据（2004-2023，由 get_data.py 导出）
├── model/
│   ├── trainer_harmonic.py  # ★ 主训练脚本：谐波回归 + 气候态/异常AR(1)，预测未来730天
│   ├── trainer.py           # 早期 ARIMAX+Fourier 实现（复现/对比用）
│   └── img/                 # 评估图与预测图
└── experiments/             # EDA 与对比实验脚本、图、报告（对比实验报告.md）
```

## 运行

```bash
# 1) 准备数据（需 MySQL weather_dwd 已由 statistic 模块产出）
#    python data/get_data.py        # 导出 weather_data_clean.csv

# 2) 训练 + 评估 + 预测（默认只存 CSV 与图）
python model/trainer_harmonic.py

# 3) 如需把预测写回 MySQL（show 模块大屏读取 ads_weather_forecast）
#    Windows:  set DB_PASSWORD=xxx && python model/trainer_harmonic.py
#    Linux:    DB_PASSWORD=xxx python model/trainer_harmonic.py
```

输出：
- `model/img/harmonic_eval_2022_2023.png`：留出测试段拟合对比
- `model/img/harmonic_forecast_730d.png`：未来 730 天预测 + 95% 区间（按月残差 σ）
- `model/forecast_future_730d.csv`：`ds, yhat, yhat_lower, yhat_upper`

## 复现对比实验

```bash
python experiments/compare_light.py     # 轻量候选（气候态/谐波/异常AR1/去年同日）
python experiments/compare_arimax.py    # ARIMAX+Fourier 复现（需要 statsmodels）
python experiments/compare_finalize.py  # 汇总出图 + 生成 对比实验报告.md
```
