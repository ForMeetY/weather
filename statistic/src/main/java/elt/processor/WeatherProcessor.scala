package elt.processor

import org.apache.spark.sql.functions._
import org.apache.spark.sql.{DataFrame, SparkSession}

/**
 * @author Xbx
 * @date 2026/6/9 15:25
 */
class WeatherProcessor(spark: SparkSession) {

  /**
   * 数据清洗与特征衍生（仅呼和浩特单城市）
   * 1. 类型转换：date_key(yyyyMMdd) -> 日期类型
   * 2. 异常清洗：
   *    - 非空、max_temp >= min_temp
   *    - 物理合理温度范围 [-50, 60]
   *    - 全局箱线图(IQR)剔除温度离群点
   * 3. 衍生特征：日较差 daily_range、季节 season
   */
  def cleanAndTransform(odsDf: DataFrame): DataFrame = {
    import spark.implicits._

    // 类型转换 + 基础业务规则过滤
    val rawWithDate = odsDf.select(
      col("id"),
      col("city_name"),
      // 转换 日期格式
      to_date(col("date_key"), "yyyyMMdd").as("record_date"),
      col("avg_temp").cast("double"),
      col("min_temp").cast("double"),
      col("max_temp").cast("double")
    )
      // 非空过滤 + 业务规则过滤
      .filter(
        col("max_temp").isNotNull
          && col("min_temp").isNotNull
          && col("avg_temp").isNotNull
          && col("max_temp") >= col("min_temp")
      )
      //
      .filter(
        col("min_temp") >= -50 && col("max_temp") <= 60
      )

    // 2. 计算呼和浩特全局四分位数 & IQR & 上下界
    val globalStats = rawWithDate.agg(
      percentile_approx(col("min_temp"), lit(0.25), lit(100)).as("min_q1"),
      percentile_approx(col("min_temp"), lit(0.75), lit(100)).as("min_q3"),
      percentile_approx(col("max_temp"), lit(0.25), lit(100)).as("max_q1"),
      percentile_approx(col("max_temp"), lit(0.75), lit(100)).as("max_q3"),
      percentile_approx(col("avg_temp"), lit(0.25), lit(100)).as("avg_q1"),
      percentile_approx(col("avg_temp"), lit(0.75), lit(100)) .as("avg_q3")
    )
      .withColumn("min_iqr", col("min_q3") - col("min_q1"))
      .withColumn("min_lower", col("min_q1") - lit(1.5) * col("min_iqr"))
      .withColumn("min_upper", col("min_q3") + lit(1.5) * col("min_iqr"))
      .withColumn("max_iqr", col("max_q3") - col("max_q1"))
      .withColumn("max_lower", col("max_q1") - lit(1.5) * col("max_iqr"))
      .withColumn("max_upper", col("max_q3") + lit(1.5) * col("max_iqr"))
      .withColumn("avg_iqr", col("avg_q3") - col("avg_q1"))
      .withColumn("avg_lower", col("avg_q1") - lit(1.5) * col("avg_iqr"))
      .withColumn("avg_upper", col("avg_q3") + lit(1.5) * col("avg_iqr"))

    // 把统计阈值 cross join 回原数据（只有一行统计值）
    val withStats = rawWithDate.crossJoin(globalStats)
    val originalCount = rawWithDate.count()
    println(s" 清洗前总行数：${originalCount} ===")
    // 直接过滤箱线图离群点
    val filtered = withStats.filter(
      col("min_temp").between(col("min_lower"), col("min_upper")) &&
        col("max_temp").between(col("max_lower"), col("max_upper")) &&
        col("avg_temp").between(col("avg_lower"), col("avg_upper"))
    )
      // 过滤多少行
    val filteredCount = filtered.count()
    println(s" 数据清洗后行数：${filteredCount} ")

    // 特征衍生 + 剔除辅助字段
    filtered
      .withColumn("daily_range", col("max_temp") - col("min_temp"))
      .withColumn("season", when(month(col("record_date")).isin(3, 4, 5), "春")
        .when(month(col("record_date")).isin(6, 7, 8), "夏")
        .when(month(col("record_date")).isin(9, 10, 11), "秋")
        .otherwise("冬"))
      .select(
        "id", "city_name", "record_date",
        "avg_temp", "min_temp", "max_temp",
        "daily_range", "season"
      )
  }
}