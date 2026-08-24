package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @author X
 * @date 2026/6/9 18:51
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class WeatherRangeDistribution {
    private String rangeBucket; // 对应 range_bucket
    private Integer year;
    private Long cnt;
}
