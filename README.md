# 呼和浩特市气温大数据分析与预测系统

基于大数据 + 时序预测的气温分析项目，覆盖「数据采集清洗 → 数仓分层 ETL → 时序建模预测 → 可视化大屏」全链路。仓库按模块分为三个平级子目录：

## 目录结构

```
weather/
├── forecast/     # 时序预测（Python · SARIMAX + 傅里叶外生变量）
├── statistic/    # 数仓分层 ETL（Scala · Spark，ODS→DWD→ADS）
└── show/         # 可视化后端与大屏（Spring Boot + Vue3）
```

## 各模块说明

| 模块 | 技术栈 | 职责 |
|---|---|---|
| `forecast/` | Python · pandas · statsmodels SARIMAX | 傅里叶级数项作为外生变量建模季节性，AIC/BIC 网格搜索选参，预测未来气温 |
| `statistic/` | Scala · Spark SQL | 数据清洗（IQR 剔除离群点）、三层数仓（ODS/DWD/ADS）ETL 与多维统计 |
| `show/` | Spring Boot · MyBatis · Vue3 · ECharts | 趋势/极端天气/日较差统计接口与可视化大屏 |

## 环境变量

代码中的数据库密码与大模型 API Key 均从环境变量读取，不再硬编码：

| 变量 | 用途 |
|---|---|
| `DB_PASSWORD` | MySQL 密码（forecast / statistic / show 三处通用） |
| `DEEPSEEK_API_KEY` | DeepSeek 大模型 API Key（仅 show 使用） |

本地运行时，先设置环境变量或填入对应配置文件（`db.properties`、`application.yml`）后启动。

## 数据说明

原始天气数据（CSV）未纳入版本控制。数据来源与清洗逻辑见 `forecast/data/clean_data.py`。
