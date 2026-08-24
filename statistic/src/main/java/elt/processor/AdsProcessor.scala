package elt.processor

import org.apache.spark.sql.{DataFrame}
import org.apache.spark.sql.functions._

/**
 * @author Xbx
 * @date 2026/6/9 15:55
 */
class AdsProcessor {

  // 计算趋势，只返回 DataFrame
  // 计算每年的趋势 从 weather_dwd
  def calcTrendYear(dwdDf: DataFrame): DataFrame = {
    dwdDf.createOrReplaceTempView("dwd")
    // 计算每年趋势 每年的平均气温、最低气温、最高气温、平均气温较差（最高气温与最低气温）
    dwdDf.sparkSession.sql(
      """
      select
        year(record_date) as year,
        avg(avg_temp) as avg_temp,
        min(min_temp) as min_temp,
        max(max_temp) as max_temp,
        avg(daily_range) as avg_daily_range
      from dwd
      group by YEAR(record_date)
      """
    )
  }

  /*
  * 月趋势
  * 执行SQL得到
  * 月度的平均气温、最低气温、最高气温、平均气温较差
  * */
  def calcTrendMonth(dwdDf: DataFrame): DataFrame = {
    dwdDf.createOrReplaceTempView("dwd")
    // 计算每月趋势 包括 日期 每月平均气温、最低气温、最高气温、平均气温较差
    dwdDf.sparkSession.sql(
      """
        select
        date_format(record_date, 'yyyy-MM') as month_dimension,
        avg(avg_temp) as avg_temp,
        min(min_temp) as min_temp,
        max(max_temp) as max_temp,
        avg(daily_range) as avg_daily_range
      from dwd
      group by DATE_FORMAT(record_date, 'yyyy-MM')
      order by month_dimension ASC
      """
    )
  }

  // 计算极端天气，返回 DataFrame
  /*
  * 通过阈值进行判断极端天气
  * 1. 获取全局阈值 用来区分极端天气
  * 2. 过滤极端天气
  * 3. 打标签
  * 4. 计算偏差
  * 5. 聚合
  * */
  def calcExtremeAdvanced(dwdDf: DataFrame): DataFrame = {
    // 1. 获取全局阈值 用来区分极端天气
    val thresholdDf = dwdDf.agg(
      expr("percentile_approx(max_temp, 0.95, 10000)").as("highT"),
      expr("percentile_approx(min_temp, 0.05, 10000)").as("lowT")
    ).head()

    val highT = thresholdDf.getDouble(0)
    val lowT = thresholdDf.getDouble(1)

    // 引入分段统计 用来统计极端天气
    // 过滤极端天气
    dwdDf.filter(col("max_temp") >= highT || col("min_temp") <= lowT)
      // 打标签
      .withColumn("extreme_type", when(col("max_temp") >= highT, "EXTREME_HIGH").otherwise("EXTREME_LOW"))
      // 计算偏差 某日高温极端减去高温阈值 低温极端减去低温阈值
      .withColumn("deviation",
        when(col("extreme_type") === "EXTREME_HIGH", col("max_temp") - lit(highT))
          .otherwise(lit(lowT) - col("min_temp"))
      )
      // 聚合
      .groupBy(
        //年月季节极端天气情况分组
        year(col("record_date")).as("year"),
        month(col("record_date")).as("month"), //
        col("season"),
        col("extreme_type")
      )
      // 聚合统计
      .agg(
        count("*").as("occurrence_count"),
        avg("deviation").as("avg_intensity"),
        lit(highT).as("threshold_value")
      )
  }

  // 计算日较差分布，返回 DataFrame
  /*
  * 主要是判断天气温度的范围
  *
  * */
  def calcDistribution(dwdDf: DataFrame): DataFrame = {
    // 打标签
    dwdDf.withColumn("range_bucket",
      when(col("daily_range") < 5, "0-5℃")
        .when(col("daily_range") < 10, "5-10℃")
        .when(col("daily_range") < 15, "10-15℃")
        .otherwise(">15℃")
    ).groupBy(col("range_bucket"), year(col("record_date")).as("year"))
      .agg(count("*").as("cnt"))
  }

  // 月度日较差分布
  def calcDiurnalMonthly(dwdDf: DataFrame): DataFrame = {
    dwdDf.createOrReplaceTempView("dwd")
    // 计算月度 平均日较差 、最大日较差 、最小日较差 、日较差标准差
    dwdDf.sparkSession.sql(
      """
    select
      date_format(record_date, 'yyyy-MM') as month_dimension,
      avg(daily_range)                    as avg_daily_range,
      max(daily_range)                    as max_daily_range,
      min(daily_range)                    as min_daily_range,
      stddev(daily_range)                 as std_daily_range
    from dwd
    group by date_format(record_date, 'yyyy-MM')
    order by month_dimension asc
    """
    )
  }


  /*
  * 首页展示的基本数据
  * */
  def calcKpiMetrics(dwdDf: DataFrame): DataFrame = {
    dwdDf.createOrReplaceTempView("dwd")
    dwdDf.sparkSession.sql(
      """
      select
        avg(avg_temp) as avg_all,
        percentile_approx(max_temp, 0.95, 10000) as high_threshold,
        percentile_approx(min_temp, 0.05, 10000) as low_threshold,
        avg(daily_range) as avg_range_all
      from dwd
      """
    )
  }
}