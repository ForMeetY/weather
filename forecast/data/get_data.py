import os

import pandas as pd
from sqlalchemy import create_engine

# 1. 数据库配置
# 格式: mysql+pymysql://用户名:密码@主机IP:端口/数据库名
# 密码从环境变量 DB_PASSWORD 读取，避免硬编码泄露
db_password = os.environ.get("DB_PASSWORD", "your_password")
db_connection_str = f'mysql+pymysql://root:{db_password}@localhost:3306/weatherdb'
db_connection = create_engine(db_connection_str)

# 2. 编写强制格式化的 SQL
# 使用 DATE_FORMAT 强制日期为文本，确保导出时不乱码
query = """
SELECT 
    DATE_FORMAT(record_date, '%%Y-%%m-%%d') as record_date,
    city_name,
    avg_temp,
    min_temp,
    max_temp,
    daily_range,
    season
FROM weather_dwd
"""
# 3. 读取数据到 DataFrame
df = pd.read_sql(query, db_connection)

# 4. 导出到 CSV
# index=False 表示不要导出序号列
# encoding='utf-8-sig' 确保在 Windows 下用 Excel 打开中文不乱码
df.to_csv('weather_data_clean.csv', index=False, encoding='utf-8-sig')

print("数据导出成功，已保存为 weather_data_clean.csv")