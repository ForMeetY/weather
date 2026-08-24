package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @author X
 * @date 2026/6/11 17:23
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class DistributionMonthlyVo {
    private String monthDimension;
    private Double avgDailyRange;
    private Double maxDailyRange;
    private Double minDailyRange;
    private Double stdDailyRange;
}
