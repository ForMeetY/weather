package com.example.weathershow.service;

import com.example.weathershow.pojo.*;
import org.apache.ibatis.annotations.Delete;
import org.springframework.stereotype.Service;
import java.util.List;
/**
 * @author X
 * @date 2026/6/9 19:00
 */


public interface StatisticService {

    // 获取主页四个kpi数据
    WeatherKpiMetrics getKpiData();

    // 获取气温趋势年变化图数据
    TrendVo getTrendYearData();

    // 获取气温趋势月变化图数据
    TrendVo getTrendMonthData();

    ExtremeVo getExtremeData();

    List<SeasonExtremeVo> getExtremeBySeason();

    // 极端天气月份热力图
    List<WeatherExtreme> getExtremeByMonth();

    // StatisticService.java
    YearlyIntensityVo getYearlyIntensity();

    ExtremeVo getYearlyTrend();          // 高温/低温天数年度趋势

    // 月度偏差
    YearlyIntensityVo getMonthlyIntensity();

    // 日较差 按年聚合
    List<DistributionRangeVo> getDayDistribution();

    // 日较差和平均气温相关性
    List<DistributionCorrelationVo> getDayDistributionByMonth();

    // 日较差 按月聚合
    List<DistributionMonthlyVo> getDiurnalMonthly();

    // 日较差 季节
    List<DistributionSeason> getDiurnalSeason();

    // 预测表
    List<WeatherForecast> getForecast();

    List<WeatherData> getActualData();
}
