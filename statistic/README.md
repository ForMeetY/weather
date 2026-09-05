# statistic —— 数仓分层 ETL 模块（Spark / Scala）

> 本模块是整个系统的**数据治理与多维统计层**：把 MySQL 中的原始气温明细（ODS）经 Spark 清洗、
> 特征衍生后落为明细事实表（DWD），再按"趋势 / 极端 / 分布"等业务主题聚合成统计结果表（ADS），
> 供上层可视化（show 模块）与建模（forecast 模块）直接读取。
>
> **注意**：时序预测（谐波回归等）见 [`../forecast/README.md`](../forecast/README.md)。

## 一、模块定位与数据流

```
 原始数据(Excel/CSV/API)──入库──▶ MySQL: weather_data        (ODS 原始明细)
                                        │
                              Spark ETL  (本模块)
                                        ▼
                             MySQL: weather_dwd               (DWD 清洗+特征)
                                        │
                              Spark 多维聚合
                                        ▼
   ads_weather_trend_year / ads_weather_trend_month           (ADS 趋势)
   ads_weather_extreme                                        (ADS 极端)
   ads_weather_range_distribution                             (ADS 日较差分布)
   ads_weather_kpi_metrics                                    (ADS 首页 KPI)
   ads_diurnal_monthly                                        (ADS 月度日较差)
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
             show 模块（Spring Boot + Vue 大屏）      forecast 模块（谐波回归预测）
```

## 二、技术栈与环境

| 项 | 值 |
|---|---|
| 语言 | Scala 2.12.18 |
| 计算引擎 | Apache Spark 3.5.1（本地 `local[*]` 调试模式） |
| Hadoop | 3.3.6 |
| 存储 | MySQL（JDBC 直读直写，无需中间文件） |
| 构建 | Maven（`org.xbx:weatherStatistic:1.0-SNAPSHOT`） |

## 三、目录结构

```
statistic/
├── pom.xml
└── src/main/
    ├── java/elt/
    │   ├── job/WeatherEtlJob.scala        # 主任务：编排 ODS→DWD→ADS 全流程
    │   ├── processor/
    │   │   ├── WeatherProcessor.scala      # 清洗与特征工程（ODS→DWD）
    │   │   └── AdsProcessor.scala          # 多维统计（DWD→ADS 各主题表）
    │   └── utils/mysql/
    │       ├── ReadMysql.scala             # JDBC 读取工具
    │       └── WriteMysql.scala            # JDBC 写入 / TRUNCATE 工具
    └── resources/db.properties             # 数据库连接配置（密码走环境变量）
```

## 四、三层数仓设计

### 1. ODS 层 —— 原始数据明细表 `weather_data`

按原始记录逐条落库，保留日期字符串、城市、温度等原始字段，不做业务加工。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | VARCHAR(64) | 原始记录 ID（主键） |
| city_name | VARCHAR(50) | 城市（本项目为"呼和浩特市"） |
| avg_temp / min_temp / max_temp | DOUBLE | 当日平均 / 最低 / 最高气温 |
| province | VARCHAR(50) | 所属省份 |
| date_key | VARCHAR(10) | 原始日期字符串（yyyyMMdd） |
| area_code | VARCHAR(20) | 行政区划代码 |

索引：`idx_date(date_key)`、`idx_city(city_name)` 加速统计查询。

### 2. DWD 层 —— 清洗后明细事实表 `weather_dwd`

对 ODS 做**类型转换 → 规则过滤 → 全局 IQR 离群剔除 → 特征衍生**后得到逐日事实表，
是本模块后续所有统计与 forecast 建模的数据基础。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | VARCHAR(64) | 原始记录 ID（主键） |
| city_name | VARCHAR(50) | 城市 |
| record_date | DATE | 标准清洗日期 |
| avg_temp / min_temp / max_temp | DOUBLE | 清洗后气温 |
| daily_range | DOUBLE | 气温日较差 = max − min（衍生） |
| season | VARCHAR(10) | 季节标签（衍生：3-5 春 / 6-8 夏 / 9-11 秋 / 12-2 冬） |

**清洗规则**（`WeatherProcessor.scala`）：
1. 类型转换：`date_key` → `record_date`（DATE），温度列转 DOUBLE；
2. 业务规则：温度非空 且 `max_temp >= min_temp`；
3. 物理合理区间：`min_temp >= -50` 且 `max_temp <= 60`；
4. **IQR 离群剔除**：对 min/max/avg 三列分别求全局 Q1/Q3 与 IQR，剔除超出
   `[Q1 − 1.5·IQR, Q3 + 1.5·IQR]` 的记录（`percentile_approx` 近似分位，精度 100）。

### 3. ADS 层 —— 应用统计表（面向可视化）

| 表名 | 主题 | 主要字段与口径 |
|---|---|---|
| `ads_weather_trend_year` | 年趋势 | year；avg_temp=年均温(avg)；min/max_temp=全年最低/最高极值(min/max)；avg_daily_range=年平均日较差 |
| `ads_weather_trend_month` | 月趋势 | month_dimension(yyyy-MM)；avg/min/max_temp、avg_daily_range 同上年/月口径 |
| `ads_weather_extreme` | 极端天气 | year, month, season, extreme_type(EXTREME_HIGH/LOW), occurrence_count, avg_intensity, threshold_value |
| `ads_weather_range_distribution` | 日较差分布 | range_bucket(0-5/5-10/10-15/>15℃), year, cnt（每年落入各区间的天数） |
| `ads_weather_kpi_metrics` | 首页 KPI | avg_all(多年平均气温), high_threshold(高温阈值 P95), low_threshold(低温阈值 P5), avg_range_all(平均日较差) |
| `ads_diurnal_monthly` | 月度日较差 | month_dimension, avg/max/min_daily_range, std_daily_range |

> ⚠️ 消费说明：show 侧趋势 / 极端 / 分布 / KPI 接口分别读上述 ADS 表；
> 但"月度日较差 / 季节箱线 / 日较差-气温相关性"等接口（`WeatherDwdMapper`）
> 当前**直接基于 `weather_dwd` 用 SQL 现场聚合**，未读取 `ads_diurnal_monthly`。
> 该 ADS 表保留作"预聚合 + 明细灵活查询"两种口径并存的设计，文档与代码以此为准。

## 五、ADS 统计口径与业务含义

### 1. 趋势分析
- **年 / 月趋势**：按年（月）对 DWD 分组，`avg(avg_temp)`、`min(min_temp)`、`max(max_temp)`、`avg(daily_range)`。
- **距平（Anomaly）**：可视化侧用"某年平均值 − 气候基线（全局均值）"度量冷暖偏离 —— 为正表示比历史平均热，为负表示偏冷（前端计算，见 show 模块）。

### 2. 极端天气（`calcExtremeAdvanced`）
1. **阈值**：`percentile_approx(max_temp, 0.95)` 定高温阈值，`percentile_approx(min_temp, 0.05)` 定低温阈值（全局分位，精度 10000）；
2. **判定与打标**：`max_temp >= P95` → `EXTREME_HIGH`；`min_temp <= P5` → `EXTREME_LOW`；
3. **偏差（强度）**：高温偏差 = `当日最高温 − 高温阈值`；低温偏差 = `低温阈值 − 当日最低温`（保证均为正数，统一表示"偏离程度"）；
4. **聚合**：按 year / month / season / extreme_type 统计 `occurrence_count`、`avg_intensity`，并记录 `threshold_value`。

### 3. 日较差分布（`calcDistribution`）
- 物理意义：日较差（DTR）= 一日最高与最低气温之差，是衡量气候稳定性与天气剧烈程度的核心指标：
  - DTR 小（0-5℃）→ 云量多 / 阴雨连绵；DTR 大（>15℃）→ 晴朗少云、干燥（沙漠 / 高原型气候）；
  - 某年 `>15℃` 天数显著增加，往往与"极端化 / 干旱化"趋势相关。
- 分桶映射：`<5→0-5℃`，`<10→5-10℃`，`<15→10-15℃`，`≥15→>15℃`；
- 聚合：以 `range_bucket × year` 为维度 `count(*)`。
- 分析结论：呼和浩特日较差常年稳定在 **12-15℃**，不随冷暖季节剧烈收缩，体现大陆性气候的稳定性。

### 4. 月度日较差（`calcDiurnalMonthly`）
按 `yyyy-MM` 计算 avg / max / min / std 四类日较差统计，用于观察日较差的季节规律与波动幅度。

### 5. 首页 KPI（`calcKpiMetrics`）
一次汇总四项概览指标：多年平均气温、高温阈值(P95)、低温阈值(P5)、平均日较差。

## 六、运行方式

```bash
# 1. 数据库配置：statistic/src/main/resources/db.properties
#    db.url / db.user 直接填写；密码从环境变量读取，避免硬编码：
#    db.password=${DB_PASSWORD}
#    Windows:  set DB_PASSWORD=你的密码
#    Linux:    export DB_PASSWORD=你的密码

# 2. 运行主任务（本地 Spark，local[*]）
#    在 IDE 中直接运行 elt.job.WeatherEtlJob.main，或：
mvn package
#    然后以包含依赖的 classpath 运行 WeatherEtlJob（本地调试时通常用 IDE 更省事）
```

执行后自动：
1. `TRUNCATE` 并重建 DWD 与各 ADS 表（先清空再全量写入，保证幂等）；
2. 从 `weather_data` 读取 ODS → 清洗 → 写 `weather_dwd`；
3. 从 `weather_dwd` 计算 6 张 ADS 表并写回 MySQL。

> 注：`pom.xml` 未配置 scala-maven / shade 打包插件，本地调试以 IDE 运行主类为主；
> 若需 `spark-submit` 提交，需自行补充打包插件与运行参数。

## 七、已知口径注意点（面试可主动说明）

- **IQR 剔除 vs 极端统计的边界**：DWD 层做了全局 1.5×IQR 离群剔除，而极端天气统计同样建立在 DWD 之上，
  因此**最极端的真实寒潮/热浪日理论上可能被清洗规则过滤**，极端频次存在轻微低估风险。
  更严格的做法是"清洗只做业务规则，极端统计在原始 ODS 上做"——作为后续优化方向保留。
- **阈值口径**：极端阈值采用全局 P95/P5，未区分季节；如需更细粒度可用季节分位数或极值理论（GEV）。
- 20 年单城市样本属"中长序列小样本"，结论用于趋势观察，统计显著性见 forecast 模块实验（Mann-Kendall 思路）。

## 八、与其他模块的衔接

| 下游 | 读取内容 | 用途 |
|---|---|---|
| `show/` | ADS 趋势/极端/分布/KPI 表、`weather_dwd`、`weather_data` | 大屏可视化接口（见 show 模块） |
| `forecast/` | `weather_dwd` 导出 CSV | 谐波回归长期预测 / 气候态+异常AR(1) 短期预测 |
