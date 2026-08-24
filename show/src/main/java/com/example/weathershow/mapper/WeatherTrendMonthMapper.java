package com.example.weathershow.mapper;

import com.example.weathershow.pojo.WeatherTrendMonth;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;
@Mapper
public interface WeatherTrendMonthMapper {

    // 查询全部数据
    List<WeatherTrendMonth> queryAll();
}
