package elt.utils.mysql

import java.io.InputStream
import java.util.Properties

import org.apache.spark.sql.{DataFrame, SparkSession}

/**
 * @author Xbx
 * @date 2026/6/9 15:14
 */
class ReadMysql {
  private val config = new Properties()
  private val input: InputStream = getClass.getClassLoader.getResourceAsStream("db.properties")
  if (input != null) {
    config.load(input)
    input.close()
  } else {
    throw new RuntimeException("未能找到 db.properties 文件！")
  }
  // 从db.properties中获取mysql连接信息
  private val jdbcurl = config.getProperty("db.url")
  private val jdbcuser = config.getProperty("db.user")
  private val jdbcpw = sys.env.getOrElse("DB_PASSWORD", config.getProperty("db.password"))

  // 按表名读取mysql
  def readMysql(spark:SparkSession, tableName: String): DataFrame = {
    val df = spark.read.format("jdbc")
      .option("url", jdbcurl)
      .option("dbtable", tableName)
      .option("user", jdbcuser)
      .option("password", jdbcpw)
      .load()
    return  df
  }


}
