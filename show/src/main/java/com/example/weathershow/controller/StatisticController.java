package com.example.weathershow.controller;


import com.example.weathershow.pojo.*;
import com.example.weathershow.service.StatisticService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;
/**
 * @author X
 * @date 2026/6/9 18:06
 */

@RestController
public class StatisticController {

    @Autowired
    private StatisticService statisticService;
    /*
     * 获取主页四个kpi数据
     * 年均气温（20年均值）
     * 极端高温阈值
     * 极端低温阈值
     * 气温日较差均值
     * */
    @GetMapping("/kpi")
    public Result getKpiData() {
        WeatherKpiMetrics weatherKpiMetrics = statisticService.getKpiData();
        return Result.success(weatherKpiMetrics);
    }

    /*
    * 气温趋势图
    * */
    @GetMapping("/trendYear")
    public Result getTrendData() {
        TrendVo trendVo = statisticService.getTrendYearData();
        return Result.success(trendVo);
    }

    @GetMapping("/trendMonth")
    public Result getTrendMonthData() {
        TrendVo trendVo = statisticService.getTrendMonthData();
        return Result.success(trendVo);
    }

    // 极端天气 各年份各类型的极端天气总数
    @GetMapping("/extreme")
    public Result getExtremeData() {
        ExtremeVo extremeVo = statisticService.getExtremeData();
        return Result.success(extremeVo);
    }

    //极端天气季节性分布图
    @GetMapping("/extremeSeason")
    public Result getExtremeSeasonData() {
        List<SeasonExtremeVo> extremeSeasonData = statisticService.getExtremeBySeason();
        return Result.success(extremeSeasonData);

    }

    // 极端天气月份热力图
    @GetMapping("/extremeMonth")
    public Result getExtremeMonthData() {
        List<WeatherExtreme> extremeMonthData = statisticService.getExtremeByMonth();
        return Result.success(extremeMonthData);
    }

    // 年度偏差强度趋势
    @GetMapping("/extremeIntensity")
    public Result getExtremeIntensity() {
        return Result.success(statisticService.getYearlyIntensity());
    }
    // 月度偏差  按月聚合统计
    // 月度偏差强度趋势
    @GetMapping("/monthlyIntensity")
    public Result getMonthlyIntensity() {
        return Result.success(statisticService.getMonthlyIntensity());
    }
    // 日偏差 按日聚合统计

    // 高温/低温天数年度对比趋势 重复
    @GetMapping("/extremeTrend")
    public Result getExtremeTrend() {
        return Result.success(statisticService.getYearlyTrend());
    }

    //日较差分布 最低温和最高温的差
    @GetMapping("/dayDistribution")
    public Result getDayDistribution() {
        return Result.success(statisticService.getDayDistribution());
    }

    // 日较差与平均气温相关性 做散点图
    @GetMapping("/dayDistributionByMonth")
    public Result getDayDistributionByMonth() {
        return Result.success(statisticService.getDayDistributionByMonth());
    }

    // 月度日较差统计折线图
    @GetMapping("/monthDistribution")
    public Result getMonthDistribution() {
        return Result.success(statisticService.getDiurnalMonthly());
    }

    // 季节日较差箱线图
    @GetMapping("/diurnalSeason")
    public Result getDiurnalSeason() {
        return Result.success(statisticService.getDiurnalSeason());
    }

    // 预测表
    @GetMapping("/forecast")
    public Result getForecast() {
        return Result.success(statisticService.getForecast());
    }

    // 2024年的实际数据
    @GetMapping("/actualData")
    public Result getActualData() {
        return Result.success(statisticService.getActualData());
    }

}