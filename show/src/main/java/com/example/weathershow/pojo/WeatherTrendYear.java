package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @author X
 * @date 2026/6/9 18:52
 */

@Data
@AllArgsConstructor
@NoArgsConstructor
public class WeatherTrendYear {
    private Integer year;
    private Double avgTemp;
    private Double minTemp;
    private Double maxTemp;
    private Double avgDailyRange;
}
