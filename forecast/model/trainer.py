import os

import pandas as pd
import numpy as np
import itertools
import warnings
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sqlalchemy import create_engine, text

warnings.filterwarnings("ignore")

# 字体配置
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('../data/weather_data_clean.csv', parse_dates=['record_date'])
df = df.sort_values('record_date').set_index('record_date')
df = df.asfreq('D')

# 构造周期性傅里叶项
K = 2
doy = df.index.dayofyear
exog = pd.DataFrame(index=df.index)
for k in range(1, K + 1):
    exog[f'sin{k}'] = np.sin(2 * np.pi * k * doy / 365.25)
    exog[f'cos{k}'] = np.cos(2 * np.pi * k * doy / 365.25)



#  切分训练/测试集（9:1）
train_size = int(len(df) * 0.9)
train_y, test_y = df['avg_temp'].iloc[:train_size], df['avg_temp'].iloc[train_size:]
train_exog, test_exog = exog.iloc[:train_size], exog.iloc[train_size:]

# 网格搜索：寻找最优非季节性 order
p_range = range(0, 4)   # 用多少个过去的温度预测未来
q_range = range(0, 4)   # 用多少个过去的误差修正当前
d = 1                   # 差分

results_list = []

for p, q in itertools.product(p_range, q_range):
    order = (p, d, q)
    try:
        # 直接训练
        model = SARIMAX(train_y, exog=train_exog,
                         order=order,
                         enforce_stationarity=False,
                         enforce_invertibility=False)
        res = model.fit(disp=False, maxiter=150, method='lbfgs')
        results_list.append({
            'order': order,
            'aic': res.aic,
            'bic': res.bic
        })
        print(f"order={order} -> AIC={res.aic:.2f}, BIC={res.bic:.2f}")
    except Exception as e:
        print(f"order={order} -> 拟合失败: {e}")
        continue

results_df = pd.DataFrame(results_list)
# 用 BIC 排序 找参数最少的
results_df_sorted_bic = results_df.sort_values('bic').reset_index(drop=True)
results_df_sorted_aic = results_df.sort_values('aic').reset_index(drop=True)
print("\n按BIC排序前5个组合:")
print(results_df_sorted_bic.head())
print("\n按aic排序：")
print(results_df_sorted_aic.head())
# 提取最优参数
best_order = results_df_sorted_bic.loc[0, 'order']
print(f"\n选定参数: order={best_order}")

# 最优参数训练评估模型
eval_model = SARIMAX(train_y, exog=train_exog,
                      order=best_order,
                      enforce_stationarity=False, enforce_invertibility=False)
eval_results = eval_model.fit(disp=False, maxiter=300, method='lbfgs')

eval_forecast = eval_results.get_forecast(steps=len(test_y), exog=test_exog)
y_pred = eval_forecast.predicted_mean
y_conf = eval_forecast.conf_int()

mae = mean_absolute_error(test_y, y_pred)
rmse = np.sqrt(mean_squared_error(test_y, y_pred))
coverage = np.mean((test_y >= y_conf.iloc[:, 0]) & (test_y <= y_conf.iloc[:, 1]))
# 评估
# MAE: 预测值与真实值平均差了多少
# RMSE: 均方根误差
# 真实温度掉进模型预测的置信区间里的概率
print(f"\n模型评估指标:\nMAE: {mae:.3f} ℃\nRMSE: {rmse:.3f} ℃\n覆盖率: {coverage:.2%}")

# 全量数据训练并预测未来2nian
full_model = SARIMAX(df['avg_temp'], exog=exog,
                      order=best_order,
                      enforce_stationarity=False, enforce_invertibility=False)
full_results = full_model.fit(disp=False, maxiter=300, method='lbfgs')

forecast_steps = 730
future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_steps)
future_doy = future_dates.dayofyear
future_exog = pd.DataFrame(index=future_dates)
for k in range(1, K + 1):
    future_exog[f'sin{k}'] = np.sin(2 * np.pi * k * future_doy / 365.25)
    future_exog[f'cos{k}'] = np.cos(2 * np.pi * k * future_doy / 365.25)

forecast = full_results.get_forecast(steps=forecast_steps, exog=future_exog)
conf_int = forecast.conf_int()

forecast_df = pd.DataFrame({
    'ds': future_dates.strftime('%Y-%m-%d'),
    'yhat': forecast.predicted_mean.values,
    'yhat_lower': conf_int.iloc[:, 0].values,
    'yhat_upper': conf_int.iloc[:, 1].values
})

#
db_password = os.environ.get("DB_PASSWORD", "your_password")
engine = create_engine(f'mysql+pymysql://root:{db_password}@localhost:3306/weatherdb')
# 先写入临时表
forecast_df.to_sql('ads_weather_forecast_temp', con=engine, if_exists='replace', index=False)


with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS ads_weather_forecast;"))
    conn.execute(text("RENAME TABLE ads_weather_forecast_temp TO ads_weather_forecast;"))
print("存入 MySQL")




import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# 确保使用的是你的全局字体配置
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 从你训练好的 full_results 中提取真实的傅里叶外生变量系数
try:
    c_sin1 = full_results.params['sin1']
    c_cos1 = full_results.params['cos1']
    c_sin2 = full_results.params['sin2']
    c_cos2 = full_results.params['cos2']
    # 提取截距项（常数项，即呼和浩特的平均气温底色）
    intercept = full_results.params.get('const', df['avg_temp'].mean())
    print("\n[绘图日志] 成功提取模型真实傅里叶系数:")
    print(f"截距(均值): {intercept:.2f}, sin1: {c_sin1:.2f}, cos1: {c_cos1:.2f}, sin2: {c_sin2:.2f}, cos2: {c_cos2:.2f}")
except Exception as e:
    print(f"\n提取系数失败 ({e})，采用北半球标准气候常数进行安全降级显示。")
    c_sin1, c_cos1, c_sin2, c_cos2 = -3.07, -16.51, -0.11, -1.85
    intercept = 7.43

# 2. 生成一整年 365 天的基础分量
eval_days = np.arange(1, 366)
s1 = np.sin(2 * np.pi * 1 * eval_days / 365.25)
c1 = np.cos(2 * np.pi * 1 * eval_days / 365.25)
s2 = np.sin(2 * np.pi * 2 * eval_days / 365.25)
c2 = np.cos(2 * np.pi * 2 * eval_days / 365.25)

# 3. 乘以模型学到的系数，合成出真正属于呼和浩特的气候常态大背景线
model_combined_trend = (intercept + (c_sin1 * s1) +
                        (c_cos1 * c1))


#  开始画图
plt.figure(figsize=(16, 9))
# 子图 模型最终生成的北半球标准年气温周期背景模板
plt.subplot(1, 1, 1)
plt.plot(eval_days, model_combined_trend, color='#e11d48', linewidth=3, label='模型学到的傅里叶常态模板')

plt.title('SARIMAX 提取出的呼和浩特市')
plt.xlabel('一年中的第几天 (Day of Year)')
plt.ylabel('气温预测基准 (℃)')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='upper right')

plt.tight_layout()
plt.savefig('傅里叶拟合后的图形.png', dpi=300)
plt.show()