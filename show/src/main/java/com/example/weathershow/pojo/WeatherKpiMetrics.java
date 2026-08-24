package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * @author X
 * @date 2026/6/9 19:09
 */

@Data
@AllArgsConstructor
@NoArgsConstructor
public class WeatherKpiMetrics {
    private Integer id;
    private Double avgAll;
    private Double highThreshold;
    private Double lowThreshold;
    private Double avgRangeAll;
    private LocalDateTime updateTime;
}
