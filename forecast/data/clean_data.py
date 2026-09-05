import pandas as pd
import re
from datetime import datetime, timedelta

# 读取数据
file_path = r"原始数据位置"  # 表格
df = pd.read_excel(file_path, engine="openpyxl", header=None)


def parse_row(row):
    # 1. 转换 Excel 序列号日期 (Excel 的 45292 对应 2024-01-01)
    # Excel 时间戳是从 1899-12-30 开始计算的
    excel_date = row[0]
    date_val = (datetime(1899, 12, 30) + timedelta(days=float(excel_date))).strftime('%Y-%m-%d')

    # 2. 提取第 2 列 (索引 2) 的温度
    temp_text = str(row[2])  # 例如: "-4℃ / -13℃"
    temps = re.findall(r'(-?\d+)', temp_text)

    if len(temps) >= 2:
        max_t = float(temps[0])
        min_t = float(temps[1])
        avg_t = round((max_t + min_t) / 2, 1)
        diff = round(max_t - min_t, 1)
    else:
        avg_t, min_t, max_t, diff = 0, 0, 0, 0

    # 3. 季节判断
    month = int(date_val.split('-')[1])
    season = "冬" if month in [12, 1, 2] else ("春" if month in [3, 4, 5] else ("夏" if month in [6, 7, 8] else "秋"))

    return pd.Series(["呼和浩特市", date_val, avg_t, min_t, max_t, diff, season])


# 执行清洗
cleaned_df = df.apply(parse_row, axis=1)
cleaned_df.columns = ['城市', '日期', '平均气温', '最低气温', '最高气温', '温差', '季节']

# 保存
cleaned_df.to_csv("weather_clean_2024.csv", index=False, encoding='utf-8-sig')
print("清洗成功！前5行预览：")
print(cleaned_df.head())