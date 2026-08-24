package com.example.weathershow.mapper;

import com.example.weathershow.pojo.WeatherData;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;
/**
 * @author X
 * @date 2026/6/14 16:54
 */
@Mapper
public interface WeatherDataMapper {
    // 查询全部
    @Select("SELECT city_name, date, avg_temp, min_temp, max_temp, temp_diff, season \n" +
            "FROM weather_data_2024;")
    List<WeatherData> queryAll();
}
