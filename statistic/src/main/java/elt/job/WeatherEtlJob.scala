package elt.job
import elt.processor.{AdsProcessor, WeatherProcessor}
import elt.utils.mysql.{ReadMysql, WriteMysql}
import org.apache.hadoop.hdfs.client.HdfsClientConfigKeys.Write
import org.apache.spark.sql.{SaveMode, SparkSession}
/**
 * @author Xbx
 * @date 2026/6/9 15:28
 */
object WeatherEtlJob {

  def main(args: Array[String]): Unit = {
    // 1. 初始化 Spark 环境
    val spark = SparkSession.builder()
      .appName("WeatherEtlJob")
      .master("local[*]") // 本地调试模式
      .getOrCreate()

    // 引入隐式转换
    import spark.implicits._

    // 实例化读取工具与处理器
    val mysqlReader = new ReadMysql()
    val mysqlWriter = new WriteMysql()
    val processor = new WeatherProcessor(spark)

    // 执行 ETL 流程
    // 读取数据
    val odsDf = mysqlReader.readMysql(spark, "weather_data")

    // 清洗数据
    val dwdDf = processor.cleanAndTransform(odsDf)



    // 数据挖掘
    // 逻辑计算
    val adsProcessor = new AdsProcessor()
    val trendYearDf = adsProcessor.calcTrendYear(dwdDf)
    val trendMonthDf = adsProcessor.calcTrendMonth(dwdDf)
    val extremeDf = adsProcessor.calcExtremeAdvanced(dwdDf)
    val distDf = adsProcessor.calcDistribution(dwdDf)
    val kpiDf = adsProcessor.calcKpiMetrics(dwdDf)
    val diurnalMonthlyDf = adsProcessor.calcDiurnalMonthly(dwdDf)
    // 统一存储
    val tablesToTruncate = Array(
      "weather_dwd",
      "ads_weather_trend_year",
      "ads_weather_trend_month",
      "ads_weather_extreme",
      "ads_weather_range_distribution",
      "ads_weather_kpi_metrics",
      "ads_diurnal_monthly"
    )

    // 循环清空各表
    tablesToTruncate.foreach(table => mysqlWriter.truncateTable(table))

    // 写入 DWD 层
    // 写入 DWD 层
    mysqlWriter.write(dwdDf, "weather_dwd", SaveMode.Append)

    // 写入 ADS 层 (直接写表名，不要用数组索引)
    mysqlWriter.write(trendYearDf, "ads_weather_trend_year", SaveMode.Append)
    mysqlWriter.write(trendMonthDf, "ads_weather_trend_month", SaveMode.Append)
    mysqlWriter.write(extremeDf, "ads_weather_extreme", SaveMode.Append)
    mysqlWriter.write(distDf, "ads_weather_range_distribution", SaveMode.Append)
    mysqlWriter.write(kpiDf, "ads_weather_kpi_metrics", SaveMode.Append)
    mysqlWriter.write(diurnalMonthlyDf, "ads_diurnal_monthly", SaveMode.Append)
    // 4. 关闭资源
    spark.stop()
  }

}
