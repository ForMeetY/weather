package com.example.weathershow.mapper;


import com.example.weathershow.pojo.DistributionMonthlyVo;
import com.example.weathershow.pojo.WeatherRangeDistribution;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface WeatherRangeDistributionMapper {

    List<WeatherRangeDistribution> findAll();


}
