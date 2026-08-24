package com.example.weathershow.mapper;

import com.example.weathershow.pojo.WeatherTrendYear;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;
@Mapper
public interface WeatherTrendYearMapper {
    // 查询全部数据
    List<WeatherTrendYear> queryAll();

}
