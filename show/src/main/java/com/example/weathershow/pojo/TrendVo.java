package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
/**
 * @author X
 * @date 2026/6/9 19:32
 */

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class TrendVo {
    private List<Object> xAxis;       // 年份或月份
    private List<Double> avgSeries;   // 平均气温序列
    private List<Double> maxSeries;   // 最高气温序列
    private List<Double> minSeries;   // 最低气温序列
    private List<Double> rangeSeries; // 日较差序列
}
