package elt.utils.mysql

import java.util.Properties
import java.io.InputStream
import java.sql.DriverManager

import org.apache.spark.sql.{DataFrame, SaveMode}

/**
 * @author Xbx
 * @date 2026/6/9 15:30
 */
class WriteMysql {
  private val config = new Properties()

  // 1. 在构造函数中确保配置文件被加载
  private val input: InputStream = getClass.getClassLoader.getResourceAsStream("db.properties")
  if (input != null) {
    config.load(input)
    input.close()
  } else {
    throw new RuntimeException("找不到 db.properties 配置文件！")
  }

  // 2. 加载完配置后再获取属性
  private val jdbcurl = config.getProperty("db.url")
  private val jdbcuser = config.getProperty("db.user")
  private val jdbcpw = sys.env.getOrElse("DB_PASSWORD", config.getProperty("db.password"))

  def write(data: DataFrame, tableName: String, mode: SaveMode): Unit = {
    data.write
      .format("jdbc")
      .option("url", jdbcurl)
      .option("user", jdbcuser)
      .option("password", jdbcpw)
      .option("dbtable", tableName)
      .option("driver", "com.mysql.cj.jdbc.Driver")
      .mode(mode)
      .save()
    println(s"表 $tableName 写入成功！")
  }

  def truncateTable(tableName: String): Unit = {
    val conn = DriverManager.getConnection(jdbcurl, config.getProperty("db.user"), jdbcpw)
    try {
      val stmt = conn.createStatement()
      stmt.execute(s"TRUNCATE TABLE $tableName")
    } finally {
      conn.close()
    }
  }
}