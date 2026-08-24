package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @author X
 * @date 2026/6/9 18:50
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class WeatherExtreme {
    private Integer year;              // 年份
    private Integer month;             // 月份
    private String season;             // 季节
    private String extremeType;        // 极端类型: EXTREME_HIGH 或 EXTREME_LOW
    private Integer occurrenceCount;   // 发生天数
    private Double thresholdValue;     // 判定阈值
    private Double avgIntensity;       // 极端偏离强度


    // 辅助字段（用于 API 返回时的数据重组，不在表中）
    private Integer totalCount;        // 用于聚合查询时统计总数

}
