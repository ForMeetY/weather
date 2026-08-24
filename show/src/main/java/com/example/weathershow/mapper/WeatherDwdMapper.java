package com.example.weathershow.mapper;


import com.example.weathershow.pojo.DistributionCorrelationVo;
import com.example.weathershow.pojo.DistributionMonthlyVo;
import com.example.weathershow.pojo.DistributionSeason;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;
@Mapper
public interface WeatherDwdMapper {
    //日较差与平均气温相关性 做散点
    List<DistributionCorrelationVo> getDiurnalCorrelation();
    //月度日较差统计折线图
    List<DistributionMonthlyVo> getDiurnalMonthly();
    // 日较差季节
    List<DistributionSeason> getDiurnalSeason();
}
