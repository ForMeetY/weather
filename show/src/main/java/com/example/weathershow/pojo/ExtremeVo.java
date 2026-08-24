package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
/**
 * @author X
 * @date 2026/6/10 16:34
 */

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ExtremeVo {
    private List<Object> xAxis;      // 年份列表
    private List<Object> highSeries; // 高温频次
    private List<Object> lowSeries;  // 低温频次
}
