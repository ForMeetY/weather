package com.example.weathershow.service.impl;

import com.example.weathershow.mapper.*;
import com.example.weathershow.pojo.*;
import com.example.weathershow.service.StatisticService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

/**
 * @author X
 * @date 2026/6/9 19:00
 */
@Service
public class StatisticServiceImpl implements StatisticService {
    @Autowired
    private WeatherKpiMetricsMapper weatherKpiMetricsMapper;

    @Autowired
    private WeatherTrendYearMapper weatherTrendYearMapper;

    @Autowired
    private WeatherTrendMonthMapper weatherTrendMonthMapper;

    @Autowired
    private WeatherExtremeMapper weatherExtremeMapper;

    @Autowired
    private WeatherRangeDistributionMapper weatherRangeDistributionMapper;

    @Autowired
    private WeatherDwdMapper weatherDwdMapper;

    @Autowired
    private WeatherForecastMapper weatherForecastMapper;

    @Autowired
    private WeatherDataMapper weatherDataMapper;

    @Override
    public WeatherKpiMetrics getKpiData() {
        WeatherKpiMetrics weatherKpiMetrics = weatherKpiMetricsMapper.queryAll();
        return weatherKpiMetrics;
    }

    @Override
    public TrendVo getTrendYearData() {

        List<WeatherTrendYear> list = weatherTrendYearMapper.queryAll();

        return TrendVo.builder()
                .xAxis(list.stream().map(item -> (Object) item.getYear()).collect(Collectors.toList()))
                .avgSeries(list.stream().map(WeatherTrendYear::getAvgTemp).collect(Collectors.toList()))
                .maxSeries(list.stream().map(WeatherTrendYear::getMaxTemp).collect(Collectors.toList()))
                .minSeries(list.stream().map(WeatherTrendYear::getMinTemp).collect(Collectors.toList()))
                .rangeSeries(list.stream().map(WeatherTrendYear::getAvgDailyRange).collect(Collectors.toList()))
                .build();
    }

    @Override
    public TrendVo getTrendMonthData() {
        List<WeatherTrendMonth> list = weatherTrendMonthMapper.queryAll();

        return TrendVo.builder()
                .xAxis(list.stream().map(item -> (Object) item.getMonthDimension()).collect(Collectors.toList()))
                .avgSeries(list.stream().map(WeatherTrendMonth::getAvgTemp).collect(Collectors.toList()))
                .maxSeries(list.stream().map(WeatherTrendMonth::getMaxTemp).collect(Collectors.toList()))
                .minSeries(list.stream().map(WeatherTrendMonth::getMinTemp).collect(Collectors.toList()))
                .rangeSeries(list.stream().map(WeatherTrendMonth::getAvgDailyRange).collect(Collectors.toList()))
                .build();
    }

    @Override
    public ExtremeVo getExtremeData() {
        // 查询所有极端天气数据
        List<WeatherExtreme> list = weatherExtremeMapper.queryAllGroupByYearAndType();

        // 1. 获取唯一的年份列表
        List<Object> years = list.stream()
                .map(WeatherExtreme::getYear)
                .distinct()
                .sorted()
                .collect(Collectors.toList());


        // 使用 Map<Integer, Integer> 代替 var
        java.util.Map<Integer, Integer> highMap = list.stream()
                .filter(i -> "EXTREME_HIGH".equals(i.getExtremeType()))
                .collect(Collectors.toMap(WeatherExtreme::getYear, WeatherExtreme::getTotalCount));

        java.util.Map<Integer, Integer> lowMap = list.stream()
                .filter(i -> "EXTREME_LOW".equals(i.getExtremeType()))
                .collect(Collectors.toMap(WeatherExtreme::getYear, WeatherExtreme::getTotalCount));
        // 3. 构建 VO
        return ExtremeVo.builder()
                .xAxis(years)
                .highSeries(years.stream().map(y -> highMap.getOrDefault(y, 0)).collect(Collectors.toList()))
                .lowSeries(years.stream().map(y -> -lowMap.getOrDefault(y, 0)).collect(Collectors.toList())) // 负号处理
                .build();
    }

    @Override
    public List<SeasonExtremeVo> getExtremeBySeason() {
        List<SeasonExtremeVo> seasonExtremeVos = weatherExtremeMapper.getExtremeBySeason();
        return seasonExtremeVos;
    }

    // 极端天气月份热力图
    @Override
    public List<WeatherExtreme> getExtremeByMonth() {
        List<WeatherExtreme> extremeByMonth = weatherExtremeMapper.getExtremeByMonth();
        return extremeByMonth;
    }

    @Override
    public YearlyIntensityVo getYearlyIntensity() {
        List<WeatherExtreme> list = weatherExtremeMapper.getYearlyAvgIntensity();

        List<Object> years = list.stream()
                .map(WeatherExtreme::getYear)
                .distinct().sorted()
                .collect(Collectors.toList());

        java.util.Map<Integer, Double> highMap = list.stream()
                .filter(i -> "EXTREME_HIGH".equals(i.getExtremeType()))
                .collect(Collectors.toMap(WeatherExtreme::getYear, WeatherExtreme::getAvgIntensity));

        java.util.Map<Integer, Double> lowMap = list.stream()
                .filter(i -> "EXTREME_LOW".equals(i.getExtremeType()))
                .collect(Collectors.toMap(WeatherExtreme::getYear, WeatherExtreme::getAvgIntensity));

        return YearlyIntensityVo.builder()
                .xAxis(years)
                .highSeries(years.stream()
                        .map(y -> highMap.getOrDefault((Integer) y, 0.0))
                        .collect(Collectors.toList()))
                .lowSeries(years.stream()
                        .map(y -> lowMap.getOrDefault((Integer) y, 0.0))
                        .collect(Collectors.toList()))
                .build();
    }

    @Override
    public ExtremeVo getYearlyTrend() {
        List<WeatherExtreme> list = weatherExtremeMapper.getYearlyCountByType();

        List<Object> years = list.stream()
                .map(WeatherExtreme::getYear)
                .distinct().sorted()
                .collect(Collectors.toList());

        java.util.Map<Integer, Integer> highMap = list.stream()
                .filter(i -> "EXTREME_HIGH".equals(i.getExtremeType()))
                .collect(Collectors.toMap(WeatherExtreme::getYear, WeatherExtreme::getTotalCount));

        java.util.Map<Integer, Integer> lowMap = list.stream()
                .filter(i -> "EXTREME_LOW".equals(i.getExtremeType()))
                .collect(Collectors.toMap(WeatherExtreme::getYear, WeatherExtreme::getTotalCount));

        return ExtremeVo.builder()
                .xAxis(years)
                .highSeries(years.stream()
                        .map(y -> highMap.getOrDefault((Integer) y, 0))
                        .collect(Collectors.toList()))
                .lowSeries(years.stream()
                        .map(y -> lowMap.getOrDefault((Integer) y, 0))
                        .collect(Collectors.toList()))
                .build();
    }

    @Override
    public YearlyIntensityVo getMonthlyIntensity() {
        List<WeatherExtreme> list = weatherExtremeMapper.getMonthlyAvgIntensity();

        // xaxis 拼成 "2018-01" 格式，保持有序去重
        List<Object> months = list.stream()
                .map(i -> (Object) String.format("%d-%02d", i.getYear(), i.getMonth()))
                .distinct()
                .sorted()
                .collect(Collectors.toList());

        java.util.Map<String, Double> highMap = list.stream()
                .filter(i -> "EXTREME_HIGH".equals(i.getExtremeType()))
                .collect(Collectors.toMap(
                        i -> String.format("%d-%02d", i.getYear(), i.getMonth()),
                        WeatherExtreme::getAvgIntensity));

        java.util.Map<String, Double> lowMap = list.stream()
                .filter(i -> "EXTREME_LOW".equals(i.getExtremeType()))
                .collect(Collectors.toMap(
                        i -> String.format("%d-%02d", i.getYear(), i.getMonth()),
                        WeatherExtreme::getAvgIntensity));

        return YearlyIntensityVo.builder()
                .xAxis(months)
                .highSeries(months.stream()
                        .map(m -> highMap.getOrDefault((String) m, 0.0))
                        .collect(Collectors.toList()))
                .lowSeries(months.stream()
                        .map(m -> lowMap.getOrDefault((String) m, 0.0))
                        .collect(Collectors.toList()))
                .build();
    }

    @Override
    public List<DistributionRangeVo> getDayDistribution() {
        List<WeatherRangeDistribution> list = weatherRangeDistributionMapper.findAll();

        return list.stream()
                .collect(Collectors.groupingBy(WeatherRangeDistribution::getYear))
                .entrySet().stream()
                .map(entry -> {
                    // 使用 Builder 模式构建对象，代码更加直观
                    DistributionRangeVo.DistributionRangeVoBuilder builder = DistributionRangeVo.builder()
                            .year(entry.getKey())
                            .range0to5(0L).range5to10(0L).range10to15(0L).rangeOver15(0L); // 默认初始化

                    // 填充数据
                    entry.getValue().forEach(item -> {
                        switch (item.getRangeBucket()) {
                            case "0-5℃": builder.range0to5(item.getCnt()); break;
                            case "5-10℃": builder.range5to10(item.getCnt()); break;
                            case "10-15℃": builder.range10to15(item.getCnt()); break;
                            case ">15℃": builder.rangeOver15(item.getCnt()); break;
                        }
                    });
                    return builder.build();
                })
                .sorted(Comparator.comparing(DistributionRangeVo::getYear))
                .collect(Collectors.toList());
    }

    @Override
    public List<DistributionCorrelationVo> getDayDistributionByMonth() {
        return weatherDwdMapper.getDiurnalCorrelation();
    }

    @Override
    public List<DistributionMonthlyVo> getDiurnalMonthly() {
        return weatherDwdMapper.getDiurnalMonthly();
    }

    @Override
    public List<DistributionSeason> getDiurnalSeason() {
        return weatherDwdMapper.getDiurnalSeason();
    }

    @Override
    public List<WeatherForecast> getForecast() {
        return weatherForecastMapper.queryAll();
    }

    @Override
    public List<WeatherData> getActualData() {
        return weatherDataMapper.queryAll();
    }
}
