package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
/**
 * @author X
 * @date 2026/6/10 17:53
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class YearlyIntensityVo {
    private List<Object> xAxis;       // 年份列表
    private List<Double> highSeries;  // 高温年均偏差强度
    private List<Double> lowSeries;   // 低温年均偏差强度
}
