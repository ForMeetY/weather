import pandas as pd
file_path = r"F:\Users\肖炳旭\Desktop\动手学机器学习\期末复习\天气预报_202401-202412.xlsx"
df = pd.read_excel(file_path, engine="openpyxl", header=None)
print(df.head(5)) # 把打印出来的结果复制给我看看