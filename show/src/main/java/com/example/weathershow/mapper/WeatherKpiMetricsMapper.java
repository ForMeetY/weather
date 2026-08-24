package com.example.weathershow.mapper;


import com.example.weathershow.pojo.WeatherKpiMetrics;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface WeatherKpiMetricsMapper {
    // 查询全部数据
    WeatherKpiMetrics queryAll();
}
