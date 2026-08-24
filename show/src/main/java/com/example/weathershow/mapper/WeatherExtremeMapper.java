package com.example.weathershow.mapper;

import com.example.weathershow.pojo.SeasonExtremeVo;
import com.example.weathershow.pojo.WeatherExtreme;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface WeatherExtremeMapper {

    // 查询各年份各类型的极端天气总数
    List<WeatherExtreme> queryAllGroupByYearAndType();

    // 获取各季节的极端天气数据
    List<SeasonExtremeVo> getExtremeBySeason();

    // 极端天气月份热力图
    List<WeatherExtreme> getExtremeByMonth();

    // 按年聚合偏差强度均值（高温/低温分别一行）
    List<WeatherExtreme> getYearlyAvgIntensity();

    // 按年统计高温/低温天数（用于趋势对比）
    List<WeatherExtreme> getYearlyCountByType();

    // 按月统计

    // 按日统计
    List<WeatherExtreme> getMonthlyAvgIntensity();

}
