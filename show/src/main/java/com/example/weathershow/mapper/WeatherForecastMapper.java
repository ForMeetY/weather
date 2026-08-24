package com.example.weathershow.mapper;

import com.example.weathershow.pojo.WeatherForecast;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;
/**
 * @author X
 * @date 2026/6/14 14:49
 */

@Mapper
public interface WeatherForecastMapper {

    // 查询全部
    public List<WeatherForecast> queryAll();

}
